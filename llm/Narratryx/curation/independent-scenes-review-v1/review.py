"""Apply explicit AI editorial decisions to a new artifact; preserve the draft packet."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import Invalid, read_jsonl, validate_dataset

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('source_packet', HERE.parent / 'independent-scenes-v1/prepare.py')
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)
OUT = ROOT / 'artifacts/independent-scenes-reviewed-v1'


def apply_decisions(records, decisions):
    entries = decisions['decisions']
    by_id = {entry['id']: entry for entry in entries}
    if len(by_id) != len(entries) or set(by_id) != {row['id'] for row in records}:
        raise Invalid('editorial decisions must cover every example exactly once')
    result = []
    for original in records:
        entry = by_id[original['id']]
        if entry['decision'] == 'reference-only':
            continue
        if entry['decision'] != 'accept' or not entry['reason']:
            raise Invalid('unknown or unreasoned editorial decision')
        row = copy.deepcopy(original)
        row.pop('_author_ids', None)
        row['dataset_version'] = 'independent-scenes-reviewed-v1'
        row['review'] = dict(status='approved', reviewer=decisions['reviewer'],
                             reviewed_on=decisions['reviewed_on'],
                             notes=decisions['review_type'] + '. ' + entry['reason']
                             + ' Source/instruction selection only; no training run or model promotion authorised by this artifact.')
        result.append(row)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'verify'])
    args = parser.parse_args()
    PREPARE.verify_files(ROOT, json.loads((PREPARE.HERE / 'packet-lock.json').read_text())['files'])
    _, _, segments = PREPARE.sources_and_segments()
    original = read_jsonl(PREPARE.OUT / 'draft.records.jsonl')
    PREPARE.audit(copy.deepcopy(original), segments)
    decisions = json.loads((HERE / 'decisions.json').read_text())
    selected = apply_decisions(original, decisions)
    if args.command == 'build':
        OUT.mkdir(exist_ok=False)
        PREPARE.write_rows(OUT / 'records.jsonl', selected)
        PREPARE.write_json(OUT / 'decisions.json', decisions)
        PREPARE.write_json(HERE / 'review-lock.json', {'files': {
            str(p.relative_to(ROOT)): PREPARE.sha(p) for p in
            [HERE / 'decisions.json', PREPARE.HERE / 'packet-lock.json',
             PREPARE.OUT / 'draft.records.jsonl', OUT / 'records.jsonl', OUT / 'decisions.json']}})
    PREPARE.verify_files(ROOT, json.loads((HERE / 'review-lock.json').read_text())['files'])
    actual = read_jsonl(OUT / 'records.jsonl')
    if actual != selected:
        raise Invalid('reviewed selection differs from recorded decisions')
    valid = validate_dataset(OUT / 'records.jsonl', PREPARE.LEDGER, ['GB', 'US'])
    for row in valid:
        if row['messages'][-1]['content'] != row['source_spans'][-1]['text']:
            raise Invalid('literary answer differs from source')
    report = dict(passed=True, reviewed_examples=len(original), accepted_examples=len(valid),
                  reference_only=len(original)-len(valid), human_approval_recorded=False,
                  generated_literary_targets=0, trained=False, model_promoted=False,
                  prior_draft_unchanged=True)
    if args.command == 'build':
        PREPARE.write_json(OUT / 'verification.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
