import { addChapter, createNovel, getChapters, getNovel } from '@/lib/storage';
import { dismissRecoveryDraft, type RecoveryDraft } from '@/lib/recoveryJournal';
import { generateId } from '@/lib/utils';

export async function recoverDraftAsCopy(draft: RecoveryDraft): Promise<{ novelId: string; chapterId: string }> {
  const novel = await getNovel(draft.chapter.novelId) || await createNovel('Recovered writing');
  const chapters = await getChapters(novel.id);
  const chapter = {
    ...draft.chapter, ...draft.updates,
    id: generateId(), novelId: novel.id, order: chapters.length,
    title: `${draft.updates.title || draft.chapter.title} (Recovered)`, updatedAt: Date.now(),
  };
  await addChapter(chapter);
  dismissRecoveryDraft(draft.key);
  return { novelId: novel.id, chapterId: chapter.id };
}
