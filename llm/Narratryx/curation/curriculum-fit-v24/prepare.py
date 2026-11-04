"""Prepare an exact-source review proposal only. No training or model calls."""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import digest, file_hash, read_jsonl

OUT = ROOT / 'artifacts/curriculum-fit-v24'
LEDGER = ROOT / 'rights/curriculum-fit-v24.scoped.jsonl'


def write_json(path, value):
    with path.open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')


def write_rows(path, rows):
    with path.open('x') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def prepare():
    assert not OUT.exists() and not LEDGER.exists(), 'Refuse overwrite'
    prior = json.loads((ROOT / 'artifacts/source-expansion-v23/verification.json').read_text())
    protected = dict(prior['protected_hashes'])
    for folder in ['curation/source-expansion-v23', 'artifacts/source-expansion-v23', 'evaluation', 'configs']:
        for p in (ROOT / folder).rglob('*'):
            if p.is_file() and '__pycache__' not in p.parts:
                protected[str(p.relative_to(ROOT))] = file_hash(p)
    for name in ['rights/source-expansion-v23.scoped.jsonl', 'docs/source-expansion-v23-2026-11-02.md', 'artifacts/source-candidates-v20/records.proposed.jsonl']:
        protected[name] = file_hash(ROOT / name)
    # Read prior proofs before preparing; fail if an already protected input drifted.
    for name, expected in prior['protected_hashes'].items():
        assert file_hash(ROOT / name) == expected, name
    OUT.mkdir()
    old = read_jsonl(ROOT / 'artifacts/source-expansion-v23/candidates.jsonl')
    records = [copy.deepcopy(q) for q in old if q['id'] != 'v23-james-reaction-revision']
    review = dict(status='approved', reviewer='Codex AI: exact-source curriculum fit and scoped rights evidence review', reviewed_on='2026-11-02', notes='AI preparation review only, not human literary approval or legal certification. Prospective training membership; no training, publication or model promotion.')
    spans = []
    for year in ['1881', '1908']:
        text = (ROOT / f'rights/raw/source-expansion-2026-11-02/james-{year}-reaction.verified.txt').read_text()
        marker = 'She had promised him'
        assert text.count(marker) == 1
        start = text.index(marker)
        end = len(text.rstrip())
        spans.append(dict(rights_record_id=f'james-{year}-reaction-v23', start=start, end=end, text=text[start:end]))
    template = copy.deepcopy(next(q for q in old if q['task'] == 'editing'))
    template.update(id='v24-james-concise-revision', source_spans=spans, review=review,
                    rubric=['source fidelity', 'instruction alignment', 'modest concision', 'psychological nuance'])
    template['messages'] = [dict(role='user', content='Revise this period psychological narration into at most 90 words. Preserve the apparent promise to consider the proposal, the bench meditation, her actual self-questioning and her frightened return to the house. The woman is Isabel; Lord Warburton has proposed. Allow stylistic and tonal revision, including a sharper self-judgement, rather than minimal copyediting. Return only revised prose.\n\nPASSAGE:\n' + spans[0]['text']), dict(role='assistant', content=spans[1]['text'])]
    records.append(template)
    text = (ROOT / 'rights/raw/curriculum-fit-2026-11-02/pg844.txt').read_text()
    turns = list(re.finditer(r'(?m)^([A-Z][A-Z .]+)\.\n', text))
    specs = [
        ('v24-wilde-case', 'JACK.\nI am quite aware of the fact,', 'Write exactly four dialogue turns, Jack and Algernon alternating, with speaker labels and no narration or stage directions. In a period comedy Jack wants his cigarette case back; Algernon challenges his claim because its inscription names Cecily, whom Jack said he did not know. Jack claims she is his aunt; Algernon reacts with disbelief. Keep Jack’s explanation a character claim, not a verified fact or a completed return of the case. Return only the exchange, at most 90 words including labels.'),
        ('v24-wilde-weather', 'JACK.\nCharming day it has been, Miss Fairfax.', 'Write exactly four dialogue turns alternating Jack and Gwendolen, with speaker labels and no narration or stage directions. Use period romantic comedy and subtext: Jack opens with the weather; Gwendolen suspects another meaning and says that makes her nervous; he admits another meaning; she confidently says she knew. Do not add a proposal, acceptance or resolution. Return only the exchange, at most 65 words including labels.'),
    ]
    wilde_spans = []
    for record_id, marker, prompt in specs:
        assert text.count(marker) == 1
        start = text.index(marker)
        index = next(i for i, match in enumerate(turns) if match.start() == start)
        end = turns[index + 4].start()
        while text[end - 1].isspace():
            end -= 1
        span = dict(rights_record_id='wilde-earnest-pg844-v24', start=start, end=end, text=text[start:end])
        assert '[' not in span['text'] and ']' not in span['text']
        wilde_spans.append(span)
        records.append(dict(schema_version='1.0', id=record_id, dataset_version='curriculum-fit-v24-review', task='dialogue', split='train', split_group='importance-of-being-earnest', origin='derived', messages=[dict(role='user', content=prompt), dict(role='assistant', content=span['text'])], source_work_ids=['importance-of-being-earnest'], rights_record_ids=['wilde-earnest-pg844-v24'], source_spans=[span], teacher=None, review=review, rubric=['source fidelity', 'four dialogue-only turns', 'subtext', 'character claims versus facts']))
    for row in records:
        row['dataset_version'] = 'curriculum-fit-v24-review'
        row['content_hash'] = digest(row['messages'])
    write_json(OUT / 'wilde-scope.json', wilde_spans)
    ledger = read_jsonl(ROOT / 'rights/source-expansion-v23.scoped.jsonl')
    q = copy.deepcopy(next(q for q in ledger if q['id'] == 'dunbar-st-rocque-pg688-v23'))
    q.update(id='wilde-earnest-pg844-v24', work_id='importance-of-being-earnest', title='The Importance of Being Earnest — two four-turn dialogue passages', author_ids=['oscar-wilde'], contributors=[dict(name='Oscar Wilde', role='author of selected original dramatic dialogue only', life_dates='1854–1900')], review=review)
    q['publication'] = dict(original_year=1899, edition='Pinned PG844 digital text; last-update header10November2025. University College Oxford collection account corroborates1899 publication. Exact physical copy behind PG is unidentified; not a facsimile or modern annotated edition.', publisher='Project Gutenberg digital transcription; historical publication in1899', evidence=['https://www.gutenberg.org/ebooks/844', 'https://www.univ.ox.ac.uk/news/the-importance-of-being-earnest/'])
    raw = ROOT / 'rights/raw/curriculum-fit-2026-11-02/pg844.txt'
    q['source'].update(url='https://www.gutenberg.org/cache/epub/844/pg844.txt', raw_path=str(raw.relative_to(ROOT / 'rights')), sha256=file_hash(raw), revision='sha256:' + file_hash(raw), included_material='Only two exact LF-normalized intervals in artifacts/curriculum-fit-v24/wilde-scope.json, SHA256 ' + file_hash(OUT / 'wilde-scope.json') + '. No whole-play clearance.', excluded_material='All other dialogue, stage directions, cast lists, headings, notices, branding, catalogue summary, modern apparatus and third-party material. David Price credit and original notices retained in raw bytes, not training targets.', terms_evidence=['https://www.gutenberg.org/ebooks/844', 'https://www.gutenberg.org/policy/permission.html', 'https://www.gutenberg.org/policy/terms_of_use.html', 'https://www.gutenberg.org/policy/license.html'], terms_decision='AI assessment supports private local GB/US training preparation on these unbranded expired original dramatic passages without an individual grant. Item catalogue and embedded standard licence checked. No whole digital artifact redistribution, trademark use, upload or publication authorised. Website terms restrict automated access: this retained single-item acquisition is not an automated bulk-ingestion permission; no repeat acquisition or crawler is supplied.', notices='Complete original acquired PG header/footer/licence retained; no special copyright-holder grant appears in selected original dialogue. Exact physical print source remains unidentified.')
    q['clearances'] = [dict(jurisdiction='GB', uses=['training'], basis='Wilde died1900; ordinary life-plus-70 dramatic term elapsed by end1970. Work published1899; selected original dialogue only, excluding modern additions and printed layout.', evidence=['https://www.gutenberg.org/ebooks/844', 'https://www.univ.ox.ac.uk/news/the-importance-of-being-earnest/', 'https://www.gov.uk/copyright/how-long-copyright-lasts']), dict(jurisdiction='US', uses=['training'], basis='PG844 item-specific US public-domain statement and1899 publication beyond historical maximum95-year term; no modern independent additions included.', evidence=['https://www.gutenberg.org/ebooks/844', 'https://www.univ.ox.ac.uk/news/the-importance-of-being-earnest/', 'https://www.copyright.gov/circs/circ15a.pdf'])]
    ledger.append(q)
    write_rows(LEDGER, ledger)
    write_rows(OUT / 'candidates.jsonl', records)
    parents = read_jsonl(ROOT / 'artifacts/source-candidates-v20/records.proposed.jsonl')
    proposal = [dict(q, dataset_version='curriculum-fit-v24-review') for q in parents] + records
    write_rows(OUT / 'records.review-only.jsonl', proposal)
    decisions = dict(retain=[q['id'] for q in records[:3]], replace=dict(reserved='v23-james-reaction-revision', selected='v24-james-concise-revision', mutually_exclusive=True, reason='Same source/revision family; suffix is91→87words, modest4.4percent compression. Do not sample both.'), add=[q['id'] for q in records[-2:]], limits=['Historical comic dialogue, not modern practical negotiation or physical-testing supervision.', 'James is an existing scoped-source derivative, not new author diversity or proof of literary improvement.', 'All six are prospective source lessons; no executable recipe, installed trainer audit or training run.', 'Evaluation responses and AI review annotations are excluded from training.'])
    write_json(OUT / 'selection.json', decisions)
    packet = ['# Six source-backed review candidates', '', 'Preparation only. AI briefs; exact published answers. No human approval, training or quality claim.', '']
    for row in records:
        packet += ['## ' + row['id'], '', row['messages'][0]['content'], '', '### Source-derived answer', '', row['messages'][-1]['content'], '']
    (OUT / 'REVIEW.md').write_text('\n'.join(packet))
    inputs = [LEDGER, Path(__file__), ROOT / 'curation/curriculum-fit-v24/verify.py', ROOT / 'curation/curriculum-fit-v24/preflight.py']
    for folder in ['rights/raw/curriculum-fit-2026-11-02', 'rights/evidence/curriculum-fit-2026-11-02']:
        inputs += [p for p in (ROOT / folder).iterdir() if p.is_file()]
    for year in ['1881', '1908']:
        inputs.append(ROOT / f'rights/raw/source-expansion-2026-11-02/james-{year}-reaction.verified.txt')
    write_json(OUT / 'preparation.lock.json', dict(protected_hashes=protected, input_hashes={str(p.relative_to(ROOT)): file_hash(p) for p in inputs}, output_hashes={p.name: file_hash(p) for p in OUT.iterdir() if p.is_file()}, training=False, inference_requests=0))
    print('Prepared6 candidates and34train+16exposed-monitor review-only records; no training.')


if __name__ == '__main__':
    prepare()
