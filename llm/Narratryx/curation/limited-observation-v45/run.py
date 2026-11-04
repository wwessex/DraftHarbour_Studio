"""Evaluate the new adapter on the six prior prose-format development cases."""
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TRAINING = ROOT / 'artifacts/source-training-v45'
REFERENCE = ROOT / 'artifacts/scene-brief-v43'
RUN = ROOT / 'artifacts/limited-observation-v45'
PREVIOUS = ROOT / 'curation/source-training-v26'
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl


def main():
    assert __debug__
    if sys.argv[1:] == ['--evaluate']:
        evaluate = runpy.run_path(str(PREVIOUS / 'evaluate.py'))['main']
        evaluate.__globals__['RUN'] = RUN
        sys.argv[1:] = ['candidate']
        evaluate()
        return
    assert not RUN.exists()
    assert json.loads((TRAINING / 'experiment-complete.json').read_text())['training_steps'] == 55
    previous = runpy.run_path(str(PREVIOUS / 'run.py'))
    plan = json.loads((TRAINING / 'protocol.frozen.json').read_text())
    previous['verify_inputs'](plan)
    completion = json.loads((TRAINING / 'completion.json').read_text())
    weights = TRAINING / 'adapter/adapters.safetensors'
    assert file_hash(weights) == completion['adapter_sha256']
    source = REFERENCE / 'current-craft.responses.jsonl'
    assert file_hash(source) == json.loads((REFERENCE / 'baseline.json').read_text())['response_sha256']
    cases = [c for c in read_jsonl(REFERENCE / 'cases.frozen.jsonl') if c['id'].endswith('-prose')]
    refs = [r for r in read_jsonl(source) if r['case_id'].endswith('-prose')]
    assert len(cases) == len(refs) == 6 and all(c['training_eligible'] is False for c in cases)
    helpers = runpy.run_path(str(previous['HELPERS']))
    helpers['phase'].__globals__.update(RUN=RUN, PYTHON=Path(sys.executable))
    assert helpers['port_free']()
    RUN.mkdir()
    (RUN / 'adapter').symlink_to(TRAINING / 'adapter', target_is_directory=True)
    for name in ('completion.json',):
        (RUN / name).symlink_to(TRAINING / name)
    case_path = RUN / 'cases.frozen.jsonl'
    with case_path.open('x') as stream:
        for case in cases:
            stream.write(json.dumps(case, ensure_ascii=False) + '\n')
    plan.update(test_cases_path=str(case_path.relative_to(ROOT)), status='limited-observation-diagnostic')
    paths = (Path(__file__), case_path, source, weights, TRAINING / 'adapter/adapter_config.json')
    plan['input_hashes'].update({str(p.relative_to(ROOT)): file_hash(p) for p in paths})
    helpers['save']('protocol.frozen.json', plan)
    helpers['phase']('candidate', [str(Path(__file__)), '--evaluate'], 1200)
    path = RUN / 'candidate.responses.jsonl'
    rows = read_jsonl(path)
    assert [r['case_id'] for r in rows] == [c['id'] for c in cases] == [r['case_id'] for r in refs]
    for candidate, craft in zip(rows, refs):
        assert candidate['prompt_sha256'] == craft['prompt_sha256']
        assert candidate['finish_reason'] == 'stop' and not candidate['error']
    helpers['save']('comparison.json', dict(new_responses=6, reused_craft_responses=6,
                                           candidate_sha256=file_hash(path),
                                           craft_sha256=file_hash(source), training_eligible=False))


if __name__ == '__main__':
    main()
