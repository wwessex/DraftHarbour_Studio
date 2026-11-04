"""Add selected O. Henry and Saki lessons with exact text and scope."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.mixed_curriculum import require_distinct_source_spans
from foundation.scoped_excerpt import excerpt
from foundation.validation import digest, file_hash, load_ledger, read_jsonl, validate_dataset

OUT = ROOT / 'artifacts/short-fiction-v37'
BASE = ROOT / 'artifacts/practical-scenes-v34'
OLD_LEDGER = ROOT / 'rights/watsons-v33.scoped.jsonl'
LEDGER = ROOT / 'rights/short-fiction-v37.scoped.jsonl'
RAW = ROOT / 'rights/raw/short-fiction-v37'
SOURCES = [
    (2776, 'o-henry', 'O. Henry', '1862–1910', 1906, 'The Four Million', [
        ('hair-bargain', 'dialogue', '“Will you buy my hair?” asked Della.',
         'Oh, and the next two hours', 'Write four spoken turns with brief action and speech tags. Della asks a hair dealer to buy her hair. The dealer asks to see it, offers twenty dollars after Della reveals it, and Della accepts urgently. Return only the exchange.'),
        ('chain-purchase', 'fiction', 'She found it at last. It surely had been made for Jim',
         'When Della reached home', 'Write one period-fiction paragraph showing Della finally finding a plain platinum chain for Jim’s watch. Make the object reflect his character, then show the purchase for twenty-one dollars and her leaving with eighty-seven cents. Mention the worn strap it will replace.'),
        ('food-return', 'fiction', 'He dashed out the green door and down the stairs.',
         '“This is ridiculous,” said Rudolf', 'Write one short paragraph of period fiction. Rudolf hurries out for food and returns twenty minutes later with both arms full. Show how he signals at the door and sets the supplies down. Let the visible food show what he accomplished.'),
    ]),
    (3688, 'saki', 'Saki', '1870–1916', 1911, 'The Chronicles of Clovis', [
        ('false-alarm', 'pacing', 'On this particular morning the sight of Lady Bastable',
         'Lost dignity is not a possession', 'Write a period comic scene that accelerates from Clovis spotting an opportunity to Lady Bastable running across the lawn. Use the ambiguous summons, the servants’ rush and the gardener’s sickle to make her response understandable. Keep her reason for fleeing an inference.'),
        ('casting-agreement', 'dialogue', '"I thought you said it was a tragedy."',
         '"Dear no.  Agamemnon was', 'Write five period dialogue turns in a comic rehearsal discussion. The Baroness questions the tragedy, mistakes Agamemnon’s murder for another story, and accepts the role when Clovis identifies Clytemnestra. End with her asking what part he wants.'),
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
        path = RAW / f'pg{number}.txt'
        source = path.read_text()
        rid = f'{author_id}-pg{number}-v37'
        work = f'{author_id}-short-stories-pg{number}'
        catalogue = f'https://www.gutenberg.org/ebooks/{number}'
        review = dict(status='approved', reviewer='Codex AI: exact-source rights and task-fit assessment',
                      reviewed_on='2026-11-03', notes='Bounded GB/US private local training assessment on selected original prose. Review proposal.')
        spans = []
        for name, task, opening, following, prompt in lessons:
            span = dict(excerpt(source, opening, following), rights_record_id=rid)
            if name == 'false-alarm':
                # The following decorative separator is outside the selected story paragraph.
                end = span['text'].index('\n\n      *')
                span.update(end=span['start'] + end, text=span['text'][:end])
            assert source[span['start']:span['end']] == span['text']
            spans.append(span)
            messages = [dict(role='user', content=prompt), dict(role='assistant', content=span['text'])]
            records.append(dict(schema_version='1.0', id=f'v37-{name}',
                                dataset_version='short-fiction-v37-review', task=task, split='train',
                                split_group=work, origin='derived', messages=messages, source_work_ids=[work],
                                rights_record_ids=[rid], source_spans=[span], teacher=None, review=review,
                                rubric=['source fidelity', 'concrete action', 'task fit'],
                                content_hash=digest(messages)))
        entry = copy.deepcopy(old[-1])
        entry.update(id=rid, work_id=work, title=title + ' — selected story intervals',
                     author_ids=[author_id], contributors=[dict(name=author, life_dates=dates,
                     role='author of selected original story text')], review=review,
                     publication=dict(original_year=year, edition=f'Exact PG{number} plain-text digital artifact. Original collection dated {year}. Physical exemplar not established.',
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
    rows = [dict(r, dataset_version='short-fiction-v37-review') for r in read_jsonl(BASE / 'records.review-only.jsonl')] + records
    OUT.mkdir()
    write_rows(LEDGER, old + entries)
    path = OUT / 'records.review-only.jsonl'
    write_rows(path, rows)
    write_rows(OUT / 'candidates.jsonl', records)
    require_distinct_source_spans(rows, load_ledger(LEDGER))
    checked = validate_dataset(path, LEDGER, ['GB', 'US'],
                               benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    assert len(checked) == 66 and sum(r['split'] == 'train' for r in checked) == 50
    with (OUT / 'review.json').open('x') as stream:
        json.dump(dict(training_started=False, training_records=50, exposed_monitors=16,
                       additions={r['id']: len(r['messages'][-1]['content'].split()) for r in records},
                       hashes={str(p.relative_to(ROOT)): file_hash(p) for p in
                               (Path(__file__), path, LEDGER, *RAW.glob('*.txt'))}), stream, indent=2)
        stream.write('\n')
    print('Validated five short-fiction targets in the 50-example review proposal.')


if __name__ == '__main__':
    main()
