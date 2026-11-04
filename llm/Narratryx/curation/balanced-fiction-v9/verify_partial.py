"""Validate a failed evaluation's saved evidence; never declare the full experiment passed."""
import hashlib,json,sys
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(Path(__file__).resolve().parent))
from foundation.validation import file_hash,read_jsonl,validate_dataset
from plan_checks import validate_plan
RUN=ROOT/'artifacts/balanced-training-v9';DATA=ROOT/'artifacts/balanced-fiction-v9'
def verify():
 p=json.loads((RUN/'protocol.frozen.json').read_text());cfg=json.loads((RUN/'request.json').read_text());pre=json.loads((DATA/'tokenizer-preflight.json').read_text());selection=json.loads((DATA/'selection.json').read_text())
 assert validate_plan(p,cfg,pre,selection)
 for group in ['input_hashes','protected_artifacts']:
  for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
 assert file_hash(Path(p['base_path'])/'model.safetensors')==p['base_weights_sha256']
 records=validate_dataset(DATA/'records.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US']);assert sum(r['split']=='train' for r in records)==92 and sum(r['split']=='validation' for r in records)==16
 focus={r['id'] for r in read_jsonl(ROOT/'artifacts/tiny-fit-v8/records.jsonl')};freq=Counter(selection['presentation_order']);assert len(freq)==92 and sum(freq.values())==128 and all(v==(4 if k in focus else 1) for k,v in freq.items())
 cases=read_jsonl(DATA/'primary.cases.frozen.jsonl');total=0;hashes={}
 for side in ['base','current-craft','candidate']:
  rows=read_jsonl(RUN/f'{side}.responses.jsonl');expected=45 if side=='candidate' else 72;assert len(rows)==expected
  assert [r['case_id'] for r in rows]==[c['id'] for c in cases[:expected]]
  adapter=RUN/'adapter/adapters.safetensors' if side=='candidate' else ROOT/'artifacts/craft-training-v2/adapter/adapters.safetensors'
  for i,(c,r) in enumerate(zip(cases,rows)):
   assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest() and r['protocol_sha256']==file_hash(RUN/'protocol.frozen.json')
   assert r['messages_count']==1 and r['prior_assistant_messages']==0 and r['usage']['prompt_tokens_details']['cached_tokens']==0 and r['usage']['prompt_tokens']+r['usage']['completion_tokens']<=2048
   assert r['error'] is None and r['adapter_enabled']==(side!='base') and r['adapter_sha256']==file_hash(adapter)
   assert (r['finish_reason']=='length')==(side=='candidate' and i==44)
  if side!='candidate':
   marker=json.loads((RUN/f'{side}.complete.json').read_text());assert marker['completed'] and marker['cases']==72 and marker['response_sha256']==file_hash(RUN/f'{side}.responses.jsonl')
  total+=len(rows);hashes[side]=file_hash(RUN/f'{side}.responses.jsonl')
 assert total==189 and not (RUN/'candidate.complete.json').exists() and not (RUN/'experiment-complete.json').exists()
 assert json.loads((RUN/'experiment-failed.json').read_text())['automatic_retry'] is False
 progress=json.loads((RUN/'final-progress.json').read_text());completion=json.loads((RUN/'completion.json').read_text());phase=json.loads((RUN/'training.phase.json').read_text())
 assert progress['is_completed'] and progress['step']==128 and not progress['error'] and not progress['warnings'] and progress['peak_memory_gb']<=10 and progress['num_tokens']==10173
 assert completion['completed'] and completion['steps']==128 and completion['adapter_sha256']==file_hash(RUN/'adapter/adapters.safetensors') and not completion['model_promoted']
 assert phase['completed'] and phase['elapsed_seconds']<=1200
 initial=json.loads((RUN/'service-initial.json').read_text());final=json.loads((RUN/'service-final.json').read_text());assert final['experiment_error']
 assert final['http_ready'] if initial['running'] else final['port_free'] and not final['started_by_experiment']
 ballots=read_jsonl(RUN/'partial-human-ballots.blank.jsonl');assert len(ballots)==40 and all(r['preference'] is None and r['evidence'] is None and all(v is None for v in r['ratings'].values()) for r in ballots)
 assert (RUN/'partial-key.private.json').stat().st_mode & 0o777==0o600
 return dict(evidence_integrity_passed=True,training_completed=True,training_steps=128,training_presentations=128,unique_training_lessons=92,supervised_token_exposures=10173,training_elapsed_seconds=phase['elapsed_seconds'],peak_mlx_gb=progress['peak_memory_gb'],evaluation_complete=False,evaluation_stopped_on_truncation=True,attempted_responses=total,complete_responses=188,truncated_responses=1,candidate_attempted=45,candidate_planned=108,candidate_unattempted=63,response_sha256=hashes,base_weights_and_prior_models_unchanged=True,selected_app_model_unchanged=True,initial_service_state_preserved=True,model_promoted=False,human_quality_ratings=0)
if __name__=='__main__':
 report=verify()
 with (RUN/'partial-verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps(report,indent=2))
