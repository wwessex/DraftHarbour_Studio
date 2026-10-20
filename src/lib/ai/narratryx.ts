import type { AIProviderConfig, CustomLlmConfig } from './types';

export const NARRATRYX_MODEL = 'narratryx-craft-v1';
export const NARRATRYX_BASE_MODEL = 'narratryx-base';
export const NARRATRYX_LABEL = 'Narratryx (experimental)';
export const NARRATRYX_HELP = 'Experimental fiction model. Review every suggestion; improved literary quality is not established. Connect to your inference service—no training is required on this device.';

/** Explicit opt-in. Never carry another provider's key to a new endpoint. */
export function createNarratryxConfig(baseUrl = ''): AIProviderConfig {
  return {
    provider: 'custom-llm',
    customLlm: {
      profile: 'narratryx',
      backend: 'generic-openai',
      baseUrl: baseUrl.trim().replace(/\/+$/, ''),
      model: NARRATRYX_MODEL,
      streaming: false,
      maxTokens: 512,
      temperature: 0,
    },
  };
}

export function isNarratryxConfig(config?: CustomLlmConfig): boolean {
  return config?.profile === 'narratryx';
}
