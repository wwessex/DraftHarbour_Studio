/** Passage-scoped writing plans, independent of any model or editor engine. */
export type WritingAction = 'write' | 'rewrite' | 'copyedit' | 'continue';
export const replacesPassage = (action?: WritingAction): boolean => action === 'rewrite' || action === 'copyedit';
export const writingActionTitle = (action: WritingAction): string => action[0].toUpperCase() + action.slice(1);

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
  if (action === 'copyedit') task = `Copyedit only TARGET PASSAGE. Correct clear spelling, punctuation and accidental repetition; preserve meaning, voice and all other wording. Return JSON only: {"edits":[{"before":"exact unique original span","after":"corrected span"}]}. Use at most 32 non-overlapping edits. Each before span must occur exactly once in the original target. Return {"edits":[]} if no correction is needed. No markdown, prose or commentary.\n\nTARGET PASSAGE:\n${source.slice(from, to)}`;
  return { action, source, from, to, prompt: [task, direction.trim() ? `AUTHOR INSTRUCTIONS:\n${direction.trim()}` : ''].filter(Boolean).join('\n\n') };
}

export function writingReplacement(plan: WritingPlan, current: string, output: string): { text: string; replacement: string } {
  if (current !== plan.source) throw new Error('The chapter changed after generation. Generate again before applying this suggestion.');
  if (!output.trim()) throw new Error('The model returned no passage to apply.');
  const separator = replacesPassage(plan.action) || !current.trim() ? '' : current.endsWith('\n\n') ? '' : current.endsWith('\n') ? '\n' : '\n\n';
  const target = current.slice(plan.from, plan.to);
  const replacement = plan.action === 'copyedit' ? output : replacesPassage(plan.action)
    ? (target.match(/^\s*/)?.[0] ?? '') + output.trim() + (target.match(/\s*$/)?.[0] ?? '')
    : separator + output.trim();
  return { text: current.slice(0, plan.from) + replacement + current.slice(plan.to), replacement };
}

/** Validate every anchor against the original snapshot, then apply atomically to a preview. */
export interface CopyeditChange { before: string; after: string }
export function copyeditPreview(plan: WritingPlan, json: string): string {
  return copyeditReview(plan, json).text;
}
export function copyeditReview(plan: WritingPlan, json: string): { text: string; changes: CopyeditChange[] } {
  const invalid = () => new Error('The copyedit proposal could not be verified. Generate again; no manuscript text was changed.');
  let proposal: unknown;
  try { proposal = JSON.parse(json); } catch { throw invalid(); }
  if (!proposal || typeof proposal !== 'object' || Array.isArray(proposal)
    || Object.keys(proposal).join() !== 'edits' || !('edits' in proposal)
    || !Array.isArray(proposal.edits) || proposal.edits.length > 32) throw invalid();
  const target = plan.source.slice(plan.from, plan.to);
  const edits = proposal.edits.map((edit: unknown) => {
    if (!edit || typeof edit !== 'object' || Array.isArray(edit) || Object.keys(edit).sort().join() !== 'after,before'
      || !('before' in edit) || !('after' in edit) || typeof edit.before !== 'string' || !edit.before.length || typeof edit.after !== 'string') throw invalid();
    const from = target.indexOf(edit.before);
    const splitsSurrogate = (index: number) => index > 0 && index < target.length && /[\uD800-\uDBFF]/.test(target[index - 1]) && /[\uDC00-\uDFFF]/.test(target[index]);
    if (from < 0 || target.indexOf(edit.before, from + 1) !== -1 || splitsSurrogate(from) || splitsSurrogate(from + edit.before.length)) throw invalid();
    return { from, to: from + edit.before.length, after: edit.after };
  }).sort((a, b) => a.from - b.from);
  if (edits.some((edit, index) => index > 0 && edit.from < edits[index - 1].to)) throw invalid();
  let result = target;
  for (const edit of edits.reverse()) result = result.slice(0, edit.from) + edit.after + result.slice(edit.to);
  if (!result.trim()) throw invalid();
  return { text: result, changes: result === target ? [] : edits.reverse().map(edit => ({ before: target.slice(edit.from, edit.to), after: edit.after })).filter(edit => edit.before !== edit.after) };
}
