/** @vitest-environment jsdom */
import 'fake-indexeddb/auto';
import { beforeEach, expect, it } from 'vitest';
import { addChapter, createChapter, createNovel, db, getChapter, getChapters, getCommentThreads, getSnapshots, listTrash, upsertCommentThread } from './storage';
import { splitChapterAt, mergeWithNextChapter, moveSceneToChapter } from './chapterOperations';

beforeEach(async () => {
  await db.open();
  await db.transaction('rw', db.tables, async () => { for (const table of db.tables) await table.clear(); });
});
async function seed() {
  const novel = await createNovel('Novel');
  const chapter = createChapter(novel.id, 0); chapter.content = 'First halfSecond half'; chapter.tags = ['tag']; chapter.part = 'Act One';
  await addChapter(chapter);
  return { novel, chapter };
}
it('splits text without losing content, keeps metadata and remaps comments after the cursor', async () => {
  const { novel, chapter } = await seed();
  upsertCommentThread({ id: 'note', chapterId: chapter.id, anchor: { from: 10, to: 16, length: 6 }, resolved: false, comments: [], createdAt: 1, updatedAt: 1 });
  const newId = await splitChapterAt(chapter.id, 10);
  const chapters = await getChapters(novel.id);
  expect(chapters.map(item => item.content).join('')).toBe(chapter.content);
  expect(chapters[1].part).toBe('Act One');
  expect(getCommentThreads(newId)[0].anchor.from).toBe(0);
  expect(getCommentThreads(chapter.id)).toHaveLength(0);
  expect((await getSnapshots(chapter.id))[0].doc).toBe(chapter.content);
});
it('refuses to split a comment anchor or an invalid cursor position', async () => {
  const { novel, chapter } = await seed();
  upsertCommentThread({ id: 'note', chapterId: chapter.id, anchor: { from: 5, to: 15, length: 10 }, resolved: false, comments: [], createdAt: 1, updatedAt: 1 });
  await expect(splitChapterAt(chapter.id, 10)).rejects.toThrow('commented');
  await expect(splitChapterAt(chapter.id, 0)).rejects.toThrow('cursor');
  expect(await getChapters(novel.id)).toHaveLength(1);
});
it('merges chapters with a safety snapshot and a recoverable original of the following chapter', async () => {
  const { novel, chapter } = await seed();
  const next = createChapter(novel.id, 1); next.content = 'Following chapter'; next.summary = 'Notes'; next.tags = ['next'];
  await addChapter(next);
  await mergeWithNextChapter(chapter.id);
  expect(await getChapters(novel.id)).toHaveLength(1);
  expect((await getChapter(chapter.id))?.content).toBe(`${chapter.content}\n\n${next.content}`);
  expect((await getChapter(chapter.id))?.tags).toEqual(['tag', 'next']);
  expect((await listTrash())[0].data.sections[0].content).toBe(next.content);
  expect((await getSnapshots(chapter.id))[0].label).toBe('Before merge');
});
it('moves all scene metadata atomically and rejects cross-project moves', async () => {
  const { novel, chapter } = await seed();
  const scene = { id: 'scene', title: 'A scene', summary: 'All notes', pov: 'Alice', status: 'draft' as const, tags: ['a'], wordGoal: 500 };
  await db.chapters.update(chapter.id, { scenes: [scene] });
  const target = createChapter(novel.id, 1); await addChapter(target);
  await moveSceneToChapter(chapter.id, target.id, scene.id);
  expect((await getChapter(target.id))?.scenes).toEqual([scene]);
  expect((await getChapter(chapter.id))?.scenes).toHaveLength(0);
  const other = createChapter((await createNovel('Other')).id, 0); await addChapter(other);
  await expect(moveSceneToChapter(target.id, other.id, scene.id)).rejects.toThrow('same project');
  expect((await getChapter(target.id))?.scenes).toEqual([scene]);
});
