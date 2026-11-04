"""Prepare two exact-source criticism candidates and validate the expanded proposal."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.mixed_curriculum import require_distinct_source_spans
from foundation.scoped_excerpt import excerpt
from foundation.validation import digest, file_hash, load_ledger, read_jsonl, validate_dataset

OUT = ROOT / 'artifacts/close-reading-v32'
OLD_LEDGER = ROOT / 'rights/curriculum-fit-v24.scoped.jsonl'
LEDGER = ROOT / 'rights/close-reading-v32.scoped.jsonl'
BASE = ROOT / 'artifacts/curriculum-fit-v31/records.review-only.jsonl'
RAW = ROOT / 'rights/raw/close-reading-v32'


def write_rows(path, rows):
    with path.open('x') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')


def main():
    assert not OUT.exists() and not LEDGER.exists()
    old = read_jsonl(OLD_LEDGER)
    prior = json.loads((BASE.parent / 'review.json').read_text())
    assert file_hash(BASE) == prior['hashes'][str(BASE.relative_to(ROOT))]
    outline = [
        (55749, 'edgar-allan-poe', 'Edgar Allan Poe', '1809–1849',
         'philosophy-of-composition', 'The Philosophy of Composition', 1846,
         'PG55749 plain text of the Harwell-Evans 1906 illustrated reprint. Essay first printed in Graham’s Magazine, April 1846. Original author text only.',
         'https://www.eapoe.org/Works/info/petpc.htm',
         'It will be observed that the words,', ' The reader begins now',
         'Using the supplied lines, reproduce Poe’s published observation about the metaphor and the effect of the refrain. Return the two sentences of criticism only.'),
        (64457, 'virginia-woolf', 'Virginia Woolf', '1882–1941',
         'common-reader-jane-austen-essay', 'The Common Reader — Jane Austen essay', 1925,
         'PG64457 plain text transcribed from the 1925 New York Harcourt, Brace and Company edition, as identified by the title and copyright pages.',
         'https://www.gutenberg.org/files/64457/64457-h/64457-h.htm',
         'How, we are made to wonder,', ' Here, indeed, in',
         'In this scene from The Watsons, Lord Osborne and Tom Musgrove call just as Mary brings in the tray and knife-case. Reproduce Woolf’s published critical account of how the awkward timing and dialogue create suspense about Emma’s behavior. Return the source criticism only.'),
    ]
    records, rights, scope = [], [], []
    for number, author_id, author, dates, work_id, title, year, edition, bibliography, opening, following, prompt in outline:
        path = RAW / f'pg{number}.txt'
        text = path.read_text(encoding='utf-8')
        rid = f'{author_id}-pg{number}-v32'
        target = dict(excerpt(text, opening, following), rights_record_id=rid)
        spans = [target]
        if number == 55749:
            context = dict(excerpt(text, '“Take thy beak from out my heart,', '\n\nIt will be observed'), rights_record_id=rid)
            prompt += '\n\nLINES:\n' + context['text']
            spans.insert(0, context)
        scope.extend(spans)
        catalogue = f'https://www.gutenberg.org/ebooks/{number}'
        review = dict(status='approved', reviewer='Codex AI: scoped source and task-fit assessment',
                      reviewed_on='2026-11-03',
                      notes='AI evidence assessment for private GB/US training preparation. No human or legal certification. Candidate review only.')
        q = copy.deepcopy(old[-1])
        q.update(id=rid, work_id=work_id, title=title, author_ids=[author_id],
                 contributors=[dict(name=author, role='author of included original text', life_dates=dates)],
                 publication=dict(original_year=year, edition=edition, publisher='Project Gutenberg digital transcription',
                                  evidence=[catalogue, bibliography]), review=review)
        q['source'].update(url=f'https://www.gutenberg.org/cache/epub/{number}/pg{number}.txt',
                           raw_path=str(path.relative_to(ROOT / 'rights')), retrieved_on='2026-11-03',
                           sha256=file_hash(path), revision='sha256:' + file_hash(path),
                           included_material='Only these LF-normalized codepoint intervals: ' +
                           ', '.join(f"{s['start']}:{s['end']}" for s in spans),
                           excluded_material='All other passages, third-party quotations, images, layout, modern editorial material and provider apparatus.',
                           notices='Original header, footer, credit and provider license retained in raw bytes.',
                           terms_evidence=[catalogue, 'https://www.gutenberg.org/policy/license.html',
                                           'https://www.gutenberg.org/policy/terms_of_use.html'],
                           terms_decision='Scoped private training preparation on expired original author text. No branding or digital edition redistribution. No bulk acquisition.')
        q['clearances'] = [
            dict(jurisdiction='GB', uses=['training'],
                 basis=f'Original author life dates {dates}. Ordinary life-plus-70 term elapsed for the published text. Selected spans contain only original author text.',
                 evidence=[catalogue, bibliography, 'https://www.gov.uk/copyright/how-long-copyright-lasts']),
            dict(jurisdiction='US', uses=['training'],
                 basis=f'Original text published in {year}, beyond the historical 95-year term. PG item catalogue identifies US public domain.',
                 evidence=[catalogue, bibliography, 'https://www.copyright.gov/circs/circ15a.pdf']),
        ]
        rights.append(q)
        messages = [dict(role='user', content=prompt), dict(role='assistant', content=target['text'])]
        records.append(dict(schema_version='1.0', id=f'v32-{author_id}-criticism',
                            dataset_version='close-reading-v32-review', task='analysis', split='train',
                            split_group=work_id, origin='derived', messages=messages,
                            source_work_ids=[work_id], rights_record_ids=[rid], source_spans=spans,
                            teacher=None, review=review, rubric=['source fidelity', 'specific evidence', 'interpretation'],
                            content_hash=digest(messages)))
    OUT.mkdir()
    write_rows(LEDGER, old + rights)
    write_rows(OUT / 'scope.jsonl', scope)
    write_rows(OUT / 'candidates.jsonl', records)
    dataset = OUT / 'records.review-only.jsonl'
    write_rows(dataset, [dict(r, dataset_version='close-reading-v32-review') for r in read_jsonl(BASE)] + records)
    require_distinct_source_spans(read_jsonl(dataset), load_ledger(LEDGER))
    checked = validate_dataset(dataset, LEDGER, ['GB', 'US'],
                               benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    assert len(checked) == 58 and sum(r['split'] == 'train' for r in checked) == 42
    with (OUT / 'review.json').open('x') as stream:
        paths = [Path(__file__), OLD_LEDGER, LEDGER, BASE, *RAW.glob('*.txt'), *OUT.glob('*.jsonl')]
        json.dump(dict(training_started=False, candidates=2, training_records=42, exposed_monitors=16,
                       hashes={str(p.relative_to(ROOT)): file_hash(p) for p in paths}), stream, indent=2)
        stream.write('\n')
    print('Validated two exact-source criticism lessons in a 42-example review proposal.')


if __name__ == '__main__':
    main()
