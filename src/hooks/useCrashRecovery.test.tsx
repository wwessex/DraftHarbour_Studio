/** @vitest-environment jsdom */
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { useCrashRecovery } from './useCrashRecovery';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const KEY = 'draftharbour_crash_recovery';
let root: ReturnType<typeof createRoot>;
let container: HTMLDivElement;
beforeEach(() => {
  localStorage.clear();
  container = document.createElement('div');
  root = createRoot(container);
});
afterEach(() => { act(() => root.unmount()); container.remove(); });

it('does not mistake the current session marker for a crash when callbacks change', () => {
  const recovered = vi.fn();
  function Probe() {
    useCrashRecovery({ hasUnsavedEdits: false, novelId: 'novel', activeChapterId: 'chapter', onRecoveryDetected: info => recovered(info) });
    return null;
  }
  act(() => root.render(<Probe />));
  act(() => root.render(<Probe />));
  expect(recovered).not.toHaveBeenCalled();
});

it('reports the previous unclean session once', () => {
  localStorage.setItem(KEY, JSON.stringify({ novelId: 'old', chapterId: 'old-chapter', clean: false }));
  const recovered = vi.fn();
  function Probe() {
    useCrashRecovery({ hasUnsavedEdits: false, novelId: 'novel', activeChapterId: 'chapter', onRecoveryDetected: info => recovered(info) });
    return null;
  }
  act(() => root.render(<Probe />));
  act(() => root.render(<Probe />));
  expect(recovered).toHaveBeenCalledExactlyOnceWith({ novelId: 'old', chapterId: 'old-chapter' });
});

it('keeps recovery unclean if the tab closes with pending edits and warns before unload', () => {
  const onRecoveryDetected = vi.fn();
  function Probe({ dirty }: { dirty: boolean }) {
    useCrashRecovery({ hasUnsavedEdits: dirty, novelId: 'novel', activeChapterId: 'chapter', onRecoveryDetected });
    return null;
  }
  act(() => root.render(<Probe dirty />));
  const unload = new Event('beforeunload', { cancelable: true });
  window.dispatchEvent(unload);
  expect(unload.defaultPrevented).toBe(true);
  window.dispatchEvent(new Event('pagehide'));
  expect(JSON.parse(localStorage.getItem(KEY)!).clean).toBe(false);
  act(() => root.render(<Probe dirty={false} />));
  window.dispatchEvent(new Event('pagehide'));
  expect(JSON.parse(localStorage.getItem(KEY)!).clean).toBe(true);
});
