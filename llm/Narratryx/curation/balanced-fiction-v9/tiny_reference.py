"""Compare only the same exposed tiny diagnostics, not different fresh cohorts."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];RUN=ROOT/'artifacts/balanced-training-v9';DATA=ROOT/'artifacts/balanced-fiction-v9';OLD=ROOT/'artifacts/tiny-fit-training-v8b'
def rows(p):return [json.loads(s) for s in p.read_text().splitlines()]
def main():
 oldcases={c['id']:c for c in rows(ROOT/'artifacts/tiny-fit-v8/cases.frozen.jsonl')};extra=rows(DATA/'candidate-extra.cases.frozen.jsonl')
 old={r['case_id']:r for r in rows(OLD/'candidate.responses.jsonl')};new={r['case_id']:r for r in rows(RUN/'candidate.responses.jsonl')}
 details=[];summary={}
 for c in extra:
  assert c['prompt']==oldcases[c['id']]['prompt']
  role=c['evaluation_role'];summary.setdefault(role,dict(tiny_correct=0,balanced_correct=0,total=0));summary[role]['total']+=1
  from scoring import claim_match
  before=claim_match(old[c['id']]['text'],c['expected_json']);after=claim_match(new[c['id']]['text'],c['expected_json'])
  summary[role]['tiny_correct']+=before;summary[role]['balanced_correct']+=after
  details.append(dict(case_id=c['id'],role=role,tiny_correct=before,balanced_correct=after))
 result=dict(exposed_diagnostic_only=True,summary=summary,details=details,not_an_independent_literary_benchmark=True)
 with (RUN/'tiny-reference-comparison.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
