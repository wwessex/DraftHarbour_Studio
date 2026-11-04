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

OUT = ROOT / 'artifacts/limited-observation-v44'
BASE = ROOT / 'artifacts/short-fiction-v37'
OLD_LEDGER = ROOT / 'rights/short-fiction-v37.scoped.jsonl'
LEDGER = ROOT / 'rights/limited-observation-v44.scoped.jsonl'
RAW = ROOT / 'rights/raw/limited-observation-v44'
SOURCES = [
    (710, 'jack-london', 'Jack London', '1876–1916', 1907, 'Love of Life', [
        ('match-inventory', 'fiction', 'He unwrapped his pack and the first thing he did was to count his',
         'He dried his wet foot-gear by the fire.',
         'Write one paragraph of wilderness fiction. Show an exhausted traveller counting his sixty-seven matches, dividing them between three locations, and counting again when panic returns. Preserve the total and show the recount rather than reassuring him about his future safety.'),
        ('course-correction', 'fiction', 'The sun came out, and he succeeded in locating the points of the',
         'Though the hunger pangs were no longer so exquisite',
         'Write one short paragraph of wilderness fiction. The sun lets the lost traveller establish the compass directions. He suspects he veered left earlier and bears right to compensate. Keep the earlier deviation a possibility and leave his location uncertain.'),
        ('lost-equipment', 'fiction', 'He sat up and turned his attention to immediate affairs.',
         'He was calm and collected. Though extremely weak',
         'Write one paragraph of wilderness fiction showing a traveller checking his supplies and his watch. The rifle, knife, hat and the matches in its band are gone. Only the matches stored against his chest are confirmed dry. Show the watch still running and let his conclusion about winding it remain an inference.'),
        ('pool-search', 'fiction', 'He came to a pool of water. Stooping over in quest of minnows,',
         'That day he decreased the distance between him and the ship',
         'Write one paragraph of wilderness fiction. The traveller sees his reflection while looking for minnows, tries using his tin bucket, then stops because of his weakness and fear of falling in. He catches nothing. Link the same fear to his decision to leave the drift logs alone.'),
    ]),
    (3688, 'saki', 'Saki', '1870–1916', 1911, 'The Chronicles of Clovis', [
        ('pantry-checks', 'pacing', 'At eleven the\nservants went to bed, announcing',
         "At two o'clock Clovis broke the dominating silence.",
         'Write a short stretch of period fiction that slows the pace during an anxious vigil. The servants say they have left the pantry window open for Tobermory. The guests run through their reading while Lady Blemley repeatedly checks the pantry. Show her expression on returning without resolving what happened to the cat.'),
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
        rid = f'{author_id}-pg{number}-v44'
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
                                dataset_version='limited-observation-v44-review', task=task, split='train',
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
    rows = [dict(r, dataset_version='limited-observation-v44-review') for r in read_jsonl(BASE / 'records.review-only.jsonl')] + records
    OUT.mkdir()
    write_rows(LEDGER, old + entries)
    path = OUT / 'records.review-only.jsonl'
    write_rows(path, rows)
    write_rows(OUT / 'candidates.jsonl', records)
    require_distinct_source_spans(rows, load_ledger(LEDGER))
    checked = validate_dataset(path, LEDGER, ['GB', 'US'],
                               benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    assert len(checked) == 71 and sum(r['split'] == 'train' for r in checked) == 55
    with (OUT / 'review.json').open('x') as stream:
        json.dump(dict(training_started=False, training_records=55, exposed_monitors=16,
                       additions={r['id']: len(r['messages'][-1]['content'].split()) for r in records},
                       hashes={str(p.relative_to(ROOT)): file_hash(p) for p in
                               (Path(__file__), path, LEDGER, OLD_LEDGER, *RAW.glob('*.txt'), ROOT / 'rights/raw/short-fiction-v37/pg3688.txt')}), stream, indent=2)
        stream.write('\n')
    print('Validated five limited-observation targets in the 55-example review proposal.')


if __name__ == '__main__':
    main()
