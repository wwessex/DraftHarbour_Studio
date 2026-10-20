"""Small authenticated, non-streaming OpenAI-compatible experimental service.

HTTP/protocol tests use only the standard library and an injected fake engine.
No model imports, downloads, training or remote jobs occur on module import.
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import hmac
import json
import math
import os
import secrets
import select
import socket
import threading
import time
import uuid

from .engine import ContextTooLong


def access_token(path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'w') as f:
            f.write(secrets.token_urlsafe(32) + '\n')
    if path.stat().st_mode & 0o077:
        raise ValueError('Access token file must be private (chmod 600)')
    token = path.read_text().strip()
    if len(token) < 32:
        raise ValueError('Access token must contain at least 32 characters')
    return token


def validate_payload(data, pin):
    if not isinstance(data, dict):
        raise ValueError('Expected a JSON object')
    if data.get('model') not in (pin['model_id'], pin['base_model_id']):
        raise LookupError('Unknown model. Use an ID returned by /v1/models.')
    if data.get('stream', False) is not False:
        raise ValueError('Disable streaming for this experimental service')
    messages = data.get('messages')
    if not isinstance(messages, list) or not 1 <= len(messages) <= 32:
        raise ValueError('Provide 1–32 text chat messages')
    for i, message in enumerate(messages):
        if not isinstance(message, dict) or set(message) - {'role', 'content'}:
            raise ValueError('Only text role/content messages are supported')
        role = message.get('role')
        if role not in ('system', 'user', 'assistant') or (role == 'system' and i != 0):
            raise ValueError('Unsupported message role or system-message position')
        if not isinstance(message.get('content'), str) or not message['content'].strip():
            raise ValueError('Message content must be nonempty text')
    if messages[-1]['role'] != 'user':
        raise ValueError('The final message must be a user request')
    if data.get('tools') or data.get('tool_choice') or data.get('functions'):
        raise ValueError('Tool execution is not supported')
    count = data.get('max_tokens', pin['max_output_tokens'])
    if type(count) is not int or count < 1:
        raise ValueError('max_tokens must be a positive integer')
    temperature = data.get('temperature', 0)
    if type(temperature) not in (int, float) or not math.isfinite(temperature) or not 0 <= temperature <= 2:
        raise ValueError('temperature must be between 0 and 2')
    return messages, data['model'], min(count, pin['max_output_tokens']), temperature


class InferenceServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, engine, pin, token, origins=(), deadline=120):
        if not isinstance(token, str) or len(token) < 32:
            raise ValueError('A private access token is required')
        if '*' in origins:
            raise ValueError('List explicit allowed origins instead of a wildcard')
        self.engine, self.pin, self.token = engine, pin, token
        self.origins = frozenset(origins)
        self.deadline = deadline
        self.generation_lock = threading.Lock()
        super().__init__(address, Handler)


class Handler(BaseHTTPRequestHandler):
    server_version = 'Narratryx/1'

    def log_message(self, *_):
        # Do not log credentials, request bodies, manuscript text or query URLs.
        pass

    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def reply(self, status, body):
        encoded = json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(encoded)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Connection', 'close')
        origin = self.headers.get('Origin')
        if origin in self.server.origins:
            self.send_header('Access-Control-Allow-Origin', origin)
            self.send_header('Vary', 'Origin')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
        self.end_headers()
        try:
            self.wfile.write(encoded)
        except (BrokenPipeError, ConnectionResetError):
            pass
        self.close_connection = True

    def error(self, status, message):
        self.reply(status, {'error': {'message': message, 'type': 'narratryx_error'}})

    def allowed(self, auth=True):
        origin = self.headers.get('Origin')
        if origin and origin not in self.server.origins:
            self.error(403, 'This client origin is not enabled on the inference service')
            return False
        if auth:
            actual = self.headers.get('Authorization', '')
            expected = 'Bearer ' + self.server.token
            if not hmac.compare_digest(actual.encode(), expected.encode()):
                self.error(401, 'A valid inference-service access token is required')
                return False
        return True

    def do_OPTIONS(self):
        if self.allowed(auth=False):
            self.reply(200, {})

    def do_GET(self):
        if self.path == '/health':
            if self.allowed(auth=False):
                self.reply(200, {'status': 'ready', 'experimental': True})
            return
        if not self.allowed():
            return
        if self.path != '/v1/models':
            self.error(404, 'Unknown inference route')
            return
        pin = self.server.pin
        models = []
        for ident, adapter in [(pin['model_id'], True), (pin['base_model_id'], False)]:
            models.append(dict(id=ident, object='model', owned_by='narratryx-experimental',
                               experimental=True, base_revision=pin['base_revision'],
                               adapter_sha256=pin['adapter_sha256'] if adapter else None,
                               context_limit=pin['context_limit'], max_output_tokens=pin['max_output_tokens']))
        self.reply(200, {'object': 'list', 'data': models})

    def do_POST(self):
        if not self.allowed():
            return
        if self.path != '/v1/chat/completions':
            self.error(404, 'Unknown inference route')
            return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 65536 or self.headers.get('Transfer-Encoding'):
                self.error(413, 'Use a smaller text request (maximum 64 KiB)')
                return
            if self.headers.get_content_type() != 'application/json':
                self.error(415, 'Content-Type must be application/json')
                return
            data = json.loads(self.rfile.read(length), parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Invalid JSON number')))
            messages, model, count, temperature = validate_payload(data, self.server.pin)
        except LookupError as e:
            self.error(404, str(e))
            return
        except (ValueError, UnicodeDecodeError, socket.timeout):
            self.error(400, 'Invalid text completion request; check model, messages and generation settings')
            return
        if not self.server.generation_lock.acquire(blocking=False):
            self.error(429, 'This experimental model is busy; please retry after the current request')
            return
        cancel, finished = threading.Event(), threading.Event()
        timer = threading.Timer(self.server.deadline, cancel.set)
        timer.daemon = True
        timer.start()

        def watch_disconnect():
            while not finished.wait(0.2):
                try:
                    readable, _, _ = select.select([self.connection], [], [], 0)
                    if readable and self.connection.recv(1, socket.MSG_PEEK) == b'':
                        cancel.set()
                        return
                except OSError:
                    cancel.set()
                    return

        threading.Thread(target=watch_disconnect, daemon=True).start()
        try:
            result = self.server.engine.generate(messages, model, count, temperature, cancel)
            if cancel.is_set():
                raise TimeoutError()
            pin = self.server.pin
            self.reply(200, dict(id='chatcmpl-' + uuid.uuid4().hex, object='chat.completion', created=int(time.time()),
                model=model, choices=[dict(index=0, message=dict(role='assistant', content=result['text']), finish_reason=result['finish_reason'])],
                usage=result.get('usage', {}), narratryx=dict(experimental=True, base_revision=pin['base_revision'],
                adapter_sha256=pin['adapter_sha256'] if model == pin['model_id'] else None)))
        except ContextTooLong as e:
            self.error(413, str(e))
        except TimeoutError:
            self.error(504, 'Generation was cancelled or timed out; your manuscript was not changed')
        except Exception:
            self.error(500, 'Model inference failed; check the private service environment')
        finally:
            finished.set()
            timer.cancel()
            self.server.generation_lock.release()
