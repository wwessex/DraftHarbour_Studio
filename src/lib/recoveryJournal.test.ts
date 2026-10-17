/** @vitest-environment jsdom */
import { expect, it, vi } from 'vitest';
import { createChapter } from './storage';
import { commitJournalChapter, journalChapter, listRecoveryDrafts } from './recoveryJournal';
import { ChapterSaveQueue } from './chapterSaveQueue';

it('retains newer edits and metadata when an older write commits', () => {
  const chapter = createChapter('novel', 0); chapter.content = 'Saved draft';
  journalChapter(chapter, { content: 'First draft' });
  journalChapter(chapter, { content: 'Second draft', summary: 'Notes' });
  commitJournalChapter(chapter.id, { content: 'First draft' });
  expect(listRecoveryDrafts(true)[0].updates).toEqual({ content: 'Second draft', summary: 'Notes' });
  commitJournalChapter(chapter.id, { content: 'Second draft' });
  expect(listRecoveryDrafts(true)[0].updates).toEqual({ summary: 'Notes' });
  commitJournalChapter(chapter.id, { summary: 'Notes' });
  expect(listRecoveryDrafts(true)).toHaveLength(0);
});

it('finds uncommitted drafts after a new page lifetime without overwriting them', async () => {
  const chapter = createChapter('novel', 0); chapter.content = 'Saved';
  journalChapter(chapter, { content: 'Recover this' });
  vi.resetModules();
  const reloaded = await import('./recoveryJournal');
  expect(reloaded.listRecoveryDrafts()[0].updates.content).toBe('Recover this');
  reloaded.journalChapter(chapter, { content: 'New page edit' });
  expect(reloaded.listRecoveryDrafts()[0].updates.content).toBe('Recover this');
});

it('keeps journaled text after a failed primary write and removes it after retry', async () => {
  const chapter = createChapter('novel', 0);
  const write = vi.fn(async () => {}).mockRejectedValueOnce(new Error('Disk full'));
  const queue = new ChapterSaveQueue(write, vi.fn(), vi.fn(), 1000, {
    stage: (_id, updates) => journalChapter(chapter, updates), commit: commitJournalChapter,
  });
  queue.enqueue(chapter.id, { content: 'Recover this' });
  await expect(queue.flush()).rejects.toThrow('Disk full');
  expect(listRecoveryDrafts(true)[0].updates.content).toBe('Recover this');
  await queue.flush();
  expect(listRecoveryDrafts(true)).toHaveLength(0);
});
