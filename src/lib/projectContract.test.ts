/** @vitest-environment jsdom */
import 'fake-indexeddb/auto';
import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { beforeEach, expect, it } from 'vitest';
import type { CharacterEntity, DhprojData, WorldEntry } from '@/types';
import { db, exportDhproj, getChapters, getStoryBlueprint, importDhproj } from './storage';
import JSZip from 'jszip';

const fixture = readFileSync(resolve('fixtures/dhproj-v1.json'), 'utf8');
beforeEach(async () => {
  await db.open();
  await db.transaction('rw', db.tables, async () => { for (const table of db.tables) await table.clear(); });
});
it.each(['json', 'zip'])('imports the shared %s native/web fixture, preserving core data and references', async container => {
  const bytes = container === 'json' ? fixture : Buffer.from(readFileSync(resolve('fixtures/dhproj-v1.zip.base64'), 'utf8').trim(), 'base64');
  const novel = await importDhproj(new File([bytes], 'shared.dhproj'));
  expect((await getChapters(novel.id))[0].content).toBe('Alice watched the harbour.');
  expect(getStoryBlueprint(novel.id)?.genre).toBe('Mystery');
  const characters = JSON.parse(localStorage.getItem('draftharbour_characters')!) as CharacterEntity[];
  const world = JSON.parse(localStorage.getItem('draftharbour_world')!) as WorldEntry[];
  expect(world[0].linkedCharacters).toEqual([characters[0].id]);
  expect(characters[0].novelId).toBe(novel.id);
});
it('retains native revision records and remaps their section references through a web round trip', async () => {
  const data = JSON.parse(fixture);
  data.deletedSections = [{ id: 'trash-1', section: { id: 'old-chapter', novelId: 'project-fixture', content: 'Archived native writing' }, snapshots: [], comments: [] }];
  data.aiRevisionLog = [{ id: 'revision-1', sectionId: 'chapter-fixture', beforeText: 'Before', afterText: 'After' }];
  const novel = await importDhproj(new File([JSON.stringify(data)], 'native.dhproj'));
  const [chapter] = await getChapters(novel.id);
  const blob = await exportDhproj(novel.id);
  const zip = await JSZip.loadAsync(blob);
  const restored = JSON.parse(await zip.file('project.json')!.async('string')) as DhprojData & { aiRevisionLog: Array<{ sectionId: string; afterText: string }> };
  expect((restored as unknown as { deletedSections: Array<{ section: { novelId: string; content: string } }> }).deletedSections[0].section).toMatchObject({ novelId: novel.id, content: 'Archived native writing' });
  expect(restored.aiRevisionLog[0]).toMatchObject({ sectionId: chapter.id, afterText: 'After' });
});
