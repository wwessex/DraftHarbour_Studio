import { getTauriRuntime } from '@/lib/tauriRuntime';
import { getManagedPolicy } from '@/lib/policy';
import type { AIProvider, AIRequest, AIResponse } from './types';

export const DESKTOP_LOCAL_MODEL = 'narratryx-craft-v1-q4-k-m';

export function assertLocalAIAllowed() {
  const policy = getManagedPolicy();
  if (policy.disableAIProviders || policy.disabledAIProviderTypes?.includes('custom-llm')) {
    throw new Error('Local AI is disabled by managed policy.');
  }
}

export async function inspectDesktopLocalAI(): Promise<string> {
  assertLocalAIAllowed();
  const runtime = await getTauriRuntime();
  if (!runtime) throw new Error('This model needs the desktop app and a verified local package. Browser and iOS setup do not install desktop models.');
  return runtime.invoke<string>('local_ai_inspect');
}

export async function stopDesktopLocalAI(): Promise<void> {
  const runtime = await getTauriRuntime();
  if (runtime) await runtime.invoke('local_ai_stop');
}

/** The renderer sends text through native IPC. It never receives a port or key. */
export class DesktopLocalProvider implements AIProvider {
  readonly type = 'custom-llm' as const;
  readonly supportsStreaming = false;
  isAvailable() { return typeof window !== 'undefined' && ('__TAURI_INTERNALS__' in window || '__TAURI__' in window); }
  async execute(request: AIRequest): Promise<AIResponse> {
    assertLocalAIAllowed();
    const runtime = await getTauriRuntime();
    if (!runtime) throw new Error('Managed local AI requires the desktop app. No text was sent online.');
    if (request.signal?.aborted) throw new DOMException('Cancelled', 'AbortError');
    let stopping: Promise<unknown> | undefined;
    const cancel = () => { stopping = runtime.invoke('local_ai_stop').catch(() => undefined); };
    request.signal?.addEventListener('abort', cancel, { once: true });
    try {
      const result = await runtime.invoke<{ text: string; model: string; latencyMs: number }>('local_ai_generate', {
        prompt: [request.context, request.prompt].filter(Boolean).join('\n\n'),
      });
      if (request.signal?.aborted) throw new DOMException('Cancelled', 'AbortError');
      if (result.model !== DESKTOP_LOCAL_MODEL || !result.text?.trim()) throw new Error('Local AI returned an invalid draft.');
      return { text: result.text, latencyMs: result.latencyMs, provider: this.type, streamed: false };
    } catch (error) {
      if (request.signal?.aborted) throw new DOMException('Cancelled', 'AbortError');
      throw error instanceof Error ? error : new Error(String(error));
    } finally {
      request.signal?.removeEventListener('abort', cancel);
      await stopping;
    }
  }
  destroy() { /* Runtime belongs to the app, not a short-lived composer instance. */ }
}
