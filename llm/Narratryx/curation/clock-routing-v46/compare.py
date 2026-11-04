"""Compare both adapters on frozen timeline cases."""
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
TRAINING = ROOT / 'artifacts/source-training-v45'
REFERENCE = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/clock-routing-v46/fresh'
PREVIOUS = ROOT / 'curation/source-training-v26'
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl


def main():
    assert __debug__
    if len(sys.argv) == 3 and sys.argv[1] == '--evaluate':
        evaluate = runpy.run_path(str(PREVIOUS / 'evaluate.py'))['main']
        evaluate.__globals__['RUN'] = RUN
        sys.argv[1:] = [sys.argv[2]]
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
    source = REFERENCE / 'fresh-clock-cases.jsonl'
    lock = json.loads((REFERENCE / 'fresh-clock-cases.lock.json').read_text())
    assert file_hash(source) == lock['sha256']
    cases = read_jsonl(source)
    assert len(cases) == lock['cases'] == 6
    assert all(c['training_eligible'] is False for c in cases)
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
    sys.path.insert(0, str(PREVIOUS))
    from scoring import strict_json_match
    scores = {}
    for side in ('current-craft', 'candidate'):
        helpers['phase'](side, [str(Path(__file__)), '--evaluate', side], 1200)
        path = RUN / f'{side}.responses.jsonl'
        rows = read_jsonl(path)
        assert [r['case_id'] for r in rows] == [c['id'] for c in cases]
        scores[side] = {}
        for row, case in zip(rows, cases):
            assert row['finish_reason'] == 'stop' and not row['error']
            assert row['prior_assistant_messages'] == 0
            scores[side][case['id']] = strict_json_match(row['text'], case['expected_json'])
    old, new = scores['current-craft'], scores['candidate']
    result = dict(scores=scores, totals={side: sum(rows.values()) for side, rows in scores.items()},
                  corrected=[k for k in old if not old[k] and new[k]],
                  regressed=[k for k in old if old[k] and not new[k]], training_eligible=False)
    helpers['save']('comparison.json', result)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
