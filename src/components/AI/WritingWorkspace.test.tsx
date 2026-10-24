/** @vitest-environment jsdom */
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { WritingWorkspace } from './WritingWorkspace';
import { setAISetupMode } from '@/lib/ai/setupPreferences';
import type { WritingAction, WritingSelectionSnapshot } from '@/lib/ai/writingActions';

let workspaceEditor: { getContent: () => string; getSelection: () => { from: number; to: number } } | null = null;
vi.mock('@/lib/editor/EditorContext', () => ({ useCurrentEditor: () => ({ editor: workspaceEditor }) }));

vi.mock('@/components/Modals/AIWritingModal', () => ({
  AIWritingModal: ({ actionRequest, onClose, onConfigure }: { actionRequest?: { action: WritingAction; target?: WritingSelectionSnapshot }; onClose: () => void; onConfigure?: () => void }) => <section aria-label="Writing assistant">
    <span>{actionRequest?.action} preview</span><button onClick={onClose}>Close</button><button onClick={onConfigure}>Connect model</button>
    <output data-testid="captured-target">{JSON.stringify(actionRequest?.target)}</output>
  </section>,
}));
let root: ReturnType<typeof createRoot> | undefined;
let container: HTMLDivElement;
afterEach(() => { act(() => root?.unmount()); container?.remove(); localStorage.clear(); workspaceEditor = null; });

describe('main manuscript writing bar', () => {
  it('captures highlighted text before a pointer click blurs the editor and loads the composer', async () => {
    const source = 'Before rough after.\n\nKeep this paragraph.';
    let selection = { from: 7, to: 12 };
    workspaceEditor = { getContent: () => source, getSelection: () => selection };
    container = document.createElement('div'); document.body.appendChild(container); root = createRoot(container);
    await act(async () => root!.render(<WritingWorkspace />));
    const rewrite = [...container.querySelectorAll('button')].find(button => button.textContent === 'Rewrite')!;
    await act(async () => rewrite.dispatchEvent(new MouseEvent('pointerdown', { bubbles: true })));
    selection = { from: source.length, to: source.length };
    await act(async () => rewrite.click());
    expect(JSON.parse(container.querySelector('[data-testid="captured-target"]')!.textContent!)).toEqual({ source, selection: { from: 7, to: 12 } });
  });
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
