"""Generate a bounded sample of alternatives for originality evaluation."""
import json
import os
from pathlib import Path
import runpy
import sys
import threading

os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                  UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl

HERE = Path(__file__).resolve().parent
OUT = ROOT / 'artifacts/originality-v35-varied-seeds'
PREVIOUS = ROOT / 'curation/source-training-v26'
SCREEN = ROOT / 'curation/curriculum-reset-v30/fresh-screen.jsonl'
SELECTED = ('v30-02-kiln', 'v30-03-bus', 'v30-07-bakery')


def generate():
    from runtime.local.engine import MLXEngine

    protocol = json.loads((OUT / 'protocol.json').read_text())
    for path, digest in protocol['hashes'].items():
        assert file_hash(ROOT / path) == digest, path
    adapter = ROOT / 'artifacts/craft-training-v2/adapter'
    config = json.loads((ROOT / 'configs/narratryx-craft-v1.json').read_text())
    config.update(context_limit=2048, adapter_sha256=file_hash(adapter / 'adapters.safetensors'),
                  adapter_config_sha256=file_hash(adapter / 'adapter_config.json'))
    engine = MLXEngine(config, Path(protocol['base_path']), adapter)
    original = engine.backend.generate_with_adapter_control
    seed = 42

    def with_seed(**kwargs):
        kwargs['seed'] = seed
        return original(**kwargs)

    # Override the seed only on this private evaluation backend.
    engine.backend.generate_with_adapter_control = with_seed
    try:
        with (OUT / 'alternatives.jsonl').open('x') as stream:
            for case in read_jsonl(SCREEN):
                if case['id'] not in SELECTED:
                    continue
                for attempt in range(1, 4):
                    seed = 41 + attempt
                    cancel = threading.Event()
                    timer = threading.Timer(120, cancel.set)
                    timer.daemon = True
                    timer.start()
                    try:
                        result = engine.generate([dict(role='user', content=case['prompt'])],
                                                 config['model_id'], 384, 0.7, cancel)
                    finally:
                        timer.cancel()
                    result.update(case_id=case['id'], attempt=attempt, seed=seed)
                    stream.write(json.dumps(result, ensure_ascii=False) + '\n')
                    stream.flush()
                    assert result['finish_reason'] == 'stop'
                    assert result['usage']['prompt_tokens_details']['cached_tokens'] == 0
    finally:
        engine.close()


def main():
    assert __debug__
    if sys.argv[1:] == ['--generate']:
        generate()
        return
    assert not OUT.exists()
    previous = runpy.run_path(str(PREVIOUS / 'run.py'))
    plan = previous['load_plan']()
    previous['verify_inputs'](plan)
    frozen = json.loads(SCREEN.with_suffix('.lock.json').read_text())
    assert file_hash(SCREEN) == frozen['sha256']
    assert {c['id'] for c in read_jsonl(SCREEN) if c['id'] in SELECTED and
            c['training_eligible'] is False} == set(SELECTED)
    helpers = runpy.run_path(str(previous['HELPERS']))
    helpers['phase'].__globals__.update(RUN=OUT, PYTHON=Path(sys.executable))
    assert helpers['port_free']()
    OUT.mkdir()
    paths = (SCREEN, Path(__file__), ROOT / 'configs/narratryx-craft-v1.json',
             ROOT / 'artifacts/craft-training-v2/adapter/adapters.safetensors',
             ROOT / 'artifacts/craft-training-v2/adapter/adapter_config.json')
    helpers['save']('protocol.json', dict(base_path=plan['base_path'], selected=SELECTED,
                                        temperature=0.7, seeds=[42, 43, 44], alternatives_per_case=3,
                                        training_eligible=False,
                                        hashes={str(p.relative_to(ROOT)): file_hash(p) for p in paths}))
    helpers['phase']('originality', [str(Path(__file__)), '--generate'], 1200)


if __name__ == '__main__':
    main()
