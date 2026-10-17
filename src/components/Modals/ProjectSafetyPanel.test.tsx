/** @vitest-environment jsdom */
import 'fake-indexeddb/auto';
import { webcrypto } from 'node:crypto';
import { act } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { addChapter, createChapter, createNovel, db, getChapters } from '@/lib/storage';
import { ProjectSafetyPanel } from './ProjectSafetyPanel';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
const mocks = vi.hoisted(() => ({ novelId: '', flush: vi.fn(async () => {}), load: vi.fn(async () => {}), select: vi.fn(), toast: vi.fn() }));
const toastValue = { showToast: mocks.toast };
vi.mock('@/components/UI', async () => ({ ...await vi.importActual('@/components/UI'), useToast: () => toastValue }));
vi.mock('@/context/AppContext', () => ({ useApp: () => ({ state: { novelId: mocks.novelId }, flushPendingSaves: mocks.flush, loadNovelById: mocks.load, setActiveChapter: mocks.select }) }));
let root: Root;
let container: HTMLDivElement;
const onRestored = vi.fn();
beforeEach(async () => {
  vi.stubGlobal('crypto', webcrypto);
  vi.clearAllMocks();
  await db.open();
  await db.transaction('rw', db.tables, async () => { for (const table of db.tables) await table.clear(); });
  mocks.novelId = (await createNovel('Original')).id;
  container = document.createElement('div'); document.body.appendChild(container); root = createRoot(container);
});
afterEach(async () => { await act(async () => root.unmount()); container.remove(); });
const click = async (text: string) => {
  const button = [...container.querySelectorAll('button')].find(item => item.textContent?.includes(text));
  expect(button).toBeDefined();
  await act(async () => button!.click());
  await vi.waitFor(async () => {
    await act(async () => { await Promise.resolve(); });
    expect(!button!.isConnected || !button!.disabled).toBe(true);
  });
};

it('creates a verified backup and restores a separate project without replacing the original', async () => {
  await act(async () => root.render(<ProjectSafetyPanel onRestored={onRestored} />));
  await click('Create verified backup');
  expect(await db.backups.count()).toBe(1);
  expect(container.textContent).toContain('Manual');
  await click('Restore as project copy');
  expect(mocks.flush).toHaveBeenCalledTimes(2);
  expect(mocks.load).toHaveBeenCalled();
  expect(await db.novels.count()).toBe(2);
  expect(await db.novels.get(mocks.novelId)).toBeDefined();
});
it('compares saved and recovery text, then recovers as a new chapter', async () => {
  const chapter = createChapter(mocks.novelId, 0); chapter.content = 'Saved original'; await addChapter(chapter);
  const key = 'draftharbour_draft_journal_v1_previous_chapter';
  localStorage.setItem(key, JSON.stringify({ key, chapter, updates: { content: 'Unsaved writing' }, savedAt: 1 }));
  await act(async () => root.render(<ProjectSafetyPanel onRestored={onRestored} />));
  expect(container.textContent).toContain('Saved original');
  expect(container.textContent).toContain('Unsaved writing');
  await click('Recover as new chapter');
  const chapters = await getChapters(mocks.novelId);
  expect(chapters.map(item => item.content)).toEqual(['Saved original', 'Unsaved writing']);
  expect(localStorage.getItem(key)).toBeNull();
  expect(mocks.select).toHaveBeenCalledWith(chapters[1].id);
});
