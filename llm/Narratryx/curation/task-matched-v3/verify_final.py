"""Verify completed experimental evidence without modifying frozen inputs or rating prose."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import validate_dataset
RUN=ROOT/'artifacts/task-matched-training-v3';DATA=ROOT/'artifacts/task-matched-v3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 protocol=json.loads((RUN/'protocol.frozen.json').read_text());snapshot=RUN/'frozen-inputs'
 for rel,value in protocol['input_hashes'].items():assert sha(ROOT/rel)==value==sha(snapshot/rel),rel
 for rel,value in protocol['protected_artifacts'].items():assert sha(ROOT/rel)==value,rel
 assert sha(Path(protocol['base_path'])/'model.safetensors')==protocol['base_weights_sha256']
 launch=json.loads((RUN/'launch-state.frozen.json').read_text());assert sha(ROOT/'configs/narratryx-craft-v1.json')==launch['model_pin_sha256']
 cases=[json.loads(l) for l in (ROOT/protocol['test_cases_path']).read_text().splitlines()];case_ids=[r['id'] for r in cases]
 responses=0
 for side in protocol['model_conditions']:
  path=RUN/f'{side}.responses.jsonl';complete=json.loads((RUN/f'{side}.complete.json').read_text());assert complete['completed'] and complete['cases']==24 and sha(path)==complete['response_sha256']
  rows=[json.loads(l) for l in path.read_text().splitlines()];assert [r['case_id'] for r in rows]==case_ids
  for row,case in zip(rows,cases):
   assert not row['error'] and row['messages_count']==1 and row['prior_assistant_messages']==0
   assert row['prompt_sha256']==hashlib.sha256(case['prompt'].encode()).hexdigest() and row['protocol_sha256']==sha(RUN/'protocol.frozen.json')
   assert row['usage'].get('prompt_tokens_details',{}).get('cached_tokens',0)==0
  responses+=len(rows)
 before=RUN/'current-craft.pre-resume-2026-10-26.jsonl';assert (RUN/'current-craft.responses.jsonl').read_bytes().startswith(before.read_bytes())
 audit=json.loads((RUN/'resume-audit-2026-10-26.json').read_text());assert sha(before)==audit['original_sha256'] and sha(Path(__file__).with_name('resume_evaluate.py'))==audit['resume_script_sha256']
 completion=json.loads((RUN/'completion.json').read_text());assert completion['completed'] and completion['steps']==13 and not completion['model_promoted']
 assert sha(RUN/'adapter/adapters.safetensors')==completion['adapter_sha256']
 rows=validate_dataset(DATA/'records.jsonl',ROOT/'rights/literary-mix-v2.scoped.jsonl',['GB','US']);assert len([r for r in rows if r['split']=='train'])==50
 ballots=[json.loads(l) for l in (RUN/'human-ballots.blank.jsonl').read_text().splitlines()];assert len(ballots)==48
 assert all(all(value is None for value in row['ratings'].values()) and row['preference'] is None and row['evidence'] is None for row in ballots)
 restored=json.loads((RUN/'service-restored.json').read_text());assert restored['http_ready'] and restored['selected_model_unchanged']
 report=dict(passed=True,matched_responses=responses,retained_preinterruption_responses=4,training_steps=13,frozen_inputs_unchanged=True,base_and_all_protected_adapters_unchanged=True,current_service_model_unchanged=True,training_records=50,generated_literary_targets=0,human_quality_ratings=0,model_promoted=False)
 with (RUN/'final-verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
