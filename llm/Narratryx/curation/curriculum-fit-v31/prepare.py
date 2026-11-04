"""Select a bounded craft-commentary reserve with exact source provenance."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.mixed_curriculum import require_distinct_source_spans
from foundation.validation import file_hash, load_ledger, read_jsonl, validate_dataset

OUT = ROOT / 'artifacts/curriculum-fit-v31'
SOURCE = ROOT / 'artifacts/craft-expansion-v1/train.records.jsonl'
SCOPE = SOURCE.parent / 'scope.json'
BASE = ROOT / 'artifacts/curriculum-fit-v24/records.review-only.jsonl'
LEDGER = ROOT / 'rights/curriculum-fit-v24.scoped.jsonl'
SELECTED = {
    'wharton-writing-craft-017': 'viewpoint and perception',
    'wharton-writing-craft-025': 'dialogue placement and narrative time',
    'wharton-writing-craft-027': 'scene selection and scale',
    'hamilton-manual-craft-026': 'character, action and setting',
    'hamilton-manual-craft-055': 'illustrated limits of viewpoint',
    'hamilton-manual-craft-064': 'attention and ironic emphasis',
}


def main():
    assert not OUT.exists()
    candidates = read_jsonl(SOURCE)
    assert len(candidates) == 20
    reserve = [r for r in candidates if r['id'] in SELECTED]
    assert set(SELECTED) == {r['id'] for r in reserve}
    ledger = load_ledger(LEDGER)
    scope = json.loads(SCOPE.read_text())
    for row in reserve:
        assert row['task'] == 'analysis' and row['split'] == 'train' and row['teacher'] is None
        for span in row['source_spans']:
            rid = span['rights_record_id']
            assert file_hash(SCOPE) in ledger[rid]['source']['included_material']
            assert any(s['id'] == row['id'] and s['source_id'] == rid and
                       (s['start'], s['end']) == (span['start'], span['end'])
                       and s['use'] == 'training' for s in scope)
    rows = [dict(r, dataset_version='curriculum-fit-v31-review') for r in read_jsonl(BASE) + reserve]
    require_distinct_source_spans(rows, ledger)
    OUT.mkdir()
    dataset = OUT / 'records.review-only.jsonl'
    with dataset.open('x') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    checked = validate_dataset(dataset, LEDGER, ['GB', 'US'],
                               benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    assert len(checked) == 56 and sum(r['split'] == 'train' for r in checked) == 40
    with (OUT / 'review.json').open('x') as stream:
        json.dump(dict(selected=SELECTED, reviewed=20, reserved=14,
                       direct_passage_analysis_added=0, training_records=40, exposed_monitors=16,
                       training_started=False, hashes={str(p.relative_to(ROOT)): file_hash(p)
                                                       for p in (SOURCE, SCOPE, BASE, LEDGER, dataset)}),
                  stream, indent=2)
        stream.write('\n')
    print('Validated six craft-commentary lessons in a 40-example review proposal.')


if __name__ == '__main__':
    main()
