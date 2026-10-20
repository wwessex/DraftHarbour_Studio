"""Protocol/security/identity tests; no model dependencies or downloads."""
from pathlib import Path
import hashlib
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

from runtime.local.server import InferenceServer, access_token
from runtime.local.engine import ContextTooLong, verify_files

ROOT = Path(__file__).resolve().parents[1]
PIN = json.loads((ROOT / 'configs/narratryx-craft-v1.json').read_text())
TOKEN = 'local-test-credential-not-a-real-secret-12345'


class FakeEngine:
    def __init__(self):
        self.calls = []
        self.block = False
        self.started = threading.Event()
        self.release = threading.Event()
        self.cancelled = threading.Event()
        self.too_long = False

    def generate(self, messages, model, count, temperature, cancel):
        self.calls.append((messages, model, count, temperature))
        self.started.set()
        if self.too_long:
            raise ContextTooLong('Use a shorter passage; nothing was truncated')
        if self.block:
            while not self.release.wait(.01):
                if cancel.is_set():
                    self.cancelled.set()
                    raise TimeoutError()
        return dict(text='A proposed continuation.', usage=dict(prompt_tokens=12, completion_tokens=5, total_tokens=17), finish_reason='stop')


class LocalServingTests(unittest.TestCase):
    def setUp(self):
        self.engine = FakeEngine()
        self.server = InferenceServer(('127.0.0.1', 0), self.engine, PIN, TOKEN,
                                      ['http://localhost:5173', 'capacitor://localhost', 'http://tauri.localhost'], deadline=.2)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.server.server_port}'

    def tearDown(self):
        self.engine.release.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(2)

    def request(self, path, body=None, auth=True, origin=None, method=None):
        headers = {'Content-Type': 'application/json'}
        if auth:
            headers['Authorization'] = 'Bearer ' + TOKEN
        if origin:
            headers['Origin'] = origin
        encoded = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request(self.base + path, data=encoded, headers=headers, method=method)
        try:
            response = urllib.request.urlopen(request, timeout=3)
        except urllib.error.HTTPError as e:
            response = e
        with response:
            return response.code, json.load(response), response.headers

    def payload(self, **updates):
        return dict(model=PIN['model_id'], messages=[dict(role='user', content='Continue briefly.')], **updates)

    def test_authentication_precedes_discovery_and_inference(self):
        for path, body in [('/v1/models', None), ('/v1/chat/completions', self.payload())]:
            status, _, headers = self.request(path, body, auth=False)
            self.assertEqual(status, 401)
            self.assertEqual(headers['Cache-Control'], 'no-store')
        self.assertFalse(self.engine.calls)

    def test_exact_model_identity_and_source_pin_are_public_metadata_only(self):
        status, data, _ = self.request('/v1/models')
        self.assertEqual(status, 200)
        candidate, base = data['data']
        self.assertEqual(candidate['id'], PIN['model_id'])
        self.assertEqual(candidate['adapter_sha256'], PIN['adapter_sha256'])
        self.assertEqual(base['id'], PIN['base_model_id'])
        self.assertIsNone(base['adapter_sha256'])
        self.assertNotIn(TOKEN, json.dumps(data))
        self.assertNotIn(str(Path.home()), json.dumps(data))
        contract = json.loads((ROOT.parents[1] / 'fixtures/narratryx-profile.json').read_text())
        self.assertEqual(candidate['id'], contract['model'])
        self.assertEqual(base['id'], contract['baseModel'])

    def test_real_chat_contract_caps_generation_and_attests_adapter(self):
        status, data, _ = self.request('/v1/chat/completions', self.payload(max_tokens=2048, stream=False, temperature=0))
        self.assertEqual(status, 200)
        self.assertEqual(data['choices'][0]['message']['content'], 'A proposed continuation.')
        self.assertEqual(self.engine.calls[0][2], 512)
        self.assertEqual(data['narratryx']['adapter_sha256'], PIN['adapter_sha256'])
        self.assertEqual(data['model'], PIN['model_id'])
        request = self.payload()
        request['model'] = PIN['base_model_id']
        status, data, _ = self.request('/v1/chat/completions', request)
        self.assertEqual(status, 200)
        self.assertIsNone(data['narratryx']['adapter_sha256'])

    def test_unknown_models_never_silently_fall_back(self):
        payload = self.payload()
        payload['model'] = '/arbitrary/model/path'
        self.assertEqual(self.request('/v1/chat/completions', payload)[0], 404)
        self.assertFalse(self.engine.calls)

    def test_only_explicit_origins_are_allowed_with_no_wildcard(self):
        self.assertEqual(self.request('/v1/models', origin='https://untrusted.example')[0], 403)
        for origin in ['http://localhost:5173', 'capacitor://localhost', 'http://tauri.localhost']:
            status, _, headers = self.request('/v1/chat/completions', auth=False, origin=origin, method='OPTIONS')
            self.assertEqual(status, 200)
            self.assertEqual(headers['Access-Control-Allow-Origin'], origin)
            self.assertIn('Authorization', headers['Access-Control-Allow-Headers'])
        with self.assertRaises(ValueError):
            InferenceServer(('127.0.0.1', 0), self.engine, PIN, TOKEN, ['*'])

    def test_stream_tools_and_invalid_payloads_fail_without_execution(self):
        for payload in [self.payload(stream=True), self.payload(tools=[{'name': 'execute'}]),
                        self.payload(max_tokens=True), self.payload(temperature=3), [],
                        dict(model=PIN['model_id'], messages=[dict(role='user', content={'image': 'x'})])]:
            self.assertEqual(self.request('/v1/chat/completions', payload)[0], 400)
        self.assertFalse(self.engine.calls)

    def test_oversized_context_fails_without_rewriting_it(self):
        self.engine.too_long = True
        payload = self.payload()
        before = json.dumps(payload)
        status, data, _ = self.request('/v1/chat/completions', payload)
        self.assertEqual(status, 413)
        self.assertIn('nothing was truncated', data['error']['message'])
        self.assertEqual(before, json.dumps(payload))

    def test_deadline_cancels_generation_and_releases_busy_state(self):
        self.engine.block = True
        self.assertEqual(self.request('/v1/chat/completions', self.payload())[0], 504)
        self.assertTrue(self.engine.cancelled.is_set())
        self.engine.block = False
        self.assertEqual(self.request('/v1/chat/completions', self.payload())[0], 200)

    def test_concurrent_generation_is_rejected_instead_of_loading_another_model(self):
        self.engine.block = True
        result = []
        thread = threading.Thread(target=lambda: result.append(self.request('/v1/chat/completions', self.payload())[0]))
        thread.start()
        self.assertTrue(self.engine.started.wait(2))
        self.assertEqual(self.request('/v1/chat/completions', self.payload())[0], 429)
        self.engine.release.set()
        thread.join(2)
        self.assertEqual(result, [200])


class LocalPinTests(unittest.TestCase):
    def test_private_token_is_created_once_and_never_returned_in_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'access-token'
            first = access_token(path)
            self.assertGreaterEqual(len(first), 32)
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            self.assertEqual(first, access_token(path))
            path.chmod(0o644)
            with self.assertRaisesRegex(ValueError, 'private'):
                access_token(path)

    def test_changed_artifacts_are_rejected_before_ml_imports(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); base = root / 'base'; adapter = root / 'adapter'
            base.mkdir(); adapter.mkdir()
            (base / 'model.safetensors').write_bytes(b'original base')
            (base / 'config.json').write_text('{}')
            (adapter / 'adapters.safetensors').write_bytes(b'original adapter')
            (adapter / 'adapter_config.json').write_text(json.dumps(dict(base_model_name_or_path='original-base')))
            h = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
            pin = dict(base_repo='original-base', base_weights_sha256=h(base / 'model.safetensors'),
                       adapter_sha256=h(adapter / 'adapters.safetensors'), adapter_config_sha256=h(adapter / 'adapter_config.json'),
                       base_metadata={'config.json': h(base / 'config.json')})
            verify_files(pin, base, adapter)
            (adapter / 'adapters.safetensors').write_bytes(b'wrong adapter')
            with self.assertRaisesRegex(ValueError, 'pin mismatch'):
                verify_files(pin, base, adapter)


if __name__ == '__main__':
    unittest.main()
