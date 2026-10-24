/** @vitest-environment jsdom */
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, expect, it, vi } from 'vitest';
import { AISetup } from './AISetup';
import { inspectDesktopLocalAI, stopDesktopLocalAI, DESKTOP_LOCAL_MODEL } from '@/lib/ai/desktopLocalProvider';
import { saveAIConfig } from '@/lib/ai/providerManager';
vi.mock('@/lib/ai/desktopLocalProvider', () => ({ inspectDesktopLocalAI: vi.fn(), stopDesktopLocalAI: vi.fn(), DESKTOP_LOCAL_MODEL: 'narratryx-craft-v1-q4-k-m' }));
vi.mock('@/lib/ai/providerManager', () => ({ saveAIConfig: vi.fn() }));
let root: ReturnType<typeof createRoot>;
let container: HTMLDivElement;
async function render() {
  container = document.createElement('div'); document.body.appendChild(container); root = createRoot(container);
  const changed = vi.fn();
  await act(async () => root.render(<AISetup onChanged={changed} />));
  return changed;
}
async function click(label: string) { await act(async () => [...container.querySelectorAll('button')].find(b => b.textContent === label)!.click()); }
afterEach(() => { act(() => root?.unmount()); container?.remove(); vi.resetAllMocks(); localStorage.clear(); });
it('selects only a verified native package without an API key', async () => {
  vi.mocked(inspectDesktopLocalAI).mockResolvedValue(DESKTOP_LOCAL_MODEL);
  const changed = await render(); await click('On this computer');
  expect(saveAIConfig).toHaveBeenCalledWith(expect.objectContaining({ customLlm: expect.objectContaining({ managedRuntime: true, model: DESKTOP_LOCAL_MODEL }) }));
  expect(container.textContent).toContain('No key entry is needed'); expect(changed).toHaveBeenCalledOnce();
  expect(container.querySelector('input[type=password]')).toBeNull();
});
it('preserves the existing connection when the package is unavailable', async () => {
  vi.mocked(inspectDesktopLocalAI).mockRejectedValue(new Error('Unsupported device'));
  const changed = await render(); await click('On this computer');
  expect(saveAIConfig).not.toHaveBeenCalled(); expect(changed).not.toHaveBeenCalled();
  expect(container.textContent).toContain('No text was sent online');
  expect([...container.querySelectorAll('button')].find(b => b.textContent?.startsWith('Online AI'))?.disabled).toBe(true);
});
it('decide later stops local inference and leaves drafting available', async () => {
  vi.mocked(stopDesktopLocalAI).mockResolvedValue();
  const changed = await render(); await click('Decide later');
  expect(stopDesktopLocalAI).toHaveBeenCalledOnce(); expect(localStorage.getItem('draftharbour_ai_setup_mode_v1')).toBe('later');
  expect(changed).toHaveBeenCalledOnce(); expect(container.textContent).toContain('Keep writing');
});
