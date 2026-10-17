// @vitest-environment node
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ChapterSaveQueue } from './chapterSaveQueue';

afterEach(() => vi.useRealTimers());

function setup(write = vi.fn(async (_id: string, _updates: unknown) => {})) {
  const dirty = vi.fn();
  const error = vi.fn();
  return { queue: new ChapterSaveQueue(write, dirty, error, 1000), write, dirty, error };
}

describe('chapter autosave', () => {
  it('persists edits to multiple chapters and merges fields with latest edits winning', async () => {
    vi.useFakeTimers();
    const { queue, write, dirty } = setup();
    queue.enqueue('a', { content: 'First draft' });
    queue.enqueue('b', { content: 'Other chapter' });
    queue.enqueue('a', { summary: 'Synopsis' });
    queue.enqueue('a', { content: 'Latest draft' });
    expect(dirty).toHaveBeenLastCalledWith(true);
    await vi.advanceTimersByTimeAsync(1000);
    expect(write.mock.calls).toEqual([
      ['a', { content: 'Latest draft', summary: 'Synopsis' }],
      ['b', { content: 'Other chapter' }],
    ]);
    expect(dirty).toHaveBeenLastCalledWith(false);
  });

  it('retains failed edits for retry without discarding successful chapters or newer changes', async () => {
    const { queue, write, dirty, error } = setup();
    write.mockRejectedValueOnce(new Error('Disk full'));
    queue.enqueue('a', { content: 'Draft', summary: 'Synopsis' });
    queue.enqueue('b', { content: 'Saved' });
    await expect(queue.flush()).rejects.toThrow('Disk full');
    expect(dirty).toHaveBeenLastCalledWith(true);
    expect(error).toHaveBeenCalledOnce();
    queue.enqueue('a', { content: 'Revised' });
    await queue.flush();
    expect(write.mock.calls).toEqual([
      ['a', { content: 'Draft', summary: 'Synopsis' }],
      ['b', { content: 'Saved' }],
      ['a', { content: 'Revised', summary: 'Synopsis' }],
    ]);
    expect(dirty).toHaveBeenLastCalledWith(false);
  });

  it('serializes writes and flushes changes made during a pending write', async () => {
    const { queue, write, dirty } = setup();
    let finish!: () => void;
    write.mockImplementationOnce(() => new Promise<void>(resolve => { finish = resolve; }));
    queue.enqueue('a', { content: 'Old' });
    const first = queue.flush();
    queue.enqueue('a', { content: 'New' });
    const second = queue.flush();
    expect(write).toHaveBeenCalledTimes(1);
    finish();
    await Promise.all([first, second]);
    expect(write).toHaveBeenLastCalledWith('a', { content: 'New' });
    expect(dirty).toHaveBeenLastCalledWith(false);
  });

  it('keeps pending patches when changing autosave delay and discards deleted chapters', async () => {
    vi.useFakeTimers();
    const { queue, write } = setup();
    queue.enqueue('deleted', { content: 'Removed' });
    queue.enqueue('a', { content: 'Keep' });
    queue.discard('deleted');
    queue.setDelay(2000);
    await vi.advanceTimersByTimeAsync(1000);
    expect(write).not.toHaveBeenCalled();
    await vi.advanceTimersByTimeAsync(1000);
    expect(write).toHaveBeenCalledExactlyOnceWith('a', { content: 'Keep' });
  });
});
