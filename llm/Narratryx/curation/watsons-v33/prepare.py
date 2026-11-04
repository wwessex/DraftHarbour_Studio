"""Pair Austen's visit scene with the existing exact Woolf answer."""
import copy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.mixed_curriculum import require_distinct_source_spans
from foundation.scoped_excerpt import excerpt
from foundation.validation import digest, file_hash, load_ledger, read_jsonl, validate_dataset

BASE = ROOT / 'artifacts/close-reading-v32'
OUT = ROOT / 'artifacts/watsons-v33'
OLD_LEDGER = ROOT / 'rights/close-reading-v32.scoped.jsonl'
LEDGER = ROOT / 'rights/watsons-v33.scoped.jsonl'
RAW = ROOT / 'rights/raw/watsons-v33/pg63569.txt'
RID = 'austen-watsons-pg63569-v33'
CATALOGUE = 'https://www.gutenberg.org/ebooks/63569'
HEADNOTE = 'https://janeausten.ac.uk/edition/ms/WatsonsHeadNote.html'
PAGES = [f'https://janeausten.ac.uk/manuscripts/qmwats/b7-{n}.html' for n in range(4, 8)]


def write_rows(path, rows):
    with path.open('x') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')


def main():
    assert not OUT.exists() and not LEDGER.exists()
    evidence = json.loads((BASE / 'review.json').read_text())
    for path, expected in evidence['hashes'].items():
        assert file_hash(ROOT / path) == expected, path
    text = RAW.read_text(encoding='utf-8')
    assert 'COPYRIGHT, 1923, BY\nD. APPLETON AND COMPANY' in text
    span = dict(excerpt(text, 'On the third day after the ball, as Nanny',
                        '\n\nHe was rewarded by a gracious answer'), rights_record_id=RID)
    assert 'it cannot turn a small income into a large one.' in span['text']
    old = read_jsonl(OLD_LEDGER)
    entry = copy.deepcopy(old[-1])
    entry.update(id=RID, work_id='the-watsons-austen-fragment',
                 title='The Watsons — original visit scene', author_ids=['jane-austen'],
                 contributors=[dict(name='Jane Austen', role='author of included original fiction',
                                    life_dates='1775–1817')],
                 publication=dict(original_year=1871,
                                  edition='PG63569 transcription of D. Appleton and Company, New York, 1923. Uses only the Austen-authored passage corroborated by Bodleian MS. Eng. e.3764, b7-4 to b7-7. Print wording and punctuation retained.',
                                  publisher='Project Gutenberg digital transcription of D. Appleton and Company',
                                  evidence=[CATALOGUE, HEADNOTE, *PAGES]),
                 review=dict(status='approved', reviewer='Codex AI: exact edition and authorship assessment',
                             reviewed_on='2026-11-03',
                             notes='Bounded AI evidence assessment for local GB/US training preparation. Manuscript comparisons establish scene attribution and do not supply training text.'))
    entry['source'].update(url='https://www.gutenberg.org/cache/epub/63569/pg63569.txt',
                           raw_path=str(RAW.relative_to(ROOT / 'rights')),
                           sha256=file_hash(RAW), revision='sha256:' + file_hash(RAW),
                           included_material=f"Only LF-normalized codepoint interval {span['start']}:{span['end']} as input context.",
                           excluded_material='Oulton continuation, Austen-Leigh introduction, all other text, layout, images, provider material and modern manuscript transcriptions.',
                           terms_evidence=[CATALOGUE, 'https://www.gutenberg.org/policy/license.html',
                                           'https://www.gutenberg.org/policy/terms_of_use.html'])
    entry['clearances'] = [
        dict(jurisdiction='GB', uses=['training'],
             basis='Original Austen text published in 1871 and Austen died in 1817. Ordinary life-plus-70 term elapsed. Later continuation and layout excluded.',
             evidence=[CATALOGUE, HEADNOTE, 'https://www.gov.uk/copyright/how-long-copyright-lasts']),
        dict(jurisdiction='US', uses=['training'],
             basis='Original text published in 1871 and the exact print edition dates to 1923. Catalogue identifies US public domain.',
             evidence=[CATALOGUE, HEADNOTE, 'https://www.copyright.gov/circs/circ15a.pdf']),
    ]
    original = read_jsonl(BASE / 'records.review-only.jsonl')
    rows = copy.deepcopy(original)
    woolf = next(row for row in rows if row['id'] == 'v32-virginia-woolf-criticism')
    old_target = woolf['messages'][-1]['content']
    woolf['id'] = 'v33-watsons-woolf-close-reading'
    woolf['messages'][0]['content'] = (
        'Read the supplied passage from Jane Austen’s The Watsons. Reproduce Virginia Woolf’s published interpretation of how the timing of the call and the ensuing dialogue create suspense about Emma’s behavior. '
        'The critic’s retelling uses Mary for the servant and Musgrove for the visitor; this edition uses Nanny and Musgrave. Preserve the published criticism as written.\n\nPASSAGE:\n' + span['text'])
    woolf['source_work_ids'].append(entry['work_id'])
    woolf['rights_record_ids'].append(RID)
    woolf['source_spans'].append(span)
    woolf['content_hash'] = digest(woolf['messages'])
    assert woolf['messages'][-1]['content'] == old_target
    for row in rows:
        row['dataset_version'] = 'watsons-v33-review'
    OUT.mkdir()
    write_rows(LEDGER, old + [entry])
    dataset = OUT / 'records.review-only.jsonl'
    write_rows(dataset, rows)
    write_rows(OUT / 'scope.jsonl', [span])
    require_distinct_source_spans(rows, load_ledger(LEDGER))
    checked = validate_dataset(dataset, LEDGER, ['GB', 'US'],
                               benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    assert len(checked) == 58 and sum(r['split'] == 'train' for r in checked) == 42
    with (OUT / 'review.json').open('x') as stream:
        json.dump(dict(replaces='v32-virginia-woolf-criticism', answer_unchanged=True,
                       context_words=len(span['text'].split()), training_records=42,
                       exposed_monitors=16, training_started=False,
                       hashes={str(p.relative_to(ROOT)): file_hash(p) for p in
                               (Path(__file__), RAW, OLD_LEDGER, LEDGER, dataset, OUT / 'scope.jsonl')}),
                  stream, indent=2)
        stream.write('\n')
    print(f'Validated the Austen/Woolf pair with {len(span["text"].split())} source-context words.')


if __name__ == '__main__':
    main()
