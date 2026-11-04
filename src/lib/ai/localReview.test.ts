import { describe, expect, it, vi } from 'vitest';
import { isLocalAIConfig, reviewManuscript, splitReviewText } from './localReview';
import type { AIProvider } from './types';
import type { Chapter } from '@/types';

const chapter = (title: string, content: string, order: number) => ({ title, content, order }) as Chapter;
function mockProvider(): AIProvider {
  return { type: 'custom-llm', isAvailable: () => true, destroy: vi.fn(), execute: vi.fn(async () => ({ text: 'Specific feedback and suggestions.', provider: 'custom-llm' as const, latencyMs: 1 })) };
}
describe('local manuscript review', () => {
  it('accepts only on-device or exact loopback configuration', () => {
    expect(isLocalAIConfig({ provider: 'chrome-ai' })).toBe(true);
    expect(isLocalAIConfig({ provider: 'managed-cloud' })).toBe(false);
    for (const endpoint of ['http://localhost:8080/v1', 'http://127.0.0.1:8080', 'http://[::1]:8080']) expect(isLocalAIConfig({ provider: 'openai-compatible', endpoint })).toBe(true);
    for (const endpoint of ['https://localhost.evil.test', 'https://example.com/127.0.0.1', 'file://localhost/model']) expect(isLocalAIConfig({ provider: 'openai-compatible', endpoint })).toBe(false);
  });
  it('covers every character and later chapter in manuscript order', async () => {
    const provider = mockProvider();
    const text = 'A'.repeat(9000);
    expect(splitReviewText(text).join('')).toBe(text);
    const result = await reviewManuscript([chapter('Last', 'The ending.', 2), chapter('First', text, 0), chapter('Empty', '', 1)], 'book', provider, new AbortController().signal, vi.fn());
    expect(result.findings.map(item => item.title)).toEqual(['First — part 1/3', 'First — part 2/3', 'First — part 3/3', 'Last — part 1/1']);
    expect(result.emptyCount).toBe(1);
    expect(provider.execute).toHaveBeenCalledTimes(5);
    expect(result.overview).toContain('feedback');
  });
  it('cancels before submitting text', async () => {
    const provider = mockProvider();
    const controller = new AbortController(); controller.abort();
    await expect(reviewManuscript([chapter('Opening', 'Draft.', 0)], 'book', provider, controller.signal, vi.fn())).rejects.toThrow();
    expect(provider.execute).not.toHaveBeenCalled();
  });
  it('does not report success for empty or failed model responses', async () => {
    const provider = mockProvider();
    vi.mocked(provider.execute).mockResolvedValue({ text: '', provider: 'custom-llm', latencyMs: 1 });
    await expect(reviewManuscript([chapter('Opening', 'Draft.', 0)], 'book', provider, new AbortController().signal, vi.fn())).rejects.toThrow('no feedback');
  });
  it('combines all findings in bounded batches for long manuscripts', async () => {
    const provider = mockProvider();
    vi.mocked(provider.execute).mockImplementation(async request => ({ text: request.sectionTitle ? 'F'.repeat(3000) : 'Combined feedback', provider: 'custom-llm', latencyMs: 1 }));
    const result = await reviewManuscript(Array.from({ length: 6 }, (_, index) => chapter(`Chapter ${index}`, 'Draft.', index)), 'book', provider, new AbortController().signal, vi.fn());
    expect(result.findings).toHaveLength(6);
    const summaryRequests = vi.mocked(provider.execute).mock.calls.map(([request]) => request).filter(request => !request.sectionTitle);
    expect(summaryRequests.length).toBeGreaterThan(1);
    expect(summaryRequests.every(request => request.context.length <= 6000)).toBe(true);
  });
});
