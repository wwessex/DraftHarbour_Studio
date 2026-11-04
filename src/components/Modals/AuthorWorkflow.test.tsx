import { StoryBibleEntries } from './StoryBibleEntries';
import { newBibleEntry, persistBibleEntry, loadBibleEntries } from '@/lib/storyBibleEntries';
/** @vitest-environment jsdom */
import { act, type ReactNode } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { createChapter } from '@/lib/storage';
import { OnboardingModal } from './OnboardingModal';
import { CharacterBibleModal } from './CharacterBibleModal';
import { ExportHistoryModal } from './ExportHistoryModal';
import { OutlinePanel } from '../Sidebar/OutlinePanel';
import { recordExport } from '@/lib/exportHistory';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
const mocks = vi.hoisted(() => ({ select: vi.fn(), update: vi.fn(), blueprint: vi.fn(), add: vi.fn(), scene: vi.fn(), remove: vi.fn(), close: vi.fn(), toast: vi.fn() }));
const chapter = createChapter('n1', 0);
const state = { novelId: 'n1', projectType: 'book', chapters: [chapter], activeChapterId: chapter.id, storyBlueprint: null };
const context = { state, activeChapter: chapter, setActiveChapter: mocks.select, updateChapterImmediate: mocks.update, updateStoryBlueprint: mocks.blueprint, addScene: mocks.add, updateScene: mocks.scene, deleteScene: mocks.remove };
vi.mock('@/context/AppContext', () => ({ useApp: () => context }));
const toast = { showToast: mocks.toast };
vi.mock('@/components/UI', async () => ({ ...await vi.importActual('@/components/UI'), useToast: () => toast,
  Dialog: ({ open, children, footer }: { open: boolean; children: ReactNode; footer?: ReactNode }) => open ? <div>{children}{footer}</div> : null,
}));
let root: Root;
let host: HTMLDivElement;
beforeEach(() => { vi.clearAllMocks(); state.novelId = 'n1'; state.projectType = 'book'; chapter.content = ''; host = document.createElement('div'); document.body.appendChild(host); root = createRoot(host); });
afterEach(async () => { await act(async () => root.unmount()); host.remove(); });
const button = (text: string) => [...document.querySelectorAll('button')].find(item => item.textContent?.includes(text))!;
const click = async (text: string) => { const target = button(text); expect(target).toBeDefined(); await act(async () => target.click()); };
const fill = async (placeholder: string, value: string) => {
  const input = document.querySelector(`[placeholder="${placeholder}"]`) as HTMLInputElement;
  expect(input).not.toBeNull();
  await act(async () => { Object.getOwnPropertyDescriptor(input.tagName === 'TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype, 'value')!.set!.call(input, value); input.dispatchEvent(new Event('input', { bubbles: true })); });
};

it('starts writing immediately and keeps the optional blueprint wizard usable', async () => {
  await act(async () => root.render(<OnboardingModal open onClose={mocks.close} />));
  await click('Start Writing');
  expect(mocks.close).toHaveBeenCalledOnce();
  expect(mocks.blueprint).not.toHaveBeenCalled();
  await click('Create Blueprint');
  await fill('Genre (e.g. Fantasy)', 'Mystery');
  await click('Next'); await fill('Audience (e.g. Adult thriller readers)', 'Adult');
  await click('Next'); await fill('Tone (e.g. brooding, intimate)', 'Warm');
  await click('Next'); await click('Next'); await fill('Target word count', '90000');
  await click('Save Blueprint');
  expect(mocks.blueprint).toHaveBeenCalledWith(expect.objectContaining({ genre: 'Mystery', targetAudience: 'Adult', tone: 'Warm', targetWordCount: 90000 }));
  await click('Quick Tips'); expect(document.body.textContent).toContain('Use snapshots before major rewrites');
});

it('keeps empty outlines quiet while retaining editable chapter and scene planning', async () => {
  await act(async () => root.render(<OutlinePanel />));
  expect(document.body.textContent).not.toContain('No critical recommendations');
  await click('Heuristic Insights');
  expect(document.body.textContent).toContain('No critical recommendations');
  await fill('Point of view', 'Alice');
  expect(mocks.update).toHaveBeenCalledWith(chapter.id, { pov: 'Alice' });
  await click('Scenes'); await click('Add Scene');
  expect(mocks.add).toHaveBeenCalledWith(chapter.id);
  await click(chapter.title); expect(mocks.select).toHaveBeenCalledWith(chapter.id);
});

it('links story-bible evidence to chapters and reloads entries on project changes', async () => {
  chapter.content = 'Alice waited at the Quay.';
  localStorage.setItem('draftharbour_characters', JSON.stringify([{ id: 'alice', novelId: 'n1', name: 'Alice', aliases: [], description: '', role: 'supporting', traits: [], notes: '', relationships: [], createdAt: 1, updatedAt: 1 }, { id: 'other', novelId: 'n2', name: 'Private other character', aliases: [], description: '', role: 'supporting', traits: [], notes: '', relationships: [], createdAt: 1, updatedAt: 1 }]));
  await act(async () => root.render(<CharacterBibleModal open onClose={mocks.close} />));
  await click('Characters & World');
  expect(document.body.textContent).not.toContain('Private other character');
  const alice = [...document.querySelectorAll('span')].find(item => item.textContent === 'Alice')!;
  await act(async () => alice.click());
  expect(document.body.textContent).toContain('Manuscript mentions (1)');
  await click('Alice waited at the Quay.'); expect(mocks.select).toHaveBeenCalledWith(chapter.id);
  await fill('Comma-separated aliases', 'Al');
  expect(JSON.parse(localStorage.getItem('draftharbour_characters')!)[0].aliases).toEqual(['Al']);
  await click('Add Character'); await fill('Character Name', 'Bob');
  expect(localStorage.getItem('draftharbour_characters')).toContain('Bob');
  await click('World ('); await click('Add Entry'); await fill('Entry Name', 'Quay');
  expect(document.body.textContent).toContain('Manuscript mentions (1)');
  await fill('Detailed description...', 'Old harbour');
  expect(localStorage.getItem('draftharbour_world')).toContain('Old harbour');
  state.novelId = 'n2';
  await act(async () => root.render(<CharacterBibleModal open onClose={mocks.close} />));
  expect(document.body.textContent).not.toContain('Old harbour');
  await click('Characters (');
  expect(document.body.textContent).toContain('Private other character');
  expect(document.body.textContent).not.toContain('Alice');
});

it('records EPUB handoff history and removes history without affecting manuscripts', async () => {
  recordExport({ format: 'epub', filename: 'Novel.epub', novelTitle: 'Novel', chapterCount: 1, wordCount: 10, preset: 'ebook' });
  await act(async () => root.render(<ExportHistoryModal open onClose={mocks.close} />));
  expect(document.body.textContent).toContain('Novel.epub');
  expect(document.body.textContent).toContain('auto_stories');
  await act(async () => (document.querySelector('[aria-label="Remove from history"]') as HTMLButtonElement).click());
  expect(document.body.textContent).toContain('No exports recorded yet');
  expect(chapter.id).toBe(state.chapters[0].id);
});

it('edits, searches, archives and restores Story Bible entries without altering manuscripts', async () => {
  await act(async () => root.render(<CharacterBibleModal open onClose={mocks.close} />));
  await click('New entry');
  const title = [...document.querySelectorAll('label')].find(e => e.firstChild?.textContent === 'Title')!.querySelector('input')!;
  const setTitle = async (value: string) => act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(title, value);
    title.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await setTitle('Mara Venn');
  await click('Save entry');
  expect(localStorage.getItem('draftharbour_bible_entries')).toContain('Mara Venn');
  await setTitle('Captain Venn');
  await click('Save entry');
  await click('Restore this version');
  expect(title.value).toBe('Mara Venn');
  expect(JSON.parse(localStorage.getItem('draftharbour_bible_entries')!)[0].revisions).toHaveLength(2);
  await click('Archive entry');
  expect(JSON.parse(localStorage.getItem('draftharbour_bible_entries')!)[0].archived).toBe(true);
  await click('Unarchive entry');
  expect(JSON.parse(localStorage.getItem('draftharbour_bible_entries')!)[0].archived).toBe(false);
  expect(mocks.update).not.toHaveBeenCalled();
});

it('saves AI field controls, hides renamed custom fields and retains policy history', async () => {
  localStorage.removeItem('draftharbour_bible_entries');
  const entry = { ...newBibleEntry('n1'), title: 'Policy case', status: 'canon' as const, fields: { Voice: 'Soft' } };
  persistBibleEntry(entry);
  await act(async () => root.render(<StoryBibleEntries />));
  await click('Policy case');
  const field = [...host.querySelectorAll('textarea')].find(input => input.placeholder === 'Goal: Find the missing ship')!;
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')!.set!.call(field, 'Voice: Soft\nForm: Human hands');
    field.dispatchEvent(new Event('input', { bubbles: true }));
  });
  const checkbox = (label: string) => [...host.querySelectorAll('label')].find(node => node.textContent === label)?.querySelector('input') as HTMLInputElement;
  expect(checkbox(' Allow Form').checked).toBe(false);
  await act(async () => checkbox(' Allow Form').click());
  await act(async () => checkbox(' Allow Notes').click());
  const condition = [...host.querySelectorAll('label')].find(node => node.textContent === 'Only use Form when')!.querySelector('input')!;
  await act(async () => {
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')!.set!.call(condition, 'form=human');
    condition.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await click('Save entry');
  const saved = loadBibleEntries('n1')[0];
  expect(saved.aiAccess?.hiddenFields).toContain('body');
  expect(saved.aiAccess?.hiddenFields).not.toContain('field:Form');
  expect(saved.aiAccess?.conditions?.['field:Form']).toBe('form=human');
  expect(saved.revisions[0].state.aiAccess).toBeUndefined();
});
