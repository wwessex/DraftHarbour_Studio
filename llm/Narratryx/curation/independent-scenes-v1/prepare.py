"""Prepare a review-only, source-derived packet; never downloads, trains or approves it."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import (Invalid, check_leakage, clear_source, digest,
                                   load_ledger, read_jsonl, validate_dataset, validate_schema)

HERE = Path(__file__).resolve().parent
RAW = ROOT / 'rights/raw/independent-scenes-2026-10-26'
EVIDENCE = ROOT / 'rights/evidence/independent-scenes-2026-10-26'
OUT = ROOT / 'artifacts/independent-scenes-v1'
LEDGER = ROOT / 'rights/independent-scenes-v1.scoped.jsonl'
SOURCES = {
    'hopkins': ('contending-forces', 'contending-forces', 'Pauline E. Hopkins',
                'pauline-hopkins', '1859–1930', 1900,
                'The Colored Co-operative Publishing Co., Boston',
                'https://www.searchablemuseum.com/pauline-elizabeth-hopkins/'),
    'james-1881': ('portraitoflady01jamerich', 'portrait-of-a-lady', 'Henry James',
                   'henry-james', '1843–1916', 1881, 'Macmillan and Co., London',
                   'https://www.gutenberg.org/ebooks/2833'),
    'james-1908': ('portraitlady103jameuoft', 'portrait-of-a-lady', 'Henry James',
                   'henry-james', '1843–1916', 1908, 'Charles Scribner’s Sons, New York',
                   'https://www.gutenberg.org/ebooks/2833'),
}
BRIEFS = [
    ('hopkins-room', 'fiction', None,
     'Write a period domestic-fiction description of Sappho’s lodging as Dora first notices its transformation. Use the practical fabrics, improvised furniture and working typewriter to reveal how its occupant makes a temporary room welcoming.'),
    ('hopkins-embroidery', 'dialogue', None,
     'Write a complete exchange between Dora and Sappho about Sappho’s room and embroidery. Let warmth develop, then have Sappho offer to teach the skill while politely leaving unanswered where she learned it. Include brief narration that makes Dora notice the omission.'),
    ('hopkins-work', 'dialogue', None,
     'Write a period exchange in which Dora asks Sappho about her typewriting work. Let Sappho distinguish the work she likes from the frustrations of taking dictation, then offer Dora a chair. Include the physical setting without an explanatory afterword.'),
    ('hopkins-invitation', 'dialogue', None,
     'Write a playful, mock-formal invitation from Dora to Sappho for a Sunday lodging-house reception at half past seven, with refreshments at nine. Give Sappho a matching acceptance and end with Dora leaving to prepare. Keep the period social register and brief physical actions.'),
    ('hopkins-host', 'storytelling', None,
     'Write two sentences of period social-fiction narration connecting Mrs. Smith’s opinion of her lodgers to her wish to make them happy together and her decision to have Dora organise musical evenings or receptions. Present the social judgements as this historical narrator’s perspective.'),
    ('james-face-1908', 'editing', 'james-face-1881',
     'Make a stylistic revision of this period character description. Recast the distribution of the features, let the narrator consider what the face represents, and vary the contrast about success while retaining the description’s restrained irony. Allow that interpretive nuance; this is not minimal error correction.'),
    ('james-dogs-1908', 'editing', 'james-dogs-1881',
     'Revise only the master’s act of looking at the house, using a lighter phrasal verb in place of the more formal verb. Retain the collie’s attention, the comparison with the house, the terrier and the rest of the sentence.'),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_files(root: Path, files: dict) -> None:
    for relative, expected in files.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()) or sha(path) != expected:
            raise Invalid(f'pinned source/evidence mismatch: {relative}')


def verify_segments(segments: list[dict], texts: dict[str, str]) -> None:
    seen = set()
    for source, text in texts.items():
        cursor = 0
        for row in [s for s in segments if s['source'] == source]:
            if row['id'] in seen:
                raise Invalid('duplicate transcription segment')
            seen.add(row['id'])
            start, end = row['start'], row['end']
            if (start < cursor or not start < end <= len(text)
                    or text[start:end] != row['text']
                    or text[cursor:start] not in ('', '\n\n')):
                raise Invalid('non-exact, overlapping or discontinuous canonical span')
            cursor = end
        if text[cursor:] != '\n':
            raise Invalid('unscoped canonical material')
    if len(seen) != len(segments):
        raise Invalid('unknown transcription source')


def write_json(path: Path, value) -> None:
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def write_rows(path: Path, rows) -> None:
    with path.open('x', encoding='utf-8') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')


def sources_and_segments():
    lock = json.loads((HERE / 'source-lock.json').read_text())
    verify_files(ROOT, lock['files'])
    texts = {source: (RAW / f'{source}.verified.txt').read_text() for source in SOURCES}
    segments = json.loads((RAW / 'transcriptions.json').read_text())
    verify_segments(segments, texts)
    images = {(i['source'], i['leaf']): i for i in lock['images']}
    for segment in segments:
        for leaf in segment['leaves']:
            if (segment['source'], leaf) not in images:
                raise Invalid('transcription has no pinned scan image')
    return lock, texts, segments


def rights_rows(texts, segments):
    rows = []
    for source, (item, work, name, author, dates, year, publisher, bio) in SOURCES.items():
        url = f'https://archive.org/details/{item}'
        metadata = json.loads((EVIDENCE / f'{source}-metadata.json').read_text())['metadata']
        if str(metadata['date']) != str(year):
            raise Invalid('edition year mismatch')
        mark = metadata.get('licenseurl')
        if source == 'james-1881':
            if metadata.get('possible-copyright-status') != 'NOT_IN_COPYRIGHT':
                raise Invalid('missing original archive rights signal')
        elif not mark or 'publicdomain' not in mark:
            raise Invalid('missing original archive rights signal')
        selected = [s for s in segments if s['source'] == source]
        row = dict(
            schema_version='1.0', id=f'{source}-independent-scenes-v1', work_id=work,
            title='Contending Forces: selected Chapter VI prose' if source == 'hopkins'
                  else 'The Portrait of a Lady, Volume I: selected opening prose',
            source_kind='public_domain_candidate', author_ids=[author],
            contributors=[dict(name=name, role='author of included original prose', life_dates=dates)],
            publication=dict(original_year=year, edition=f'{year} original scan, IA {item}; selected spans only, not a modern reprint',
                             publisher=publisher, evidence=[url, bio]),
            source=dict(url=url, retrieved_on='2026-10-26', revision='sha256:' + sha(RAW / f'{source}.verified.txt'),
                        raw_path=f'raw/independent-scenes-2026-10-26/{source}.verified.txt',
                        sha256=sha(RAW / f'{source}.verified.txt'),
                        included_material='Only AI scan-transcribed segments ' + ', '.join(
                            f'{s["id"]} {s["start"]}:{s["end"]}' for s in selected)
                            + '. Canonical UTF-8 code-point offsets; source-lock.json binds original OCR, metadata and scan images.',
                        excluded_material='All other prose, epigraphs, verse, scripture, front matter, illustrations, captions, layout, site material and modern additions. Downloaded evidence is never a teaching target.',
                        terms_evidence=[url] + ([mark] if mark else []),
                        terms_decision='Selected expired historical prose only, private GB/US preparation, training and evaluation. Archive public-domain metadata corroborates the historical evidence but is not the sole basis. No redistribution, upload or publication authorised. Full site terms could not be retrieved; no claim that they were fully reviewed or that the scan images themselves have been licensed for redistribution.',
                        notices='Original notices and OCR retained locally. Transcriptions made from scanned original pages, not a modern scholarly electronic edition; no artwork is included.'),
            clearances=[
                dict(jurisdiction='GB', uses=['training', 'evaluation'],
                     basis=f'Original prose published {year}, before 1989; {name} died {dates.split("–")[-1]}, so ordinary life-plus-70 term expired. Only this named author’s selected prose is included; no previously unpublished modern text or other contributor material.',
                     evidence=['https://www.gov.uk/copyright/how-long-copyright-lasts', bio, url]),
                dict(jurisdiction='US', uses=['training', 'evaluation'],
                     basis=f'Original prose published {year}; applicable historical maximum 95-year term has elapsed. Archive item also marked public domain/not in copyright. No new literary additions included.',
                     evidence=['https://www.copyright.gov/circs/circ15a.pdf', url]),
            ], unresolved_issues=[],
            review=dict(status='approved', reviewer='Codex AI: scoped original-prose rights evidence assessment',
                        reviewed_on='2026-10-26', notes='AI evidence assessment, not human approval or legal certification. Restricted to exact selected author prose and GB/US private uses. Historical edition variants do not prove authorship of each punctuation change. Dataset examples remain pending review and outside training.'))
        validate_schema(row, 'rights-record')
        rows.append(row)
    return rows


def draft_rows(segments):
    index = {s['id']: s for s in segments}
    records = []
    for ident, task, original, brief in BRIEFS:
        target = index[ident]
        used = ([index[original]] if original else []) + [target]
        prompt = brief + ' Return only the passage, without a heading or explanation.'
        if original:
            prompt += '\n\nPASSAGE:\n' + index[original]['text']
        rights = sorted({f'{s["source"]}-independent-scenes-v1' for s in used})
        row = dict(schema_version='1.0', id=ident, dataset_version='independent-scenes-v1',
                   task=task, split='train', split_group=SOURCES[target['source']][1], origin='derived',
                   messages=[dict(role='user', content=prompt), dict(role='assistant', content=target['text'])],
                   source_work_ids=[SOURCES[target['source']][1]], rights_record_ids=rights,
                   source_spans=[dict(rights_record_id=f'{s["source"]}-independent-scenes-v1',
                                      start=s['start'], end=s['end'], text=s['text']) for s in used],
                   teacher=None,
                   review=dict(status='pending', reviewer=None, reviewed_on=None,
                               notes='Prospective train split only; not training authorisation. Review transcription accuracy, task fit and sampling value. Task brief constructed by AI after reading source; literary answer copied from scan transcription. James edition variants are stylistic alternatives, not a universal preference or minimal copyedit.'),
                   rubric=['source fidelity', 'instruction alignment', 'narrative coherence'],
                   content_hash='')
        row['content_hash'] = digest(row['messages'])
        validate_schema(row, 'dataset-record')
        records.append(row)
    return records


def audit(records, segments):
    ledger = load_ledger(LEDGER)
    texts = {r: clear_source(v, LEDGER, ['GB', 'US'], 'training') for r, v in ledger.items()}
    for row in records:
        validate_schema(row, 'dataset-record')
        if row['review']['status'] != 'pending' or row['teacher'] is not None or row['content_hash'] != digest(row['messages']):
            raise Invalid('review-only or source-derived gate changed')
        for span in row['source_spans']:
            if texts[span['rights_record_id']][span['start']:span['end']] != span['text']:
                raise Invalid('source span mismatch')
        if row['messages'][-1]['content'] != row['source_spans'][-1]['text']:
            raise Invalid('literary answer is not exact source text')
        row['_author_ids'] = sorted({a for rid in row['rights_record_ids'] for a in ledger[rid]['author_ids']})
    prior = []
    old_ledger = load_ledger(ROOT / 'rights/literary-mix-v2.scoped.jsonl')
    for relative in ('artifacts/literary-mix-v2/records.jsonl', 'artifacts/task-matched-v3/records.jsonl'):
        for row in read_jsonl(ROOT / relative):
            row['_author_ids'] = sorted({a for rid in row['rights_record_ids'] for a in old_ledger[rid]['author_ids']})
            prior.append(row)
    check_leakage(records + prior)
    # The original formal pack is still a draft; do not imply it was approved.
    benchmark = read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl')
    for relative in ('artifacts/literary-mix-v2/test.cases.jsonl', 'artifacts/task-matched-v3/test.cases.jsonl'):
        for case in read_jsonl(ROOT / relative):
            benchmark.append(dict(id=case['id'], split_group='diagnostic-' + case['scenario_id'],
                                  context=case['context'] + '\n' + case['prompt']))
    check_leakage(records, benchmark)
    for row in records:
        answer = row['messages'][-1]['content']
        if any(answer in m['content'] for old in prior for m in old['messages']):
            raise Invalid('new answer already present in prior datasets')
    try:
        validate_dataset(OUT / 'draft.records.jsonl', LEDGER, ['GB', 'US'])
    except Invalid as exc:
        if 'review status is pending' not in str(exc):
            raise
    else:
        raise Invalid('draft incorrectly accepted for training')
    return dict(passed=True, draft_examples=len(records), source_segments=len(segments),
                independent_works=2, authors=2, source_records=3,
                generated_literary_targets=0, new_training_runs=0, human_approval_recorded=False,
                release_dataset_validation='correctly rejected: example review pending',
                prior_datasets_screened=2, evaluation_packs_screened=3,
                original_formal_pack_status='draft, not release approved',
                exact_source_answers=True, prior_answer_reuse=False,
                apps_changed=False, model_promoted=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'verify'])
    args = parser.parse_args()
    _, texts, segments = sources_and_segments()
    if args.command == 'build':
        if OUT.exists() or LEDGER.exists():
            raise Invalid('refusing to overwrite a review packet or scoped ledger')
        rights = rights_rows(texts, segments)
        records = draft_rows(segments)
        OUT.mkdir(parents=True)
        write_rows(LEDGER, rights)
        write_rows(OUT / 'draft.records.jsonl', records)
        images = json.loads((HERE / 'source-lock.json').read_text())['images']
        lines = ['# Independent scenes — review packet', '',
                 'Seven pending examples; two works/authors. AI scan transcription and scoped rights assessment, no human approval. Not included in training.', '',
                 'Instructions were constructed after reading the source. Answers are historical prose, not generated teaching targets. James pairs show edition variants; later does not automatically mean better. No editing minimum length.', '']
        for row in records:
            lines += [f'## {row["id"]} ({row["task"]})', '', row['messages'][0]['content'], '',
                      '### Source-derived answer', '', row['messages'][1]['content'], '', '### Scan evidence', '']
            for segment in [s for s in segments if any(s['text'] == p['text'] for p in row['source_spans'])]:
                for leaf in segment['leaves']:
                    image = next(i for i in images if i['source'] == segment['source'] and i['leaf'] == leaf)
                    lines += [f'- [{segment["source"]}, scan leaf {leaf}]({image["url"]})']
            lines += ['', 'Review: transcription / task fit / accept, revise or exclude. No decision recorded.', '']
        (OUT / 'REVIEW.md').write_text('\n'.join(lines), encoding='utf-8')
        write_json(HERE / 'packet-lock.json', {'files': {str(p.relative_to(ROOT)): sha(p) for p in
                   [LEDGER, OUT / 'draft.records.jsonl', OUT / 'REVIEW.md']}})
    verify_files(ROOT, json.loads((HERE / 'packet-lock.json').read_text())['files'])
    report = audit(read_jsonl(OUT / 'draft.records.jsonl'), segments)
    if args.command == 'build':
        write_json(OUT / 'verification.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
