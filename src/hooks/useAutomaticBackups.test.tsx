/** @vitest-environment jsdom */
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { useAutomaticBackups } from './useAutomaticBackups';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
const createBackup = vi.hoisted(() => vi.fn(async () => {}));
vi.mock('@/lib/storage', () => ({ createProjectBackup: createBackup }));
let root: ReturnType<typeof createRoot>;
const flush = vi.fn(async () => {}), error = vi.fn();
function Probe({ novelId = 'novel' }) { useAutomaticBackups(novelId, flush, error); return null; }
beforeEach(() => { vi.useFakeTimers(); vi.clearAllMocks(); root = createRoot(document.createElement('div')); });
afterEach(async () => { await act(async () => root.unmount()); vi.useRealTimers(); });
it('flushes before backing up after one minute and every five minutes', async () => {
  await act(async () => root.render(<Probe />));
  await act(async () => vi.advanceTimersByTimeAsync(60_000));
  expect(createBackup).toHaveBeenCalledExactlyOnceWith('novel', true);
  expect(flush).toHaveBeenCalledOnce();
  await act(async () => vi.advanceTimersByTimeAsync(240_000));
  expect(createBackup).toHaveBeenCalledTimes(2);
});
it('reports a failed flush without recording a stale backup', async () => {
  flush.mockRejectedValueOnce(new Error('Storage full'));
  await act(async () => root.render(<Probe />));
  await act(async () => vi.advanceTimersByTimeAsync(60_000));
  expect(createBackup).not.toHaveBeenCalled();
  expect(error).toHaveBeenCalledOnce();
});
it('cancels pending backup timers when the project closes', async () => {
  await act(async () => root.render(<Probe />));
  await act(async () => root.render(<Probe novelId="" />));
  await act(async () => vi.advanceTimersByTimeAsync(600_000));
  expect(createBackup).not.toHaveBeenCalled();
});
