import { readFileSync } from 'node:fs';
import { describe, expect, it, vi } from 'vitest';
import { createNarratryxConfig, NARRATRYX_BASE_MODEL, NARRATRYX_LABEL, NARRATRYX_MODEL } from './narratryx';
import { CustomLlmProvider } from './customLlmProvider';
import { fetchWithPolicy } from '@/lib/integrations/providerClient';

vi.mock('@/lib/integrations/providerClient', () => ({ fetchWithPolicy: vi.fn() }));

describe('Narratryx experimental integration', () => {
  it('shares version IDs and defaults with native clients and serving configuration', () => {
    const contract = JSON.parse(readFileSync('fixtures/narratryx-profile.json', 'utf8'));
    const pin = JSON.parse(readFileSync('llm/Narratryx/configs/narratryx-craft-v1.json', 'utf8'));
    const config = createNarratryxConfig();
    expect(config.customLlm).toMatchObject({ model: contract.model, streaming: contract.streaming, maxTokens: contract.maxTokens, temperature: contract.temperature });
    expect(NARRATRYX_LABEL).toBe(contract.label);
    expect(NARRATRYX_BASE_MODEL).toBe(contract.baseModel);
    expect(pin.model_id).toBe(NARRATRYX_MODEL);
    expect(pin.base_model_id).toBe(NARRATRYX_BASE_MODEL);
    expect(config.customLlm?.baseUrl).toBe('');
    expect(config.customLlm?.apiKey).toBeUndefined();
  });

  it('sends an explicitly selected candidate to its service with auth and bounded non-streaming generation', async () => {
    const config = createNarratryxConfig('https://models.example.test/');
    config.customLlm!.apiKey = 'test-inference-credential';
    vi.mocked(fetchWithPolicy).mockResolvedValueOnce(new Response(JSON.stringify({
      model: NARRATRYX_MODEL, choices: [{ message: { content: 'The door opened.' }, finish_reason: 'stop' }],
    }), { status: 200 }));
    const signal = new AbortController().signal;
    const result = await new CustomLlmProvider(config).execute({ action: 'continue', projectType: 'book', prompt: 'Continue briefly.', context: 'The latch moved.', signal });
    const [url, options] = vi.mocked(fetchWithPolicy).mock.calls.at(-1)!;
    expect(url).toBe('https://models.example.test/v1/chat/completions');
    expect(options?.signal).toBe(signal);
    expect(options?.headers).toMatchObject({ Authorization: 'Bearer test-inference-credential' });
    expect(vi.mocked(fetchWithPolicy).mock.calls.at(-1)?.[2]).toMatchObject({ retries: 0, timeoutMs: 125_000 });
    expect(JSON.parse(options?.body as string)).toMatchObject({ model: NARRATRYX_MODEL, stream: false, max_tokens: 512, temperature: 0 });
    expect(result.text).toBe('The door opened.');
  });

  it('keeps connection failures actionable and never returns a fabricated suggestion', async () => {
    vi.mocked(fetchWithPolicy).mockResolvedValueOnce(new Response(JSON.stringify({ error: { message: 'Use a shorter passage. Nothing was truncated.' } }), { status: 413 }));
    await expect(new CustomLlmProvider(createNarratryxConfig('https://models.example.test')).execute({
      action: 'custom', projectType: 'book', prompt: 'Revise', context: 'Original manuscript',
    })).rejects.toThrow('Use a shorter passage');
  });
});
