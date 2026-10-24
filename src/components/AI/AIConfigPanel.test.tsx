/** @vitest-environment jsdom */
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { AIConfigPanel } from './AIConfigPanel';
import { createNarratryxConfig, NARRATRYX_BASE_MODEL } from '@/lib/ai/narratryx';
import type { AIProviderConfig } from '@/lib/ai';

let root: ReturnType<typeof createRoot> | undefined;
let container: HTMLDivElement;
afterEach(() => {
  act(() => root?.unmount());
  container?.remove();
  root = undefined;
});

function render(config: AIProviderConfig) {
  container = document.createElement('div');
  document.body.appendChild(container);
  root = createRoot(container);
  const change = vi.fn();
  const localChange = vi.fn();
  act(() => root!.render(<AIConfigPanel mode="full" config={config} onConfigChange={change} onCustomLlmConfigChange={localChange} showProviderFields={false} showLocalFields />));
  return { change, localChange };
}

describe('Narratryx setup', () => {
  it('requires explicit opt-in and starts a new configuration without an unrelated provider key', () => {
    const { change } = render({ provider: 'custom-llm', customLlm: { backend: 'generic-openai', baseUrl: 'https://old.example.test', model: 'old-model', apiKey: 'old-private-key' } });
    expect(change).not.toHaveBeenCalled();
    const button = [...container.querySelectorAll('button')].find(b => b.textContent?.includes('Set up Narratryx'))!;
    act(() => button.click());
    expect(change).toHaveBeenCalledWith(createNarratryxConfig());
    expect(change.mock.calls[0][0].customLlm.apiKey).toBeUndefined();
    expect(change.mock.calls[0][0].customLlm.baseUrl).toBe('');
  });

  it('offers an explicit base comparison and keeps future model IDs editable', () => {
    const config = createNarratryxConfig('https://models.example.test');
    config.customLlm!.model = 'narratryx-next-reviewed-version';
    const { localChange } = render(config);
    expect(container.textContent).toContain('improved literary quality is not established');
    const select = container.querySelector('select[aria-label="Narratryx experiment model"]') as HTMLSelectElement;
    expect(select.value).toBe('narratryx-next-reviewed-version');
    act(() => {
      select.value = NARRATRYX_BASE_MODEL;
      select.dispatchEvent(new Event('change', { bubbles: true }));
    });
    expect(localChange).toHaveBeenCalledWith({ model: NARRATRYX_BASE_MODEL });
  });

  it('clears the experimental profile and credential when selecting another backend', () => {
    const config = createNarratryxConfig('https://models.example.test');
    config.customLlm!.apiKey = 'private-test-key';
    const { localChange } = render(config);
    const button = [...container.querySelectorAll('button')].find(b => b.querySelector('strong')?.textContent === 'Ollama')!;
    act(() => button.click());
    expect(localChange).toHaveBeenCalledWith(expect.objectContaining({ backend: 'ollama', apiKey: undefined, profile: undefined }));
  });
});
