"""Compile source-backed structural lessons; no literary answer generation or training."""
from collections import Counter, defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import (Invalid, check_leakage, digest, file_hash, load_ledger,
                                   read_jsonl, validate_dataset, validate_schema)
from foundation.grounding_lessons import STATUSES, arrival_state, evidence_target, selection_pair
from foundation.anchored_edits import AnchorEdit, apply_anchor_edits

HERE = Path(__file__).resolve().parent
OUT = ROOT / 'artifacts/grounding-editing-v1'
LEDGER = ROOT / 'rights/grounding-editing-v1.scoped.jsonl'
INPUTS = [('literary-mix-v2', 'literary-mix-v2'), ('revision-preflight-v1', 'revision-preflight-v1')]
INSTRUCTION = ('Return JSON only with status and evidence. Classify only what this supplied excerpt establishes. '
               'explicit_fact: unqualified narration within this fiction; character_statement: a spoken/written claim, not independent corroboration; '
               'plan: announced intention or promise, not completion; request: an instruction or request, not an accomplished event; '
               'hypothetical: imagined/counterfactual content, not actual speech/action; uncertain_or_inferred: qualified interpretation or uncertainty; '
               'reported_information: a report of what someone heard, not direct verification; '
               'not_established: the supplied excerpt does not answer the question. '
               'For classification copy the exact supplied quotation as the sole evidence string. '
               'For not_established use evidence:[]; do not invent an answer or evidence. No explanation.')


def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        f.write(json.dumps(value, ensure_ascii=False, indent=2)+'\n')


def save_rows(path, values):
    with path.open('x', encoding='utf-8') as f:
        for value in values:
            f.write(json.dumps(value, ensure_ascii=False)+'\n')


def gather():
    ledger, datasets, files = {}, {}, {}
    for data, rights in INPUTS:
        p = ROOT/f'artifacts/{data}/records.jsonl'
        lp = ROOT/f'rights/{rights}.scoped.jsonl'
        datasets[data] = validate_dataset(p, lp, ['GB', 'US'])
        files[str(p.relative_to(ROOT))] = file_hash(p)
        files[str(lp.relative_to(ROOT))] = file_hash(lp)
        for ident, row in load_ledger(lp).items():
            if ident in ledger and ledger[ident] != row:
                raise Invalid('rights identity changed across source inputs')
            ledger[ident] = row
    return datasets, ledger, files


def lesson(ident, kind, task, prompt, target, span, ledger, unit):
    rid = span['rights_record_id']
    row = dict(schema_version='1.0', id=ident, dataset_version='grounding-editing-v1',
               task=task, split='train', split_group=ledger[rid]['work_id'], origin='derived',
               teacher=None, messages=[dict(role='user', content=prompt),
                                      dict(role='assistant', content=json.dumps(target, ensure_ascii=False, separators=(',', ':')))],
               source_work_ids=[ledger[rid]['work_id']], rights_record_ids=[rid],
               source_spans=[copy.deepcopy(span)],
               review=dict(status='approved', reviewer='Codex AI: source alignment and deterministic-target audit',
                           reviewed_on='2026-10-29', notes='AI assessment, not human approval or literary-quality certification. Structural labels/JSON and exact source quotations only; no generated literary teaching answer. Semantic categories are AI annotations; clock states and duplicate repairs are deterministic. Hypothetical task metadata is separate from source plot. Prepared only, not trained.'),
               rubric=['source fidelity', 'selection boundaries', 'evidence discipline'], content_hash='')
    row['content_hash'] = digest(row['messages'])
    validate_schema(row, 'dataset-record')
    return row, dict(id=ident, kind=kind, unit=unit, target=target)


def build():
    if OUT.exists() or LEDGER.exists():
        raise Invalid('refusing to overwrite a curriculum or rights ledger')
    datasets, ledger, files = gather()
    by_id = {(name, row['id']): row for name, rows in datasets.items() for row in rows if row['split']=='train'}
    rows, trace = [], []
    def add(*args, unit):
        row, audit = lesson(*args, ledger=ledger, unit=unit)
        rows.append(row)
        trace.append(audit)
    # Distinct normalized passages, not distinct prompt variants, define source units.
    units, seen = defaultdict(list), set()
    for dataset, records in datasets.items():
        for row in records:
            if row['split'] != 'train':
                continue
            for span in row['source_spans']:
                text = ' '.join(span['text'].split())
                key = text.casefold()
                if key in seen:
                    continue
                seen.add(key)
                try:
                    pair = selection_pair(text)
                except ValueError:
                    continue
                units[ledger[span['rights_record_id']]['work_id']].append((span, pair))
    selected = []
    # Fixed cap is per work, not a target example count; never pad by paraphrasing.
    for work in sorted(units):
        selected += [(work, span, pair) for span, pair in units[work][:20]]
    for number, (work, span, pair) in enumerate(selected):
        unit = f'passage-{number:03d}'
        prompt = ('Copyedit only TARGET. Remove only an accidentally repeated consecutive word inside TARGET. '
                  'Preserve spelling, punctuation, names, historical grammar and all other characters. '
                  'Do not repair CONTEXT BEFORE, even when it contains the same error. '
                  'Return only {"edits":[{"before":"exact unique target anchor","after":"replacement"}]}; '
                  'use {"edits":[]} if TARGET has no such error. No minimum output length.\n\n')
        add(f'ge-{number:03d}-repair', 'selected-repair', 'editing',
            prompt+'CONTEXT BEFORE:\n'+pair['outside_with_duplicate']+'\n\nTARGET:\n'+pair['broken'],
            dict(edits=pair['edits']), span, unit=unit)
        add(f'ge-{number:03d}-unchanged', 'outside-error-unchanged', 'editing',
            prompt+'CONTEXT BEFORE:\n'+pair['outside_with_duplicate']+'\n\nTARGET:\n'+pair['clean'],
            dict(edits=[]), span, unit=unit)
    specs = json.loads((HERE/'evidence-specs.json').read_text())['specifications']
    for number, spec in enumerate(specs):
        original = by_id[(spec['dataset'], spec['record_id'])]
        text = original['messages'][-1]['content']
        span = original['source_spans'][-1]
        if ' '.join(text.split()) not in ' '.join(span['text'].split()):
            raise Invalid('classification context not source-derived')
        target = evidence_target(text, spec['status'], spec['quote'])
        query = 'QUESTION:\n'+spec['question'] if spec['quote'] is None else 'CLASSIFY THIS QUOTATION:\n'+spec['quote']
        add(f'ge-evidence-{number:02d}', 'evidence-status', 'analysis',
            INSTRUCTION+'\n\n'+query+'\n\nSOURCE EXCERPT:\n'+text,
            target, span, unit=spec['record_id'])
    clock_sources = [('literary-mix-v2', 'v2-new-010-write', '19:45', 'at a quarter to eight o’clock'),
                     ('revision-preflight-v1', 'hopkins-invitation', '19:30', 'at half after seven')]
    for source_index, (dataset, ident, scheduled, quote) in enumerate(clock_sources):
        original = by_id[(dataset, ident)]
        text = original['messages'][-1]['content']
        if text.count(quote) != 1:
            raise Invalid('schedule evidence does not match reviewed source')
        for index, (offset, arrived) in enumerate((o, a) for o in [-60, 0, 30, 90] for a in [False, None, True]):
            total = int(scheduled[:2])*60+int(scheduled[3:])+offset
            now = f'{total//60:02d}:{total%60:02d}'
            state = dict(day='same constructed evening', now=now, scheduled=scheduled, arrived=arrived)
            prompt = ('This is a constructed clock exercise, not additional original plot. The source supplies an announced schedule only. '
                      'The hypothetical TASK STATE supplies the current snapshot, with same-day24-hour HH:MM times. '
                      'arrived:null means unknown, not absent. A future appointment cannot already be overdue. '
                      'Return JSON only: state (arrived/not_established/not_yet_due/due_now/overdue), '
                      'minutes_to_schedule (scheduled minus now; negative if past). Do not invent a cause or visitor identity.\n\n'
                      'SCHEDULE QUOTATION:\n'+quote+'\n\nTASK STATE:\n'+json.dumps(state)+'\n\nSOURCE EXCERPT:\n'+text)
            add(f'ge-clock-{source_index}-{index:02d}', 'clock-state', 'analysis', prompt,
                arrival_state(now, scheduled, arrived), original['source_spans'][-1], unit=ident)
    used = {rid for row in rows for rid in row['rights_record_ids']}
    if any(any(name in author for name in ['mansfield','chesnutt','austen','wray'])
           for rid in used for author in ledger[rid]['author_ids']):
        raise Invalid('reserved author entered preparation')
    OUT.mkdir()
    save_rows(LEDGER, [ledger[rid] for rid in sorted(used)])
    save_rows(OUT/'records.jsonl', rows)
    save_rows(OUT/'trace.jsonl', trace)
    # Keep structured temporal test states disjoint in clock values from training.
    tests = []
    for scheduled in ['06:25', '14:10']:
        for offset in [-30, 0, 15, 60]:
            total = int(scheduled[:2])*60+int(scheduled[3:])+offset
            now = f'{total//60:02d}:{total%60:02d}'
            for arrived in [False, None, True]:
                tests.append(dict(id=f'ge-clock-test-{len(tests):02d}', now=now, scheduled=scheduled,
                                  arrived=arrived, expected=arrival_state(now, scheduled, arrived),
                                  provenance='Deterministic nonliterary evaluation state only; not training data or an independent human-reviewed benchmark.'))
    save_rows(OUT/'clock-tests.evaluation-only.jsonl', tests)
    save(OUT/'manifest.json', dict(created_on='2026-10-29', examples=len(rows),
        components=dict(Counter(t['kind'] for t in trace)), distinct_edit_passages=len(selected),
        edit_passages_by_work=dict(Counter(work for work, _, _ in selected)),
        semantic_annotation_examples=len(specs), semantic_source_units=len({s['record_id'] for s in specs}),
        clock_examples=24, clock_source_units=2, independent_new_books_acquired=0,
        generated_literary_teaching_answers=0, human_quality_approvals=0, trained=False,
        limitations=['Paired edits share a passage;24 clock examples share two schedules. Example count is not independent source count.',
                     'Structural JSON lessons do not teach elegant prose and may bias response format if oversampled.',
                     'Semantic labels are informed AI annotations, not human gold.',
                     'This packet has no approved final training mixture, weights, run length or model promotion.']))
    for rid in used:
        raw = (LEDGER.parent/ledger[rid]['source']['raw_path']).resolve()
        files[str(raw.relative_to(ROOT))] = file_hash(raw)
    for path in [HERE/'build.py', HERE/'evidence-specs.json', ROOT/'foundation/grounding_lessons.py',
                 LEDGER, *OUT.glob('*.json*')]:
        files[str(path.relative_to(ROOT))] = file_hash(path)
    save(HERE/'packet-lock.json', dict(files=files))
    print(json.dumps(json.loads((OUT/'manifest.json').read_text()), indent=2))


def verify():
    lock = json.loads((HERE/'packet-lock.json').read_text())['files']
    for relative, expected in lock.items():
        if file_hash(ROOT/relative) != expected:
            raise Invalid('packet/source changed: '+relative)
    rows = validate_dataset(OUT/'records.jsonl', LEDGER, ['GB', 'US'])
    traces = read_jsonl(OUT/'trace.jsonl')
    if len(rows) != len(traces):
        raise Invalid('trace coverage mismatch')
    for row, trace in zip(rows, traces):
        target = json.loads(row['messages'][-1]['content'])
        if row['id'] != trace['id'] or target != trace['target'] or row['teacher'] is not None:
            raise Invalid('structural target mismatch')
        prompt = row['messages'][0]['content']
        if row['task']=='editing':
            captured = prompt.split('TARGET:\n',1)[1]
            result = apply_anchor_edits(captured, captured, [AnchorEdit(**e) for e in target['edits']])
            if trace['kind']=='selected-repair' and len(target['edits']) != 1:
                raise Invalid('missing minimal repair')
            if trace['kind']=='outside-error-unchanged' and (target['edits'] or result != captured):
                raise Invalid('outside-context error leaked into the selection')
            if ' '.join(result.split()) not in ' '.join(row['source_spans'][0]['text'].split()):
                raise Invalid('editing adds non-source prose')
        elif trace['kind']=='evidence-status':
            source = prompt.split('SOURCE EXCERPT:\n',1)[1]
            evidence_target(source, target['status'], target['evidence'][0] if target['evidence'] else None)
        elif trace['kind']=='clock-state':
            state = json.loads(prompt.split('TASK STATE:\n',1)[1].split('\n\nSOURCE EXCERPT:',1)[0])
            if target != arrival_state(state['now'], state['scheduled'], state['arrived']):
                raise Invalid('clock target differs from snapshot')
    # Keep prior validation/test authors and original evaluation packs outside training.
    prior = []
    for data, rights in INPUTS:
        prior += [r for r in validate_dataset(ROOT/f'artifacts/{data}/records.jsonl', ROOT/f'rights/{rights}.scoped.jsonl', ['GB','US']) if r['split']!='train']
    benchmark = read_jsonl(ROOT/'evaluation/tasks.draft.jsonl')
    for rel in ['artifacts/task-matched-v3/test.cases.jsonl', 'artifacts/revision-preflight-v1/test.cases.jsonl']:
        benchmark += [dict(id=c['id'], split_group=c['scenario_id'], context=c['prompt']+'\n'+c['context']) for c in read_jsonl(ROOT/rel)]
    check_leakage(rows+prior, benchmark)
    return dict(passed=True, examples=len(rows), exact_source_quotes=True, selection_boundaries_verified=True,
                deterministic_clock_labels_verified=True, prior_heldout_splits_preserved=True,
                generated_literary_teaching_answers=0, trained=False, apps_changed=False)


if __name__ == '__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ['build','verify']:
        raise SystemExit('Use build or verify; neither launches training.')
    if sys.argv[1]=='build':
        build()
    print(json.dumps(verify(), indent=2))
