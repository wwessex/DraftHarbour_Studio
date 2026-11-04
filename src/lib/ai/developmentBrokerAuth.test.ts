import { afterEach, expect, it, vi } from 'vitest';
import { developmentBrokerAuth, setDevelopmentBrokerToken } from './developmentBrokerAuth';

afterEach(() => {
  sessionStorage.clear();
  vi.unstubAllEnvs();
});

it('uses a manually entered token only for the approved loopback origin in development', () => {
  vi.stubEnv('DEV', true);
  const endpoint = 'http://localhost:1420/api/chat';
  setDevelopmentBrokerToken(endpoint, 'local-test-token');
  expect(developmentBrokerAuth(endpoint)).toEqual({
    headers: { Authorization: 'Bearer local-test-token' },
    redirect: 'error',
  });
  expect(developmentBrokerAuth('http://localhost:5173/api/chat').headers).toBeUndefined();
  expect(developmentBrokerAuth('https://localhost.example/api/chat').headers).toBeUndefined();

  vi.stubEnv('DEV', false);
  expect(developmentBrokerAuth(endpoint).headers).toBeUndefined();
});
