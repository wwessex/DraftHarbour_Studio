/** Passage-scoped writing plans, independent of any model or editor engine. */
export type WritingAction = 'write' | 'rewrite' | 'continue';
export interface WritingSelectionSnapshot {
  source: string;
  selection: { from: number; to: number };
}
export interface WritingPlan {
  action: WritingAction;
  source: string;
  from: number;
  to: number;
  prompt: string;
}

export function prepareWritingAction(action: WritingAction, source: string, selection?: { from: number; to: number }, direction = ''): WritingPlan {
  const end = source.trimEnd().length;
  const paragraphs = [...source.slice(0, end).matchAll(/(?:\r?\n)(?:[ \t]*\r?\n)+/g)];
  const last = paragraphs.at(-1);
  const paragraphStart = last ? last.index! + last[0].length : 0;
  let from = source.length;
  let to = source.length;
  let task: string;
  if (action === 'write') {
    if (!direction.trim()) throw new Error('Describe what you want to write in the instruction box first.');
    task = 'Write new fiction from the author’s instructions. Use the project’s prose or screenplay format. Use the chapter context for continuity. Return only the new passage to append, without repeating existing text or adding commentary.';
  } else if (action === 'continue') {
    if (!source.trim()) throw new Error('Write a paragraph first, or use Write to start a new scene.');
    task = `Continue immediately after the final paragraph below. Match its voice, point of view, tense, format and continuity. Return only the next passage; do not repeat, rewrite or summarise the existing ending.\n\nFINAL PARAGRAPH:\n${source.slice(paragraphStart, end)}`;
  } else {
    if (!source.trim()) throw new Error('Select a passage or write a paragraph to rewrite first.');
    const selected = selection && Number.isInteger(selection.from) && Number.isInteger(selection.to)
      && selection.from >= 0 && selection.to <= source.length && selection.to > selection.from;
    if (selection && selection.to !== selection.from && !selected) {
      throw new Error('The selected passage is no longer valid. Select it again before rewriting.');
    }
    from = selected ? selection.from : paragraphStart;
    to = selected ? selection.to : end;
    if (!source.slice(from, to).trim()) throw new Error('Select a passage containing text to rewrite.');
    task = `Rewrite only the target passage below. Preserve meaning, point of view, tense, format and the author’s voice unless instructed otherwise. Return one replacement passage only, without headings, alternatives or explanation. Do not continue the story or expand this target into a scene unless the author explicitly requests it.\n\nTARGET PASSAGE:\n${source.slice(from, to)}`;
  }
  return { action, source, from, to, prompt: [task, direction.trim() ? `AUTHOR INSTRUCTIONS:\n${direction.trim()}` : ''].filter(Boolean).join('\n\n') };
}

export function writingReplacement(plan: WritingPlan, current: string, output: string): { text: string; replacement: string } {
  if (current !== plan.source) throw new Error('The chapter changed after generation. Generate again before applying this suggestion.');
  if (!output.trim()) throw new Error('The model returned no passage to apply.');
  const separator = plan.action === 'rewrite' || !current.trim() ? '' : current.endsWith('\n\n') ? '' : current.endsWith('\n') ? '\n' : '\n\n';
  const target = current.slice(plan.from, plan.to);
  const replacement = plan.action === 'rewrite'
    ? (target.match(/^\s*/)?.[0] ?? '') + output.trim() + (target.match(/\s*$/)?.[0] ?? '')
    : separator + output.trim();
  return { text: current.slice(0, plan.from) + replacement + current.slice(plan.to), replacement };
}
