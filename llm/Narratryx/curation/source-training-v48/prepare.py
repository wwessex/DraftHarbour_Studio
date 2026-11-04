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

OUT = ROOT / 'artifacts/stylistic-writing-v48'
BASE = ROOT / 'artifacts/limited-observation-v44'
OLD_LEDGER = ROOT / 'rights/limited-observation-v44.scoped.jsonl'
LEDGER = ROOT / 'rights/stylistic-writing-v48.scoped.jsonl'
RAW = ROOT / 'rights/raw/stylistic-writing-v48'
SOURCES = [
    (3688, 'saki', 'Saki', '1870–1916', 1911, 'The Chronicles of Clovis', [
        ('intelligence-turn', 'dialogue', '"What do you think of human intelligence?"',
         "Lady Blemley's protestations", 'Write four spoken turns in a social satire, with speech tags. Mavis asks a talking cat for a general opinion, then asks about herself. Let the cat respond with elaborate politeness while revealing the hosts’ practical motive for inviting her.'),
        ('dinner-deflection', 'dialogue', '"Would you like to go and see if cook has got your dinner ready?"',
         '"Adelaide!" said Mrs. Cornett', 'Write four spoken turns with brief narration. A hostess tries to divert a talking cat with an early dinner. The cat refuses, another guest invokes nine lives, and the cat answers with a dry retort about his liver.'),
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
        rid = f'{author_id}-pg{number}-v48'
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
                                dataset_version='stylistic-writing-v48-review', task=task, split='train',
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
    ledger = load_ledger(OLD_LEDGER)
    original = read_jsonl(BASE / 'records.review-only.jsonl')
    james = copy.deepcopy(next(r for r in original if r['id'] == 'v24-james-concise-revision'))
    spans = []
    for rid in james['rights_record_ids']:
        source = ROOT / 'rights' / ledger[rid]['source']['raw_path']
        assert file_hash(source) == ledger[rid]['source']['sha256']
        text = source.read_text()
        end = text.index('She had promised him')
        end = len(text[:end].rstrip())
        spans.append(dict(rights_record_id=rid, start=0, end=end, text=text[:end]))
    assert len(spans) == 2 and spans[0]['rights_record_id'].startswith('james-1881')
    james.update(id='v48-james-interiority', source_spans=spans, messages=[
        dict(role='user', content='Revise this narration of Isabel’s refusal. Keep the decision and her fear of pride, but give her resistance a sharper sense of confinement and missed freedom. Recast diction and rhythm. Return revised prose only.\n\nPASSAGE:\n' + spans[0]['text']),
        dict(role='assistant', content=spans[1]['text'])])
    james['content_hash'] = digest(james['messages'])
    records.append(james)

    reserve = ROOT / 'artifacts/author-revision-followup-2026-10-26/selected-spans.json'
    assert file_hash(reserve) == '39001841fe28530ccf65ae6100431eb5e71cf5a6a8549d93ab3b79ffb438825d'
    ending = []
    for span in json.loads(reserve.read_text()):
        rid = span['id']
        source = ROOT / 'rights' / ledger[rid]['source']['raw_path']
        assert file_hash(source) == ledger[rid]['source']['sha256']
        assert source.read_text()[span['start']:span['end']] == span['text']
        ending.append(dict(rights_record_id=rid, start=span['start'], end=span['end'], text=span['text']))
    assert len(ending) == 2 and 'discarded' in ending[0]['rights_record_id']
    dickens = copy.deepcopy(james)
    rids = [s['rights_record_id'] for s in ending]
    dickens.update(id='v48-dickens-alternative-ending', split_group='great-expectations',
                   rights_record_ids=rids, source_work_ids=[ledger[r]['work_id'] for r in rids],
                   source_spans=ending, messages=[
        dict(role='user', content='Replace this earlier ending with a developed scene in Pip’s first-person viewpoint. Move the reunion to the ruins of Satis House and let the changed relationship emerge through setting and dialogue. Return only the replacement ending.\n\nEARLIER ENDING:\n' + ending[0]['text']),
        dict(role='assistant', content=ending[1]['text'])])
    dickens['content_hash'] = digest(dickens['messages'])
    records.append(dickens)
    rows = [dict(r, dataset_version='stylistic-writing-v48-review') for r in original
            if r['id'] != 'v24-james-concise-revision']
    rows += [dict(r, dataset_version='stylistic-writing-v48-review') for r in records]
    OUT.mkdir()
    write_rows(LEDGER, old + entries)
    path = OUT / 'records.review-only.jsonl'
    write_rows(path, rows)
    write_rows(OUT / 'candidates.jsonl', records)
    require_distinct_source_spans(rows, load_ledger(LEDGER))
    checked = validate_dataset(path, LEDGER, ['GB', 'US'],
                               benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    assert len(checked) == 74 and sum(r['split'] == 'train' for r in checked) == 58
    with (OUT / 'review.json').open('x') as stream:
        json.dump(dict(training_started=False, training_records=58, exposed_monitors=16,
                       additions={r['id']: len(r['messages'][-1]['content'].split()) for r in records},
                       hashes={str(p.relative_to(ROOT)): file_hash(p) for p in
                               (Path(__file__), path, LEDGER, OLD_LEDGER, reserve, *RAW.glob('*.txt'), ROOT / 'rights/raw/short-fiction-v37/pg3688.txt')}), stream, indent=2)
        stream.write('\n')
    print('Validated four writing targets in the 58-example review proposal.')


if __name__ == '__main__':
    main()
