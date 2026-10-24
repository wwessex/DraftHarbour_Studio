"""Portable package trust/lifecycle tests: no downloads, model or GPU needed."""
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from unittest.mock import patch

from runtime.packaging.bundle import RuntimeSession, digest, platform_id, verify_bundle

FAKE_SERVER = r'''
import argparse, json
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--port',type=int); p.add_argument('--api-key-file'); p.add_argument('--alias')
a,_=p.parse_known_args()
token=Path(a.api_key_file).read_text().strip()
class Handler(BaseHTTPRequestHandler):
 def log_message(self,*args): pass
 def do_GET(self):
  if self.headers.get('Authorization') != 'Bearer '+token:
   self.send_response(401); self.end_headers(); return
  if self.path=='/redirect':
   self.send_response(302); self.send_header('Location','http://127.0.0.1:1/credential-target'); self.end_headers(); return
  self.send_response(200); self.end_headers()
  self.wfile.write(json.dumps({'data':[{'id':a.alias}]}).encode())
 def do_POST(self):
  body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
  self.send_response(200); self.end_headers()
  self.wfile.write(json.dumps({'choices':[{'message':{'content':'A proposed draft.'},'finish_reason':'stop'}], 'received':body}).encode())
HTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
'''


class PortableBundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'model.gguf').write_bytes(b'not-a-real-model')
        self.exe = self.root / 'runtime' / 'llama-server'
        self.exe.parent.mkdir()
        self.exe.write_text('#!' + sys.executable + '\n' + FAKE_SERVER)
        self.exe.chmod(0o700)
        self.manifest = dict(schema_version=1, engine='llama.cpp', platform=platform_id(),
            model_id='test-model', context_limit=4096, max_output_tokens=512,
            model='model.gguf', executable='runtime/llama-server', files={})
        for path in (self.exe, self.root / 'model.gguf'):
            self.manifest['files'][path.relative_to(self.root).as_posix()] = dict(bytes=path.stat().st_size, sha256=digest(path))
        self.write_manifest()

    def write_manifest(self):
        path = self.root / 'manifest.json'
        path.write_text(json.dumps(self.manifest))
        self.hash = digest(path)

    def verify(self):
        return verify_bundle(self.root, self.hash)

    def test_trust_is_external_and_model_bytes_are_verified(self):
        self.assertEqual(self.verify()['model_id'], 'test-model')
        with self.assertRaisesRegex(ValueError, 'trusted catalog'):
            verify_bundle(self.root, '0' * 64)
        (self.root / 'model.gguf').write_bytes(b'changed-content!')
        with self.assertRaisesRegex(ValueError, 'hash or size'):
            self.verify()

    def test_wrong_platform_and_unsafe_paths_fail(self):
        with self.assertRaisesRegex(ValueError, 'platform'):
            verify_bundle(self.root, self.hash, expected_platform='not-this-device')
        for name in ('../model.gguf', '/model.gguf', 'C:/model.gguf', 'runtime/../model.gguf', 'runtime\\llama-server'):
            with self.subTest(name=name):
                self.manifest['files'] = {name: dict(bytes=1, sha256='0'*64)}
                self.write_manifest()
                with self.assertRaisesRegex(ValueError, 'traversal'):
                    self.verify()

    def test_symlink_and_unlisted_library_fail(self):
        extra = self.root / 'runtime' / 'injected.dylib'
        extra.write_bytes(b'not-pinned')
        with self.assertRaisesRegex(ValueError, 'unlisted'):
            self.verify()
        extra.unlink()
        model = self.root / 'model.gguf'
        model.unlink()
        model.symlink_to(self.exe)
        with self.assertRaisesRegex(ValueError, 'leaves the package'):
            self.verify()

    def test_invalid_output_budget_is_rejected(self):
        self.manifest['max_output_tokens'] = True
        self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'output limit'):
            self.verify()

    @unittest.skipIf(os.name == 'nt', 'Executable script fixture requires POSIX; real Windows runtime is a separate gate')
    def test_private_auth_fresh_requests_and_owned_process_shutdown(self):
        with RuntimeSession(self.root, self.hash, startup_seconds=5) as session:
            process = session.process
            key = Path(session.private.name) / 'access-token'
            folder = key.parent
            self.assertEqual(stat.S_IMODE(key.stat().st_mode), 0o600)
            self.assertNotIn(session.token, process.args)
            self.assertIn('--api-key-file', process.args)
            self.assertIn('127.0.0.1', process.args)
            with self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(session.base_url + '/v1/models')
            self.assertEqual(error.exception.code, 401)
            error.exception.close()
            with self.assertRaises(urllib.error.HTTPError) as error:
                session.request('/redirect')
            self.assertEqual(error.exception.code, 302)
            error.exception.close()
            for passage in ('First fresh request', 'Independent request'):
                messages = [dict(role='user', content=passage)]
                result = session.complete(messages)
                self.assertEqual(result['received']['messages'], messages)
                self.assertFalse(result['received']['cache_prompt'])
                self.assertFalse(result['received']['chat_template_kwargs']['enable_thinking'])
            with self.assertRaises(ValueError):
                session.complete([], max_tokens=513)
            with self.assertRaises(ValueError):
                session.request('//external.example')
        self.assertIsNotNone(process.poll())
        self.assertFalse(folder.exists())
        self.assertIsNone(session.token)
        self.assertIsNone(session.base_url)

    def test_package_change_between_selection_and_launch_fails_before_execution(self):
        session = RuntimeSession(self.root, self.hash)
        (self.root / 'model.gguf').write_bytes(b'changed')
        with patch('runtime.packaging.bundle.subprocess.Popen') as popen:
            with self.assertRaises(ValueError):
                session.__enter__()
            popen.assert_not_called()

    def test_launch_failure_cleans_private_credentials(self):
        session = RuntimeSession(self.root, self.hash)
        with patch('runtime.packaging.bundle.subprocess.Popen', side_effect=OSError('not executable')):
            with self.assertRaises(OSError):
                session.__enter__()
        self.assertFalse(Path(session.private.name).exists())
        self.assertIsNone(session.token)

    @unittest.skipIf(os.name == 'nt', 'POSIX executable fixture')
    def test_early_runtime_exit_cleans_credentials(self):
        self.exe.write_text('#!' + sys.executable + '\nraise SystemExit(1)\n')
        self.manifest['files']['runtime/llama-server'] = dict(bytes=self.exe.stat().st_size, sha256=digest(self.exe))
        self.write_manifest()
        session = RuntimeSession(self.root, self.hash, startup_seconds=3)
        with self.assertRaisesRegex(RuntimeError, 'exited during startup'):
            session.__enter__()
        self.assertFalse(Path(session.private.name).exists())
        self.assertIsNotNone(session.process.poll())

    def test_editing_diagnostic_has_no_minimum_word_count(self):
        from runtime.packaging.evaluate import summarize
        cases = [dict(id='edit', kind='editing', exact_reference='The gull called.', word_count_min=None, word_count_max=None)]
        rows = [dict(case_id='edit', text='The gull called.', error=None, stats={'finish_reason': 'stop'})]
        score = summarize(cases, rows)
        self.assertEqual(score['exact_minimal_repairs'], 1)
        self.assertEqual(score['word_limits_by_kind']['editing'], dict(passed=1, total=1))
        self.assertIsNone(score['quality_ratings'])


if __name__ == '__main__':
    unittest.main()
