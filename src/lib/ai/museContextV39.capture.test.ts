/** @vitest-environment jsdom */
import { readFileSync, writeFileSync } from 'node:fs';
import { expect, it } from 'vitest';
import { newBibleEntry, persistBibleEntry } from '@/lib/storyBibleEntries';
import { storyBibleReferences } from './storyBibleReferences';

it('captures the real shared Story Bible selection for the synthetic Muse comparison project', () => {
  const base = process.env.NARRATRYX_CONTEXT_FIXTURE ?? 'llm/Narratryx/curation/muse-context-v39';
  const fixture = JSON.parse(readFileSync(`${base}/project.json`, 'utf8'));
  for (const [index, entry] of fixture.entries.entries()) {
    persistBibleEntry({
      ...newBibleEntry(fixture.id), id: `v39-${index}`, title: entry.title,
      aliases: entry.aliases, status: 'canon', body: entry.body,
      aiAccess: { hidden: entry.hidden, conditions: entry.condition ? { body: entry.condition } : {} },
    });
  }
  const cases = fixture.cases.map((item: { id: string; action: string; query: string; brief: string; scene: Record<string, string>; required: number[] }) => {
    const chapter = fixture.chapters.at(-1).text;
    const references = storyBibleReferences(fixture.id, item.query + '\n' + chapter, 3200, item.scene);
    const oracle = item.required.map(index => fixture.entries[index].body).join('\n');
    expect(references).not.toMatch(/PRIVATE_V39|DAY_V39/);
    expect(references.includes('NIGHT_V39')).toBe(item.scene.light === 'night');
    return { ...item, chapter, oracle, references,
      missingRequired: item.required.filter(index => !references.includes(fixture.entries[index].body)),
      included: fixture.entries.filter((entry: { body: string }) => references.includes(entry.body)).map((entry: { title: string }) => entry.title) };
  });
  if (process.env.NARRATRYX_V39_CAPTURE) {
    writeFileSync(process.env.NARRATRYX_V39_CAPTURE, JSON.stringify(cases, null, 2) + '\n', { flag: 'wx' });
  }
});
