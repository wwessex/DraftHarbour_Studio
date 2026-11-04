"""Read-only exact-source, selected-family, rights and split verification."""
import json
import re
import runpy
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl, load_ledger, validate_dataset
from foundation.mixed_curriculum import require_distinct_source_spans
OUT = ROOT / 'artifacts/curriculum-fit-v24'
LEDGER = ROOT / 'rights/curriculum-fit-v24.scoped.jsonl'


def verify():
    proof = json.loads((OUT / 'preparation.lock.json').read_text())
    for group in ['protected_hashes', 'input_hashes']:
        for name, expected in proof[group].items():
            assert file_hash(ROOT / name) == expected, name
    for name, expected in proof['output_hashes'].items():
        assert file_hash(OUT / name) == expected, name
    assert runpy.run_path(str(ROOT / 'curation/source-expansion-v23/verify.py'))['verify']()['passed']
    ledger = load_ledger(LEDGER)
    old = load_ledger(ROOT / 'rights/source-expansion-v23.scoped.jsonl')
    assert len(ledger) == 19 and all(ledger[k] == v for k, v in old.items())
    rows = read_jsonl(OUT / 'candidates.jsonl')
    assert len(rows) == 6
    validate_dataset(OUT / 'candidates.jsonl', LEDGER, ['GB', 'US'], benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    proposal = validate_dataset(OUT / 'records.review-only.jsonl', LEDGER, ['GB', 'US'], benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    require_distinct_source_spans(proposal, ledger)
    assert len(proposal) == 50 and sum(q['split'] == 'train' for q in proposal) == 34
    assert not {a for q in proposal if q['split'] == 'train' for a in q['_author_ids']} & {a for q in proposal if q['split'] == 'validation' for a in q['_author_ids']}
    parents = read_jsonl(ROOT / 'artifacts/source-candidates-v20/records.proposed.jsonl')
    for old_row, new_row in zip(parents, read_jsonl(OUT / 'records.review-only.jsonl')):
        assert {k: v for k, v in old_row.items() if k != 'dataset_version'} == {k: v for k, v in new_row.items() if k != 'dataset_version'}
    assert 'v23-james-reaction-revision' not in {q['id'] for q in proposal}
    for row in rows:
        assert row['teacher'] is None
        for span in row['source_spans']:
            path = ROOT / 'rights' / ledger[span['rights_record_id']]['source']['raw_path']
            assert path.read_text()[span['start']:span['end']] == span['text']
        if row['id'].startswith('v24-'):
            assert row['messages'][-1]['content'] == row['source_spans'][-1]['text']
    revision = next(q for q in rows if q['id'] == 'v24-james-concise-revision')
    assert [len(s['text'].split()) for s in revision['source_spans']] == [91, 87]
    assert 'minimum' not in revision['messages'][0]['content'].lower()
    scope = json.loads((OUT / 'wilde-scope.json').read_text())
    for row in rows[-2:]:
        answer = row['messages'][-1]['content']
        assert len(re.findall(r'(?m)^[A-Z][A-Z .]+\.\n', answer)) == 4
        assert '[' not in answer and ']' not in answer
        assert row['source_spans'][0] in scope
    assert [len(q['messages'][-1]['content'].split()) for q in rows[-2:]] == [84, 59]
    for folder in ['evaluation', 'configs']:
        assert not any(re.search(r'oscar.wilde|importance.of.being.earnest', p.read_text(errors='replace'), re.I) for p in (ROOT / folder).rglob('*') if p.is_file())
    result = dict(passed=True, candidates=6, train_records=34, exposed_monitors=16, new_scoped_rights_records=1, prior_ledger_records_unchanged=18, concise_revision_words=[91, 87], dialogue_turns=[4, 4], dialogue_words_with_labels=[84, 59], overlapping_full_revision_reserved=True, source_and_author_split_verified=True, previous_artifacts_and_models_unchanged=True, training=False, inference_requests=0, human_quality_ratings=0, app_changes=False)
    if (OUT / 'tokenizer-preflight.json').exists():
        tokens = json.loads((OUT / 'tokenizer-preflight.json').read_text())
        assert tokens['passed'] and tokens['records'] == 50 and tokens['train_records'] == 34
        for name, expected in tokens['input_hashes'].items():
            assert file_hash(ROOT / name) == expected
        result.update(maximum_tokens=tokens['maximum_tokens'], supervised_train_tokens=tokens['supervised_train_tokens'])
    return result


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
