"""Add exact scenes that preserve resource state and limit conclusions."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.mixed_curriculum import require_distinct_source_spans
from foundation.scoped_excerpt import excerpt
from foundation.validation import digest, file_hash, load_ledger, read_jsonl, validate_dataset

OUT = ROOT / 'artifacts/balanced-writing-v47'
BASE = ROOT / 'artifacts/limited-observation-v44'
OLD_LEDGER = ROOT / 'rights/limited-observation-v44.scoped.jsonl'
LEDGER = ROOT / 'rights/balanced-writing-v47.scoped.jsonl'
RAW = ROOT / 'rights/raw/balanced-writing-v47'
SOURCES = [
    (3688, 'saki', 'Saki', '1870–1916', 1911, 'The Chronicles of Clovis', [
        ('milk-exchange', 'dialogue', '"Will you have some milk, Tobermory?"',
         '\n\nAnother silence fell on the group, and then Miss Resker', 'Write four spoken turns with brief action. Lady Blemley offers the talking cat milk, he accepts, she apologizes for spilling it, and he answers dryly about the carpet.'),
        ('staging-disagreement', 'dialogue', '"Dear no.  Agamemnon was',
         '"My dear boy, I can ask', 'Write five spoken turns in a period comedy. Clovis declines the lead, explains his staging idea when asked, and suggests reframing it after the Baroness objects. Leave her agreement unresolved.'),
    ]),
]


def write_rows(path, rows):
    with path.open('x') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')


def main():
    assert not OUT.exists() and not LEDGER.exists()
    manifest = json.loads((BASE / 'review.json').read_text())
    for name, expected in manifest['hashes'].items():
        assert file_hash(ROOT / name) == expected, name
    old = read_jsonl(OLD_LEDGER)
    records, entries = [], []
    for number, author_id, author, dates, year, title, lessons in SOURCES:
        path = (RAW if number == 710 else ROOT / 'rights/raw/short-fiction-v37') / f'pg{number}.txt'
        source = path.read_text()
        rid = f'{author_id}-pg{number}-v47'
        work = 'jack-london-love-of-life' if number == 710 else 'saki-short-stories-pg3688'
        catalogue = f'https://www.gutenberg.org/ebooks/{number}'
        review = dict(status='approved', reviewer='Codex AI: exact-source rights and task-fit assessment',
                      reviewed_on='2026-11-03', notes='Bounded GB/US private local training assessment on selected original prose. Review proposal.')
        spans = []
        for name, task, opening, following, prompt in lessons:
            span = dict(excerpt(source, opening, following), rights_record_id=rid)
            assert source[span['start']:span['end']] == span['text']
            spans.append(span)
            messages = [dict(role='user', content=prompt), dict(role='assistant', content=span['text'])]
            records.append(dict(schema_version='1.0', id=f'v44-{name}',
                                dataset_version='balanced-writing-v47-review', task=task, split='train',
                                split_group=work, origin='derived', messages=messages, source_work_ids=[work],
                                rights_record_ids=[rid], source_spans=[span], teacher=None, review=review,
                                rubric=['source fidelity', 'concrete action', 'task fit'],
                                content_hash=digest(messages)))
        entry = copy.deepcopy(old[-1])
        entry.update(id=rid, work_id=work, title=title + ' — selected story intervals',
                     author_ids=[author_id], contributors=[dict(name=author, life_dates=dates,
                     role='author of selected original story text')], review=review,
                     publication=dict(original_year=year, edition=('Exact PG710 transcription of the 1913 Macmillan printing. Collection published in 1907.' if number == 710 else 'Exact PG3688 plain-text digital artifact. Collection dated 1911. Physical exemplar not established.'),
                                      publisher='Project Gutenberg digital transcription', evidence=[catalogue]))
        entry['source'].update(url=f'https://www.gutenberg.org/cache/epub/{number}/pg{number}.txt',
                               raw_path=str(path.relative_to(ROOT / 'rights')), sha256=file_hash(path),
                               revision='sha256:' + file_hash(path), retrieved_on='2026-11-03',
                               included_material='Only LF-normalized intervals ' +
                               ', '.join(f"{s['start']}:{s['end']}" for s in spans),
                               excluded_material='All other material including Milne introduction, title matter, publisher notices, illustrations, quotations outside the selected text and provider apparatus.',
                               terms_evidence=[catalogue, 'https://www.gutenberg.org/policy/license.html',
                                               'https://www.gutenberg.org/policy/terms_of_use.html'])
        entry['clearances'] = [
            dict(jurisdiction='GB', uses=['training'], basis=f'Original author life dates {dates}. Ordinary life-plus-70 term elapsed for included original stories.',
                 evidence=[catalogue, 'https://www.gov.uk/copyright/how-long-copyright-lasts']),
            dict(jurisdiction='US', uses=['training'], basis=f'Publication by {year} is beyond the historical 95-year term. Catalogue identifies US public domain.',
                 evidence=[catalogue, 'https://www.copyright.gov/circs/circ15a.pdf']),
        ]
        entries.append(entry)
    reserve = ROOT / 'artifacts/revision-preflight-v1/records.jsonl'
    edits = [r for r in read_jsonl(reserve) if r['id'] in {
        'v3-032-anchored-copyedit', 'v3-033-anchored-copyedit',
        'v3-038-anchored-copyedit', 'v3-039-anchored-copyedit'}]
    assert len(edits) == 4 and all(r['split'] == 'train' and r['teacher'] is None for r in edits)
    records.extend(dict(r, dataset_version='balanced-writing-v47-review') for r in edits)
    rows = [dict(r, dataset_version='balanced-writing-v47-review') for r in read_jsonl(BASE / 'records.review-only.jsonl')] + records
    OUT.mkdir()
    write_rows(LEDGER, old + entries)
    path = OUT / 'records.review-only.jsonl'
    write_rows(path, rows)
    write_rows(OUT / 'candidates.jsonl', records)
    require_distinct_source_spans(rows, load_ledger(LEDGER))
    checked = validate_dataset(path, LEDGER, ['GB', 'US'],
                               benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    assert len(checked) == 77 and sum(r['split'] == 'train' for r in checked) == 61
    with (OUT / 'review.json').open('x') as stream:
        json.dump(dict(training_started=False, training_records=61, exposed_monitors=16,
                       additions={r['id']: len(r['messages'][-1]['content'].split()) for r in records},
                       hashes={str(p.relative_to(ROOT)): file_hash(p) for p in
                               (Path(__file__), path, LEDGER, OLD_LEDGER, reserve, *RAW.glob('*.txt'), ROOT / 'rights/raw/short-fiction-v37/pg3688.txt')}), stream, indent=2)
        stream.write('\n')
    print('Validated six writing targets in the 61-example review proposal.')


if __name__ == '__main__':
    main()
