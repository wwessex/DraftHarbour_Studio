import { beforeEach, describe, expect, it, vi } from 'vitest';
import { createLocalAIProvider } from './localReview';
import type { AIProviderConfig } from './types';
const mocks = vi.hoisted(() => ({ config: { provider: 'managed-cloud' } as AIProviderConfig, mode: 'existing', policy: {}, create: vi.fn(), available: true }));
vi.mock('./providerManager', () => ({ loadAIConfig: () => mocks.config, hydrateDesktopSecrets: async (config: AIProviderConfig) => config, createProvider: mocks.create }));
vi.mock('./setupPreferences', () => ({ getAISetupMode: () => mocks.mode }));
vi.mock('@/lib/policy', () => ({ getManagedPolicy: () => mocks.policy }));
vi.mock('./chromeAI', () => ({ ChromeAIProvider: class { isAvailable() { return mocks.available; } } }));

describe('local-only provider factory', () => {
  beforeEach(() => { mocks.create.mockReset(); mocks.policy = {}; mocks.mode = 'existing'; mocks.available = true; });
  it('removes configured cloud fallback before constructing a local server provider', async () => {
    mocks.config = { provider: 'custom-llm', customLlm: { backend: 'ollama', baseUrl: 'http://localhost:11434', model: 'local', fallbackProvider: 'managed-cloud' } };
    await createLocalAIProvider();
    expect(mocks.create).toHaveBeenCalledWith(expect.objectContaining({ customLlm: expect.objectContaining({ fallbackProvider: undefined }) }));
  });
  it('rejects cloud configuration without constructing a provider', async () => {
    mocks.config = { provider: 'managed-cloud' };
    await expect(createLocalAIProvider()).rejects.toThrow('Choose a local model');
    expect(mocks.create).not.toHaveBeenCalled();
  });
  it('does not use the cloud-fallback factory when Chrome AI is unavailable', async () => {
    mocks.config = { provider: 'chrome-ai' }; mocks.available = false;
    await expect(createLocalAIProvider()).rejects.toThrow('unavailable');
    expect(mocks.create).not.toHaveBeenCalled();
  });
  it('respects disabled AI and managed policy', async () => {
    mocks.config = { provider: 'chrome-ai' }; mocks.mode = 'later';
    await expect(createLocalAIProvider()).rejects.toThrow('AI is off');
    mocks.mode = 'existing'; mocks.policy = { disableAIProviders: true };
    await expect(createLocalAIProvider()).rejects.toThrow('managed policy');
  });
});
