import type { Chapter } from '@/types';
import { generateId } from '@/lib/utils';

const PREFIX = 'draftharbour_draft_journal_v1_';
// A new page lifetime gets a new journal namespace, including in the same tab.
const sessionId = generateId();
export interface RecoveryDraft {
  key: string;
  chapter: Chapter;
  updates: Partial<Chapter>;
  savedAt: number;
}

export function journalChapter(chapter: Chapter, updates: Partial<Chapter>): void {
  const key = `${PREFIX}${sessionId}_${chapter.id}`;
  const raw = localStorage.getItem(key);
  const previous: RecoveryDraft | null = raw ? JSON.parse(raw) : null;
  localStorage.setItem(key, JSON.stringify({ key, chapter: previous?.chapter || chapter,
    updates: { ...previous?.updates, ...updates }, savedAt: Date.now() } satisfies RecoveryDraft));
}

export function commitJournalChapter(id: string, updates: Partial<Chapter>): void {
  const key = `${PREFIX}${sessionId}_${id}`;
  const raw = localStorage.getItem(key);
  if (!raw) return;
  const draft: RecoveryDraft = JSON.parse(raw);
  // A newer edit can arrive while IndexedDB is writing. Never erase that edit.
  for (const field of Object.keys(updates) as Array<keyof Chapter>) {
    if (JSON.stringify(draft.updates[field]) === JSON.stringify(updates[field])) delete draft.updates[field];
  }
  if (Object.keys(draft.updates).length) localStorage.setItem(key, JSON.stringify(draft));
  else localStorage.removeItem(key);
}

export function listRecoveryDrafts(includeCurrent = false): RecoveryDraft[] {
  const drafts: RecoveryDraft[] = [];
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (!key?.startsWith(PREFIX) || (!includeCurrent && key.startsWith(`${PREFIX}${sessionId}_`))) continue;
    try {
      const draft = JSON.parse(localStorage.getItem(key)!);
      if (draft?.chapter?.id && draft.chapter.novelId && draft.updates && typeof draft.updates === 'object') drafts.push({ ...draft, key });
    } catch { /* Preserve unreadable journals rather than deleting them. */ }
  }
  return drafts.sort((a, b) => b.savedAt - a.savedAt);
}

export function dismissRecoveryDraft(key: string): void {
  if (!key.startsWith(PREFIX)) throw new Error('Invalid recovery journal key');
  localStorage.removeItem(key);
}
