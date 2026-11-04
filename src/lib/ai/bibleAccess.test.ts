/** @vitest-environment jsdom */
import { beforeEach, expect, it } from 'vitest';
import { newBibleEntry, persistBibleEntry, reviseBibleEntry, importBibleEntries, isBibleEntry } from '@/lib/storyBibleEntries';
import { bibleFieldVisible, inferenceBibleEntry, parseSceneFacts, referenceMatch } from './bibleAccess';
import { storyBibleReferences } from './storyBibleReferences';
import { loadCharacterBibleEntities } from './storyBible';
beforeEach(() => localStorage.clear());
it('filters conditional and private fields before inference and preserves author data', () => {
  const entry = { ...newBibleEntry('a'), status: 'canon' as const, body: 'Private notes', aliases: ['Secret identity'], fields: { Form: 'Human hands', Secret: 'Hidden marker' }, aiAccess: { hiddenFields: ['body', 'aliases', 'field:Secret'], conditions: { 'field:Form': 'form=human' } } };
  expect(inferenceBibleEntry(entry)?.fields).toEqual({});
  expect(inferenceBibleEntry(entry, parseSceneFacts('form=human'))?.fields).toEqual({ Form: 'Human hands' });
  expect(inferenceBibleEntry(entry, { form: 'wolf' })?.fields).toEqual({});
  expect(inferenceBibleEntry(entry)?.body).toBe('');
  expect(inferenceBibleEntry(entry)?.aliases).toEqual([]);
  expect(bibleFieldVisible({ ...entry, aiAccess: { conditions: { body: 'invalid' } } }, 'body')).toBe(false);
  const revised = reviseBibleEntry(entry, { ...entry, body: 'Edited' });
  expect(revised.revisions[0].state.aiAccess).toEqual(entry.aiAccess);
  expect(importBibleEntries({ bibleEntries: [revised] }, 'b')[0].aiAccess).toEqual(entry.aiAccess);
  expect(entry.body).toBe('Private notes');
  expect(isBibleEntry({ ...entry, aiAccess: { hidden: 'no' } })).toBe(false);
});
it('prevents hidden structured canon from reappearing through legacy cards or the bridge', () => {
  localStorage.setItem('draftharbour_characters', JSON.stringify([{ novelId: 'a', name: 'Mara', aliases: [], description: 'LEGACY SECRET', role: 'other', traits: [], notes: '' }]));
  persistBibleEntry({ ...newBibleEntry('a'), title: 'Mara', status: 'canon', body: 'PRIVATE SECRET', aiAccess: { hidden: true } });
  expect(storyBibleReferences('a', 'Mara')).not.toMatch(/SECRET|Mara/);
  expect(loadCharacterBibleEntities('a')).toEqual([]);
});
it('selects conditional facts only with matching explicit scene facts and fails closed on damaged data', () => {
  persistBibleEntry({ ...newBibleEntry('a'), title: 'Mara', status: 'canon', body: 'UNIQUE_HUMAN', aiAccess: { conditions: { body: 'form=human' } } });
  expect(storyBibleReferences('a', '', 3200)).not.toContain('UNIQUE_HUMAN');
  expect(storyBibleReferences('a', '', 3200, { form: 'human' })).toContain('UNIQUE_HUMAN');
  localStorage.setItem('draftharbour_bible_entries', 'broken');
  expect(storyBibleReferences('a')).toBe('');
});
it('matches aliases at Unicode word boundaries and rejects ambiguous state input', () => {
  expect(referenceMatch('Joann arrives', 'Ann')).toBe(false);
  expect(referenceMatch('Éva arrives', 'éva')).toBe(true);
  expect(referenceMatch('Captain Venn arrives', 'Captain Venn')).toBe(true);
  for (const input of ['form=human,form=wolf', 'broken', 'form=', '=human', 'a=b=c']) expect(() => parseSceneFacts(input)).toThrow();
});
