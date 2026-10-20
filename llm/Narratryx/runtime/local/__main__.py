"""Launch the optional local serving environment; never launches training."""
from pathlib import Path
import argparse
import json
import signal

from .server import InferenceServer, access_token

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description='Serve the pinned experimental Narratryx adapter separately from DraftHarbour')
    parser.add_argument('--manifest', type=Path, default=ROOT / 'configs/narratryx-craft-v1.json')
    parser.add_argument('--base-snapshot', type=Path)
    parser.add_argument('--adapter', type=Path)
    parser.add_argument('--token-file', type=Path, default=ROOT / 'artifacts/local-serving/access-token')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8890)
    parser.add_argument('--allow-origin', action='append', default=[])
    args = parser.parse_args()
    pin = json.loads(args.manifest.read_text())
    base = args.base_snapshot or Path.home() / '.cache/huggingface/hub' / ('models--' + pin['base_repo'].replace('/', '--')) / 'snapshots' / pin['base_revision']
    adapter = args.adapter or ROOT / pin['adapter_path']
    token = access_token(args.token_file)
    from .engine import MLXEngine
    engine = MLXEngine(pin, base, adapter)
    try:
        server = InferenceServer((args.host, args.port), engine, pin, token, args.allow_origin)
        print(f'Narratryx experimental API: http://{args.host}:{args.port}', flush=True)
        print(f'Model: {pin["model_id"]}; adapter SHA-256: {pin["adapter_sha256"]}', flush=True)
        print(f'Private access token file: {args.token_file.resolve()}', flush=True)
        def stop(*_):
            raise KeyboardInterrupt()
        signal.signal(signal.SIGTERM, stop)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
    finally:
        engine.close()


if __name__ == '__main__':
    main()
