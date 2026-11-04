"""Build the scoped Wilde revision reserve from two pinned edition transcriptions."""
import re
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import digest, file_hash, read_jsonl, validate_dataset

RAW = ROOT / 'rights/raw/wilde-rewrite-v56'
OUT = ROOT / 'artifacts/wilde-rewrite-v56'
LEDGER = ROOT / 'rights/wilde-rewrite-v56.scoped.jsonl'
EDITIONS = (
    (1890, 4078, 'J. B. Lippincott Company',
     'a25df0325a1693c09a000306ab218efd8e29a10a5b6de7149ca5fea606977108',
     'https://www.themorgan.org/printed-books/130859'),
    (1891, 174, 'Ward, Lock & Co.',
     '38f36b510417177aa87a6a24c968e3ec63a447b7df36a9c1a7c5a3f2d9e51547',
     'https://catalogue.nli.ie/Record/vtls000106195'),
)
PAIRS = (
    ('exhibition', 13, 19,
     'Make Lord Henry’s advice more epigrammatic. Use a balanced contrast between visitors and pictures at the Academy. Keep Basil as the addressee, the Grosvenor as the recommendation, and next year as the timing.'),
    ('tea', 189, 188,
     'Revise the close to make the invitation teasing through a question. Keep the painting’s planned treatment, the bell for tea, and the same two guests.'),
    ('lamp', 742, 970,
     'Stretch the moment between remembering the lamp and taking it. You may enrich its surface details and add a moment of hesitation. Keep the same lamp, the fear of questions, the removal from the table, and the unnaturally still figure.'),
)
WORK = 'wilde-dorian-gray'
DATE = '2026-11-04'


def write_jsonl(path, rows):
    content = ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows)
    if path.exists() and path.read_text() != content:
        raise ValueError(f'Refusing to replace changed evidence at {path}')
    path.write_text(content)


def main():
    records, spans_by_year = [], []
    for index, (year, ebook, publisher, expected, catalogue) in enumerate(EDITIONS):
        source = RAW / f'{year}.txt'
        if file_hash(source) != expected:
            raise ValueError(f'{year} transcription differs from the reviewed bytes')
        text = source.read_text().split('*** START', 1)[1].split('*** END', 1)[0]
        paragraphs = [' '.join(p.split()) for p in re.split(r'\n\s*\n', text)]
        excerpts = [paragraphs[pair[index + 1]] for pair in PAIRS]
        raw = RAW / f'{year}.selected.txt'
        if raw.exists() and raw.read_text() != '\n\n'.join(excerpts) + '\n':
            raise ValueError(f'{year} selected text differs from the reviewed spans')
        raw.write_text('\n\n'.join(excerpts) + '\n')
        ident = f'wilde-dorian-gray-{year}-pg{ebook}-v56'
        offset = 0
        spans = []
        for excerpt in excerpts:
            spans.append(dict(rights_record_id=ident, start=offset, end=offset + len(excerpt), text=excerpt))
            offset += len(excerpt) + 2
        spans_by_year.append(spans)
        catalog = f'https://www.gutenberg.org/ebooks/{ebook}'
        text_url = f'https://www.gutenberg.org/cache/epub/{ebook}/pg{ebook}.txt'
        evidence = [catalog, catalogue, text_url]
        checksum = file_hash(raw)
        records.append(dict(schema_version='1.0', id=ident, work_id=WORK, title='The Picture of Dorian Gray',
            source_kind='public_domain_candidate', author_ids=['oscar-wilde'],
            contributors=[dict(name='Oscar Wilde', role='author of selected fiction prose',
                               life_dates='1854–1900')],
            publication=dict(original_year=year, edition=f'{year} published text, PG {ebook} transcription. Physical copy unidentified',
                             publisher=publisher, evidence=evidence),
            source=dict(url=text_url, retrieved_on=DATE, revision=f'sha256:{checksum}', sha256=checksum,
                        raw_path=str(raw.relative_to(ROOT / 'rights')),
                        included_material=f'Three original-prose excerpts only, from UTF-8 source SHA256 {expected}. Paragraph indices: {[pair[index + 1] for pair in PAIRS]}. Whitespace normalised.',
                        excluded_material='All other text, prefaces, introductions, layout, images, notes, wrappers, branding and modern editorial matter.',
                        terms_evidence=['https://www.gutenberg.org/policy/permission.html',
                                        'https://www.gutenberg.org/policy/license.html', catalog],
                        terms_decision='Private GB/US training and evaluation only for the selected unbranded historical prose.',
                        notices='Original acquired UTF-8 file retained locally. Transcription punctuation and paragraph boundaries can differ from corroborating editions.'),
            clearances=[
                dict(jurisdiction='GB', basis='Published original prose by an author who died in 1900. The ordinary life-plus-70 term has elapsed.',
                     uses=['training', 'evaluation'], evidence=[catalogue, 'https://www.gov.uk/copyright/how-long-copyright-lasts']),
                dict(jurisdiction='US', basis='Exact catalogue item identifies public domain in the USA. The historical publication predates the maximum relevant historical term.',
                     uses=['training', 'evaluation'], evidence=[catalog, 'https://www.copyright.gov/circs/circ15a.pdf'])],
            unresolved_issues=[], review=dict(status='approved', reviewer='Codex AI: bounded historical original-prose evidence assessment',
                                               reviewed_on=DATE, notes='Project eligibility assessment for the named uses and excerpts. Approval covers only the selected historical wording. The physical copy and individual editorial interventions are unidentified.')))
    write_jsonl(LEDGER, records)
    rows = []
    for (slug, _, _, brief), before, after in zip(PAIRS, *spans_by_year):
        messages = [
            dict(role='user', content=f'{brief} Return only the revised passage.\n\nPASSAGE:\n{before["text"]}'),
            dict(role='assistant', content=after['text']),
        ]
        rows.append(dict(schema_version='1.0', id=f'v56-wilde-{slug}', dataset_version='wilde-rewrite-v56',
            task='editing', split='train', split_group=WORK, origin='derived', messages=messages,
            source_work_ids=[WORK], rights_record_ids=[before['rights_record_id'], after['rights_record_id']],
            source_spans=[before, after], teacher=None, content_hash=digest(messages),
            rubric=['state fidelity', 'stylistic change', 'narrative coherence'],
            review=dict(status='approved', reviewer='Codex AI: historical passage and brief comparison',
                        reviewed_on=DATE, notes='Reserved for a future source-backed pilot. Target is the historical revision.')))
    OUT.mkdir(exist_ok=True)
    path = OUT / 'records.review-only.jsonl'
    write_jsonl(path, rows)
    checked = validate_dataset(path, LEDGER, ['GB', 'US'],
                               benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    print(f'Validated {len(checked)} exact Wilde pairs for GB/US training use')


if __name__ == '__main__':
    main()
