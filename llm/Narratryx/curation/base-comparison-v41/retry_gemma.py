"""Compare local model configurations on matched story-state prompts."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shutil
import socket
import subprocess
import sys
import time
from urllib.error import URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/base-comparison-v41-gemma-retry'
PREVIOUS = ROOT / 'curation/source-training-v26'
PORT = 11485
MODEL = 'gemma4:e4b'
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl


def gemma():
    protocol = json.loads((RUN / 'protocol.frozen.json').read_text())
    for name, digest in protocol['gemma_pins'].items():
        assert file_hash(Path(name)) == digest, name
    with socket.socket() as check:
        check.bind(('127.0.0.1', PORT))
    env = dict(os.environ, OLLAMA_HOST=f'127.0.0.1:{PORT}', OLLAMA_NO_CLOUD='1',
               OLLAMA_NUM_PARALLEL='1', OLLAMA_MAX_LOADED_MODELS='1')
    url = f'http://127.0.0.1:{PORT}'
    with (RUN / 'ollama-server.log').open('x') as log:
        server = subprocess.Popen([protocol['ollama_executable'], 'serve'],
                                  env=env, stdout=log, stderr=subprocess.STDOUT)
        try:
            for _ in range(60):
                assert server.poll() is None
                try:
                    with urlopen(url + '/api/tags', timeout=2) as response:
                        tags = json.load(response)
                    break
                except (URLError, TimeoutError):
                    time.sleep(0.5)
            else:
                raise RuntimeError('Private Ollama server failed readiness')
            assert any(r['name'] == MODEL for r in tags['models'])
            with (RUN / 'gemma.responses.jsonl').open('x') as stream:
                for case in read_jsonl(RUN / 'cases.frozen.jsonl'):
                    payload = dict(model=MODEL, messages=[dict(role='user', content=case['prompt'])],
                                   stream=False, think=False, keep_alive='2m',
                                   options=dict(seed=42, temperature=0, num_ctx=2048, num_predict=384))
                    request = Request(url + '/api/chat', data=json.dumps(payload).encode(),
                                      headers={'Content-Type': 'application/json'})
                    start = time.monotonic()
                    with urlopen(request, timeout=180) as response:
                        result = json.load(response)
                    row = dict(case_id=case['id'], condition='gemma', text=result['message']['content'],
                               finish_reason=result.get('done_reason'), elapsed_seconds=time.monotonic() - start,
                               prompt_sha256=hashlib.sha256(case['prompt'].encode()).hexdigest(),
                               prompt_tokens=result.get('prompt_eval_count'), completion_tokens=result.get('eval_count'))
                    stream.write(json.dumps(row, ensure_ascii=False) + '\n')
                    stream.flush()
                    assert result.get('done') and row['finish_reason'] == 'stop' and row['text'].strip()
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()


if __name__ == '__main__':
    assert __debug__
    previous = ROOT / 'artifacts/base-comparison-v41'
    protocol = json.loads((previous / 'protocol.frozen.json').read_text())
    for name, digest in protocol['input_hashes'].items():
        assert file_hash(ROOT / name) == digest, name
    assert file_hash(Path(protocol['ollama_executable'])) == protocol['ollama_sha256']
    helpers = runpy.run_path(str(ROOT / 'curation/stability-v10/run.py'))
    helpers['phase'].__globals__.update(RUN=RUN, PYTHON=Path(sys.executable))
    if sys.argv[1:] == ['--generate']:
        gemma()
    else:
        assert not RUN.exists()
        RUN.mkdir()
        for name in ('protocol.frozen.json', 'cases.frozen.jsonl'):
            shutil.copyfile(previous / name, RUN / name)
        helpers['phase']('gemma', [str(Path(__file__)), '--generate'], 1200)
