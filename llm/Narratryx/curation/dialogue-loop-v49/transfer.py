"""Run a local decoding probe on the two recorded v48 failures."""
import json
import os
from pathlib import Path
import runpy
import sys
import threading

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
from foundation.validation import file_hash, read_jsonl

OUT = ROOT / 'artifacts/dialogue-loop-v49'
TRAIN = ROOT / 'artifacts/source-training-v48'
TARGETS = [('stylistic-screen-v48', 'v48-dialogue-subtext'),
           ('stylistic-screen-v48', 'v48-dialogue-boundary')]


def run():
    from runtime.local.engine import MLXEngine
    from analyse import analyse

    p = json.loads((TRAIN / 'protocol.frozen.json').read_text())
    adapter = TRAIN / 'adapter'
    config = json.loads((ROOT / 'configs/narratryx-craft-v1.json').read_text())
    config.update(adapter_sha256=file_hash(adapter / 'adapters.safetensors'),
                  adapter_config_sha256=file_hash(adapter / 'adapter_config.json'))
    engine = MLXEngine(config, Path(p['base_path']), adapter)
    original = engine.backend.generate_with_adapter_control
    penalty = 1.0

    def decode(**kwargs):
        kwargs['repetition_penalty'] = penalty
        return original(**kwargs)

    engine.backend.generate_with_adapter_control = decode
    try:
        with (OUT / 'transfer.jsonl').open('x') as stream:
            for run_name, case_id in TARGETS:
                cases = read_jsonl(ROOT / 'artifacts' / run_name / 'cases.frozen.jsonl')
                case, = [c for c in cases if c['id'] == case_id]
                for penalty in (1.0, 1.12):
                    cancel = threading.Event()
                    timer = threading.Timer(90, cancel.set)
                    timer.start()
                    try:
                        result = engine.generate([dict(role='user', content=case['prompt'])],
                                                 config['model_id'], 384, 0, cancel)
                    finally:
                        timer.cancel()
                    assert result['usage']['prompt_tokens_details']['cached_tokens'] == 0
                    result.update(case=case_id, penalty=penalty, training_eligible=False,
                                  **analyse(result['text']))
                    stream.write(json.dumps(result, ensure_ascii=False) + '\n')
                    stream.flush()
    finally:
        engine.close()


if __name__ == '__main__':
    if sys.argv[1:] == ['--probe']:
        run()
    else:
        lock = ROOT / 'curation/source-training-v48/results.lock.json'
        for name, expected in json.loads(lock.read_text()).items():
            assert file_hash(ROOT / name) == expected, name
        previous = runpy.run_path(str(ROOT / 'curation/source-training-v26/run.py'))
        previous['verify_inputs'](json.loads((TRAIN / 'protocol.frozen.json').read_text()))
        helper = runpy.run_path(str(previous['HELPERS']))
        helper['phase'].__globals__.update(RUN=OUT, PYTHON=Path(sys.executable))
        assert helper['port_free']()
        helper['phase']('transfer-probe', [str(Path(__file__)), '--probe'], 600)
