"""Serial offline experiment with bounded subprocesses and development-service restore."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import urllib.request

import psutil

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, validate_dataset

HERE = Path(__file__).resolve().parent
DATA = ROOT / 'artifacts/revision-preflight-v1'
RUN = ROOT / 'artifacts/revision-training-v4'
PYTHON = Path('/Users/williamwessex/.unsloth/studio/unsloth_studio/bin/python')


def save(name, value, private=False):
    path = RUN / name
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600 if private else 0o644)
    with os.fdopen(fd, 'w') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def verify(protocol):
    for group in ['input_hashes', 'protected_artifacts']:
        for relative, expected in protocol[group].items():
            if file_hash(ROOT / relative) != expected:
                raise RuntimeError('Pinned artifact mismatch: ' + relative)
    if file_hash(Path(protocol['base_path']) / 'model.safetensors') != protocol['base_weights_sha256']:
        raise RuntimeError('Base weight mismatch')
    validate_dataset(DATA / 'records.jsonl', ROOT / 'rights/revision-preflight-v1.scoped.jsonl', ['GB', 'US'])


def stop_tree(process):
    try:
        root = psutil.Process(process.pid)
        children = root.children(recursive=True)
    except psutil.NoSuchProcess:
        return
    for child in reversed(children):
        try:
            child.terminate()
        except psutil.NoSuchProcess:
            pass
    process.terminate()
    _, alive = psutil.wait_procs(children + [root], timeout=10)
    for item in alive:
        try:
            item.kill()
        except psutil.NoSuchProcess:
            pass


def phase(name, command, seconds):
    print('Starting ' + name, flush=True)
    started = time.monotonic()
    with (RUN / (name + '.log')).open('x') as log:
        process = subprocess.Popen([str(PYTHON), *command], cwd=ROOT, stdout=log,
                                   stderr=subprocess.STDOUT, env={**os.environ,
                                   'HF_HUB_OFFLINE': '1', 'TRANSFORMERS_OFFLINE': '1',
                                   'UNSLOTH_MLX_PROMPT_CACHE_BYTES': '0'}, start_new_session=True)
        try:
            while process.poll() is None:
                if time.monotonic() - started > seconds:
                    raise RuntimeError(name + ' exceeded deadline')
                try:
                    members = [psutil.Process(process.pid)]
                    members += members[0].children(recursive=True)
                    rss = sum(p.memory_info().rss for p in members if p.is_running())
                    if rss > 10_000_000_000:
                        raise RuntimeError(name + ' resident process memory exceeded10GB')
                except psutil.NoSuchProcess:
                    pass
                time.sleep(1)
            if process.returncode:
                raise RuntimeError(name + ' exited with code ' + str(process.returncode))
        except BaseException:
            stop_tree(process)
            raise
    save(name + '.phase.json', dict(completed=True, elapsed_seconds=time.monotonic()-started))
    print('Completed ' + name, flush=True)


def main():
    if RUN.exists():
        raise RuntimeError('Refusing to overwrite an experiment')
    RUN.mkdir()
    proposed = DATA / 'protocol.proposed.frozen.json'
    protocol = json.loads(proposed.read_text())
    verify(protocol)
    protocol.update(status='execution_authorised', user_authorization='User proceeded with fresh baselines and the bounded eight-update trial; local only, no app defaults or promotion.',
                    training_steps=8, context_limit=2048,
                    test_cases_path=str((DATA / 'test.cases.jsonl').relative_to(ROOT)),
                    model_conditions=['base', 'current-craft', 'candidate'])
    protocol['input_hashes'][str(proposed.relative_to(ROOT))] = file_hash(proposed)
    for name in ['run.py', 'evaluate.py', 'train.py', 'guards.py']:
        protocol['input_hashes'][str((HERE / name).relative_to(ROOT))] = file_hash(HERE / name)
    for name in ['adapters.safetensors', 'adapter_config.json']:
        relative = 'artifacts/task-matched-training-v3/adapter/' + name
        protocol['protected_artifacts'][relative] = file_hash(ROOT / relative)
    save('request.json', json.loads((DATA / 'request.proposed.json').read_text()))
    protocol['input_hashes'][str((RUN / 'request.json').relative_to(ROOT))] = file_hash(RUN / 'request.json')
    save('protocol.frozen.json', protocol)
    service = psutil.Process(8479)
    command, cwd, environment = service.cmdline(), service.cwd(), service.environ()
    if 'runtime.local' not in ' '.join(command):
        raise RuntimeError('Unexpected service identity; refusing interruption')
    save('service-state.private.json', dict(pid=service.pid, create_time=service.create_time(), command=command, cwd=cwd), private=True)
    paused = False
    error = None
    try:
        service.terminate()
        paused = True
        service.wait(timeout=30)
        save('service-paused.json', dict(paused=True, model_pin_sha256=file_hash(ROOT / 'configs/narratryx-craft-v1.json')))
        for side in ['base', 'current-craft']:
            phase(side, [str(HERE / 'evaluate.py'), side], 3600)
        phase('training', [str(HERE / 'train.py')], 1200)
        phase('candidate', [str(HERE / 'evaluate.py'), 'candidate'], 3600)
        verify(protocol)
        save('experiment-complete.json', dict(completed=True, conditions=3, responses=72,
                                              training_steps=8, model_promoted=False))
    except BaseException as exc:
        error = repr(exc)
        save('experiment-failed.json', dict(error=error, automatic_retry=False))
        raise
    finally:
        if paused:
            log = (RUN / 'service-restored.log').open('x')
            restored = subprocess.Popen(command, cwd=cwd, env=environment, stdout=log,
                                        stderr=subprocess.STDOUT, start_new_session=True)
            ready = False
            deadline = time.monotonic() + 120
            while time.monotonic() < deadline and restored.poll() is None:
                try:
                    # Readiness check only; never print private access tokens.
                    with urllib.request.urlopen('http://127.0.0.1:8890/health', timeout=2) as response:
                        ready = response.status == 200
                    if ready:
                        break
                except Exception:
                    time.sleep(1)
            save('service-restored.json', dict(pid=restored.pid, http_ready=ready,
                                              selected_model_unchanged=file_hash(ROOT / 'configs/narratryx-craft-v1.json') == protocol['input_hashes']['configs/narratryx-craft-v1.json'], experiment_error=error))
            print('Development service restored; HTTP ready=' + str(ready), flush=True)
            if not ready:
                raise RuntimeError('Development service did not regain readiness')


if __name__ == '__main__':
    main()
