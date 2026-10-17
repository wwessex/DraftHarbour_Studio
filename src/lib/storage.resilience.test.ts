/** @vitest-environment jsdom */
import 'fake-indexeddb/auto';
import { webcrypto } from 'node:crypto';
import { beforeEach, expect, it, vi } from 'vitest';
import Dexie from 'dexie';
import { clearAllData } from './storage';
import type { CharacterEntity, WorldEntry, StoryBlueprint } from '@/types';
import { addChapter, createChapter, createNovel, createProjectBackup, createSnapshot, db, deleteChapter, deleteNovel, exportBackup, getChapters, getCommentThreads, getSnapshots, getStoryBlueprint, importBackup, listProjectBackups, listTrash, restoreProjectBackup, restoreTrash, upsertCommentThread, upsertStoryBlueprint } from './storage';

beforeEach(async () => {
  vi.stubGlobal('crypto', webcrypto);
  await db.open();
  await db.transaction('rw', db.tables, async () => { for (const table of db.tables) await table.clear(); });
});

async function seed() {
  const novel = await createNovel('Complete novel');
  const chapter = createChapter(novel.id, 0); chapter.content = 'A complete draft';
  await addChapter(chapter);
  const base = { novelId: novel.id, aliases: [], description: '', role: 'supporting' as const, traits: [], notes: 'Research notes', createdAt: 1, updatedAt: 1 };
  const characters: CharacterEntity[] = [{ ...base, id: 'alice', name: 'Alice', relationships: [{ targetId: 'bob', type: 'friend' }] }, { ...base, id: 'bob', name: 'Bob', relationships: [] }];
  const world: WorldEntry[] = [{ id: 'quay', novelId: novel.id, name: 'Quay', category: 'location', description: 'Location research', tags: [], linkedCharacters: ['alice'], notes: 'Map notes', createdAt: 1, updatedAt: 1 }];
  localStorage.setItem('draftharbour_characters', JSON.stringify(characters));
  localStorage.setItem('draftharbour_world', JSON.stringify(world));
  const blueprint: StoryBlueprint = { genre: 'Mystery', subgenre: '', targetAudience: 'Adult', ageBand: '', tone: 'Warm', voice: '', structure: 'three-act', targetWordCount: 80000, pacingProfile: 'balanced' };
  upsertStoryBlueprint(novel.id, blueprint);
  upsertCommentThread({ id: 'thread', chapterId: chapter.id, anchor: { from: 0, to: 1, length: 1 }, resolved: false, createdAt: 1, updatedAt: 1, comments: [{ id: 'comment', author: 'Author', text: 'Keep this note', createdAt: 1 }] });
  return { novel, chapter, blueprint };
}

it('round-trips the complete project and isolates copied entity identities and relationships', async () => {
  const { novel, blueprint } = await seed();
  const backup = await exportBackup(novel.id);
  const copy = await importBackup(backup);
  const copy2 = await importBackup(backup);
  const characters = JSON.parse(localStorage.getItem('draftharbour_characters')!) as CharacterEntity[];
  const a = characters.filter(item => item.novelId === copy.id);
  expect(a).toHaveLength(2);
  expect(a[0].id).not.toBe('alice');
  expect(a[0].relationships[0].targetId).toBe(a[1].id);
  expect(new Set(characters.map(item => item.id)).size).toBe(6);
  const world = JSON.parse(localStorage.getItem('draftharbour_world')!) as WorldEntry[];
  expect(world.find(item => item.novelId === copy.id)?.linkedCharacters).toEqual([a[0].id]);
  expect(getStoryBlueprint(copy.id)).toEqual(blueprint);
  expect(getStoryBlueprint(copy2.id)).toEqual(blueprint);
  const [chapter] = await getChapters(copy.id);
  expect(getCommentThreads(chapter.id)[0].comments[0].text).toBe('Keep this note');
});

it('rolls back both imported manuscript and auxiliary writes on a quota failure', async () => {
  const { novel } = await seed();
  const backup = await exportBackup(novel.id);
  const previous = localStorage.getItem('draftharbour_characters');
  const original = localStorage.setItem.bind(localStorage);
  let failed = false;
  const spy = vi.spyOn(localStorage, 'setItem').mockImplementation((key, value) => {
    if (key === 'draftharbour_world' && !failed) { failed = true; throw new DOMException('Full', 'QuotaExceededError'); }
    original(key, value);
  });
  try { await expect(importBackup(backup)).rejects.toThrow('Full'); }
  finally { spy.mockRestore(); }
  expect(await db.novels.count()).toBe(1);
  expect(await db.chapters.count()).toBe(1);
  expect(localStorage.getItem('draftharbour_characters')).toBe(previous);
});

it('rotates only automatic backups and verifies integrity before restoring as a copy', async () => {
  const { novel } = await seed();
  const manual = await createProjectBackup(novel.id);
  for (let i = 0; i < 12; i++) {
    const [chapter] = await getChapters(novel.id);
    await db.chapters.update(chapter.id, { summary: `Revision ${i}` });
    await createProjectBackup(novel.id, true);
  }
  expect(await listProjectBackups(novel.id)).toHaveLength(11);
  expect(await db.backups.get(manual.id)).toBeDefined();
  const recovered = await restoreProjectBackup(manual.id);
  expect(recovered.id).not.toBe(novel.id);
  await db.backups.update(manual.id, { data: { ...manual.data, sections: [] } });
  await expect(restoreProjectBackup(manual.id)).rejects.toThrow('integrity');
  expect((await getChapters(novel.id))[0].content).toBe('A complete draft');
});

it.each(['chapter', 'project'])('recovers deleted %s content, snapshots and notes from trash', async kind => {
  const { novel, chapter, blueprint } = await seed();
  await createSnapshot(chapter.id, 'Earlier draft', 'Milestone');
  await (kind === 'chapter' ? deleteChapter(chapter.id) : deleteNovel(novel.id));
  const [entry] = await listTrash();
  const restored = await restoreTrash(entry.id);
  const [restoredChapter] = await getChapters(restored.id);
  expect(restoredChapter.content).toBe('A complete draft');
  expect((await getSnapshots(restoredChapter.id))[0].doc).toBe('Earlier draft');
  expect(getCommentThreads(restoredChapter.id)).toHaveLength(1);
  expect(getStoryBlueprint(restored.id)).toEqual(blueprint);
  expect(await listTrash()).toHaveLength(0);
});

it('caps automatic chapter snapshots while retaining manual and safety versions', async () => {
  const { chapter } = await seed();
  await createSnapshot(chapter.id, 'Safety', 'Before restore');
  for (let i = 0; i < 35; i++) await createSnapshot(chapter.id, `Draft ${i}`, 'Auto');
  const snapshots = await getSnapshots(chapter.id);
  expect(snapshots.filter(item => item.label === 'Auto')).toHaveLength(30);
  expect(snapshots.some(item => item.label === 'Before restore')).toBe(true);
});

it('clears the added recovery stores when all manuscript data is explicitly cleared', async () => {
  const { novel, chapter } = await seed();
  await createProjectBackup(novel.id);
  await deleteChapter(chapter.id);
  localStorage.setItem('draftharbour_draft_journal_v1_old_chapter', 'pending draft');
  await clearAllData();
  expect(await db.backups.count()).toBe(0);
  expect(await db.trash.count()).toBe(0);
  expect(await db.novels.count()).toBe(0);
  expect(localStorage.getItem('draftharbour_draft_journal_v1_old_chapter')).toBeNull();
  expect(localStorage.getItem('draftharbour_characters')).toBeNull();
});

it('upgrades a v4 database additively without changing existing manuscripts or IDs', async () => {
  await db.delete();
  const legacy = new Dexie('DraftHarbourDB');
  legacy.version(4).stores({ novels: 'id, title, projectType, updatedAt', chapters: 'id, novelId, order, title, updatedAt', snapshots: 'id, chapterId, createdAt' });
  await legacy.open();
  await legacy.table('novels').add({ id: 'legacy-novel', title: 'Keep me', projectType: 'book', updatedAt: 1 });
  const chapter = { ...createChapter('legacy-novel', 0), id: 'legacy-chapter', content: 'Existing manuscript' };
  await legacy.table('chapters').add(chapter);
  legacy.close();
  await db.open();
  expect(await db.chapters.get('legacy-chapter')).toEqual(chapter);
  expect(await db.backups.count()).toBe(0);
  expect(await db.trash.count()).toBe(0);
});
