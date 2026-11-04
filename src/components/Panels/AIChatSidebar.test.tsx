/** @vitest-environment jsdom */
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AIChatSidebar } from './AIChatSidebar';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
const mocks = vi.hoisted(() => ({ create: vi.fn(), apply: vi.fn(async () => true), novelId: 'project-1', content: 'The the bell rang.' }));
vi.mock('@/lib/ai/localReview', () => ({ createLocalAIProvider: mocks.create }));
vi.mock('@/context/AppContext', () => ({ useApp: () => ({ state: { novelId: mocks.novelId, projectType: 'book', chapters: [{ id: 'first', title: 'Opening', content: 'Mara waited by the harbour.', order: 0 }, { id: 'second', title: 'Second', content: mocks.content, order: 1 }] }, applyAIChatEdit: mocks.apply, setActiveChapter: vi.fn() }) }));
vi.mock('@/lib/ai/storyBibleReferences', () => ({ storyBibleReferences: () => '' }));
const container = document.createElement('div');
let root = createRoot(container);
afterEach(async () => { await act(async () => root.unmount()); root = createRoot(container); mocks.create.mockReset(); mocks.novelId = 'project-1'; mocks.content = 'The the bell rang.'; mocks.apply.mockClear(); });
async function submit() {
  await act(async () => {
    const input = container.querySelector('textarea')!;
    Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')!.set!.call(input, 'What could happen next?');
    input.dispatchEvent(new Event('input', { bubbles: true }));
  });
  await act(async () => { container.querySelector('form')!.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); });
}
describe('local AI Chat sidebar', () => {
  it('opens independently, uses local AI, and clears context when projects change', async () => {
    const execute = vi.fn(async () => ({ text: 'Consider a difficult choice for Mara.' }));
    const destroy = vi.fn(); mocks.create.mockResolvedValue({ execute, destroy });
    const close = vi.fn();
    await act(async () => root.render(<AIChatSidebar open onClose={close} />));
    expect(container.querySelector('aside')?.getAttribute('aria-label')).toBe('AI Chat');
    await submit();
    expect(execute).toHaveBeenCalledTimes(3);

    expect(container.textContent).toContain('Consider a difficult choice');
    expect(destroy).toHaveBeenCalledOnce();
    mocks.novelId = 'project-2';
    await act(async () => root.render(<AIChatSidebar open onClose={close} />));
    expect(container.textContent).not.toContain('Consider a difficult choice');
    await act(async () => { container.querySelector<HTMLButtonElement>('[aria-label="Close AI Chat"]')!.click(); });
    expect(close).toHaveBeenCalledOnce();
  });
  it('shows a setup error without sending to another provider', async () => {
    mocks.create.mockRejectedValue(new Error('Choose a local model in Settings > AI.'));
    await act(async () => root.render(<AIChatSidebar open onClose={vi.fn()} />));
    await submit();
    expect(container.querySelector('[role="alert"]')?.textContent).toContain('Choose a local model');
    expect(container.querySelector('textarea')?.value).toBe('What could happen next?');
  });
});


it('requires approval before editing an inactive chapter and rejects stale previews', async () => {
  const execute = vi.fn(async (request: { sectionTitle?: string }) => ({ text: request.sectionTitle === 'Second' ? '{"reply":"Repeated word","edits":[{"before":"The the bell","after":"The bell","rationale":"Remove repetition"}]}' : request.sectionTitle ? '{"reply":"No change","edits":[]}' : 'One proposed chapter edit.' }));
  mocks.create.mockResolvedValue({ execute, destroy: vi.fn() });
  await act(async () => root.render(<AIChatSidebar open onClose={vi.fn()} />));
  await act(async () => container.querySelector<HTMLInputElement>('input[type="checkbox"]')!.click());
  await submit();
  expect(mocks.apply).not.toHaveBeenCalled();
  const approve = () => Array.from(container.querySelectorAll('button')).find(button => button.textContent === 'Approve edits to Second')!;
  expect(approve()).toBeDefined();
  mocks.content = 'The the bell rang loudly.';
  await act(async () => root.render(<AIChatSidebar open onClose={vi.fn()} />));
  await act(async () => approve().click());
  expect(mocks.apply).not.toHaveBeenCalled();
  expect(container.textContent).toContain('changed after generation');
});

it('applies an approved inactive-chapter proposal only after the author clicks Approve', async () => {
  mocks.create.mockResolvedValue({ execute: async (request: { sectionTitle?: string }) => ({ text: request.sectionTitle === 'Second' ? '{"reply":"Repeated word","edits":[{"before":"The the bell","after":"The bell","rationale":"Remove repetition"}]}' : request.sectionTitle ? '{"reply":"No change","edits":[]}' : 'Review the edit.' }), destroy: vi.fn() });
  await act(async () => root.render(<AIChatSidebar open onClose={vi.fn()} />));
  await act(async () => container.querySelector<HTMLInputElement>('input[type="checkbox"]')!.click());
  await submit();
  expect(mocks.apply).not.toHaveBeenCalled();
  const approve = Array.from(container.querySelectorAll('button')).find(button => button.textContent === 'Approve edits to Second')!;
  await act(async () => approve.click());
  expect(mocks.apply).toHaveBeenCalledWith('second', 'The the bell rang.', 'The bell rang.');
  expect(container.textContent).toContain('Second · accepted');
});

it('keeps a pending manuscript review running when its sidebar is hidden and reopened', async () => {
  let finish!: (value: { text: string }) => void;
  const reply = new Promise<{ text: string }>(resolve => { finish = resolve; });
  const execute = vi.fn(async (request: { sectionTitle?: string }) => request.sectionTitle ? { text: 'Chapter observation.' } : reply);
  mocks.create.mockResolvedValue({ execute, destroy: vi.fn() });
  await act(async () => root.render(<AIChatSidebar open onClose={vi.fn()} />));
  await submit();
  expect(execute).toHaveBeenCalledTimes(3);
  await act(async () => root.render(<AIChatSidebar open={false} onClose={vi.fn()} />));
  expect(container.querySelector('aside')).toBeNull();
  await act(async () => root.render(<AIChatSidebar open onClose={vi.fn()} />));
  expect(container.querySelector('[role="status"]')).not.toBeNull();
  await act(async () => { finish({ text: 'The complete review is ready.' }); });
  expect(container.querySelector('[role="log"]')?.textContent).toContain('The complete review is ready.');
  expect(execute).toHaveBeenCalledTimes(3);
  expect(mocks.create).toHaveBeenCalledOnce();
});
