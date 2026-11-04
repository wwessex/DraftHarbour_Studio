/** @vitest-environment jsdom */
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';
import type { AIProviderConfig } from '@/lib/ai';
import { newBibleEntry, persistBibleEntry } from '@/lib/storyBibleEntries';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;

const onCloseMock = vi.fn();
const executeMock = vi.fn(async () => ({ text: 'AI response', provider: 'test', latencyMs: 100 }));
const destroyMock = vi.fn();
const defaultConfig: AIProviderConfig = { provider: 'openai-compatible', endpoint: 'https://test/v1', sessionToken: 'tok', model: 'gpt-test' };
let currentConfig = defaultConfig;
const providerConfigs: AIProviderConfig[] = [];

vi.mock('@/context/AppContext', () => ({
  useApp: () => ({
    state: { projectType: 'book', novelId: 'suggestion-project' },
    activeChapter: {
      id: 'c1',
      title: 'Test Chapter',
      content: 'Some chapter text here.',
    },
  }),
}));

vi.mock('@/lib/ai', () => ({
  loadAIConfig: () => currentConfig,
  hydrateDesktopSecrets: async (config: unknown) => config,
  createProvider: (config: AIProviderConfig) => {
    providerConfigs.push(config);
    return { execute: executeMock, destroy: destroyMock, isAvailable: () => true };
  },
}));

vi.mock('@/lib/utils', () => ({
  editorToPlainText: () => 'Some chapter text here.',
  generateId: () => 'test-id-' + Math.random().toString(36).slice(2),
}));

vi.mock('@/lib/telemetry', () => ({
  recordTelemetryEvent: vi.fn(),
  isTelemetryOptedIn: () => false,
}));

vi.mock('./Panels.module.css', () => ({
  default: new Proxy({}, { get: (_, key) => String(key) }),
}));

import { AISuggestionsPanel } from './AISuggestionsPanel';

describe('AISuggestionsPanel', () => {
  let container: HTMLDivElement;

  beforeEach(() => {
    localStorage.clear();
    currentConfig = defaultConfig;
    providerConfigs.length = 0;
    onCloseMock.mockClear();
    executeMock.mockClear();
    destroyMock.mockClear();
    container = document.createElement('div');
    document.body.appendChild(container);
  });

  afterEach(() => {
    document.body.removeChild(container);
  });

  it('uses updated provider settings without reopening the panel', async () => {
    const root = createRoot(container);
    await act(async () => { root.render(<AISuggestionsPanel open={true} onClose={onCloseMock} editor={null} />); });
    currentConfig = { provider: 'custom-llm', customLlm: { backend: 'generic-openai', baseUrl: 'http://127.0.0.1:8890', model: 'narratryx-craft-v1' } };
    await act(async () => { window.dispatchEvent(new Event('draftharbour-ai-setup-changed')); });
    expect(container.textContent).toContain('computer');
    const action = Array.from(container.querySelectorAll('button')).find(button => button.textContent?.includes('Strengthen'))!;
    await act(async () => { action.click(); });
    expect(providerConfigs.at(-1)?.customLlm?.baseUrl).toBe('http://127.0.0.1:8890');
    expect(executeMock).toHaveBeenCalled();
    await act(async () => root.unmount());
  });

  it('returns null when not open', async () => {
    const root = createRoot(container);
    await act(async () => {
      root.render(<AISuggestionsPanel open={false} onClose={onCloseMock} editor={null} />);
    });

    expect(container.innerHTML).toBe('');

    await act(async () => {
      root.unmount();
    });
  });

  it('renders panel with header when open', async () => {
    const root = createRoot(container);
    await act(async () => {
      root.render(<AISuggestionsPanel open={true} onClose={onCloseMock} editor={null} />);
    });

    expect(container.textContent).toContain('AI Suggestions');

    await act(async () => {
      root.unmount();
    });
  });

  it('shows three collapsible sections', async () => {
    const root = createRoot(container);
    await act(async () => {
      root.render(<AISuggestionsPanel open={true} onClose={onCloseMock} editor={null} />);
    });

    const text = container.textContent || '';
    expect(text).toContain('Quick Actions');
    expect(text).toContain('Rewrite Tools');
    expect(text).toContain('Brainstorm');

    await act(async () => {
      root.unmount();
    });
  });

  it('shows rewrite disabled hint when no selection', async () => {
    const root = createRoot(container);
    await act(async () => {
      root.render(<AISuggestionsPanel open={true} onClose={onCloseMock} editor={null} />);
    });

    expect(container.textContent).toContain('Select text in the editor to use rewrite tools');

    await act(async () => {
      root.unmount();
    });
  });

  it('shows quick action buttons', async () => {
    const root = createRoot(container);
    await act(async () => {
      root.render(<AISuggestionsPanel open={true} onClose={onCloseMock} editor={null} />);
    });

    const buttons = Array.from(container.querySelectorAll('button'));
    const labels = buttons.map(b => b.textContent || '');

    const expected = ['Continue', 'Rephrase', 'Strengthen', 'Shorten'];
    for (const label of expected) {
      expect(labels.some(l => l.includes(label))).toBe(true);
    }

    await act(async () => {
      root.unmount();
    });
  });

  it('shows brainstorm buttons', async () => {
    const root = createRoot(container);
    await act(async () => {
      root.render(<AISuggestionsPanel open={true} onClose={onCloseMock} editor={null} />);
    });

    const buttons = Array.from(container.querySelectorAll('button'));
    const labels = buttons.map(b => b.textContent || '');

    const expected = ['Plot Ideas', 'Character Arc', 'Scene Outline', 'What If...'];
    for (const label of expected) {
      expect(labels.some(l => l.includes(label))).toBe(true);
    }

    await act(async () => {
      root.unmount();
    });
  });

  it('clicking quick action calls AI provider', async () => {
    persistBibleEntry({ ...newBibleEntry('suggestion-project'), title: 'Mara', status: 'canon', body: 'Cannot swim.' });
    const root = createRoot(container);
    await act(async () => {
      root.render(<AISuggestionsPanel open={true} onClose={onCloseMock} editor={null} />);
    });

    const continueBtn = Array.from(container.querySelectorAll('button')).find(
      b => b.textContent === 'edit_noteContinue'
    );
    expect(continueBtn).toBeTruthy();

    await act(async () => {
      continueBtn!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });

    expect(executeMock).toHaveBeenCalledWith(
      expect.objectContaining({
        action: 'continue',
        projectType: 'book',
        sectionTitle: 'Test Chapter',
        context: expect.stringContaining('Cannot swim.'),
      })
    );

    await act(async () => {
      root.unmount();
    });
  });

  it('close button calls onClose', async () => {
    const root = createRoot(container);
    await act(async () => {
      root.render(<AISuggestionsPanel open={true} onClose={onCloseMock} editor={null} />);
    });

    const closeBtn = container.querySelector('button[aria-label="Close panel"]');
    expect(closeBtn).toBeTruthy();

    await act(async () => {
      closeBtn!.dispatchEvent(new MouseEvent('click', { bubbles: true }));
    });

    expect(onCloseMock).toHaveBeenCalled();

    await act(async () => {
      root.unmount();
    });
  });
});
