"""Build the scoped Shelley revision reserve from two pinned edition transcriptions."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import digest, file_hash, read_jsonl, validate_dataset

RAW = ROOT / 'rights/raw/shelley-rewrite-v54'
OUT = ROOT / 'artifacts/shelley-rewrite-v54'
LEDGER = ROOT / 'rights/shelley-rewrite-v54.scoped.jsonl'
EDITIONS = (
    (1818, 41445, 'Lackington, Hughes, Harding, Mavor & Jones',
     '4feec0cd7b965bd2c69a5f31c9dc0c9820734633dcc11294d9b244ce7d18e466',
     'https://www.loc.gov/item/53051218/'),
    (1831, 42324, 'Henry Colburn and Richard Bentley',
     '4cf69b5c1b42ef41cc5650d6ac55961c9422f597c970cdc6f3208690dc3487a6',
     'https://old-digitalcollections.nypl.org/collections/frankenstein-or-the-modern-prometheus-to-which-is-added-vol-1-of-f-schillers'),
)
PAIRS = (
    ('accusation', 231, 246,
     'Sharpen the brother’s spoken reaction and close on the horror of the alleged crime. Preserve Elizabeth’s disbelief and leave Justine’s guilt unresolved.'),
    ('mourning', 290, 299,
     'Retain the household’s mourning and Victor’s recollection of Elizabeth. Replace the abstract summary of her later talk with a figurative close focused on the visible effect of grief.'),
    ('ice', 744, 744,
     'Keep the ship’s danger, the crew looking to Walton for help, and his continuing courage. Redirect the ending from stoic resolve to his responsibility for the risk, leaving survival uncertain.'),
)
WORK = 'shelley-frankenstein'
DATE = '2026-11-03'


class Paragraphs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.inside = False

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.inside = True
            self.rows.append('')

    def handle_endtag(self, tag):
        if tag == 'p':
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.rows[-1] += data


def write_jsonl(path, rows):
    content = ''.join(json.dumps(row, ensure_ascii=False) + '\n' for row in rows)
    if path.exists() and path.read_text() != content:
        raise ValueError(f'Refusing to replace changed evidence at {path}')
    path.write_text(content)


def main():
    records, spans_by_year = [], []
    for index, (year, ebook, publisher, expected, catalogue) in enumerate(EDITIONS):
        html = RAW / f'{year}.html'
        if file_hash(html) != expected:
            raise ValueError(f'{year} transcription differs from the reviewed bytes')
        parser = Paragraphs()
        parser.feed(html.read_text())
        excerpts = [' '.join(parser.rows[pair[index + 1]].split()) for pair in PAIRS]
        raw = RAW / f'{year}.selected.txt'
        if raw.exists() and raw.read_text() != '\n\n'.join(excerpts) + '\n':
            raise ValueError(f'{year} selected text differs from the reviewed spans')
        raw.write_text('\n\n'.join(excerpts) + '\n')
        ident = f'shelley-frankenstein-{year}-pg{ebook}-v54'
        offset = 0
        spans = []
        for excerpt in excerpts:
            spans.append(dict(rights_record_id=ident, start=offset, end=offset + len(excerpt), text=excerpt))
            offset += len(excerpt) + 2
        spans_by_year.append(spans)
        catalog = f'https://www.gutenberg.org/ebooks/{ebook}'
        text_url = f'https://www.gutenberg.org/files/{ebook}/{ebook}-h/{ebook}-h.htm'
        evidence = [catalog, catalogue, text_url]
        checksum = file_hash(raw)
        records.append(dict(schema_version='1.0', id=ident, work_id=WORK, title='Frankenstein',
            source_kind='public_domain_candidate', author_ids=['shelley'],
            contributors=[dict(name='Mary Wollstonecraft Shelley', role='author of selected fiction prose',
                               life_dates='1797–1851')],
            publication=dict(original_year=year, edition=f'{year} London edition, PG {ebook} transcription from a photo-reprint',
                             publisher=publisher, evidence=evidence),
            source=dict(url=text_url, retrieved_on=DATE, revision=f'sha256:{checksum}', sha256=checksum,
                        raw_path=str(raw.relative_to(ROOT / 'rights')),
                        included_material=f'Three original-prose excerpts only, from HTML SHA256 {expected}. HTML paragraph indices: {[pair[index + 1] for pair in PAIRS]}. Whitespace normalised.',
                        excluded_material='All other text, prefaces, introductions, layout, images, notes, wrappers, branding and modern editorial matter.',
                        terms_evidence=['https://www.gutenberg.org/policy/permission.html',
                                        'https://www.gutenberg.org/policy/license.html', catalog],
                        terms_decision='Private GB/US training and evaluation only for the selected unbranded historical prose.',
                        notices='Original acquired HTML retained locally. Transcription punctuation and paragraph boundaries can differ from corroborating editions.'),
            clearances=[
                dict(jurisdiction='GB', basis='Published original prose by an author who died in 1851. The ordinary life-plus-70 term has elapsed.',
                     uses=['training', 'evaluation'], evidence=[catalogue, 'https://www.gov.uk/copyright/how-long-copyright-lasts']),
                dict(jurisdiction='US', basis='Exact catalogue item identifies public domain in the USA. The historical publication predates the maximum relevant historical term.',
                     uses=['training', 'evaluation'], evidence=[catalog, 'https://www.copyright.gov/circs/circ15a.pdf'])],
            unresolved_issues=[], review=dict(status='approved', reviewer='Codex AI: bounded historical original-prose evidence assessment',
                                               reviewed_on=DATE, notes='Project eligibility assessment for the named uses and excerpts. Physical source copy and modern punctuation identity are outside this finding.')))
    write_jsonl(LEDGER, records)
    rows = []
    for (slug, _, _, brief), before, after in zip(PAIRS, *spans_by_year):
        messages = [
            dict(role='user', content=f'{brief} Return only the revised passage.\n\nPASSAGE:\n{before["text"]}'),
            dict(role='assistant', content=after['text']),
        ]
        rows.append(dict(schema_version='1.0', id=f'v54-shelley-{slug}', dataset_version='shelley-rewrite-v54',
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
    print(f'Validated {len(checked)} exact Shelley pairs for GB/US training use')


if __name__ == '__main__':
    main()
