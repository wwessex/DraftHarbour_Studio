/** @vitest-environment jsdom */
import { afterEach, describe, expect, it, vi } from 'vitest';
import { getTauriRuntime } from '@/lib/tauriRuntime';
import { DesktopLocalProvider, DESKTOP_LOCAL_MODEL, inspectDesktopLocalAI, manageDesktopLocalPackage } from './desktopLocalProvider';
import { createProvider, saveAIConfig } from './providerManager';
vi.mock('@/lib/tauriRuntime', () => ({ getTauriRuntime: vi.fn() }));
const input = { action: 'continue', context: 'A gull called.', prompt: 'Continue briefly.', projectType: 'book' as const };
afterEach(() => { vi.resetAllMocks(); localStorage.clear(); });
describe('app-owned local provider', () => {
  it('delegates package selection and confirmation to native code without paths from IPC', async () => {
    const invoke = vi.fn().mockResolvedValue(DESKTOP_LOCAL_MODEL);
    vi.mocked(getTauriRuntime).mockResolvedValue({ invoke, listen: vi.fn() });
    await manageDesktopLocalPackage('install'); await manageDesktopLocalPackage('restore');
    expect(invoke.mock.calls).toEqual([['local_ai_install'], ['local_ai_restore']]);
  });
  it('refuses desktop installation in browser/iOS', async () => {
    vi.mocked(getTauriRuntime).mockResolvedValue(null);
    await expect(manageDesktopLocalPackage('install')).rejects.toThrow('Browser and iOS');
  });
  it('uses native IPC without a renderer endpoint or key', async () => {
    const invoke = vi.fn().mockResolvedValue({ text: 'The quay fell silent.', model: DESKTOP_LOCAL_MODEL, latencyMs: 12 });
    vi.mocked(getTauriRuntime).mockResolvedValue({ invoke, listen: vi.fn() });
    const result = await new DesktopLocalProvider().execute(input);
    expect(result.text).toBe('The quay fell silent.');
    expect(invoke).toHaveBeenCalledWith('local_ai_generate', { prompt: 'A gull called.\n\nContinue briefly.' });
  });
  it('never falls back to HTTP or cloud when native inference fails', async () => {
    const invoke = vi.fn().mockRejectedValue(new Error('Missing verified package'));
    vi.mocked(getTauriRuntime).mockResolvedValue({ invoke, listen: vi.fn() });
    const config = { provider: 'custom-llm' as const, customLlm: { managedRuntime: true, backend: 'generic-openai' as const, baseUrl: 'https://must-not-be-contacted.test', model: DESKTOP_LOCAL_MODEL, fallbackProvider: 'managed-cloud' as const } };
    await expect(createProvider(config).execute(input)).rejects.toThrow('Missing verified package');
    expect(invoke).toHaveBeenCalledTimes(1);
  });
  it('cancels the owned child and refuses a late result', async () => {
    const controller = new AbortController();
    let finish!: (value: unknown) => void;
    const invoke = vi.fn().mockImplementation((command: string) => command === 'local_ai_generate'
      ? new Promise(resolve => { finish = resolve; }) : Promise.resolve());
    vi.mocked(getTauriRuntime).mockResolvedValue({ invoke, listen: vi.fn() });
    const pending = new DesktopLocalProvider().execute({ ...input, signal: controller.signal });
    await vi.waitFor(() => expect(finish).toBeTypeOf('function'));
    controller.abort(); finish({ text: 'Late draft', model: DESKTOP_LOCAL_MODEL, latencyMs: 1 });
    await expect(pending).rejects.toMatchObject({ name: 'AbortError' });
    expect(invoke).toHaveBeenCalledWith('local_ai_stop');
  });
  it('honours AI-off and managed policy without native calls', async () => {
    localStorage.setItem('draftharbour_ai_setup_mode_v1', 'later');
    await expect(createProvider({ provider: 'managed-cloud' }).execute(input)).rejects.toThrow('AI is off');
    localStorage.setItem('draftharbour_managed_policy_v1', JSON.stringify({ disableAIProviders: true }));
    await expect(new DesktopLocalProvider().execute(input)).rejects.toThrow('managed policy');
    expect(getTauriRuntime).not.toHaveBeenCalled();
  });
  it('does not install or pretend to run desktop AI in browser/iOS', async () => {
    vi.mocked(getTauriRuntime).mockResolvedValue(null);
    await expect(inspectDesktopLocalAI()).rejects.toThrow('Browser and iOS');
    await expect(new DesktopLocalProvider().execute(input)).rejects.toThrow('No text was sent online');
  });
  it('re-enables an explicitly configured provider after deciding later', () => {
    localStorage.setItem('draftharbour_ai_setup_mode_v1', 'later');
    saveAIConfig({ provider: 'openai-compatible', endpoint: 'https://example.test' });
    expect(localStorage.getItem('draftharbour_ai_setup_mode_v1')).toBe('existing');
  });
});
