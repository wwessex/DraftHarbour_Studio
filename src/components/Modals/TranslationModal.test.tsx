/** @vitest-environment jsdom */
import { act, type ReactNode } from 'react';
import { createRoot, type Root } from 'react-dom/client';
import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { newBibleEntry, persistBibleEntry } from '@/lib/storyBibleEntries';
import { TranslationModal } from './TranslationModal';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
const mocks = vi.hoisted(() => ({
  execute: vi.fn(), destroy: vi.fn(), available: true, source: 'Mara waited on the quay.',
}));
vi.mock('@/context/AppContext', () => ({ useApp: () => ({
  state: { novelId: 'translation-project', projectType: 'book' },
  activeChapter: { id: 'chapter', title: 'The Quay', content: mocks.source },
}) }));
vi.mock('@/lib/ai', () => ({
  loadAIConfig: () => ({ provider: 'custom-llm' }),
  createProvider: () => ({ execute: mocks.execute, destroy: mocks.destroy, isAvailable: () => mocks.available }),
}));
vi.mock('@/lib/utils', async importOriginal => ({
  ...await importOriginal<typeof import('@/lib/utils')>(), editorToPlainText: () => mocks.source,
}));
vi.mock('@/components/UI', () => ({
  Dialog: ({ open, children, footer }: { open: boolean; children: ReactNode; footer: ReactNode }) => open ? <div>{children}{footer}</div> : null,
  Button: ({ children, ...props }: React.ComponentProps<'button'>) => <button {...props}>{children}</button>,
  useToast: () => ({ showToast: vi.fn() }),
}));
let root: Root;
let container: HTMLDivElement;
beforeEach(() => {
  localStorage.clear();
  mocks.available = true;
  mocks.source = 'Mara waited on the quay.';
  mocks.execute.mockReset().mockResolvedValue({ text: 'Mara esperaba en el muelle.' });
  mocks.destroy.mockClear();
  container = document.createElement('div'); document.body.append(container);
  root = createRoot(container);
});
afterEach(() => { act(() => root.unmount()); container.remove(); });
async function translate() {
  await act(async () => root.render(<TranslationModal open onClose={() => {}} />));
  const button = [...container.querySelectorAll('button')].find(button => button.textContent?.endsWith('Translate'))!;
  await act(async () => button.click());
}
it('sends read-only canon separately from the translation source, shows a preview and leaves the source intact', async () => {
  persistBibleEntry({ ...newBibleEntry('translation-project'), title: 'Mara', status: 'canon', body: 'Cannot swim.' });
  persistBibleEntry({ ...newBibleEntry('other-project'), title: 'Other', status: 'canon', body: 'PRIVATE OTHER PROJECT' });
  await translate();
  const request = mocks.execute.mock.calls[0][0];
  expect(request.action).toBe('translate');
  expect(request.prompt).toContain('Mara waited on the quay.');
  expect(request.prompt).toContain('Spanish');
  expect(request.context).toContain('Cannot swim.');
  expect(request.context).toContain('read-only project data');
  expect(request.context).not.toContain('PRIVATE OTHER PROJECT');
  expect(container.textContent).toContain('Mara esperaba en el muelle.');
  expect(mocks.source).toBe('Mara waited on the quay.');
  expect(mocks.destroy).toHaveBeenCalledOnce();
});
it('does not send source or references when the provider is unavailable', async () => {
  mocks.available = false;
  await translate();
  expect(mocks.execute).not.toHaveBeenCalled();
  expect(container.textContent).toContain('AI is not configured');
});
it('does not translate an empty source and reports provider errors without changing the manuscript', async () => {
  mocks.source = '';
  await translate();
  expect(mocks.execute).not.toHaveBeenCalled();
  expect(container.textContent).toContain('No text to translate');
  mocks.source = 'Mara waited on the quay.';
  mocks.execute.mockRejectedValueOnce(new Error('Service unavailable'));
  await translate();
  expect(container.textContent).toContain('Service unavailable');
  expect(mocks.source).toBe('Mara waited on the quay.');
  expect(mocks.destroy).toHaveBeenCalledOnce();
});
