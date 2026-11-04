"""Verify response identity and score the frozen mechanical constraints."""
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl

RUN = ROOT / 'artifacts/base-comparison-v42'
LIMITS = {
    'continue': dict(min_words=80, max_words=120, paragraphs=1),
    'write': dict(min_words=90, max_words=125),
    'rewrite': dict(changed=True),
    'dialogue': dict(max_words=115, min_turns=4, max_turns=6),
    'pacing': dict(max_words=130, paragraphs=2),
    'analysis': dict(max_words=100, exact_quotes=2),
}


def main():
    marker = json.loads((RUN / 'complete.json').read_text())
    assert marker['responses'] == 18
    cases = read_jsonl(RUN / 'cases.frozen.jsonl')
    assert len(cases) == 6
    check = runpy.run_path(str(ROOT / 'curation/holdout-v36/constraints.py'))['checks']
    result = {}
    pins = {}
    for side in marker['conditions']:
        path = RUN / f'{side}.responses.jsonl'
        rows = read_jsonl(path)
        assert [r['case_id'] for r in rows] == [c['id'] for c in cases]
        pins[str(path.relative_to(ROOT))] = file_hash(path)
        details = []
        for case, row in zip(cases, rows):
            assert row['finish_reason'] == 'stop' and not row.get('error')
            assert row['prompt_sha256'] == hashlib.sha256(case['prompt'].encode()).hexdigest()
            flags = check(dict(case, constraints=LIMITS[case['kind']]), row['text'])
            details.append(dict(case_id=case['id'], words=len(row['text'].split()),
                                passed=all(flags.values()), checks=flags))
        result[side] = dict(passed=sum(d['passed'] for d in details), total=len(details), details=details)
    with (RUN / 'mechanical-scores.json').open('x') as stream:
        json.dump(dict(results=result, response_hashes=pins, training_eligible=False), stream, indent=2)
        stream.write('\n')
    print({side: (r['passed'], r['total']) for side, r in result.items()})


if __name__ == '__main__':
    main()
