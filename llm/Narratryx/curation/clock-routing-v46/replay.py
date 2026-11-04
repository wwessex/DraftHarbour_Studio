"""Replay explicit clock-state routing on the frozen v45 comparison."""
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'curation/source-training-v26')]
from foundation.validation import file_hash, read_jsonl

RUN = ROOT / 'artifacts/source-training-v45'


def main():
    lock = ROOT / 'curation/source-training-v45/results.lock.json'
    for name, digest in json.loads(lock.read_text()).items():
        assert file_hash(ROOT / name) == digest, name
    plan = json.loads((RUN / 'protocol.frozen.json').read_text())
    cases = read_jsonl(RUN / 'cases.frozen.jsonl')
    score = runpy.run_path(str(ROOT / 'curation/source-training-v26/report.py'))['score_case']
    responses = {}
    for side in ('current-craft', 'candidate'):
        path = RUN / f'{side}.responses.jsonl'
        if side == 'current-craft':
            assert file_hash(path) == plan['input_hashes'][str(path.relative_to(ROOT))]
        rows = read_jsonl(path)
        assert [r['case_id'] for r in rows] == [c['id'] for c in cases]
        assert all(not r['error'] and r['finish_reason'] == 'stop' for r in rows)
        responses[side] = dict(zip((c['id'] for c in cases), rows))
    # Only explicit structured clock checks are eligible. Prose always uses craft.
    selected = [c for c in cases if c['kind'] == 'clock-state' and 'expected_json' in c]
    comparisons = []
    for c in selected:
        result = {side: score(side, c, rows[c['id']])['structured_exact']
                  for side, rows in responses.items()}
        comparisons.append(dict(case_id=c['id'], **result))
    assert comparisons
    report = dict(total_cases=len(cases), routed_cases=len(selected),
                  craft_exact=sum(r['current-craft'] for r in comparisons),
                  routed_exact=sum(r['candidate'] for r in comparisons),
                  corrected=sum(not r['current-craft'] and r['candidate'] for r in comparisons),
                  regressed=sum(r['current-craft'] and not r['candidate'] for r in comparisons),
                  cases=comparisons, evaluation='post-hoc exposed replay',
                  training_eligible=False)
    output = ROOT / 'artifacts/clock-routing-v46'
    output.mkdir()
    with (output / 'replay.json').open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
