/** @vitest-environment jsdom */
import 'fake-indexeddb/auto';
import { readFileSync } from 'node:fs';
import { beforeEach, expect, it, vi } from 'vitest';
import { BIBLE_ENTRIES_KEY, bibleMarkdown, importBibleEntries, loadBibleEntries, newBibleEntry, persistBibleEntry, reviseBibleEntry } from './storyBibleEntries';
import { db, exportBackup, importBackup, exportDhproj, importDhproj } from './storage';
import { loadCharacterBibleEntities } from './ai/storyBible';
import JSZip from 'jszip';

const fixture = JSON.parse(readFileSync('fixtures/story-bible-v1.json', 'utf8'));
beforeEach(async () => {
  localStorage.clear();
  await db.open();
  await db.transaction('rw', db.tables, async () => { for (const table of db.tables) await table.clear(); });
});
it('separates project entries and admits only live canon to AI context', () => {
  const draft = newBibleEntry('a'); persistBibleEntry(draft);
  persistBibleEntry({ ...newBibleEntry('b'), title: 'Private' });
  expect(loadCharacterBibleEntities('a')).toEqual([]);
  persistBibleEntry(reviseBibleEntry(draft, { ...draft, title: 'Mara', status: 'canon', validFrom: 'Chapter 2' }));
  expect(loadCharacterBibleEntities('a')[0]).toMatchObject({ name: 'Mara', description: 'Validity: Chapter 2 to unspecified' });
  persistBibleEntry({ ...loadBibleEntries('a')[0], archived: true });
  expect(loadCharacterBibleEntities('a')).toEqual([]);
  expect(loadBibleEntries('b')[0].title).toBe('Private');
});
it('restores previous values as a new revision without erasing history', () => {
  const entry = newBibleEntry('a');
  const revised = reviseBibleEntry(entry, { ...entry, title: 'Mara', status: 'canon' });
  const restored = reviseBibleEntry(revised, revised.revisions[0].state, 'Restored revision');
  expect(restored.title).toBe(entry.title);
  expect(restored.revisions).toHaveLength(2);
  expect(restored.revisions[1].state.status).toBe('canon');
  expect(restored.id).toBe(entry.id);
});
it('remaps imported links and revision links together, leaving originals intact', () => {
  const first = importBibleEntries(fixture, 'first');
  const second = importBibleEntries(fixture, 'second');
  expect(first[0].linkedEntryIds).toEqual([first[1].id]);
  expect(first[0].revisions[0].state.linkedEntryIds).toEqual([first[1].id]);
  expect(second[0].id).not.toBe(first[0].id);
  expect(loadBibleEntries('first')).toHaveLength(2);
  expect(bibleMarkdown(first)).toContain('Links: Quay');
});
it('refuses damaged persisted or imported data and preserves the storage value', () => {
  localStorage.setItem(BIBLE_ENTRIES_KEY, '{broken');
  expect(() => persistBibleEntry(newBibleEntry('a'))).toThrow();
  expect(localStorage.getItem(BIBLE_ENTRIES_KEY)).toBe('{broken');
  expect(() => importBibleEntries({ bibleEntries: [{}] }, 'a')).toThrow('Invalid');
});
it('does not change persisted entries on a quota failure', () => {
  const entry = newBibleEntry('a'); persistBibleEntry(entry);
  const spy = vi.spyOn(localStorage, 'setItem').mockImplementation(() => { throw new DOMException('Full', 'QuotaExceededError'); });
  expect(() => persistBibleEntry({ ...entry, title: 'Lost edit' })).toThrow();
  spy.mockRestore();
  expect(loadBibleEntries('a')[0].title).toBe(entry.title);
});
it('round trips Bible entries through dhproj and backups with remapped history and links', async () => {
  const project = JSON.parse(readFileSync('fixtures/dhproj-v1.json', 'utf8'));
  project.bibleEntries = fixture.bibleEntries;
  const imported = await importDhproj(new File([JSON.stringify(project)], 'native.dhproj'));
  const entries = loadBibleEntries(imported.id);
  expect(entries[0].linkedEntryIds).toEqual([entries[1].id]);
  const backup = await exportBackup(imported.id);
  expect(backup.bibleEntries).toEqual(entries);
  const restored = await importBackup(backup);
  const copies = loadBibleEntries(restored.id);
  expect(copies[0].revisions[0].state.linkedEntryIds).toEqual([copies[1].id]);
  const zip = await JSZip.loadAsync(await exportDhproj(restored.id));
  const data = JSON.parse(await zip.file('project.json')!.async('string'));
  expect(data.bibleEntries).toEqual(copies);
});
