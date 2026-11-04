"""Select unused practical scenes from already scoped source intervals."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.mixed_curriculum import require_distinct_source_spans
from foundation.validation import digest, file_hash, load_ledger, read_jsonl, validate_dataset

BASE = ROOT / 'artifacts/watsons-v33'
OUT = ROOT / 'artifacts/practical-scenes-v34'
LEDGER = ROOT / 'rights/watsons-v33.scoped.jsonl'
SCOPE = ROOT / 'artifacts/literary-mix-v2/new-source-spans.json'
LESSONS = [
    ('v34-model-demonstration', 'wells-time-machine-pg35', 13723, 14553, 'pacing',
     'Write one paragraph of 125–165 words in first-person plural or singular eyewitness narration. In a historical speculative scene, pause before a demonstration of a model time machine. The Time Traveller asks the Psychologist for his hand and has him turn the lever. Accelerate through the wind, changes in light and the model vanishing, then end on the bare table and lamp. The narrator may express certainty about what they witnessed. Return only prose.'),
    ('v34-laboratory-inspection', 'wells-time-machine-pg35', 17429, 18192, 'fiction',
     'Write one paragraph of 110–150 words in period first-person fiction. The Time Traveller invites the party to see the larger machine and leads them down the corridor with a lamp. Show their arrival and the narrator actually picking up one unfinished bar for a closer look. Let the material seem to be quartz without establishing it as fact. Return only prose.'),
    ('v34-index-lookup', 'doyle-adventures-pg48320', 18302, 18750, 'storytelling',
     'Write one paragraph of 65–95 words from Watson’s viewpoint. Holmes asks Watson to look a woman up in his existing index. Briefly explain how the filing system makes the search possible, and show Watson finding the entry. End with its position among unrelated subjects. Return only period story prose.'),
]


def main():
    assert not OUT.exists()
    source_manifest = json.loads((BASE / 'review.json').read_text())
    for name, expected in source_manifest['hashes'].items():
        assert file_hash(ROOT / name) == expected, name
    ledger = load_ledger(LEDGER)
    scope = json.loads(SCOPE.read_text())
    old = read_jsonl(BASE / 'records.review-only.jsonl')
    records = []
    for record_id, rid, start, end, task, prompt in LESSONS:
        item = ledger[rid]
        assert file_hash(SCOPE) in item['source']['included_material']
        match, = [s for s in scope if (s['source_id'], s['start'], s['end']) == (rid, start, end)]
        raw = ROOT / 'rights' / item['source']['raw_path']
        assert file_hash(raw) == item['source']['sha256']
        answer = raw.read_text()[start:end]
        assert answer == match['raw_text'] and '\n\n' not in answer
        words = len(answer.split())
        limits = {'pacing': (125, 165), 'fiction': (110, 150), 'storytelling': (65, 95)}
        lower, upper = limits[task]
        assert lower <= words <= upper, (record_id, words)
        messages = [dict(role='user', content=prompt), dict(role='assistant', content=answer)]
        records.append(dict(
            schema_version='1.0', id=record_id, dataset_version='practical-scenes-v34-review',
            task=task, split='train', split_group=item['work_id'], origin='derived', messages=messages,
            source_work_ids=[item['work_id']], rights_record_ids=[rid],
            source_spans=[dict(rights_record_id=rid, start=start, end=end, text=answer)],
            teacher=None, review=dict(status='approved', reviewer='Codex AI: scoped curriculum assessment',
                                      reviewed_on='2026-11-03',
                                      notes='Unchanged original published text within the existing scope. Review proposal.'),
            rubric=['completed observable action', 'source fidelity', 'instruction alignment'],
            content_hash=digest(messages)))
    rows = [dict(r, dataset_version='practical-scenes-v34-review') for r in old] + records
    require_distinct_source_spans(rows, ledger)
    OUT.mkdir()
    path = OUT / 'records.review-only.jsonl'
    with path.open('x') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    checked = validate_dataset(path, LEDGER, ['GB', 'US'],
                               benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    assert len(checked) == 61 and sum(r['split'] == 'train' for r in checked) == 45
    with (OUT / 'review.json').open('x') as stream:
        json.dump(dict(training_started=False, training_records=45, exposed_monitors=16,
                       added=[r['id'] for r in records],
                       hashes={str(p.relative_to(ROOT)): file_hash(p) for p in
                               (Path(__file__), path, LEDGER, SCOPE, BASE / 'records.review-only.jsonl')}),
                  stream, indent=2)
        stream.write('\n')
    print('Validated 45 examples and 16 monitors with three new practical-scene targets.')


if __name__ == '__main__':
    main()
