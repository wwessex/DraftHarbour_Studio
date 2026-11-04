"""Separate post-hoc exploratory follow-up from the original v17 diagnostic."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from foundation.question_ablation import diagnose
RUN=ROOT/'artifacts/question-ablation-v18'
PLAN=ROOT/'artifacts/question-ablation-v18-plan'


def main():
    if not (RUN/'service-final.json').exists():raise ValueError('Execution still active')
    p=json.loads((RUN/'protocol.frozen.json').read_text())
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    cases=read_jsonl(PLAN/'cases.frozen.jsonl');details=[];summary={};bad=[]
    def count(ds):return dict(attempted=len(ds),entity_correct=sum(d['entity_correct'] is True for d in ds),entity_assessable=sum(d['entity_correct'] is not None for d in ds),format_compliant=sum(d['format_compliant'] for d in ds),exact_task_correct=sum(d['exact_task_correct'] for d in ds))
    for side in p['conditions']:
        path=RUN/(side+'.responses.jsonl');rows=read_jsonl(path) if path.exists() else []
        assert [r['case_id'] for r in rows]==[c['id'] for c in cases[:len(rows)]]
        ds=[]
        for c,r in zip(cases,rows):
            d=dict(condition=side,case_id=c['id'],**diagnose(r['text'],c))
            if r['error'] or r['finish_reason']=='length':d.update(entity_correct=None,format_compliant=False,exact_task_correct=False)
            for field in ['known_object','first_fact_object','unknown_cue_explicit','field_count','direct_question','pair_id']:d[field]=c[field]
            ds.append(d);details.append(d)
            if not d['exact_task_correct']:bad.append(dict(condition=side,case=c,response=r,diagnostic=d))
        cells={}
        for explicit in [False,True]:
            for fields in [1,2]:cells[f'cue-{int(explicit)}-fields-{fields}']=count([d for d in ds if d['unknown_cue_explicit']==explicit and d['field_count']==fields])
        pairs=[]
        for pair_id in sorted({d['pair_id'] for d in ds}):
            pair={d['direct_question']:d for d in ds if d['pair_id']==pair_id}
            if len(pair)==2:pairs.append((pair[False]['entity_correct'],pair[True]['entity_correct']))
        summary[side]=dict(overall=count(ds),cells=cells,by_question={str(q):count([d for d in ds if d['direct_question']==q]) for q in [False,True]},paired=dict(both_correct=sum(a is True and b is True for a,b in pairs),question_only_correct=sum(a is not True and b is True for a,b in pairs),no_question_only_correct=sum(a is True and b is not True for a,b in pairs),neither_correct=sum(a is not True and b is not True for a,b in pairs)),missing=32-len(ds))
    with (RUN/'scores.json').open('x') as f:json.dump(dict(summary=summary,details=details,exploratory_after_v17=True,training_executed=False,model_promoted=False),f,indent=2);f.write('\n')
    with (RUN/'counterexamples.json').open('x') as f:json.dump(bad,f,indent=2);f.write('\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
