"""Objective diagnostics and blank blinded ballots; never auto-promote literary models."""
import importlib.util
import json
import os
import random
import re
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
RUN=ROOT/'artifacts/task-matched-training-v13'
PLAN=ROOT/'artifacts/task-matched-v13-plan'


def repeated_dialogue(text):
    bodies=[]
    for line in text.splitlines():
        line=line.strip().strip('"“”')
        line=re.sub(r'^(?:Cora|Devin|Jules|Anika|Maren|Osei|Tess|Imani|Rafi|June)\s*:\s*','',line)
        body=' '.join(line.strip().strip('"“”').casefold().split())
        if len(body.split())>=6:bodies.append(body)
    return max(Counter(bodies).values(),default=0)


def main():
    if not (RUN/'service-final.json').exists():raise RuntimeError('Execution still active; do not score moving evidence')
    spec=importlib.util.spec_from_file_location('frozen_structural_scores',ROOT/'curation/stability-v10/scoring.py')
    scoring=importlib.util.module_from_spec(spec);spec.loader.exec_module(scoring)
    cases=read_jsonl(PLAN/'cases.frozen.jsonl');p=json.loads((RUN/'protocol.frozen.json').read_text())
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    answers={side:{r['case_id']:r for r in read_jsonl(RUN/(side+'.responses.jsonl'))} if (RUN/(side+'.responses.jsonl')).exists() else {} for side in ['base','current-craft','candidate']}
    summary={};details=[]
    for side,rows in answers.items():
        ds=[]
        for c in cases:
            if c['id'] not in rows:continue
            r=rows[c['id']];text=r['text'];failed=bool(r['error']) or r['finish_reason']=='length';lo=c.get('word_count_min');hi=c.get('word_count_max');words=len(text.split())
            repeat=repeated_dialogue(text) if c['kind']=='dialogue' else None
            d=dict(condition=side,case_id=c['id'],cohort='new-development' if c['id'].startswith('ta11-') else 'exposed-regression',kind=c['kind'],words=words,
                   failed=failed,truncated=r['finish_reason']=='length',dialogue_repetitions=repeat,
                   dialogue_repeat_flag=repeat>=2 if repeat is not None else None,
                   word_limit_passed=None if lo is None and hi is None else not failed and (lo is None or words>=lo) and (hi is None or words<=hi),
                   clock_exact=not failed and scoring.clock_match(text,c['expected_json']) if c['kind']=='clock-state' else None,
                   claim_exact=not failed and scoring.claim_match(text,c['expected_json']) if c['kind']=='arrival-claim' else None,
                   exact_edit=not failed and text.strip()==c['exact_reference'] if c.get('exact_reference') else None)
            ds.append(d);details.append(d)
        def count(items,key):return dict(passed=sum(d[key] is True for d in items),total=sum(d[key] is not None for d in items))
        summary[side]=dict(available=len(ds),missing=36-len(ds),failures=sum(d['failed'] for d in ds),truncated=sum(d['truncated'] for d in ds),
                           dialogue_repeat_flags=sum(d['dialogue_repeat_flag'] is True for d in ds),clock_exact=count(ds,'clock_exact'),claim_exact=count(ds,'claim_exact'),exact_edit=count(ds,'exact_edit'),
                           word_limits={cohort:{kind:count([d for d in ds if d['kind']==kind and d['cohort']==cohort],'word_limit_passed') for kind in ['dialogue','continue','rewrite','write']} for cohort in ['new-development','exposed-regression']})
    def save(n,value,private=False):
        fd=os.open(RUN/n,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600 if private else 0o644)
        with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.write('\n')
    save('scores.json',dict(summary=summary,details=details,reused_responses=0,human_quality_ratings=0,
                           all_evaluation_complete=all((RUN/(s+'.complete.json')).exists() for s in answers),
                           limits='Exact edits/JSON, length limits and repeated lines are mechanical diagnostics, not literary quality. Newly authored tasks become exposed after this run. Missing responses remain missing.'))
    writing=[c for c in cases if c['kind'] in ['dialogue','continue','rewrite','write'] and all(c['id'] in answers[s] and not answers[s][c['id']]['error'] and answers[s][c['id']]['finish_reason']!='length' for s in ['current-craft','candidate'])]
    packet=['# Current craft versus task-matched candidate','','All responses here were generated in this run in fresh contexts. A/B labels are randomised separately per case. Nine writing cases are from newly authored correlated development tasks; the remaining eight are exposed regressions. Inspect actual paired content and the full prompt; missing or truncated pairs are excluded. No human ratings have been recorded. Judge coherence, distinct aims, concrete movement, viewpoint, source copying, instruction adherence, permissions/resources and known versus unknown facts. Length and line repetition are not literary-quality scores.','']
    key=[];ballots=[];rng=random.SystemRandom()
    for c in writing:
        sides=['current-craft','candidate'];rng.shuffle(sides);key.append(dict(case_id=c['id'],**dict(zip('AB',sides))))
        packet+=['## '+c['id'],'',c['prompt'],'']
        for label,side in zip('AB',sides):packet+=['### Response '+label,'',answers[side][c['id']]['text'],'']
        for reviewer in ['reviewer-1','reviewer-2']:ballots.append(dict(case_id=c['id'],reviewer=reviewer,ratings=dict(A=None,B=None),preference=None,evidence=None))
    if not writing:packet+=['No completed writing pairs are available.','']
    with (RUN/'REVIEW.md').open('x') as f:f.write('\n'.join(packet)+'\n')
    save('blind-key.private.json',key,True)
    with (RUN/'human-ballots.blank.jsonl').open('x') as f:
        for r in ballots:f.write(json.dumps(r)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
