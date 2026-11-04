"""Keep same-scene author revisions apart from structural and copyedit targets."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl, validate_dataset

SOURCE = ROOT / 'artifacts/stylistic-writing-v48/records.review-only.jsonl'
LEDGER = ROOT / 'rights/stylistic-writing-v48.scoped.jsonl'
OUT = ROOT / 'artifacts/rewrite-reserve-v52'
IDS = {'gb-james-face-1908', 'gb-james-proposal-revision', 'v48-james-interiority'}


def main():
    validated = validate_dataset(SOURCE, LEDGER, ['GB', 'US'],
                                 benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    assert {r['id'] for r in validated if r['id'] in IDS and r['split'] == 'train'} == IDS
    selected = [r for r in read_jsonl(SOURCE) if r['id'] in IDS]
    assert all(r['task'] == 'editing' and r['teacher'] is None and len(r['source_spans']) == 2
               for r in selected)
    OUT.mkdir()
    path = OUT / 'records.review-only.jsonl'
    with path.open('x') as stream:
        for row in selected:
            stream.write(json.dumps(dict(row, dataset_version='rewrite-reserve-v52'), ensure_ascii=False) + '\n')
    checked = validate_dataset(path, LEDGER, ['GB', 'US'])
    authors = sorted({author for r in checked for author in r['_author_ids']})
    assert authors == ['henry-james']
    with (OUT / 'review.json').open('x') as stream:
        json.dump(dict(records=3, authors=authors, training_started=False,
                       source_sha256=file_hash(SOURCE), ledger_sha256=file_hash(LEDGER),
                       output_sha256=file_hash(path)), stream, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    main()
