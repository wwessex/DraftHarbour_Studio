import { readFileSync } from 'node:fs';
import { expect, it } from 'vitest';
import { copyeditReview, copyeditPreview, prepareWritingAction, writingReplacement } from './writingActions';
const cases = JSON.parse(readFileSync('fixtures/anchored-copyedit.json', 'utf8')) as { id: string; source: string; proposal?: unknown; raw?: string; expected?: string }[];
for (const item of cases) it(item.id, () => {
  const plan = prepareWritingAction('copyedit', item.source, { from: 0, to: item.source.length });
  const run = () => copyeditPreview(plan, item.raw ?? JSON.stringify(item.proposal));
  if (item.expected === undefined) expect(run).toThrow('could not be verified');
  else expect(writingReplacement(plan, item.source, run()).text).toBe(item.expected);
});
it('preserves surrounding text, refuses stale application and bounds edit count', () => {
  const source = 'Before. rough rough After.';
  const plan = prepareWritingAction('copyedit', source, { from: 8, to: 19 });
  const output = copyeditPreview(plan, '{"edits":[{"before":"rough rough","after":"rough"}]}');
  expect(writingReplacement(plan, source, output).text).toBe('Before. rough After.');
  expect(() => writingReplacement(plan, source + 'changed', output)).toThrow('changed');
  expect(() => copyeditPreview(plan, JSON.stringify({ edits: Array.from({ length: 33 }, () => ({ before: 'rough rough', after: 'rough' })) }))).toThrow('verified');
});

it('rejects partial UTF-16 surrogate anchors', () => {
  const plan = prepareWritingAction('copyedit', '😀 smiled.');
  expect(() => copyeditPreview(plan, JSON.stringify({ edits: [{ before: '\ud83d', after: '' }] }))).toThrow('verified');
});

it('reports actual changes in source order and excludes identity edits', () => {
  const plan = prepareWritingAction('copyedit', 'The the brass bell rang rang.');
  const reviewed = copyeditReview(plan, JSON.stringify({ edits: [{ before: 'rang rang', after: 'rang' }, { before: 'The the', after: 'The' }, { before: 'brass', after: 'brass' }] }));
  expect(reviewed.text).toBe('The brass bell rang.');
  expect(reviewed.changes).toEqual([{ before: 'The the', after: 'The' }, { before: 'rang rang', after: 'rang' }]);
  for (const edits of [[], [{ before: 'brass', after: 'brass' }]]) {
    expect(copyeditReview(plan, JSON.stringify({ edits }))).toEqual({ text: plan.source, changes: [] });
  }
});
