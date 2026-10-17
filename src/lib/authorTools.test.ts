/** @vitest-environment jsdom */
import JSZip from 'jszip';
import { expect, it } from 'vitest';
import { alignRevisionLines } from './revisionDiff';
import { findEntityOccurrences } from './entityOccurrences';
import { loadSavedSearches, saveSearches } from './savedSearches';
import { createChapter } from './storage';
import { buildEpub } from './export/epub';

it('aligns inserted and deleted paragraphs without marking unchanged following text', () => {
  const diff = alignRevisionLines('Opening\nEnding', 'Opening\nInserted paragraph\nEnding');
  expect(diff.oldLines).toEqual(['Opening', null, 'Ending']);
  expect(diff.newLines).toEqual(['Opening', 'Inserted paragraph', 'Ending']);
  const reversed = alignRevisionLines('Opening\nRemoved\nEnding', 'Opening\nEnding');
  expect(reversed.oldLines).toEqual(['Opening', 'Removed', 'Ending']);
  expect(reversed.newLines).toEqual(['Opening', null, 'Ending']);
});
it('bounds large revision comparisons and keeps all source text', () => {
  const old = Array.from({ length: 1100 }, (_, i) => `old${i}`).join('\n');
  const next = Array.from({ length: 1100 }, (_, i) => `new${i}`).join('\n');
  const result = alignRevisionLines(old, next);
  expect(result.oldLines.filter(item => item !== null).join('\n')).toBe(old);
  expect(result.newLines.filter(item => item !== null).join('\n')).toBe(next);
});
it('finds names and aliases as whole words with source excerpts and escaped punctuation', () => {
  const chapter = createChapter('novel', 0); chapter.content = 'Ann met Anna. Annie waved. C++ was on the sign. Élodie smiled.';
  const matches = findEntityOccurrences([chapter], ['Ann', 'Annie', 'C++', 'Élodie']);
  expect(matches.map(item => item.name)).toEqual(['Ann', 'Annie', 'C++', 'Élodie']);
  expect(matches[0].excerpt).toContain('Ann met');
  expect(findEntityOccurrences([chapter], [])).toEqual([]);
});
it('keeps saved searches separate between projects and limits duplicates', () => {
  saveSearches('one', [' Alice ', 'Alice', 'Quay']);
  saveSearches('two', ['Bob']);
  expect(loadSavedSearches('one')).toEqual(['Alice', 'Quay']);
  expect(loadSavedSearches('two')).toEqual(['Bob']);
});
it('exports a readable EPUB archive with correct container, spine, nav, formatting and escaped XML', async () => {
  const chapter = createChapter('novel', 0, 'Chapter & <One>'); chapter.content = '**Bold** and *italic*\n\n<script>unsafe</script>';
  const bytes = await buildEpub([chapter], 'Book & title', 'A <Writer>');
  const zip = await JSZip.loadAsync(bytes);
  expect(await zip.file('mimetype')!.async('string')).toBe('application/epub+zip');
  const doc = await zip.file('EPUB/chapter-1.xhtml')!.async('string');
  expect(doc).toContain('<strong>Bold</strong>');
  expect(doc).toContain('<em>italic</em>');
  expect(doc).not.toContain('<script>');
  for (const file of ['META-INF/container.xml', 'EPUB/package.opf', 'EPUB/nav.xhtml', 'EPUB/chapter-1.xhtml']) {
    const parsed = new DOMParser().parseFromString(await zip.file(file)!.async('string'), 'application/xml');
    expect(parsed.querySelector('parsererror')).toBeNull();
  }
  expect(await zip.file('EPUB/package.opf')!.async('string')).toContain('idref="ch1"');
  expect(await zip.file('EPUB/nav.xhtml')!.async('string')).toContain('chapter-1.xhtml');
  // The EPUB mimetype local header uses STORE (compression method 0).
  expect(new DataView(bytes.buffer, bytes.byteOffset).getUint16(8, true)).toBe(0);
});
