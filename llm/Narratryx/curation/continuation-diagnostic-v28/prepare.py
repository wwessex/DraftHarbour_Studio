"""Add matching length instructions to four existing source lessons."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import digest, file_hash, read_jsonl, validate_dataset

OUT = ROOT / 'artifacts/continuation-diagnostic-v28'
SOURCE = ROOT / 'artifacts/curriculum-fit-v24/records.review-only.jsonl'
LEDGER = ROOT / 'rights/curriculum-fit-v24.scoped.jsonl'


def main():
    evidence = json.loads((OUT / 'decision.json').read_text())
    assert file_hash(SOURCE) == evidence['source_dataset_sha256']
    selected = {row['id'] for row in evidence['lessons']
                if row['paragraphs'] == 1 and 60 <= row['words'] <= 100}
    assert len(selected) == 4
    original = read_jsonl(SOURCE)
    proposal = copy.deepcopy(original)
    for row in proposal:
        if row['id'] in selected:
            assert row['split'] == 'train' and row['teacher'] is None
            row['messages'][0]['content'] = (
                'Keep the new paragraph between 60 and 100 words. '
                + row['messages'][0]['content'])
            row['content_hash'] = digest(row['messages'])
    assert all(a['messages'][1:] == b['messages'][1:] for a, b in zip(original, proposal))
    output = OUT / 'records.review-only.jsonl'
    with output.open('x') as stream:
        for row in proposal:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    rows = validate_dataset(output, LEDGER, ['GB', 'US'],
                            benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    assert sum(row['split'] == 'train' for row in rows) == 34 and len(rows) == 50
    with (OUT / 'proposal.json').open('x') as stream:
        json.dump(dict(changed_brief_ids=sorted(selected), output_sha256=file_hash(output),
                       source_sha256=file_hash(SOURCE), ledger_sha256=file_hash(LEDGER),
                       training_started=False), stream, indent=2)
        stream.write('\n')
    print('Validated four length instructions against unchanged source answers.')


if __name__ == '__main__':
    main()
