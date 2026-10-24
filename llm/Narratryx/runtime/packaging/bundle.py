"""Verified local development bundle and private runtime lifecycle.

This standard-library harness validates the desktop runtime contract. It is not
an installer, downloader, public service or native app integration.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import platform
import re
import secrets
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def platform_id():
    system = dict(Darwin='darwin', Windows='windows', Linux='linux').get(platform.system())
    machine = dict(aarch64='arm64', arm64='arm64', AMD64='x86_64', x86_64='x86_64').get(platform.machine())
    if not system or not machine:
        raise ValueError('This local runtime platform is unsupported')
    return f'{system}-{machine}'


def safe_file(root, name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or '\\' in name or ':' in name or any(p in ('..', '.') for p in name.split('/')):
        raise ValueError('Bundle path must be a relative file without traversal')
    result = root.joinpath(*path.parts)
    if not result.resolve().is_relative_to(root.resolve()) or result.is_symlink() or not result.is_file():
        raise ValueError('Bundle file is missing or leaves the package')
    return result


def verify_bundle(root, expected_manifest_sha256, expected_platform=None):
    root = Path(root).resolve()
    manifest_file = root / 'manifest.json'
    if manifest_file.is_symlink() or not manifest_file.is_file() or manifest_file.stat().st_size > 1024 * 1024:
        raise ValueError('Bundle manifest is missing, linked or too large')
    if not re.fullmatch('[a-f0-9]{64}', expected_manifest_sha256 or '') or digest(manifest_file) != expected_manifest_sha256:
        raise ValueError('Bundle manifest does not match the trusted catalog hash')
    manifest = json.loads(manifest_file.read_text())
    if manifest.get('schema_version') != 1 or manifest.get('engine') != 'llama.cpp':
        raise ValueError('Unsupported local runtime manifest')
    if manifest.get('platform') != (expected_platform or platform_id()):
        raise ValueError('Runtime package does not match this platform')
    if not re.fullmatch('[a-z0-9][a-z0-9._-]{0,127}', manifest.get('model_id', '')):
        raise ValueError('Invalid model identity')
    if type(manifest.get('context_limit')) is not int or not 512 <= manifest['context_limit'] <= 4096:
        raise ValueError('Invalid development context limit')
    if type(manifest.get('max_output_tokens')) is not int or not 1 <= manifest['max_output_tokens'] <= 512:
        raise ValueError('Invalid development output limit')
    files = manifest.get('files')
    if not isinstance(files, dict) or not files:
        raise ValueError('Missing bundle file hashes')
    for name, record in files.items():
        path = safe_file(root, name)
        if (not isinstance(record, dict) or type(record.get('bytes')) is not int
                or record['bytes'] < 0 or not re.fullmatch('[a-f0-9]{64}', record.get('sha256', ''))
                or path.stat().st_size != record['bytes'] or digest(path) != record['sha256']):
            raise ValueError('Bundle artifact hash or size mismatch')
    for field in ('model', 'executable'):
        if manifest.get(field) not in files:
            raise ValueError('Model and executable must both be pinned')
    actual = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file() or p.is_symlink()}
    if actual != set(files) | {'manifest.json'}:
        raise ValueError('Bundle contains unlisted files')
    return manifest


def build_bundle(export_dir, runtime_bin, destination, model_id, model_license):
    export_dir, runtime_bin, destination = map(Path, (export_dir, runtime_bin, destination))
    report = json.loads((export_dir / 'export-report.json').read_text())
    if report.get('status') != 'exported':
        raise ValueError('A completed verified export is required')
    model = safe_file(export_dir, report['artifact'])
    if digest(model) != report['sha256'] or model.stat().st_size != report['bytes']:
        raise ValueError('Export changed after its recorded hash')
    executable = 'llama-server.exe' if platform.system() == 'Windows' else 'llama-server'
    if not (runtime_bin / executable).is_file():
        raise ValueError('Installed runtime executable is missing')
    destination.mkdir(parents=True, exist_ok=False)
    (destination / 'runtime').mkdir()
    shutil.copy2(model, destination / 'model.gguf')
    for item in runtime_bin.iterdir():
        if item.is_file() and (item.name == executable or item.name.endswith(('.dylib', '.dll', '.so', '.metallib')) or '.so.' in item.name):
            shutil.copy2(item, destination / 'runtime' / item.name, follow_symlinks=True)
    shutil.copy2(model_license, destination / 'MODEL-LICENSE')
    shutil.copy2(runtime_bin.parent.parent / 'LICENSE', destination / 'RUNTIME-LICENSE')
    (destination / 'NOTICE').write_text('Development-only Narratryx craft adapter; literary improvement unproven.\n'
        'Base: mlx-community/Qwen3.5-4B-MLX-8bit, derived from Qwen/Qwen3.5-4B.\n'
        'Adapter provenance: twenty scoped Wharton/Hamilton craft answers.\n'
        'Model conversion and Q4_K_M quantization are modifications; no training performed.\n'
        'Public redistribution and installer signing are separate release gates.\n')
    files = {p.relative_to(destination).as_posix(): dict(bytes=p.stat().st_size, sha256=digest(p))
             for p in sorted(destination.rglob('*')) if p.is_file()}
    manifest = dict(schema_version=1, engine='llama.cpp', platform=platform_id(), model_id=model_id,
                    context_limit=4096, max_output_tokens=512, model='model.gguf',
                    executable='runtime/' + executable, files=files,
                    source_adapter_sha256=report['source_adapter_sha256'], base_revision=report['base_revision'],
                    experimental=True, public_release_ready=False)
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return digest(destination / 'manifest.json')


class RuntimeSession:
    """Own one verified child, bind loopback, and keep credentials out of UI/argv."""
    def __init__(self, root, manifest_sha256, startup_seconds=120):
        self.root = Path(root).resolve()
        self.manifest_sha256 = manifest_sha256
        self.manifest = verify_bundle(self.root, manifest_sha256)
        self.startup_seconds = startup_seconds
        self.process = None
        self.private = None
        self.token = None
        self.base_url = None
        self.started_in_seconds = None

    def __enter__(self):
        if self.private is not None:
            raise RuntimeError('A runtime session cannot be entered twice')
        started = time.monotonic()
        # Recheck against the original trusted hash if the package changed while queued.
        self.manifest = verify_bundle(self.root, self.manifest_sha256)
        self.private = tempfile.TemporaryDirectory(prefix='narratryx-runtime-')
        folder = Path(self.private.name)
        key_file = folder / 'access-token'
        self.token = secrets.token_urlsafe(32)
        with os.fdopen(os.open(key_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600), 'w') as f:
            f.write(self.token + '\n')
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        self.base_url = f'http://127.0.0.1:{port}'
        args = [str(self.root / self.manifest['executable']), '-m', str(self.root / self.manifest['model']),
                '--host', '127.0.0.1', '--port', str(port), '--api-key-file', str(key_file),
                '--alias', self.manifest['model_id'], '--ctx-size', str(self.manifest['context_limit']),
                '--parallel', '1', '--no-context-shift', '--no-webui']
        try:
            with (folder / 'runtime.log').open('wb') as log:
                self.process = subprocess.Popen(args, cwd=self.root, stdin=subprocess.DEVNULL,
                                                stdout=log, stderr=log, shell=False)
            deadline = time.monotonic() + self.startup_seconds
            while time.monotonic() < deadline:
                if self.process.poll() is not None:
                    raise RuntimeError('The verified local runtime exited during startup')
                try:
                    models = self.request('/v1/models', timeout=2)
                    if any(row.get('id') == self.manifest['model_id'] for row in models.get('data', [])):
                        self.started_in_seconds = round(time.monotonic() - started, 2)
                        return self
                except (OSError, ValueError):
                    pass
                time.sleep(.1)
            raise TimeoutError('Local runtime startup exceeded its deadline')
        except BaseException:
            self.close()
            raise

    def request(self, path, payload=None, timeout=125):
        if not self.base_url or not path.startswith('/') or path.startswith('//'):
            raise ValueError('Only this private runtime may be addressed')
        request = urllib.request.Request(self.base_url + path,
            data=None if payload is None else json.dumps(payload, allow_nan=False).encode(),
            headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        # Do not follow a redirect with a private local credential.
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *_):
                return None
        with urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect()).open(request, timeout=timeout) as response:
            return json.load(response)

    def complete(self, messages, max_tokens=128):
        if type(max_tokens) is not int or not 1 <= max_tokens <= self.manifest['max_output_tokens']:
            raise ValueError('Invalid output limit')
        payload = dict(model=self.manifest['model_id'], messages=messages, max_tokens=max_tokens,
                       stream=False, temperature=0, seed=42, top_p=1, top_k=20,
                       min_p=0, repeat_penalty=1, presence_penalty=0, cache_prompt=False,
                       chat_template_kwargs={'enable_thinking': False})
        result = self.request('/v1/chat/completions', payload)
        if not result.get('choices', [{}])[0].get('message', {}).get('content', '').strip():
            raise RuntimeError('Local runtime returned no draft')
        return result

    def close(self):
        try:
            if self.process is not None and self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5)
        finally:
            if self.private is not None:
                self.private.cleanup()
            self.token = None
            self.base_url = None

    def __exit__(self, *_):
        self.close()


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    build = commands.add_parser('build', help='Copy a completed export and installed runtime; no download')
    build.add_argument('--export', dest='export_dir', type=Path, required=True)
    build.add_argument('--runtime-bin', type=Path, required=True)
    build.add_argument('--output', type=Path, required=True)
    build.add_argument('--model-id', required=True)
    build.add_argument('--model-license', type=Path, required=True)
    verify = commands.add_parser('verify', help='Check against a separately trusted manifest hash')
    verify.add_argument('--bundle', type=Path, required=True)
    verify.add_argument('--manifest-sha256', required=True)
    args = parser.parse_args()
    if args.command == 'build':
        result = build_bundle(args.export_dir, args.runtime_bin, args.output, args.model_id, args.model_license)
        print(json.dumps(dict(manifest_sha256=result, public_release_ready=False)))
    else:
        result = verify_bundle(args.bundle, args.manifest_sha256)
        print(json.dumps(dict(verified=True, model_id=result['model_id'], platform=result['platform'])))


if __name__ == '__main__':
    main()
