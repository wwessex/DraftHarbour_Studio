import { addChapter, createSnapshot, db, deleteChapter, getChapter, getChapters, getCommentThreads, saveAllCommentThreads, updateChapter } from '@/lib/storage';
import { generateId } from '@/lib/utils';
import type { CommentThread } from '@/types';

async function withCommentRollback(ids: string[], operation: () => Promise<void>) {
  const previous = ids.map(id => [id, getCommentThreads(id)] as const);
  try {
    await db.transaction('rw', [db.novels, db.chapters, db.snapshots, db.trash], operation);
  } catch (cause) {
    for (const [id, threads] of previous) saveAllCommentThreads(id, threads);
    throw cause;
  }
}

export async function splitChapterAt(id: string, position: number): Promise<string> {
  const chapter = await getChapter(id);
  if (!chapter || !Number.isInteger(position) || position <= 0 || position >= (chapter.content || '').length) throw new Error('Place the cursor inside the chapter before splitting.');
  const threads = getCommentThreads(id);
  if (threads.some(thread => thread.anchor.from < position && thread.anchor.to > position)) throw new Error('Move the cursor outside a commented passage before splitting.');
  const newId = generateId();
  await withCommentRollback([id, newId], async () => {
    await createSnapshot(id, chapter.content || '', 'Before split');
    const chapters = await getChapters(chapter.novelId);
    for (const other of chapters) if (other.order > chapter.order) await updateChapter(other.id, { order: other.order + 1 });
    await updateChapter(id, { content: chapter.content!.slice(0, position) });
    await addChapter({ ...chapter, id: newId, order: chapter.order + 1, title: `${chapter.title} (continued)`, content: chapter.content!.slice(position), scenes: [], sync: { providerRevisionIds: {}, lastSyncedContent: null }, updatedAt: Date.now() });
    saveAllCommentThreads(id, threads.filter(thread => thread.anchor.to <= position));
    saveAllCommentThreads(newId, threads.filter(thread => thread.anchor.from >= position).map(thread => ({ ...thread, chapterId: newId,
      anchor: { ...thread.anchor, from: thread.anchor.from - position, to: thread.anchor.to - position } })));
  });
  return newId;
}

export async function mergeWithNextChapter(id: string): Promise<void> {
  const chapter = await getChapter(id);
  if (!chapter) throw new Error('Chapter not found');
  const chapters = await getChapters(chapter.novelId);
  const next = chapters[chapters.findIndex(item => item.id === id) + 1];
  if (!next) throw new Error('There is no following chapter to merge.');
  const separator = '\n\n';
  const offset = (chapter.content || '').length + separator.length;
  const threads: CommentThread[] = [ ...getCommentThreads(id), ...getCommentThreads(next.id).map(thread => ({ ...thread, chapterId: id,
    anchor: { ...thread.anchor, from: thread.anchor.from + offset, to: thread.anchor.to + offset } })) ];
  await withCommentRollback([id, next.id], async () => {
    await createSnapshot(id, chapter.content || '', 'Before merge');
    // Archive the original following chapter before changing either manuscript.
    await deleteChapter(next.id);
    await updateChapter(id, {
      content: `${chapter.content || ''}${separator}${next.content || ''}`,
      summary: [chapter.summary, next.summary].filter(Boolean).join('\n\n'),
      tags: [...new Set([...chapter.tags, ...next.tags])],
      wordGoal: chapter.wordGoal + next.wordGoal,
      scenes: [...(chapter.scenes || []), ...(next.scenes || [])],
    });
    saveAllCommentThreads(id, threads);
    for (const [order, remaining] of (await getChapters(chapter.novelId)).entries()) await updateChapter(remaining.id, { order });
  });
}

export async function moveSceneToChapter(sourceId: string, targetId: string, sceneId: string): Promise<void> {
  if (sourceId === targetId) return;
  await db.transaction('rw', db.chapters, async () => {
    const source = await getChapter(sourceId), target = await getChapter(targetId);
    if (!source || !target || source.novelId !== target.novelId) throw new Error('Scenes can only move between chapters in the same project.');
    const scene = source.scenes.find(item => item.id === sceneId);
    if (!scene || target.scenes.some(item => item.id === sceneId)) throw new Error('Scene not found or already present in the target chapter.');
    await updateChapter(sourceId, { scenes: source.scenes.filter(item => item.id !== sceneId) });
    await updateChapter(targetId, { scenes: [...target.scenes, scene] });
  });
}
