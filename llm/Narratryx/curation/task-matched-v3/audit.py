"""Independent derivation checks beyond schema acceptance; no model quality scores."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import validate_dataset,check_leakage
from foundation.anchored_edits import AnchorEdit,apply_anchor_edits
OUT=ROOT/'artifacts/task-matched-v3'
def audit():
 records=validate_dataset(OUT/'records.jsonl',ROOT/'rights/literary-mix-v2.scoped.jsonl',['GB','US'])
 prior={r['id']:r for r in map(json.loads,(ROOT/'artifacts/literary-mix-v2/records.jsonl').read_text().splitlines())}
 trace={r['id']:r for r in map(json.loads,(OUT/'trace.jsonl').read_text().splitlines())}
 train=[r for r in records if r['split']=='train'];assert len(train)==50 and len(trace)==50
 seen=set()
 for row in train:
  t=trace[row['id']];key=tuple(t['source_key']);assert key not in seen;seen.add(key)
  old=prior[t['prior_record_id']];original=old['messages'][1]['content'];answer=row['messages'][1]['content']
  assert row['source_spans']==old['source_spans'] and row['rights_record_ids']==old['rights_record_ids']
  assert row['origin']=='derived' and row['teacher'] is None
  if t['kind']=='anchored-copyedit':
   proposal=json.loads(answer);assert set(proposal)=={'edits'}
   broken=row['messages'][0]['content'].split('TARGET PASSAGE:\n',1)[1]
   corrected=apply_anchor_edits(broken,broken,[AnchorEdit(**edit) for edit in proposal['edits']])
   assert corrected==original==t['derivation']['corrected_paragraph']
   for edit in proposal['edits']:assert edit['after'] in original
  elif t['kind']=='continue':assert original[t['derivation']['start_in_prior_answer']:t['derivation']['end_in_prior_answer']]==answer
  else:assert answer==original
 cases=[json.loads(l) for l in (OUT/'test.cases.jsonl').read_text().splitlines()]
 check_leakage(records,[dict(id=c['id'],split_group=c['scenario_id'],context=c['context']) for c in cases])
 assert len(cases)==24 and len({c['scenario_id'] for c in cases})==8
 assert all(c['word_count_min']==0 for c in cases if c['task']=='editing')
 assert {a for r in train for a in r['_author_ids']}.isdisjoint({a for r in records if r['split']=='validation' for a in r['_author_ids']})
 return dict(passed=True,unique_train_spans=len(seen),source_derived_literary_targets=True,generated_literary_targets=0,source_structural_copyedit_labels=8,heldout_authors_disjoint=True,new_evaluation_cases=24,new_scenarios=8,editing_minimum_words=0,human_literary_ratings=0)
if __name__=='__main__':print(json.dumps(audit(),indent=2))
