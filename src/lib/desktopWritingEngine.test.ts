import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { Chapter } from '@/types';
import { searchManuscript } from '@/lib/desktopWritingEngine';
import { getTauriRuntime } from '@/lib/tauriRuntime';

vi.mock('@/lib/tauriRuntime', () => ({
  getTauriRuntime: vi.fn(),
}));

const chapter: Chapter = {
  id: 'chapter-1',
  novelId: 'novel-1',
  order: 0,
  title: 'Arrival',
  updatedAt: 1,
  content: 'The harbour was quiet.',
  summary: '',
  pov: '',
  status: 'draft',
  tags: [],
  wordGoal: 0,
  scenes: [],
};

describe('desktopWritingEngine', () => {
  beforeEach(() => {
    vi.mocked(getTauriRuntime).mockReset();
  });

  it('uses the cross-platform search when Tauri is unavailable', async () => {
    vi.mocked(getTauriRuntime).mockResolvedValue(null);

    const results = await searchManuscript([chapter], 'harbour');

    expect(results).toHaveLength(1);
    expect(results[0].chapterId).toBe('chapter-1');
  });

  it('delegates whole-manuscript search to the Rust command on desktop', async () => {
    const invoke = vi.fn().mockResolvedValue([{
      chapterId: 'chapter-1',
      chapterTitle: 'Arrival',
      snippet: 'The harbour was quiet.',
      matchRange: { start: 4, end: 11 },
      score: 40,
    }]);
    vi.mocked(getTauriRuntime).mockResolvedValue({ invoke, listen: vi.fn() });

    const results = await searchManuscript([chapter], 'harbour', 20);

    expect(invoke).toHaveBeenCalledWith('search_manuscript', expect.objectContaining({
      query: 'harbour',
      maxResults: 20,
    }));
    expect(results[0].match).toEqual({ start: 4, end: 11 });
  });

  it('keeps search available if the native command fails', async () => {
    const invoke = vi.fn().mockRejectedValue(new Error('native engine unavailable'));
    vi.mocked(getTauriRuntime).mockResolvedValue({ invoke, listen: vi.fn() });

    const results = await searchManuscript([chapter], 'harbour');

    expect(results).toHaveLength(1);
    expect(results[0].chapterId).toBe('chapter-1');
  });
});
