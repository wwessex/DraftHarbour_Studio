"""Report every predeclared factor, keeping the original-control result separate."""
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from foundation.format_diagnostic import score
RUN=ROOT/'artifacts/format-diagnostic-v17'
PLAN=ROOT/'artifacts/format-diagnostic-v17-plan'


def main():
    if not (RUN/'service-final.json').exists():raise ValueError('Execution still active')
    p=json.loads((RUN/'protocol.frozen.json').read_text())
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    cases=read_jsonl(PLAN/'cases.frozen.jsonl');details=[];summary={};bad=[]
    def counts(ds):
        return dict(attempted=len(ds),entity_correct=sum(d['entity_correct'] is True for d in ds),entity_assessable=sum(d['entity_correct'] is not None for d in ds),
                    format_compliant=sum(d['format_compliant'] for d in ds),exact_task_correct=sum(d['exact_task_correct'] for d in ds),failures=sum(d['request_failed'] for d in ds))
    for side in p['conditions']:
        path=RUN/(side+'.responses.jsonl');rows=read_jsonl(path) if path.exists() else []
        assert [r['case_id'] for r in rows]==[c['id'] for c in cases[:len(rows)]]
        ds=[]
        for c,r in zip(cases,rows):
            failed=bool(r['error']) or r['finish_reason']=='length'
            d=dict(condition=side,case_id=c['id'],cohort=c['cohort'],request_failed=failed,**score(r['text'],c))
            if failed:d.update(entity_correct=None,format_compliant=False,exact_task_correct=False)
            for field in ['known_object','first_fact_object','question','format']:d[field]=c.get(field)
            ds.append(d);details.append(d)
            if not d['exact_task_correct']:bad.append(dict(condition=side,case=c,response=r,diagnostic=d))
        primary=[d for d in ds if d['cohort']=='balanced-factorial'];anchor=[d for d in ds if d['cohort']=='exposed-original-control']
        summary[side]=dict(factorial=counts(primary),exposed_control=counts(anchor),missing=25-len(ds),
                           by_factor={field:{value:counts([d for d in primary if d[field]==value]) for value in sorted({c[field] for c in cases if c['cohort']=='balanced-factorial'})} for field in ['known_object','first_fact_object','question','format']},
                           emitted_entities=dict(Counter(d['entity'] for d in primary)),entity_extraction_modes=dict(Counter(d['entity_extraction_mode'] for d in primary)))
    report=dict(summary=summary,details=details,training_executed=False,human_quality_ratings=0,model_promoted=False,
                interpretation='Entity selection is a transparent proxy, not proof of comprehension. Factorial responses share two logical states. Original control differs in wording/explicitness and two-field demand; do not attribute its difference solely to format.')
    with (RUN/'scores.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    with (RUN/'counterexamples.json').open('x') as f:json.dump(bad,f,indent=2);f.write('\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
