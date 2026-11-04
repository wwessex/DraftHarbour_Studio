"""Mechanical scoring and blinded human packet, never automated literary ratings."""
from pathlib import Path
import sys
import hashlib,json,random
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.literary_diagnostics import quoted_dialogue_blocks
RUN=ROOT/'artifacts/task-matched-training-v3'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(name,value):
    with (RUN/name).open('x') as f:json.dump(value,f,indent=2)
def main():
    protocol=json.loads((RUN/'protocol.frozen.json').read_text())
    for name,expected in protocol['input_hashes'].items():assert sha(ROOT/name)==expected,name
    cases=[json.loads(line) for line in (ROOT/protocol['test_cases_path']).read_text().splitlines()]
    sides=protocol['model_conditions']
    responses={side:{r['case_id']:r for r in map(json.loads,(RUN/f'{side}.responses.jsonl').read_text().splitlines())} for side in sides}
    details=[];summary={}
    for side,answers in responses.items():
        assert set(answers)=={case['id'] for case in cases}
        for case in cases:
            row=answers[case['id']];text=row['text'];words=len(text.split())
            assert row['prompt_sha256']==hashlib.sha256(case['prompt'].encode()).hexdigest()
            assert row['protocol_sha256']==sha(RUN/'protocol.frozen.json')
            assert row['messages_count']==1 and row['prior_assistant_messages']==0
            assert row['usage'].get('prompt_tokens_details',{}).get('cached_tokens',0)==0
            assert row['usage']['prompt_tokens']+row['usage']['completion_tokens']<=2048
            minimum=case['word_count_min'];maximum=case['word_count_max']
            details.append(dict(condition=side,case_id=case['id'],kind=case['kind'],words=words,error=row['error'],truncated=row['finish_reason']=='length',word_limit_passed=(not minimum or words>=minimum) and (maximum is None or words<=maximum),dialogue_blocks=quoted_dialogue_blocks(text) if case['kind']=='dialogue' else None,dialogue_turn_proxy_passed=4<=quoted_dialogue_blocks(text)<=6 if case['kind']=='dialogue' else None,minimal_repair_exact=text.strip()==case['exact_reference'] if case['kind']=='editing' else None))
        own=[row for row in details if row['condition']==side]
        summary[side]=dict(requests=len(own),errors=sum(bool(row['error']) for row in own),truncated=sum(row['truncated'] for row in own),dialogue_turn_proxy_passes=sum(row['dialogue_turn_proxy_passed'] is True for row in own),exact_minimal_repairs=sum(row['minimal_repair_exact'] is True for row in own),format_checks={kind:dict(passed=sum(row['word_limit_passed'] for row in own if row['kind']==kind),total=sum(row['kind']==kind for row in own)) for kind in sorted({row['kind'] for row in own})})
    save('scores.json',dict(summary=summary,details=details,literary_quality_ratings=None,interpretation='Mechanical formatting and exact minimal duplication repair only. No style, coherence, dialogue, pacing or Muse-equivalence quality score inferred.'))
    randomizer=random.SystemRandom();key=[];ballots=[]
    packet=['# Blinded three-condition literary comparison','', 'A/B/C are randomised independently for each case. No human ratings exist yet. Compare only the requested skill. Short editing output is valid; editing has no minimum length. Canonical continuations are not reference answers. Do not reward longer answers or extra explanation.','', 'Score 1–5 for usefulness, voice, viewpoint/tense, coherence, grounded analysis, dialogue/subtext or pacing as appropriate. Record concrete evidence and facts contradicted or invented. Two independent reviewers should cover a representative subset; adjudicate disagreement before promotion. Keep the condition key separate until ballots are submitted.','']
    for case in cases:
        conditions=sides.copy();randomizer.shuffle(conditions)
        key.append(dict(case_id=case['id'],**dict(zip('ABC',conditions))))
        packet += ['## '+case['id'],'',case['prompt'],'','Known facts: '+'; '.join(case['established_facts']),'','Unknowns: '+'; '.join(['Unstated motives, relationships and unseen outcomes remain unknown.']),'']
        for label,side in zip('ABC',conditions):packet += ['### Response '+label,'',responses[side][case['id']]['text'],'']
        for reviewer in ['reviewer-1','reviewer-2']:
            ballots.append(dict(case_id=case['id'],reviewer=reviewer,ratings={'A':None,'B':None,'C':None},preference=None,evidence=None))
    with (RUN/'BLIND-REVIEW.md').open('x') as f:f.write('\n'.join(packet)+'\n')
    save('blind-key.private.json',key)
    with (RUN/'human-ballots.blank.jsonl').open('x') as f:
        for row in ballots:f.write(json.dumps(row)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
