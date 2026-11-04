"""Review annotations and freeze a prose-majority proposal; never trains a model."""
import copy
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import (Invalid, check_leakage, digest, file_hash, load_ledger,
                                   read_jsonl, validate_dataset)
from foundation.grounding_lessons import STATUSES, evidence_target
from foundation.balanced_curriculum import retain_prose, source_unit

HERE = Path(__file__).resolve().parent
OUT = ROOT/'artifacts/grounding-balanced-v1'
LEDGER = ROOT/'rights/grounding-balanced-v1.scoped.jsonl'
CORE = ROOT/'artifacts/grounding-editing-v1'


def save(path,value):
    with path.open('x',encoding='utf-8') as f:
        f.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')


def save_rows(path,rows):
    with path.open('x',encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row,ensure_ascii=False)+'\n')


def verify_files(files):
    for relative,expected in files.items():
        path=(ROOT/relative).resolve()
        if not path.is_relative_to(ROOT) or file_hash(path)!=expected:
            raise Invalid('frozen artifact changed: '+relative)


def review_semantics(core,decisions):
    semantic=[r for r in core if r['id'].startswith('ge-evidence-')]
    accepted=decisions['accept_unchanged']
    changed=decisions['clarify']['id']
    if len(set(accepted))!=len(accepted) or changed in accepted or set(accepted+[changed])!={r['id'] for r in semantic}:
        raise Invalid('review must cover every semantic record exactly once')
    reviewed=[]
    for original in semantic:
        row=copy.deepcopy(original)
        row.pop('_author_ids',None)
        source=row['messages'][0]['content'].split('SOURCE EXCERPT:\n',1)[1]
        answer=json.loads(row['messages'][-1]['content'])
        if original['id']==changed:
            start=source.index('I’ll help you,')
            end=source.index('else will.',start)+len('else will.')
            quote=source[start:end]
            prefix,separator,remainder=row['messages'][0]['content'].partition('CLASSIFY THIS QUOTATION:\n')
            if not separator or '\n\nSOURCE EXCERPT:\n' not in remainder:
                raise Invalid('unexpected classification prompt')
            row['messages'][0]['content']=prefix+separator+quote+'\n\nSOURCE EXCERPT:\n'+source
            answer=evidence_target(source,'plan',quote)
            row['messages'][-1]['content']=json.dumps(answer,ensure_ascii=False,separators=(',',':'))
        evidence_target(source,answer['status'],answer['evidence'][0] if answer['evidence'] else None)
        row['id']='reviewed-'+original['id']
        row['dataset_version']='grounding-semantic-review-v1'
        row['review']=dict(status='approved',reviewer=decisions['reviewer'],reviewed_on='2026-10-29',
            notes='Informed AI review of its own annotations, not independent, blinded or human gold. '+
                  decisions['status_reasons'][answer['status']]+(' Explicit promise quotation clarified; source body unchanged.' if original['id']==changed else ' Original messages unchanged.'))
        row['content_hash']=digest(row['messages'])
        reviewed.append(row)
    return reviewed


def build():
    if OUT.exists() or LEDGER.exists():
        raise Invalid('refusing to overwrite frozen proposal')
    inputs={}
    for name in ['packet-lock.json','token-lock.json','review-lock.json','support-lock.json','restraint-lock.json']:
        path=ROOT/'curation/grounding-editing-v1'/name
        verify_files(json.loads(path.read_text())['files'])
        inputs[str(path.relative_to(ROOT))]=file_hash(path)
    ledger={}
    datasets={}
    sources=[('revision-preflight-v1','revision-preflight-v1'),('literary-mix-v2','literary-mix-v2'),
             ('grounding-editing-v1','grounding-editing-v1'),('grounding-editing-restraint-v1','grounding-editing-v1')]
    for data,rights in sources:
        path=ROOT/f'artifacts/{data}/records.jsonl'
        lp=ROOT/f'rights/{rights}.scoped.jsonl'
        datasets[data]=validate_dataset(path,lp,['GB','US'])
        for p in [path,lp]:inputs[str(p.relative_to(ROOT))]=file_hash(p)
        for ident,row in load_ledger(lp).items():
            if ident in ledger and ledger[ident]!=row:
                raise Invalid('inconsistent source-rights identity')
            ledger[ident]=row
    core=datasets['grounding-editing-v1']
    decisions=json.loads((HERE/'review-decisions.json').read_text())
    reviewed=review_semantics(core,decisions)
    by_id={r['id']:r for r in core}
    reviewed_by_id={r['id']:r for r in reviewed}
    # One example of every reviewed status, across multiple excerpts/authors.
    evidence_ids=['18','08','21','02','10','16','19','07']
    evidence=[reviewed_by_id['reviewed-ge-evidence-'+n] for n in evidence_ids]
    if {json.loads(r['messages'][-1]['content'])['status'] for r in evidence}!=set(STATUSES):
        raise Invalid('evidence selection must cover all eight statuses')
    repairs=[by_id[f'ge-{n:03d}-repair'] for n in [0,8,32,52]]
    noops=[by_id[f'ge-{n:03d}-unchanged'] for n in [0,32,52]]
    noops+=datasets['grounding-editing-restraint-v1']
    clocks=[by_id['ge-clock-'+n] for n in ['0-00','0-04','0-08','0-09','1-00','1-01','1-03','1-06']]
    prose_pool=datasets['revision-preflight-v1']+datasets['literary-mix-v2']
    prose,prose_kinds=retain_prose(prose_pool)
    selection=[(r,prose_kinds[r['id']],'retained-prose') for r in prose]
    selection += [(r,'selected-repair','structured-core') for r in repairs]
    selection += [(r,'unchanged-selection','structured-core-or-restraint') for r in noops]
    selection += [(r,'evidence-status','reviewed-semantics') for r in evidence]
    selection += [(r,'clock-state','structured-core') for r in clocks]
    if len(selection)!=80:
        raise Invalid('proposal must contain56 prose and24 structural records')
    records=[]
    trace=[]
    for original,kind,origin in selection:
        row=copy.deepcopy(original)
        row.pop('_author_ids',None)
        old_id=row['id']
        row['id']='gb-'+old_id
        row['dataset_version']='grounding-balanced-v1'
        records.append(row)
        trace.append(dict(id=row['id'],original_id=old_id,kind=kind,origin=origin,
                          original_messages_sha256=digest(original['messages']),
                          supporting_unit_sha256=digest(source_unit(original))))
    # This is the old exposed development monitor, not a new independent test.
    monitor=[copy.deepcopy(r) for r in datasets['revision-preflight-v1'] if r['split']=='validation']
    for row in monitor:
        row.pop('_author_ids',None)
        row['id']='gb-monitor-'+row['id']
        row['dataset_version']='grounding-balanced-v1'
    records+=monitor
    work_counts=Counter(w for r in records if r['split']=='train' for w in set(r['source_work_ids']))
    if max(work_counts.values())>24:
        raise Invalid('work exceeds30percent record cap')
    used={rid for r in records for rid in r['rights_record_ids']}
    OUT.mkdir()
    save_rows(LEDGER,[ledger[rid] for rid in sorted(used)])
    save_rows(OUT/'records.jsonl',records)
    save_rows(OUT/'semantic-reviewed.records.jsonl',reviewed)
    save_rows(OUT/'trace.jsonl',trace)
    save(OUT/'selection.json',dict(training_records=80,prose_records=56,structural_records=24,
         prose_fraction=.7,validation_records=len(monitor),work_record_counts=dict(work_counts),
         kind_counts=dict(Counter(t['kind'] for t in trace)),distinct_prose_source_units=56,
         semantic_review=dict(accepted_unchanged=23,clarified=1,human_approval=False,independent=False),
         generated_literary_teaching_answers=0,trained=False,
         limits=['Existing prose sources reused;56 units are not56 new stories.',
                 'Row balance and supervised-token balance differ; neither proves a ratio optimal.',
                 'Wray monitor was previously exposed; it is not an independent project-wide test.']))
    cases=read_jsonl(CORE/'prose-transfer.evaluation-only.jsonl')
    clock_tests=read_jsonl(CORE/'clock-tests.evaluation-only.jsonl')
    for case in clock_tests:
        state={k:case[k] for k in ['now','scheduled','arrived']}
        cases.append(dict(id=case['id'],scenario_id='held-clock-'+case['scheduled'].replace(':',''),
             kind='clock-state',task='analysis',context=json.dumps(state,separators=(',',':')),
             prompt='Use same-day24-hour HH:MM times. arrived:null means unknown, not absent. Return JSON only with state (arrived/not_established/not_yet_due/due_now/overdue) and minutes_to_schedule (scheduled minus now). A future appointment is not overdue.\n\nTASK STATE:\n'+json.dumps(state),
             expected_json=case['expected'],exact_reference=None,word_count_min=None,word_count_max=None,
             provenance=case['provenance']))
    save_rows(OUT/'evaluation.cases.frozen.jsonl',cases)
    for p in [CORE/'prose-transfer.evaluation-only.jsonl',CORE/'clock-tests.evaluation-only.jsonl',
              HERE/'build.py',HERE/'review-decisions.json',ROOT/'foundation/balanced_curriculum.py',LEDGER,
              *OUT.glob('*.json*')]:inputs[str(p.relative_to(ROOT))]=file_hash(p)
    save(HERE/'dataset-lock.json',dict(files=inputs))


def verify():
    verify_files(json.loads((HERE/'dataset-lock.json').read_text())['files'])
    rows=validate_dataset(OUT/'records.jsonl',LEDGER,['GB','US'])
    validate_dataset(OUT/'semantic-reviewed.records.jsonl',LEDGER,['GB','US'])
    train=[r for r in rows if r['split']=='train']
    if len(train)!=80 or len(rows)!=96:
        raise Invalid('unexpected frozen membership')
    trace=read_jsonl(OUT/'trace.jsonl')
    for row,t in zip(train,trace):
        if row['id']!=t['id'] or digest(row['messages'])!=t['original_messages_sha256']:
            raise Invalid('selected messages changed')
    new_cases=read_jsonl(OUT/'evaluation.cases.frozen.jsonl')
    benchmark=[dict(id=c['id'],split_group=c['scenario_id'],context=c['prompt']+'\n'+c['context'])
               for c in new_cases if c['kind']!='clock-state']
    benchmark+=read_jsonl(ROOT/'evaluation/tasks.draft.jsonl')
    for rel in ['artifacts/task-matched-v3/test.cases.jsonl','artifacts/revision-preflight-v1/test.cases.jsonl']:
        benchmark += [dict(id=c['id'],split_group=c['scenario_id'],context=c['prompt']+'\n'+c['context']) for c in read_jsonl(ROOT/rel)]
    check_leakage(rows,benchmark)
    clock_states=set()
    for row,t in zip(train,trace):
        if t['kind']=='clock-state':
            s=json.loads(row['messages'][0]['content'].split('TASK STATE:\n',1)[1].split('\n\nSOURCE EXCERPT:',1)[0])
            clock_states.add((s['now'],s['scheduled'],s['arrived']))
    if clock_states.intersection((c['now'],c['scheduled'],c['arrived']) for c in read_jsonl(CORE/'clock-tests.evaluation-only.jsonl')):
        raise Invalid('held-out clock state entered training')
    return dict(passed=True,training_records=80,prose_records=56,structural_records=24,
                development_monitor=16,evaluation_cases=len(new_cases),semantic_annotations_reviewed=24,
                human_approvals=0,generated_literary_teaching_answers=0,training_launched=False)


if __name__=='__main__':
    if len(sys.argv)!=2 or sys.argv[1] not in ['build','verify']:
        raise SystemExit('Use build or verify; neither launches training.')
    if sys.argv[1]=='build':build()
    print(json.dumps(verify(),indent=2))
