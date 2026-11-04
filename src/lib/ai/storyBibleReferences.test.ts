/** @vitest-environment jsdom */
import { beforeEach, expect, it } from 'vitest';
import { storyBibleReferences } from './storyBibleReferences';
import { newBibleEntry, persistBibleEntry } from '@/lib/storyBibleEntries';

beforeEach(() => localStorage.clear());
it('uses canon facts, fields, aliases and links without draft, archived or another project data', () => {
  const quay = { ...newBibleEntry('a'), title: 'Quay', status: 'canon' as const, body: 'Tides close the gate.' };
  const mara = { ...newBibleEntry('a'), title: 'Mara', aliases: ['Captain Venn'], status: 'canon' as const, body: 'Cannot swim.', fields: { Voice: 'Quiet' }, linkedEntryIds: [quay.id], validFrom: 'Chapter 2' };
  for (const entry of [quay, mara, { ...newBibleEntry('a'), body: 'DRAFT SECRET' }, { ...mara, id: 'archive', archived: true, body: 'ARCHIVE SECRET' }, { ...newBibleEntry('b'), status: 'canon' as const, body: 'OTHER PROJECT SECRET' }]) persistBibleEntry(entry);
  const result = storyBibleReferences('a', 'Captain Venn');
  expect(result).toContain('Cannot swim.');
  expect(result).toContain('Voice: Quiet');
  expect(result).toContain('Validity: Chapter 2');
  expect(result).toContain(mara.id);
  expect(result).toContain('"relatedCanon":["Quay"]');
  expect(result.indexOf('Cannot swim.')).toBeLessThan(result.indexOf('Tides close the gate.'));
  expect(result).not.toMatch(/DRAFT SECRET|ARCHIVE SECRET|OTHER PROJECT SECRET/);
  expect(result).toContain('Change only the requested passage');
});
it('skips oversized entries without truncating facts, reports omissions and fits the character limit', () => {
  persistBibleEntry({ ...newBibleEntry('a'), title: 'Huge', status: 'canon', body: 'x'.repeat(6000) });
  persistBibleEntry({ ...newBibleEntry('a'), title: 'Mara', status: 'canon', body: 'Cannot swim.' });
  const result = storyBibleReferences('a', 'Huge', 900);
  expect(result.length).toBeLessThanOrEqual(900);
  expect(result).toContain('Cannot swim.');
  expect(result).toContain('omitted for space');
  expect(result).not.toContain('xxx');
  expect(storyBibleReferences('a', '', 1)).toBe('');
});
it('includes legacy character and world notes and keeps canon ahead of a duplicate legacy name', () => {
  localStorage.setItem('draftharbour_characters', JSON.stringify([{ novelId: 'a', name: 'Mara', aliases: [], description: 'Legacy description', role: 'other', traits: [], notes: 'LEGACY OVERRIDE' }]));
  localStorage.setItem('draftharbour_world', JSON.stringify([{ novelId: 'a', name: 'Dock', tags: [], category: 'location', description: 'Stone', notes: 'Gate locked at dusk' }]));
  persistBibleEntry({ ...newBibleEntry('a'), title: 'Mara', status: 'canon', body: 'Cannot swim.' });
  expect(storyBibleReferences('a')).toContain('Gate locked at dusk');
  expect(storyBibleReferences('a')).not.toContain('LEGACY OVERRIDE');
});
it('does not write to the Bible and tolerates damaged local storage', () => {
  expect(storyBibleReferences('empty')).toBe('');
  const entry = { ...newBibleEntry('a'), title: 'Mara', status: 'canon' as const, body: 'Cannot swim.' };
  persistBibleEntry(entry);
  const before = JSON.stringify(localStorage);
  storyBibleReferences('a');
  expect(JSON.stringify(localStorage)).toBe(before);
});
