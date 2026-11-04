"""Read-only source/task separation audit for the prepared claim curriculum."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.arrival_claims import overdue_claim
from foundation.validation import file_hash,read_jsonl,validate_dataset
OUT=ROOT/'artifacts/arrival-claims-v1'
def verify():
 protocol=json.loads((OUT/'protocol.proposed.frozen.json').read_text())
 for group in ['input_hashes','protected_artifacts']:
  for n,h in protocol[group].items():assert file_hash(ROOT/n)==h,n
 prior=read_jsonl(ROOT/'artifacts/grounding-balanced-v1/records.jsonl');new=read_jsonl(OUT/'records.jsonl')
 assert len(prior)==96 and len(new)==120
 for a,b in zip(prior,new[:96]):
  expected=copy.deepcopy(a);expected['dataset_version']='arrival-claims-v1';assert expected==b,a['id']
 parents={r['id']:r for r in read_jsonl(ROOT/'artifacts/grounding-editing-v1/records.jsonl')}
 trace=read_jsonl(OUT/'trace.jsonl');tuples=set()
 for audit,row in zip(trace,new[96:]):
  parent=parents[audit['parent_id']];state=audit['state']
  assert row['source_spans']==parent['source_spans'] and row['rights_record_ids']==parent['rights_record_ids']
  assert json.loads(row['messages'][-1]['content'])==overdue_claim(state['now'],state['scheduled'],state['arrived'])
  assert parent['messages'][0]['content'].split('SCHEDULE QUOTATION:\n',1)[1]==row['messages'][0]['content'].split('SCHEDULE QUOTATION:\n',1)[1]
  tuples.add((state['now'],state['scheduled'],state['arrived']))
 assert len(trace)==24 and len(tuples)==24
 tests=read_jsonl(OUT/'evaluation.cases.frozen.jsonl');assert len(tests)==40
 for case in tests:
  if case['kind'] in ['clock-state','arrival-claim']:
   state=json.loads(case['prompt'].split('TASK STATE:\n')[1]);assert (state['now'],state['scheduled'],state['arrived']) not in tuples
 assert all(r['teacher'] is None and r['origin']=='derived' for r in new)
 records=validate_dataset(OUT/'records.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US'])
 return dict(passed=True,retained_messages_spans_and_other_fields_unchanged=96,only_retained_metadata_change='dataset_version',new_deterministic_claims=24,new_source_works=0,evaluation_training_tuples_disjoint=True,records=len(records),human_quality_ratings=0)
if __name__=='__main__':print(json.dumps(verify(),indent=2))
