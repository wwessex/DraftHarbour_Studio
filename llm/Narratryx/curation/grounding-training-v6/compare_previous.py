"""Paired exposed-diagnostic comparison, with baseline reproduction checked explicitly."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'artifacts/grounding-training-v5'
NEW=ROOT/'artifacts/grounding-training-v6'
def read(path):return [json.loads(s) for s in path.read_text().splitlines()]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    for folder in [OLD,NEW]:
        protocol=json.loads((folder/'protocol.frozen.json').read_text())
        for name,value in protocol['input_hashes'].items():assert sha(ROOT/name)==value,name
        assert json.loads((folder/'experiment-complete.json').read_text())['completed']
    a=read(OLD/'cases.frozen.jsonl');b=read(NEW/'cases.frozen.jsonl')
    assert [(c['id'],c['prompt']) for c in a]==[(c['id'],c['prompt']) for c in b]
    baselines={}
    for side in ['base','current-craft']:
        left=read(OLD/f'{side}.responses.jsonl');right=read(NEW/f'{side}.responses.jsonl')
        assert [r['case_id'] for r in left]==[r['case_id'] for r in right]
        equal=sum(x['text']==y['text'] for x,y in zip(left,right));assert equal==64
        baselines[side]=dict(identical_answers=equal,total=64)
    before={r['case_id']:r for r in json.loads((OLD/'scores.json').read_text())['details'] if r['condition']=='candidate'}
    after={r['case_id']:r for r in json.loads((NEW/'scores.json').read_text())['details'] if r['condition']=='candidate'}
    paired=[]
    for c in b:
        changes={}
        for key in ['clock_exact','exact_repair','word_limit_passed','dialogue_turn_proxy']:
            if key=='word_limit_passed' and c.get('word_count_min') is None and c.get('word_count_max') is None:continue
            x=before[c['id']][key];y=after[c['id']][key]
            if x is not None:changes[key]=dict(before=x,after=y)
        paired.append(dict(case_id=c['id'],original_role=c['evaluation_role'],kind=c['kind'],checks=changes))
    out=dict(exposed_diagnostics_only=True,changed_parameter='learning_rate',before='5e-6',after='5e-5',baseline_reproduction=baselines,cases=paired,human_quality_ratings=0,model_promoted=False)
    with (NEW/'paired-v5-v6.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
    for key in ['clock_exact','exact_repair','word_limit_passed','dialogue_turn_proxy']:
        changes=[r['checks'][key] for r in paired if key in r['checks']]
        print(key,dict(total=len(changes),fail_to_pass=sum(not d['before'] and d['after'] for d in changes),pass_to_fail=sum(d['before'] and not d['after'] for d in changes)))
if __name__=='__main__':main()
