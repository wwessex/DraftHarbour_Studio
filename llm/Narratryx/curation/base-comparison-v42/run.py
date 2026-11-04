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
RUN = ROOT / 'artifacts/base-comparison-v42'
PREVIOUS = ROOT / 'curation/source-training-v26'
PORT = 11485
MODEL = 'gemma4:e4b'
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl


def gemma():
    protocol = json.loads((RUN / 'protocol.frozen.json').read_text())
    assert file_hash(Path(protocol['ollama_executable'])) == protocol['ollama_sha256']
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


def main():
    assert __debug__
    if sys.argv[1:] == ['--gemma']:
        gemma()
        return
    if len(sys.argv) == 3 and sys.argv[1] == '--mlx':
        evaluate = runpy.run_path(str(PREVIOUS / 'evaluate.py'))['main']
        evaluate.__globals__['RUN'] = RUN
        sys.argv[1:] = [sys.argv[2]]
        evaluate()
        return
    assert not RUN.exists()
    previous = runpy.run_path(str(PREVIOUS / 'run.py'))
    protocol = previous['load_plan']()
    previous['verify_inputs'](protocol)
    model_dir = Path.home() / '.ollama/models'
    manifest = model_dir / 'manifests/registry.ollama.ai/library/gemma4/e4b'
    index = json.loads(manifest.read_text())
    pins = {str(manifest): file_hash(manifest)}
    for entry in [index['config'], *index['layers']]:
        path = model_dir / 'blobs' / entry['digest'].replace(':', '-')
        assert path.stat().st_size == entry['size']
        assert file_hash(path) == entry['digest'].split(':')[1]
        pins[str(path)] = entry['digest'].split(':')[1]
    executable = shutil.which('ollama')
    assert executable
    helpers = runpy.run_path(str(previous['HELPERS']))
    helpers['phase'].__globals__.update(RUN=RUN, PYTHON=Path(sys.executable))
    assert helpers['port_free']()
    cases = read_jsonl(HERE / 'cases.jsonl')
    earlier = read_jsonl(ROOT / 'artifacts/base-comparison-v41/cases.frozen.jsonl')
    assert all(c['training_eligible'] is False for c in cases)
    assert not {c['prompt'] for c in cases} & {c['prompt'] for c in earlier}
    assert len(cases) == len({c['id'] for c in cases}) == 6
    RUN.mkdir()
    path = RUN / 'cases.frozen.jsonl'
    with path.open('x') as stream:
        for case in cases:
            stream.write(json.dumps(case, ensure_ascii=False) + '\n')
    protocol.update(status='base-model-diagnostic', test_cases_path=str(path.relative_to(ROOT)),
                    context_limit=2048, gemma_model=MODEL, gemma_pins=pins,
                    ollama_executable=executable, ollama_sha256=file_hash(Path(executable)),
                    training_eligible=False)
    protocol['input_hashes'].update({str(p.relative_to(ROOT)): file_hash(p) for p in
                                    (HERE / 'cases.jsonl', Path(__file__), path,
                                     PREVIOUS / 'evaluate.py', ROOT / 'runtime/local/engine.py')})
    helpers['save']('protocol.frozen.json', protocol)
    for side in ('base', 'current-craft'):
        helpers['phase'](side, [str(Path(__file__)), '--mlx', side], 1200)
    helpers['phase']('gemma', [str(Path(__file__)), '--gemma'], 1200)
    for side in ('base', 'current-craft', 'gemma'):
        rows = read_jsonl(RUN / f'{side}.responses.jsonl')
        assert [r['case_id'] for r in rows] == [c['id'] for c in cases]
        assert all(r['finish_reason'] == 'stop' and not r.get('error') for r in rows)
    helpers['save']('complete.json', dict(responses=18, conditions=['base', 'current-craft', 'gemma'],
                                        training_eligible=False))


if __name__ == '__main__':
    main()
