// This token is entered locally, never injected into Vite's client environment.
function tokenStorageKey(endpoint: string): string | undefined {
  if (!import.meta.env.DEV) return undefined;
  try {
    const url = new URL(endpoint, window.location.href);
    if (!['http:', 'https:'].includes(url.protocol) ||
        !['127.0.0.1', 'localhost', '[::1]'].includes(url.hostname) ||
        url.username || url.password) return undefined;
    return `draftharbour.devBrokerToken:${url.origin}`;
  } catch {
    return undefined;
  }
}

export function getDevelopmentBrokerToken(endpoint: string): string {
  const key = tokenStorageKey(endpoint);
  return key ? sessionStorage.getItem(key) ?? '' : '';
}

export function setDevelopmentBrokerToken(endpoint: string, token: string): void {
  const key = tokenStorageKey(endpoint);
  if (!key) return;
  if (token) sessionStorage.setItem(key, token);
  else sessionStorage.removeItem(key);
}

export function developmentBrokerAuth(endpoint: string) {
  const token = getDevelopmentBrokerToken(endpoint).trim();
  return {
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    ...(token ? { redirect: 'error' as const } : {}),
  };
}
