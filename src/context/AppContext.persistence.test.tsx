/** @vitest-environment jsdom */
import { act, StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { expect, it, vi } from 'vitest';
import { AppProvider, useApp } from './AppContext';
import { createDefaultSettings } from './appSettings';
import { createSettingsEnvelope, loadSettingsFromStorage } from '@/lib/settingsMigration';
import { SETTINGS_STORAGE_KEY } from '@/lib/storageKeys';

(globalThis as { IS_REACT_ACT_ENVIRONMENT?: boolean }).IS_REACT_ACT_ENVIRONMENT = true;
vi.mock('@/components/UI', () => ({ useToast: () => ({ showErrorToast: vi.fn() }) }));

it('preserves stored preferences when StrictMode replays mount effects', async () => {
  const defaults = createDefaultSettings(false);
  const stored = { ...defaults, theme: 'dark' as const, dailyWordGoal: 1234, onboardingComplete: true };
  localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(createSettingsEnvelope(stored)));
  const container = document.createElement('div');
  const root = createRoot(container);
  let app!: ReturnType<typeof useApp>;
  function Probe() { app = useApp(); return null; }
  try {
    await act(async () => { root.render(<StrictMode><AppProvider><Probe /></AppProvider></StrictMode>); });
    expect(app.state.settings).toMatchObject({ theme: 'dark', dailyWordGoal: 1234, onboardingComplete: true });
    const persisted = loadSettingsFromStorage(localStorage.getItem(SETTINGS_STORAGE_KEY), defaults);
    expect(persisted).toMatchObject({ theme: 'dark', dailyWordGoal: 1234, onboardingComplete: true });
  } finally {
    await act(async () => root.unmount());
    container.remove();
  }
});
