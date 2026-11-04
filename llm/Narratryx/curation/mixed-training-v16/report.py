"""Separate transfer, exposed regression and seen training fit; blank human ballots."""
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
from foundation.mixed_curriculum import repair_diagnostics
from scoring import strict_json_match
RUN=ROOT/'artifacts/mixed-training-v16'


def repeated_dialogue(text):
    lines=[]
    for line in text.splitlines():
        line=line.strip().strip('"“”')
        line=re.sub(r"^[A-Za-z][A-Za-z '-]{0,30}:\s*",'',line)
        body=' '.join(line.strip().strip('"“”').casefold().split())
        if len(body.split())>=6:lines.append(body)
    return max(Counter(lines).values(),default=0)


def main():
    if not (RUN/'service-final.json').exists():raise ValueError('Execution is still active')
    p=json.loads((RUN/'protocol.frozen.json').read_text())
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    cases=read_jsonl(RUN/'cases.frozen.jsonl')
    answers={side:{r['case_id']:r for r in read_jsonl(RUN/(side+'.responses.jsonl'))} if (RUN/(side+'.responses.jsonl')).exists() else {} for side in ['base','current-craft','candidate']}
    details=[];summary={}
    def count(rows,key):return dict(passed=sum(r.get(key) is True for r in rows),total=sum(r.get(key) is not None for r in rows))
    for side,rows in answers.items():
        ds=[]
        for c in cases:
            r=rows.get(c['id'])
            if r is None:continue
            text=r['text'];failed=bool(r['error']) or r['finish_reason']=='length';seen=c['kind']=='seen-source-repair';new=c['id'].startswith('sr14-')
            lo=c.get('word_count_min');hi=c.get('word_count_max');words=len(text.split());repeat=repeated_dialogue(text) if c['kind']=='dialogue' else None
            d=dict(condition=side,case_id=c['id'],kind=c['kind'],cohort='seen-training-fit' if seen else 'new-development' if new else 'exposed-regression',
                   failed=failed,truncated=r['finish_reason']=='length',words=words,word_limit_passed=None if lo is None and hi is None else not failed and (lo is None or words>=lo) and (hi is None or words<=hi),
                   dialogue_repeat_flag=repeat>=2 if repeat is not None else None,dialogue_repetitions=repeat,
                   structured_exact=not failed and strict_json_match(text,c['expected_json']) if 'expected_json' in c else None,
                   selected_edit_exact=not failed and text.strip()==c['exact_reference'] if c.get('exact_reference') else None)
            if seen:
                d.update(repair_diagnostics(text,c['corruption']))
                if failed:
                    for key in ['exact_full_answer','outside_correction_preserved','correct_anchor_present_once']:d[key]=False
                    d['correction_at_expected_slot']=None
            ds.append(d);details.append(d)
        primary=[d for d in ds if d['cohort']!='seen-training-fit'];fit=[d for d in ds if d['cohort']=='seen-training-fit']
        summary[side]=dict(attempted=len(ds),missing=49-len(ds),failures=sum(d['failed'] for d in ds),truncated=sum(d['truncated'] for d in ds),
                           primary=dict(available=len(primary),new_closed_exact=count([d for d in primary if d['cohort']=='new-development'],'structured_exact'),
                                        clock_exact=count([d for d in primary if d['kind']=='clock-state' and d['cohort']=='exposed-regression'],'structured_exact'),
                                        claim_exact=count([d for d in primary if d['kind']=='arrival-claim'],'structured_exact'),selected_edits=count(primary,'selected_edit_exact'),
                                        dialogue_repeat_flags=sum(d['dialogue_repeat_flag'] is True for d in primary),
                                        word_limits={cohort:{kind:count([d for d in primary if d['cohort']==cohort and d['kind']==kind],'word_limit_passed') for kind in ['dialogue','continue','rewrite','write']} for cohort in ['new-development','exposed-regression']}),
                           seen_training_fit=dict(available=len(fit),exact_full_answer=count(fit,'exact_full_answer'),outside_preserved=count(fit,'outside_correction_preserved'),
                                                  correction_at_preserved_slot=count(fit,'correction_at_expected_slot'),lexical_anchor_proxy=count(fit,'correct_anchor_present_once')))
    def save(n,value,private=False):
        fd=os.open(RUN/n,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600 if private else 0o644)
        with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.write('\n')
    save('scores.json',dict(summary=summary,details=details,seen_training_fit_excluded_from_primary=True,human_quality_ratings=0,
                           limits='All counts are small exposed/constructed diagnostics. Seen fit measures neither generalisation nor prose quality. Lexical anchors do not excuse changed surrounding prose. No automatic model promotion.'))
    writing=[c for c in cases if c['kind'] in ['dialogue','continue','rewrite','write'] and all(c['id'] in answers[s] and not answers[s][c['id']]['error'] and answers[s][c['id']]['finish_reason']!='length' for s in ['current-craft','candidate'])]
    packet=['# Current craft versus mixed candidate','','Fresh-context responses, random A/B labels per completed writing pair. Planned coverage is four new clearer-constraint tasks and17 exposed writing regressions; see each full prompt. No human ratings are recorded. Inspect practical movement, object identities, time, permission scope and writing quality. An ordinary allowed observation is not automatically an error; check the prompt’s exact resource policy. Seen training-fit responses are excluded.','']
    key=[];ballots=[];rng=random.SystemRandom()
    for c in writing:
        sides=['current-craft','candidate'];rng.shuffle(sides);key.append(dict(case_id=c['id'],**dict(zip('AB',sides))))
        packet+=['## '+c['id'],'',c['prompt'],'']
        for label,side in zip('AB',sides):packet+=['### Response '+label,'',answers[side][c['id']]['text'],'']
        for reviewer in ['reviewer-1','reviewer-2']:ballots.append(dict(case_id=c['id'],reviewer=reviewer,ratings=dict(A=None,B=None),preference=None,evidence=None))
    if not writing:packet+=['No completed writing pairs available.','']
    with (RUN/'REVIEW.md').open('x') as f:f.write('\n'.join(packet))
    save('blind-key.private.json',key,True)
    with (RUN/'human-ballots.blank.jsonl').open('x') as f:
        for r in ballots:f.write(json.dumps(r)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
