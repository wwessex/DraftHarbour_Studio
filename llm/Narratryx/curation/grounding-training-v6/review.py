"""Separate mechanical diagnostics from blinded prose review; no literary score."""
from pathlib import Path
import hashlib,json,os,random,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.literary_diagnostics import quoted_dialogue_blocks
from scoring import clock_match
RUN=ROOT/'artifacts/grounding-training-v6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(p):return [json.loads(s) for s in p.read_text().splitlines()]
def save(name,value,private=False):
    fd=os.open(RUN/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600 if private else 0o644)
    with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
    protocol=json.loads((RUN/'protocol.frozen.json').read_text())
    for name,h in protocol['input_hashes'].items():assert sha(ROOT/name)==h,name
    cases=rows(RUN/'cases.frozen.jsonl');sides=protocol['model_conditions'];responses={};details=[];summary={}
    for side in sides:
        entries=rows(RUN/f'{side}.responses.jsonl')
        assert [r['case_id'] for r in entries]==[c['id'] for c in cases]
        complete=json.loads((RUN/f'{side}.complete.json').read_text())
        assert complete['completed'] and complete['cases']==64
        assert sha(RUN/f'{side}.responses.jsonl')==complete['response_sha256']
        responses[side]={r['case_id']:r for r in entries}
        for case,row in zip(cases,entries):
            assert row['prompt_sha256']==hashlib.sha256(case['prompt'].encode()).hexdigest()
            assert row['protocol_sha256']==sha(RUN/'protocol.frozen.json')
            assert row['messages_count']==1 and row['prior_assistant_messages']==0
            assert row['usage']['prompt_tokens_details']['cached_tokens']==0
            assert row['usage']['prompt_tokens']+row['usage']['completion_tokens']<=2048
            assert row['error'] is None and row['finish_reason']!='length'
            text=row['text'];words=len(text.split());lo=case.get('word_count_min');hi=case.get('word_count_max')
            details.append(dict(condition=side,case_id=case['id'],role=case['evaluation_role'],kind=case['kind'],words=words,
                word_limit_passed=(lo is None or words>=lo) and (hi is None or words<=hi),
                exact_repair=text.strip()==case['exact_reference'] if case.get('exact_reference') is not None else None,
                clock_exact=clock_match(text,case['expected_json']) if case['kind']=='clock-state' else None,
                dialogue_turn_proxy=4<=quoted_dialogue_blocks(text)<=6 if case['kind']=='dialogue' else None))
        own=[d for d in details if d['condition']==side]
        def count(items,key):return dict(passed=sum(d[key] is True for d in items),total=sum(d[key] is not None for d in items))
        summary[side]={}
        for role in sorted({d['role'] for d in own}):
            subset=[d for d in own if d['role']==role]
            summary[side][role]=dict(requests=len(subset),clock_exact=count(subset,'clock_exact'),exact_repair=count(subset,'exact_repair'),
                dialogue_turn_proxy=count(subset,'dialogue_turn_proxy'),word_limits={kind:count([d for d in subset if d['kind']==kind],'word_limit_passed') for kind in sorted({d['kind'] for d in subset})})
    save('scores.json',dict(summary=summary,details=details,literary_quality_ratings=None,interpretation='Clock/repair/format diagnostics only. Retention cases are exposed. No automated literary-quality or Muse-equivalence rating.'))
    key=[];ballots=[];rng=random.SystemRandom();prose=[c for c in cases if c['kind']!='clock-state']
    intro=['# Blinded local-model prose comparison','','Forty prose cases, three conditions, randomised A/B/C separately per case. No human ratings exist yet. All cases were exposed in the previous trial; role names distinguish original cohorts, not current novelty. This is a learning-rate ablation, not a fresh independent benchmark.','','Rate usefulness, voice, coherence, viewpoint/tense, grounded analysis and the requested craft skill from 1–5. Record evidence, invented facts and contradictions. Do not reward extra length. Editing has no minimum word count. Clock scores are reported separately. Two independent reviewers should compare responses before any model promotion. Keep the private key separate until ballots are submitted.','']
    packet=intro.copy();sections={}
    for case in prose:
        conditions=sides.copy();rng.shuffle(conditions);key.append(dict(case_id=case['id'],**dict(zip('ABC',conditions))))
        section=['## '+case['id'],'','Role: '+case['evaluation_role'],'',case['prompt'],'','Known facts: '+'; '.join(case.get('established_facts',[])),'','Unknowns: '+'; '.join(case.get('unknowns',[])),'']
        for label,side in zip('ABC',conditions):section+=['### Response '+label,'',responses[side][case['id']]['text'],'']
        packet+=section;sections[case['id']]=section
        for reviewer in ['reviewer-1','reviewer-2']:ballots.append(dict(case_id=case['id'],reviewer=reviewer,ratings=dict(A=None,B=None,C=None),preference=None,evidence=None))
    (RUN/'BLIND-REVIEW.md').open('x').write('\n'.join(packet)+'\n');save('blind-key.private.json',key,True)
    with (RUN/'human-ballots.blank.jsonl').open('x') as f:
        for b in ballots:f.write(json.dumps(b)+'\n')
    picks=['ge-transfer-canal-lock-analysis','ge-transfer-planetarium-analysis','ge-transfer-puppet-workshop-rewrite','ge-transfer-bookbinding-room-continue','ge-transfer-canal-lock-selected-edit','seed-library-dialogue','rehearsal-room-pacing','mountain-shelter-continue']
    quick=intro+['A suggested eight-case starting subset follows. Full coverage remains in BLIND-REVIEW.md.','']
    for name in picks:quick+=sections[name]
    (RUN/'QUICK-REVIEW.md').open('x').write('\n'.join(quick)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
