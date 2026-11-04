import { describe, expect, it, vi } from 'vitest';
import { approvedChapterText, chatWithManuscript, manuscriptChunks, verifiedChapterProposal } from './manuscriptChat';
import type { Chapter } from '@/types';
import type { AIProvider, AIRequest } from './types';
vi.mock('./storyBibleReferences', () => ({ storyBibleReferences: () => '' }));
const chapter = (id: string, content: string, order: number) => ({ id, title: id, content, order, novelId: 'project' }) as Chapter;
const provider = (): AIProvider => ({ type: 'custom-llm', isAvailable: () => true, destroy: vi.fn(), execute: vi.fn(async (request: AIRequest) => ({ text: request.sectionTitle ? JSON.stringify({ reply: request.sectionTitle, edits: [] }) : 'Whole manuscript answer', provider: 'custom-llm' as const, latencyMs: 1 })) });
const options = (engine: AIProvider, chapters: Chapter[], proposeEdits = false) => ({ chapters, novelId: 'project', projectType: 'book' as const, question: 'Review the story.', history: '', proposeEdits, provider: engine, signal: new AbortController().signal, progress: vi.fn() });

describe('whole manuscript Chat', () => {
  it('reads every chapter and text beyond the old 4000-character limit', async () => {
    const engine = provider();
    const chapters = [chapter('Last', 'The final secret.', 1), chapter('First', 'A'.repeat(7000) + 'Hidden late clue.', 0)];
    await chatWithManuscript(options(engine, chapters));
    const requests = vi.mocked(engine.execute).mock.calls.map(([request]) => request);
    expect(requests.filter(request => request.sectionTitle).map(request => request.sectionTitle)).toEqual(['First', 'First', 'First', 'Last']);
    expect(requests.some(request => request.context.includes('Hidden late clue.'))).toBe(true);
    expect(requests.at(-1)?.context).toContain('Last');
    expect(chapters[0].content).toBe('The final secret.');
    expect(manuscriptChunks('A'.repeat(2600))).toHaveLength(1);
  });
  it('generates an inactive chapter proposal without applying any changes', async () => {
    const engine = provider();
    vi.mocked(engine.execute).mockImplementation(async request => ({ text: request.sectionTitle === 'Second' ? JSON.stringify({ reply: 'Repeated word.', edits: [{ before: 'The the bell', after: 'The bell', rationale: 'Remove repetition.' }] }) : request.sectionTitle ? '{"reply":"No change","edits":[]}' : 'Review the proposed change.', provider: 'custom-llm' as const, latencyMs: 1 }));
    const chapters = [chapter('First', 'An opening.', 0), chapter('Second', 'The the bell rang.', 1)];
    const result = await chatWithManuscript(options(engine, chapters, true));
    expect(result.proposals).toHaveLength(1);
    expect(result.proposals[0].chapterId).toBe('Second');
    expect(chapters[1].content).toBe('The the bell rang.');
    expect(approvedChapterText(result.proposals[0], chapters[1])).toBe('The bell rang.');
  });
  it('rejects stale, repeated, missing and overlapping anchors', () => {
    const original = chapter('One', 'The old bell rang.', 0);
    const proposal = verifiedChapterProposal(original, [{ before: 'old bell', after: 'brass bell', rationale: 'Specific detail.' }])!;
    expect(() => approvedChapterText(proposal, { ...original, content: 'The old bell rang loudly.' })).toThrow('changed');
    expect(() => approvedChapterText({ ...proposal, status: 'rejected' }, original)).toThrow('reviewed');
    expect(() => verifiedChapterProposal(chapter('One', 'old old', 0), [{ before: 'old', after: 'new', rationale: '' }])).toThrow();
    expect(() => verifiedChapterProposal(original, [{ before: 'invented', after: 'new', rationale: '' }])).toThrow();
    expect(() => verifiedChapterProposal(original, [{ before: 'old bell', after: 'bell', rationale: '' }, { before: 'bell rang', after: 'bell tolled', rationale: '' }])).toThrow();
  });
  it('does not turn prose responses into guessed manuscript edits', async () => {
    const engine = provider();
    vi.mocked(engine.execute).mockResolvedValue({ text: 'I fixed it for you.', provider: 'custom-llm' as const, latencyMs: 1 });
    const result = await chatWithManuscript(options(engine, [chapter('One', 'Original.', 0)], true));
    expect(result.proposals).toHaveLength(0);
    expect(result.warnings[0]).toContain('No edits');
  });
  it('ignores model edits in discussion mode', async () => {
    const engine = provider();
    vi.mocked(engine.execute).mockResolvedValue({ text: '{"reply":"Observation","edits":[{"before":"Original.","after":"Changed.","rationale":"test"}]}', provider: 'custom-llm' as const, latencyMs: 1 });
    expect((await chatWithManuscript(options(engine, [chapter('One', 'Original.', 0)]))).proposals).toHaveLength(0);
  });
  it('cancels without returning partial proposals', async () => {
    const controller = new AbortController(); controller.abort();
    const engine = provider();
    await expect(chatWithManuscript({ ...options(engine, [chapter('One', 'Original.', 0)], true), signal: controller.signal })).rejects.toThrow();
    expect(engine.execute).not.toHaveBeenCalled();
  });
});
