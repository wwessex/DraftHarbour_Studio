"""Exploratory component diagnostics; strict joint accuracy remains primary."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'artifacts/grounding-training-v7'
def decode(text,kind):
 def pairs(items):
  out={}
  for k,v in items:
   if k in out:raise ValueError('duplicate key')
   out[k]=v
  return out
 try:d=json.loads(text,object_pairs_hook=pairs,parse_constant=lambda s:(_ for _ in ()).throw(ValueError(s)))
 except (TypeError,ValueError):return None
 keys={'state','minutes_to_schedule'} if kind=='clock-state' else {'verdict','minutes_to_schedule','arrival_state'}
 if not isinstance(d,dict) or set(d)!=keys or type(d['minutes_to_schedule']) is not int:return None
 if any(type(d[k]) is not str for k in keys-{'minutes_to_schedule'}):return None
 states={'arrived','not_established','not_yet_due','due_now','overdue'}
 if d['state' if kind=='clock-state' else 'arrival_state'] not in states:return None
 if kind=='arrival-claim' and d['verdict'] not in {'supported','contradicted','not_established'}:return None
 return d

def main():
 cases=[json.loads(s) for s in (RUN/'cases.frozen.jsonl').read_text().splitlines()];summary={}
 for side in ['base','current-craft','candidate']:
  answers={r['case_id']:r for r in map(json.loads,(RUN/f'{side}.responses.jsonl').read_text().splitlines())};summary[side]={}
  for kind in ['clock-state','arrival-claim']:
   own=[c for c in cases if c['kind']==kind];counts={k:0 for k in own[0]['expected_json']};valid=0
   for c in own:
    d=decode(answers[c['id']]['text'],kind)
    if d is not None:
     valid+=1
     for k,expected in c['expected_json'].items():counts[k]+=d[k]==expected
   summary[side][kind]=dict(total=len(own),valid_strict_schema=valid,field_matches=counts)
 result=dict(exploratory_not_primary=True,no_literary_quality_inference=True,summary=summary)
 with (RUN/'component-diagnostics.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
