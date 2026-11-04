"""Validate four new scan-derived examples and combine them with six AI-reviewed scenes."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import (Invalid, check_leakage, digest, load_ledger,
                                   read_jsonl, validate_dataset, validate_schema)

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('source_tools', HERE.parent / 'independent-scenes-v1/prepare.py')
TOOLS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TOOLS)
RAW = ROOT / 'rights/raw/independent-expansion-2026-10-26'
OUT = ROOT / 'artifacts/independent-curriculum-v1'
LEDGER = ROOT / 'rights/independent-curriculum-v1.scoped.jsonl'
SOURCES = {
    'harper-1893': dict(item='09509719.4821.emory.edu', work='iola-leroy',
                       title='Iola Leroy; or, Shadows Uplifted — selected Chapter I prose',
                       name='Frances Ellen Watkins Harper', author='frances-ew-harper',
                       dates='1825–1911', first_year=1892, edition_year=1893,
                       edition='Second edition, Garrigues Brothers, 608 Arch Street, Philadelphia, 1893; title page scan leaf5',
                       publisher='Garrigues Brothers, Philadelphia',
                       bio='https://lccn.loc.gov/n50026651', pages='printed pp8–10, scan leaves16–18'),
    'wilson': dict(item='ournigorsketches00wilsrich', work='our-nig',
                   title='Our Nig; or, Sketches from the Life of a Free Black — selected original prose',
                   name='Harriet E. Wilson', author='harriet-e-wilson', dates='1825–1900',
                   first_year=1859, edition_year=1859,
                   edition='Boston, printed by Geo. C. Rand & Avery, 1859; title page scan leaf7',
                   publisher='Geo. C. Rand & Avery, Boston',
                   bio='https://www.loc.gov/item/2005577156/', pages='printed pp9–10 and105, scan leaves15–16 and111'),
}
BRIEFS = {
    'harper-market': ('dialogue', 'Write a historical-fiction exchange as Robert and Tom meet other enslaved men returning from market during the American Civil War. Let apparently cheerful talk about fresh fish and eggs carry coded good news, with the long faces at the post office as a contrasting clue. Preserve the historical dialect as these particular characters’ speech; show reciprocal responses without an explanatory afterword.'),
    'harper-newspaper': ('dialogue', 'Write a historical-fiction exchange between Robert, who brings newspapers and news of a Union victory, and Linda, who cannot read the papers but reads their mistress’s expression. Retain the characters’ historical speech and opposing interests within the household. Let Linda ask whether the Yankees have horns and have Robert dismiss that rumour, without a narrator’s factual endorsement of it.'),
    'wilson-help': ('dialogue', 'Write a period exchange in which Jim asks Mag about her earnings. Let her fear of starvation and rejection draw a practical promise of support from his barrel-making work; finish with her softened but still wounded response. Preserve these characters’ historical speech and brief emotional narration.'),
    'wilson-resistance': ('pacing', 'Write a period scene in which Frado is collecting wood and Mrs. Bellmont raises a stick to strike her. Accelerate through Frado’s shouted refusal and physical defiance, then slow to show the mistress dropping the weapon, carrying the wood herself, and Frado recognising a new power to resist. Keep this as the outcome of this particular scene, without general advice or invented later consequences.'),
}


def source_material():
    lock = json.loads((HERE / 'source-lock.json').read_text())
    TOOLS.verify_files(ROOT, lock['files'])
    segments = json.loads((RAW / 'transcriptions.json').read_text())
    texts = {source: (RAW / f'{source}.verified.txt').read_text() for source in SOURCES}
    TOOLS.verify_segments(segments, texts)
    images = {(i['source'], i['leaf']) for i in lock['images'] if 'error' not in i}
    if set(BRIEFS) != {s['id'] for s in segments}:
        raise Invalid('briefs must cover exactly the selected source segments')
    for segment in segments:
        if any((segment['source'], leaf) not in images for leaf in segment['leaves']):
            raise Invalid('unbound scan transcription')
    return lock, segments


def new_rights(segments):
    template = read_jsonl(TOOLS.LEDGER)[0]
    rows = []
    for source, info in SOURCES.items():
        row = copy.deepcopy(template)
        url = 'https://archive.org/details/' + info['item']
        selected = [s for s in segments if s['source'] == source]
        row.update(id=source + '-independent-expansion-v1', work_id=info['work'],
                   title=info['title'], author_ids=[info['author']],
                   contributors=[dict(name=info['name'], role='author of selected original prose', life_dates=info['dates'])],
                   publication=dict(original_year=info['first_year'], edition=info['edition'],
                                    publisher=info['publisher'], evidence=[url, info['bio']]))
        row['source'] = dict(url=url, retrieved_on='2026-10-26',
                            revision='sha256:' + TOOLS.sha(RAW / f'{source}.verified.txt'),
                            raw_path=f'raw/independent-expansion-2026-10-26/{source}.verified.txt',
                            sha256=TOOLS.sha(RAW / f'{source}.verified.txt'),
                            included_material=info['pages'] + '; only canonical spans ' + ', '.join(
                                f'{s["id"]} {s["start"]}:{s["end"]}' for s in selected)
                                + '. Hashes and original scan/OCR bindings in curation/independent-expansion-v1/source-lock.json.',
                            excluded_material='All other text, prefaces, introductions by other authors, appendices, letters, poems, epigraphs, illustrations, captions, site apparatus, modern additions and layout. Undated Earle third edition of Harper is discovery-only and excluded.',
                            terms_evidence=[url, info['bio']],
                            terms_decision='Selected expired historical author prose only, private GB/US preparation, training and evaluation. No upload, publication or scan redistribution authorised. Wilson archive says NOT_IN_COPYRIGHT; Harper archive description explicitly identifies the Emory digital edition as public domain. These signals corroborate author dates and inspected historical edition, not whole-corpus clearance. Full IA site terms were not retrieved; no claim of a complete terms review.',
                            notices='Original OCR and notices retained locally. Canonical transcription is AI-checked against original images, with layout, contraction spacing and quotation glyph normalization; dialect/spelling retained, not a modern scholarly transcription.')
        row['clearances'] = [
            dict(jurisdiction='GB', uses=['training', 'evaluation'],
                 basis=f'{info["name"]} died {info["dates"].split("–")[-1]}; ordinary life-plus-70 term elapsed. Selected prose published in inspected {info["edition_year"]} edition, before1989. No separately authored contributions or previously unpublished modern material included.',
                 evidence=['https://www.gov.uk/copyright/how-long-copyright-lasts', info['bio'], url]),
            dict(jurisdiction='US', uses=['training', 'evaluation'],
                 basis=f'Original selected prose published in the US by {info["edition_year"]}, beyond the historical maximum95-year term. No new literary contributions included.',
                 evidence=['https://www.copyright.gov/circs/circ15a.pdf', url]),
        ]
        row['review'] = dict(status='approved', reviewer='Codex AI: scoped original-prose evidence assessment',
                             reviewed_on='2026-10-26', notes='AI assessment only, not human approval or legal certification. Exact selected prose and private GB/US uses; no whole-book or image redistribution clearance. No model training or promotion performed.')
        validate_schema(row, 'rights-record')
        rows.append(row)
    return rows


def new_examples(segments):
    rows = []
    for segment in segments:
        task, brief = BRIEFS[segment['id']]
        info = SOURCES[segment['source']]
        rid = segment['source'] + '-independent-expansion-v1'
        row = dict(schema_version='1.0', id=segment['id'], dataset_version='independent-curriculum-v1',
                   task=task, split='train', split_group=info['work'], origin='derived', teacher=None,
                   messages=[dict(role='user', content=brief + ' Return only the passage.'),
                             dict(role='assistant', content=segment['text'])],
                   source_work_ids=[info['work']], rights_record_ids=[rid],
                   source_spans=[dict(rights_record_id=rid, start=segment['start'], end=segment['end'], text=segment['text'])],
                   review=dict(status='approved', reviewer='Codex AI: scan transcription and instruction alignment review',
                               reviewed_on='2026-10-26', notes='Informed AI assessment, not independent/human literary-quality approval. Selected passage visually checked against original images; complete response/action supports the constructed brief. Literary answer is transcribed original prose, not AI-generated teaching prose. Historical language is attributed to these characters/narrator, not universal advice. Instructions were constructed after reading the source. Not yet used in training.'),
                   rubric=['source fidelity', 'instruction alignment', 'narrative coherence'], content_hash='')
        row['content_hash'] = digest(row['messages'])
        validate_schema(row, 'dataset-record')
        rows.append(row)
    return rows


def verify():
    TOOLS.verify_files(ROOT, json.loads((HERE / 'packet-lock.json').read_text())['files'])
    rows = validate_dataset(OUT / 'records.jsonl', LEDGER, ['GB', 'US'])
    ledger = load_ledger(LEDGER)
    for row in rows:
        if row['origin'] != 'derived' or row['teacher'] is not None or row['messages'][-1]['content'] != row['source_spans'][-1]['text']:
            raise Invalid('generated or non-exact literary target')
    prior = []
    old = load_ledger(ROOT / 'rights/literary-mix-v2.scoped.jsonl')
    for rel in ['artifacts/literary-mix-v2/records.jsonl', 'artifacts/task-matched-v3/records.jsonl']:
        for row in read_jsonl(ROOT / rel):
            row['_author_ids'] = sorted({a for rid in row['rights_record_ids'] for a in old[rid]['author_ids']})
            prior.append(row)
    benchmark = read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl')
    for rel in ['artifacts/literary-mix-v2/test.cases.jsonl', 'artifacts/task-matched-v3/test.cases.jsonl']:
        benchmark += [dict(id=c['id'], split_group='diagnostic-' + c['scenario_id'], context=c['prompt'] + '\n' + c['context']) for c in read_jsonl(ROOT / rel)]
    check_leakage(rows + prior, benchmark)
    for row in rows:
        if any(row['messages'][-1]['content'] in m['content'] for old_row in prior for m in old_row['messages']):
            raise Invalid('answer reused from previous training/validation corpus')
    return dict(passed=True, examples=len(rows), new_expansion_examples=4,
                previously_reviewed_examples=6, independent_works=4, authors=4,
                rights_records=len(ledger), source_derived_answers_only=True,
                original_pack_status='draft, not release approved',
                prior_datasets_screened=2, evaluation_packs_screened=3,
                human_approvals=0, human_quality_ratings=0, trained=False,
                model_promoted=False, apps_changed=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'verify'])
    args = parser.parse_args()
    lock, segments = source_material()
    if args.command == 'build':
        if LEDGER.exists() or OUT.exists():
            raise Invalid('refusing to overwrite existing curriculum')
        TOOLS.verify_files(ROOT, json.loads((HERE.parent / 'independent-scenes-review-v1/review-lock.json').read_text())['files'])
        rows = read_jsonl(ROOT / 'artifacts/independent-scenes-reviewed-v1/records.jsonl')
        for row in rows:
            row['dataset_version'] = 'independent-curriculum-v1'
        rows += new_examples(segments)
        OUT.mkdir()
        TOOLS.write_rows(LEDGER, read_jsonl(TOOLS.LEDGER) + new_rights(segments))
        TOOLS.write_rows(OUT / 'records.jsonl', rows)
        lines = ['# Expanded source-derived curriculum', '', 'Ten AI-reviewed candidate examples from four works/authors. No human quality approval, training or model promotion.', '', '## New examples', '']
        for row in rows[6:]:
            segment = next(s for s in segments if s['id'] == row['id'])
            lines += [f'### {row["id"]} ({row["task"]})', '', row['messages'][0]['content'], '', row['messages'][1]['content'], '']
            for leaf in segment['leaves']:
                image = next(i for i in lock['images'] if i['source'] == segment['source'] and i['leaf'] == leaf)
                lines += [f'- [Original scan leaf {leaf}]({image["url"]})']
            lines += ['']
        lines += ['## Earlier selection', '', 'Five Hopkins examples and one James face revision retained. James dogs pair is reference-only. Original pending packet and decisions remain intact.', '']
        (OUT / 'REVIEW.md').write_text('\n'.join(lines))
        TOOLS.write_json(HERE / 'packet-lock.json', {'files': {str(p.relative_to(ROOT)): TOOLS.sha(p) for p in
            [LEDGER, OUT / 'records.jsonl', OUT / 'REVIEW.md', HERE.parent / 'independent-scenes-review-v1/decisions.json',
             ROOT / 'artifacts/independent-scenes-reviewed-v1/records.jsonl']}})
    report = verify()
    if args.command == 'build':
        TOOLS.write_json(OUT / 'verification.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
