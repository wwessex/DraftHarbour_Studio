import type { CustomLlmConfig } from '@/lib/ai';

export interface FieldValidation {
  valid: boolean;
  error?: string;
}

export interface LocalLlmValidationResult {
  baseUrl: FieldValidation;
  model: FieldValidation;
  valid: boolean;
  disabledReason?: string;
}

function parseHttpUrl(value: string): URL | null {
  const trimmed = value.trim();
  if (!trimmed) return null;
  try {
    const url = new URL(trimmed);
    if (url.protocol !== 'http:' && url.protocol !== 'https:') return null;
    return url;
  } catch {
    return null;
  }
}

export function validateAiEndpointUrl(value: string): FieldValidation {
  if (!value.trim()) {
    return { valid: false, error: 'Enter an AI endpoint URL.' };
  }
  if (!parseHttpUrl(value)) {
    return { valid: false, error: 'Use a valid http(s) endpoint URL.' };
  }
  return { valid: true };
}

export function validateSyncServerUrl(value: string): FieldValidation {
  if (!value.trim()) {
    return { valid: true };
  }
  if (!parseHttpUrl(value)) {
    return { valid: false, error: 'Sync server URL must be a valid http(s) URL.' };
  }
  return { valid: true };
}

export function validateAuthorizationHeader(value: string): FieldValidation {
  if (!value.trim()) {
    return { valid: true };
  }
  const normalized = value.trim();
  const matchesShape = /^[A-Za-z][A-Za-z0-9_-]*\s+\S+$/.test(normalized);
  if (!matchesShape) {
    return { valid: false, error: 'Use header format: "Bearer <token>" (or another scheme + credential).' };
  }
  return { valid: true };
}

export function validateLocalLlmConfig(config: Pick<CustomLlmConfig, 'baseUrl' | 'model'>): LocalLlmValidationResult {
  const baseUrl = validateAiEndpointUrl(config.baseUrl);
  const model: FieldValidation = config.model.trim()
    ? { valid: true }
    : { valid: false, error: 'Model is required to run local AI tests.' };

  const valid = baseUrl.valid && model.valid;
  const disabledReason = !baseUrl.valid
    ? baseUrl.error
    : !model.valid
      ? model.error
      : undefined;

  return {
    baseUrl,
    model,
    valid,
    disabledReason,
  };
}

export function mapAIConnectionFailureMessage(details: { status?: number; errorText?: string; errorMessage?: string }): string {
  const normalized = `${details.errorText ?? ''} ${details.errorMessage ?? ''}`.toLowerCase();

  if (details.status === 401 || details.status === 403 || /unauthorized|invalid api key|api key|forbidden/.test(normalized)) {
    return 'API key rejected. Verify your token and permission scope.';
  }

  if (details.status === 404 || /model.*not found|unknown model|does not exist/.test(normalized)) {
    return 'Model not found. Check the model name and pull/load it on the server.';
  }

  if (details.status === 400 || /invalid url|malformed|unsupported protocol/.test(normalized)) {
    return 'Check base URL and endpoint format.';
  }

  if (/failed to fetch|networkerror|econnrefused|enotfound|timed out|timeout|abort/.test(normalized)) {
    return 'Cannot reach the AI server. Check base URL and that the server is running.';
  }

  if (details.status === 429 || /rate limit|too many requests/.test(normalized)) {
    return 'Rate limited by the AI server. Wait and retry, or lower request volume.';
  }

  if (details.status && details.status >= 500) {
    return 'AI server error. Check server logs and retry.';
  }

  return 'Connection failed. Check base URL, model, and credentials.';
}

/** Turn transport failures into recovery guidance without exposing credentials. */
export function aiTransportError(error: unknown, endpoint: string): Error {
  if (!(error instanceof Error)) return new Error('AI request failed. Try again.');
  if (error.name === 'AbortError') return error;
  if (!/failed to fetch|fetch failed|networkerror|network request failed|load failed|econnrefused|enotfound/i.test(error.message)) return error;
  const url = parseHttpUrl(endpoint);
  const local = url && ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname);
  return new Error(local
    ? `Cannot reach the local AI server at ${url.origin}. Start your local model service, then retry. If it is running, check that its browser access settings allow this app's address. On iOS, this address refers to the iPhone or simulator.`
    : 'Cannot reach the AI server. Check your connection and endpoint in Settings > AI. If the server is running, check its browser access settings.');
}
