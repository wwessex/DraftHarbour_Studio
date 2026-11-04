"""Prepare a bounded experiment, never train or replace a model."""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import (Invalid, check_leakage, digest, load_ledger,
                                   read_jsonl, validate_dataset, validate_schema)
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'artifacts/revision-preflight-v1'
LEDGER = ROOT / 'rights/revision-preflight-v1.scoped.jsonl'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def save_rows(path, rows):
    with path.open('x', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')


def verify_files(files):
    for relative, expected in files.items():
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT) or sha(path) != expected:
            raise Invalid('pinned input changed: ' + relative)


def balanced_subset(rows, count):
    groups = defaultdict(list)
    for row in rows:
        groups[tuple(row['source_work_ids'])].append(row)
    selected = []
    while len(selected) < count:
        before = len(selected)
        for key in sorted(groups):
            if groups[key] and len(selected) < count:
                selected.append(groups[key].pop(0))
        if len(selected) == before:
            raise Invalid('insufficient rows for fixed balanced quota')
    return selected


def new_record(ident, task, prompt, answer, spans, works):
    row = dict(schema_version='1.0', id=ident, dataset_version='revision-preflight-v1',
               task=task, split='train', split_group='revision-' + works[0], origin='derived',
               messages=[dict(role='user', content=prompt), dict(role='assistant', content=answer)],
               source_work_ids=works, rights_record_ids=[s['rights_record_id'] for s in spans],
               source_spans=spans, teacher=None,
               review=dict(status='approved', reviewer='Codex AI: original-prose alignment assessment',
                           reviewed_on='2026-10-26', notes='AI source/instruction assessment, not human approval, independent blind quality rating or legal certification. Literary answer is unchanged historical prose. Instructions constructed after reading the source. Structural/stylistic alternative, not minimal copyedit or a preference claiming newer is better. Prepared only; not trained.'),
               rubric=['source fidelity', 'instruction alignment', 'narrative coherence'], content_hash='')
    row['content_hash'] = digest(row['messages'])
    validate_schema(row, 'dataset-record')
    return row


def prepare():
    if OUT.exists() or LEDGER.exists():
        raise Invalid('refusing to overwrite preflight')
    source_lock = json.loads((HERE / 'source-lock.json').read_text())
    verify_files(source_lock['files'])
    old_path = ROOT / 'rights/literary-mix-v2.scoped.jsonl'
    old_data = ROOT / 'artifacts/task-matched-v3/records.jsonl'
    old = validate_dataset(old_data, old_path, ['GB', 'US'])
    trace = {r['id']: r for r in read_jsonl(ROOT / 'artifacts/task-matched-v3/trace.jsonl')}
    selected = []
    for kind, count in [('directed-write', 4), ('attributed-craft', 4), ('continue', 2),
                        ('paced-scene', 2), ('dialogue-scene', 2)]:
        selected += balanced_subset([r for r in old if r['split'] == 'train' and trace[r['id']]['kind'] == kind], count)
    selected += [next(r for r in old if r['id'] == ident) for ident in
                 ['v3-032-anchored-copyedit', 'v3-033-anchored-copyedit',
                  'v3-038-anchored-copyedit', 'v3-039-anchored-copyedit']]
    assert len(selected) == 18
    rows = copy.deepcopy(selected)
    origins = {r['id']: 'retained-v3' for r in rows}
    for row in rows:
        row.pop('_author_ids', None)
    fresh = read_jsonl(ROOT / 'artifacts/independent-curriculum-v1/records.jsonl')
    rows += fresh
    origins.update({r['id']: 'independent-curriculum-not-previously-trained' for r in fresh})
    ledger = list(load_ledger(old_path).values()) + list(load_ledger(ROOT / 'rights/independent-curriculum-v1.scoped.jsonl').values())
    # A newly scoped canonical transcription, not broader rights for the old opening spans.
    james = []
    for source, pages in [('james-1881', '138–139, leaves152–153'), ('james-1908', '152–153, leaves178–179')]:
        original = next(r for r in ledger if r['id'] == source + '-independent-scenes-v1')
        rights = copy.deepcopy(original)
        path = ROOT / f'rights/raw/substantive-revision-2026-10-26/{source}.verified.txt'
        text = path.read_text().rstrip('\n')
        rights['id'] = source + '-proposal-revision-v1'
        rights['title'] = 'The Portrait of a Lady: Isabel’s response to Warburton’s proposal'
        rights['source'].update(raw_path=str(path.relative_to(ROOT / 'rights')), sha256=sha(path),
                                 revision='sha256:' + sha(path),
                                 included_material=f'Only canonical span0:{len(text)}, printed pp{pages}; exact paragraph beginning These words and ending to-day. New scan evidence bound by curation/revision-preflight-v1/source-lock.json. Not a whole-book clearance.')
        rights['review']['notes'] += ' Additional paragraph checked against original scanned pages on26October; no manuscript-level attribution of individual punctuation. Printed dash spacing and quotation glyphs normalized; italic emphasis omitted.'
        validate_schema(rights, 'rights-record')
        ledger.append(rights)
        james.append(dict(rights_record_id=rights['id'], start=0, end=len(text), text=text))
    prompt = ('Rewrite this period passage about Isabel responding to Lord Warburton’s proposal. Make the appeal feel physically immediate through sensory imagery, then show her admiration coexisting with a sense of confinement and a wish for a greater freedom. Preserve her decision to defer answering and the final spoken request. Deliberate imagery and interpretive emphasis may change; this is a substantive stylistic revision, not copyediting. Return only the revised passage.\n\nPASSAGE:\n' + james[0]['text'])
    rows.append(new_record('james-proposal-revision', 'editing', prompt, james[1]['text'], james, ['portrait-of-a-lady']))
    origins['james-proposal-revision'] = 'new-scan-verified-substantive-revision'
    # Previously assessed Dickens pair is structurally different, never same-meaning gold.
    dickens_ledger = read_jsonl(ROOT / 'rights/author-revision-followup-v1.scoped.jsonl')
    ledger += dickens_ledger
    d = json.loads((ROOT / 'artifacts/author-revision-followup-2026-10-26/selected-spans.json').read_text())
    spans = [dict(rights_record_id=s['id'], start=s['start'], end=s['end'], text=s['text']) for s in d]
    prompt = ('Write an alternative ending to this historical novel passage. Deliberately change the later circumstances: leave Estella’s remarriage uncertain, move the reunion from a London carriage to the ruined old estate at dusk, expand it into a scene of mutual recognition and conversation, and end with their walking out together through rising mist. Retain Pip’s first-person retrospective voice. This is a structural alternative that changes events, not a fact-preserving edit or a claim that one ending is better. Return only the new ending.\n\nEARLIER ENDING:\n' + spans[0]['text'])
    rows.append(new_record('dickens-structural-ending', 'storytelling', prompt, spans[1]['text'], spans,
                           [r['work_id'] for r in dickens_ledger]))
    origins['dickens-structural-ending'] = 'previously-assessed-untrained-structural-revision'
    # Preserve the same exposed development monitor, with explicit limitations.
    ids = json.loads((ROOT / 'artifacts/task-matched-v3/tokenizer-preflight.json').read_text())['validation_monitor_ids']
    rows += [copy.deepcopy(next(r for r in old if r['id'] == ident)) for ident in ids]
    for row in rows:
        row.pop('_author_ids', None)
        row['dataset_version'] = 'revision-preflight-v1'
        if row['split'] != 'train':
            origins[row['id']] = 'retained-exposed-Wray-development-monitor'
    used = {rid for r in rows for rid in r['rights_record_ids']}
    ledger = [r for r in ledger if r['id'] in used]
    if len({r['id'] for r in ledger}) != len(ledger):
        raise Invalid('duplicate ledger identity')
    OUT.mkdir()
    save_rows(LEDGER, ledger)
    save_rows(OUT / 'records.jsonl', rows)
    save(OUT / 'membership.json', origins)
    valid = validate_dataset(OUT / 'records.jsonl', LEDGER, ['GB', 'US'])
    authors = Counter()
    byid = {r['id']: r for r in ledger}
    for row in valid:
        if row['split'] == 'train':
            for author in {a for rid in row['rights_record_ids'] for a in byid[rid]['author_ids']}:
                authors[author] += 1
    if len([r for r in valid if r['split'] == 'train']) != 30 or max(authors.values()) > 10:
        raise Invalid('pilot size or author concentration exceeds fixed record cap')
    save(OUT / 'selection.json', dict(training_examples=30, new_to_training=12, retained=18,
                                    validation_examples=len(ids), author_record_counts=dict(authors),
                                    author_record_cap=10, generated_literary_targets=0,
                                    human_quality_approval=False, training_launched=False))
    inputs = [old_data, old_path, ROOT / 'artifacts/task-matched-v3/trace.jsonl',
              ROOT / 'artifacts/task-matched-v3/tokenizer-preflight.json',
              HERE / 'source-lock.json', HERE / 'build.py', OUT / 'records.jsonl', LEDGER,
              OUT / 'membership.json', OUT / 'selection.json']
    save(HERE / 'dataset-lock.json', {'files': {str(p.relative_to(ROOT)): sha(p) for p in inputs}})
    print(json.dumps({'training_examples': 30, 'new_to_training': 12, 'development_monitor': len(ids), 'trained': False}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['build', 'verify'])
    args = parser.parse_args()
    if args.command == 'build':
        prepare()
    verify_files(json.loads((HERE / 'source-lock.json').read_text())['files'])
    verify_files(json.loads((HERE / 'dataset-lock.json').read_text())['files'])
    rows = validate_dataset(OUT / 'records.jsonl', LEDGER, ['GB', 'US'])
    benchmark = read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl')
    for rel in ['artifacts/literary-mix-v2/test.cases.jsonl', 'artifacts/task-matched-v3/test.cases.jsonl']:
        benchmark += [dict(id=c['id'], split_group=c['scenario_id'], context=c['prompt'] + '\n' + c['context']) for c in read_jsonl(ROOT / rel)]
    check_leakage(rows, benchmark)
    print('Dataset, exact provenance, split boundaries and prior evaluation overlap checks passed.')


if __name__ == '__main__':
    main()
