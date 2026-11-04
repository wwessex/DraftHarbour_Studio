"""Select a mixed source-only proposal without overlapping source variants."""
import copy
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,load_ledger,read_jsonl,validate_dataset
from foundation.mixed_curriculum import require_distinct_source_spans
OUT=ROOT/'artifacts/mixed-curriculum-v15b'
LEDGER=ROOT/'rights/grounding-balanced-v1.scoped.jsonl'
REPLACE={'gb-hopkins-room':'sr14-materials','gb-hopkins-invitation':'sr14-event-times','gb-v2-directed-opie-0262':'sr14-explicit-condition'}
ADD=['sr14-lever','sr14-announced-visit']
DROP={'gb-ge-000-repair':'Keep the no-change control from this same source span instead.',
      'gb-ge-008-repair':'Source overlaps the selected room-material semantic repair.',
      'gb-ge-032-unchanged':'Keep the duplicate-repair variant from this source span instead.',
      'gb-ge-052-unchanged':'Keep the duplicate-repair variant from this source span instead.',
      'gb-ge-grammatical-had-had':'Source overlaps the retained James author revision; preserve prose revision in this mixture.'}


def main():
    if OUT.exists():raise ValueError('Refuse overwrite')
    lock_path=ROOT/'curation/semantic-restoration-v14/preparation.lock.json'
    lock=json.loads(lock_path.read_text())
    protected=dict(lock['source_hashes'])
    protected.update({str((ROOT/'artifacts/semantic-restoration-v14'/n).relative_to(ROOT)):h for n,h in lock['artifact_hashes'].items()})
    parent=json.loads((ROOT/'artifacts/semantic-restoration-v14/verification.json').read_text());protected.update(parent['protected_hashes'])
    for n,h in protected.items():assert file_hash(ROOT/n)==h,n
    previous_path=ROOT/'artifacts/paragraph-dialogue-v12/records.proposed.jsonl'
    semantic_path=ROOT/'artifacts/semantic-restoration-v14/candidates.jsonl'
    old=read_jsonl(previous_path);semantic={r['id']:r for r in read_jsonl(semantic_path)}
    selected=[];selection=[]
    for r in old:
        if r['split']!='train':continue
        if r['id'] in DROP:
            selection.append(dict(parent_id=r['id'],decision='excluded-overlap',reason=DROP[r['id']]))
            continue
        ident=REPLACE.get(r['id'],r['id']);q=copy.deepcopy(semantic[ident] if ident in semantic else r)
        selection.append(dict(parent_id=r['id'],selected_id=ident,decision='semantic-replacement' if ident!=r['id'] else 'retained',
                              reason='One presentation; source-disjoint within this mixture.'))
        selected.append(q)
    for ident in ADD:
        selected.append(copy.deepcopy(semantic[ident]));selection.append(dict(selected_id=ident,decision='semantic-addition',reason='Existing scoped training source not otherwise represented in this mixture; no new author/work clearance.'))
    assert len(selected)==22 and len({r['id'] for r in selected})==22
    require_distinct_source_spans(selected,load_ledger(LEDGER))
    assert sum(r['id'].startswith('sr14-') for r in selected)==5
    assert sum(r['id'].startswith('gb-ge-') for r in selected)==3
    monitor=copy.deepcopy([r for r in old if r['split']=='validation'])
    assert len(monitor)==16
    records=selected+monitor
    for r in records:r['dataset_version']='mixed-curriculum-v15-proposal'
    new_cases=copy.deepcopy(read_jsonl(ROOT/'artifacts/semantic-restoration-v14/cases.frozen.jsonl'))
    regressions=copy.deepcopy(read_jsonl(ROOT/'artifacts/task-matched-v13-plan/cases.frozen.jsonl'))
    for c in regressions:c['evaluation_role']='exposed-v13-regression'
    primary=new_cases+regressions
    assert len(primary)==44 and len({c['id'] for c in primary})==44
    assert not {c['prompt'] for c in primary} & {r['messages'][0]['content'] for r in selected}
    derivations={b['id']:b for b in read_jsonl(ROOT/'artifacts/semantic-restoration-v14/derivations.jsonl')}
    fit=[]
    for r in selected:
        if r['id'].startswith('sr14-'):
            fit.append(dict(id='seen-'+r['id'],kind='seen-source-repair',prompt=r['messages'][0]['content'],source_record_id=r['id'],
                            expected_source_answer=r['messages'][-1]['content'],corruption=derivations[r['id']]['corruption'],
                            evaluation_role='seen-training-fit-not-generalisation',training_prompt_overlap_intentional=True,
                            word_count_min=None,word_count_max=None,provenance='Previously published source answer; explicitly seen-training diagnostic, outside primary quality/transfer scores.'))
    assert len(fit)==5
    OUT.mkdir()
    def rows(n,values):
        with (OUT/n).open('x') as f:
            for r in values:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    rows('records.proposed.jsonl',records);rows('selection.jsonl',selection);rows('primary.cases.frozen.jsonl',primary);rows('seen-fit.cases.frozen.jsonl',fit)
    validate_dataset(OUT/'records.proposed.jsonl',LEDGER,['GB','US'])
    selected_semantic={r['id'] for r in selected if r['id'].startswith('sr14-')}
    packet=['# Mixed source-prose and semantic-repair proposal','','Preparation only.22 unique training records, one presentation each; no overlapping source spans between selected records.14 broader prose tasks, five semantic repairs, three structural editing controls.16 previously exposed validation monitors. No training or human quality approval.','']
    for r in selected:packet+=['## '+r['id'],'',r['messages'][0]['content'],'','### Source-derived answer','',r['messages'][-1]['content'],'']
    with (OUT/'REVIEW.md').open('x') as f:f.write('\n'.join(packet))
    inputs=[previous_path,semantic_path,LEDGER,lock_path,Path(__file__),ROOT/'foundation/mixed_curriculum.py',ROOT/'artifacts/semantic-restoration-v14/cases.frozen.jsonl',ROOT/'artifacts/task-matched-v13-plan/cases.frozen.jsonl',ROOT/'artifacts/semantic-restoration-v14/derivations.jsonl']
    result=dict(status='mixed-dataset-preparation-only',training_records=22,training_presentations=22,broader_prose_records=14,semantic_repair_records=5,structural_edit_records=3,
                monitor_records=16,source_spans_overlap=False,selected_semantic=sorted(selected_semantic),reserved_semantic=sorted(set(semantic)-selected_semantic),
                excluded_overlap_records=5,replaced_prose_records=3,added_existing_source_records=2,primary_cases=44,new_unrun_primary_cases=8,exposed_primary_cases=36,seen_training_fit_cases=5,
                proposed_conditions=['base','current-craft','candidate'],proposed_primary_requests=132,proposed_seen_fit_requests=15,proposed_total_requests=147,
                proposed_recipe=dict(max_steps=22,epochs=1,batch_size=1,gradient_accumulation=1,learning_rate='5e-5',lora_rank=8,lora_alpha=16,lora_dropout=0,seed=42,context_limit=2048),
                human_quality_ratings=0,new_literary_teaching_answers_authored=0,new_training_jobs=0,model_promoted=False,
                protected_hashes=protected,input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in inputs},
                output_hashes={n:file_hash(OUT/n) for n in ['records.proposed.jsonl','selection.jsonl','primary.cases.frozen.jsonl','seen-fit.cases.frozen.jsonl','REVIEW.md']})
    with (OUT/'verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print('Selected22 train records:14 prose+5 semantic repairs+3 structural controls;16 exposed monitors;44 primary+5 seen-fit cases.')


if __name__=='__main__':main()
