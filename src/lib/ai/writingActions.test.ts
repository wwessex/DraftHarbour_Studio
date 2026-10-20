import { readFileSync } from 'node:fs';
import { describe, expect, it } from 'vitest';
import { prepareWritingAction, writingReplacement, type WritingAction } from './writingActions';

type Case = { id: string; action: WritingAction; source: string; from?: number; to?: number; direction?: string; output: string; expected: string; target?: string };
const cases: Case[] = JSON.parse(readFileSync('fixtures/writing-actions.json', 'utf8'));

describe('passage-scoped writing actions', () => {
  for (const item of cases) it(item.id, () => {
    const plan = prepareWritingAction(item.action, item.source, item.from === undefined ? undefined : { from: item.from, to: item.to! }, item.direction);
    expect(writingReplacement(plan, item.source, item.output).text).toBe(item.expected);
    if (item.target) expect(plan.prompt).toContain(item.target);
    if (item.action === 'continue') expect(plan.prompt).not.toContain('Opening.');
  });
  it('requires author instructions to Write and existing prose to Continue or Rewrite', () => {
    expect(() => prepareWritingAction('write', 'Text')).toThrow('instruction');
    expect(() => prepareWritingAction('continue', '  ')).toThrow('paragraph');
    expect(() => prepareWritingAction('rewrite', '')).toThrow('paragraph');
  });
  it('rejects stale and empty results without changing text', () => {
    const plan = prepareWritingAction('rewrite', 'Original.');
    expect(() => writingReplacement(plan, 'Edited meanwhile.', 'Replacement')).toThrow('changed');
    expect(() => writingReplacement(plan, plan.source, ' ')).toThrow('no passage');
    expect(plan.source).toBe('Original.');
  });
});
