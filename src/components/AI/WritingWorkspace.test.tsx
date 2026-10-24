/** @vitest-environment jsdom */
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { WritingWorkspace } from './WritingWorkspace';
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
