"""Compare only the same exposed retention cases; fresh cohorts differ."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'artifacts/grounding-training-v6';NEW=ROOT/'artifacts/grounding-training-v7'
def rows(p):return [json.loads(s) for s in p.read_text().splitlines()]
def main():
 oldcases={r['id']:r for r in rows(OLD/'cases.frozen.jsonl')}
 cases=[r for r in rows(NEW/'cases.frozen.jsonl') if r['evaluation_role']=='exposed-retention'];assert len(cases)==24
 for c in cases:assert c['prompt']==oldcases[c['id']]['prompt']
 baseline={}
 for side in ['base','current-craft']:
  a={r['case_id']:r for r in rows(OLD/f'{side}.responses.jsonl')};b={r['case_id']:r for r in rows(NEW/f'{side}.responses.jsonl')}
  identical=sum(a[c['id']]['text']==b[c['id']]['text'] for c in cases);assert identical==24
  baseline[side]=dict(identical_answers=identical,total=24)
 scores=[]
 for folder in [OLD,NEW]:scores.append({r['case_id']:r for r in json.loads((folder/'scores.json').read_text())['details'] if r['condition']=='candidate'})
 changes=[]
 for c in cases:
  checks={}
  for key in ['exact_repair','word_limit_passed','dialogue_turn_proxy']:
   if key=='word_limit_passed' and c.get('word_count_min') is None and c.get('word_count_max') is None:continue
   before=scores[0][c['id']][key];after=scores[1][c['id']][key]
   if before is not None:checks[key]=dict(before=before,after=after)
  changes.append(dict(case_id=c['id'],checks=checks))
 result=dict(passed=True,exposed_retention_only=True,baseline_reproduction=baseline,cases=changes,fresh_cohorts_not_compared_to_old_tests=True,human_quality_ratings=0)
 with (NEW/'retention-v6-v7.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print('Matched24 identical-prompt retention cases; fresh baselines reproduced24/24 each.')
if __name__=='__main__':main()
