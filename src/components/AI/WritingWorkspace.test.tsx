/** @vitest-environment jsdom */
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { WritingWorkspace } from './WritingWorkspace';
import { setAISetupMode } from '@/lib/ai/setupPreferences';
import type { WritingAction } from '@/lib/ai/writingActions';

vi.mock('@/components/Modals/AIWritingModal', () => ({
  AIWritingModal: ({ actionRequest, onClose, onConfigure }: { actionRequest?: { action: WritingAction }; onClose: () => void; onConfigure?: () => void }) => <section aria-label="Writing assistant">
    <span>{actionRequest?.action} preview</span><button onClick={onClose}>Close</button><button onClick={onConfigure}>Connect model</button>
  </section>,
}));
let root: ReturnType<typeof createRoot> | undefined;
let container: HTMLDivElement;
afterEach(() => { act(() => root?.unmount()); container?.remove(); localStorage.clear(); });

describe('main manuscript writing bar', () => {
  it('reflects an explicit mode change from another settings surface', async () => {
    localStorage.setItem('draftharbour_ai_setup_mode_v1', 'later');
    container = document.createElement('div'); document.body.appendChild(container); root = createRoot(container);
    await act(async () => root!.render(<WritingWorkspace />));
    const write = () => [...container.querySelectorAll('button')].find(button => button.textContent === 'Write')!;
    expect(write().disabled).toBe(true);
    await act(async () => setAISetupMode('existing'));
    expect(write().disabled).toBe(false);
  });
  it('exposes all three actions immediately and opens a non-modal composer', async () => {
    container = document.createElement('div'); document.body.appendChild(container); root = createRoot(container);
    await act(async () => root!.render(<WritingWorkspace />));
    expect([...container.querySelectorAll('button')].map(button => button.textContent)).toEqual(['AI setup', 'Write', 'Rewrite', 'Continue']);
    expect(container.querySelector('[aria-label="Writing assistant"]')).toBeNull();
    await act(async () => [...container.querySelectorAll('button')].find(button => button.textContent === 'Continue')!.click());
    expect(container.textContent).toContain('continue preview');
    expect(container.querySelector('[role="dialog"]')).toBeNull();
    await act(async () => [...container.querySelectorAll('button')].find(button => button.textContent === 'Close')!.click());
    expect(container.textContent).toContain('Rewrite');
  });
  it('closes the composer for one-time model setup so the next action reloads configuration', async () => {
    const configure = vi.fn();
    container = document.createElement('div'); document.body.appendChild(container); root = createRoot(container);
    await act(async () => root!.render(<WritingWorkspace onConfigure={configure} />));
    await act(async () => [...container.querySelectorAll('button')].find(button => button.textContent === 'Write')!.click());
    await act(async () => [...container.querySelectorAll('button')].find(button => button.textContent === 'Connect model')!.click());
    expect(configure).toHaveBeenCalledOnce();
    expect(container.querySelector('[aria-label="Writing assistant"]')).toBeNull();
  });
});
