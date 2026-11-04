"""Verify saved balanced-trial evidence without inference, training or promotion."""
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
 records=validate_dataset(DATA/'records.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US'])
 assert sum(r['split']=='train' for r in records)==92 and sum(r['split']=='validation' for r in records)==16
 focus={r['id'] for r in read_jsonl(ROOT/'artifacts/tiny-fit-v8/records.jsonl')};counts=Counter(selection['presentation_order'])
 assert len(counts)==92 and sum(counts.values())==128 and all(v==(4 if k in focus else 1) for k,v in counts.items())
 primary=read_jsonl(DATA/'primary.cases.frozen.jsonl');extra=read_jsonl(DATA/'candidate-extra.cases.frozen.jsonl');assert len(primary)==72 and len(extra)==36
 total=0
 for side in p['model_conditions']:
  cases=primary+extra if side=='candidate' else primary;rows=read_jsonl(RUN/f'{side}.responses.jsonl');complete=json.loads((RUN/f'{side}.complete.json').read_text())
  assert complete['completed'] and complete['cases']==len(cases) and complete['response_sha256']==file_hash(RUN/f'{side}.responses.jsonl')
  assert [r['case_id'] for r in rows]==[c['id'] for c in cases]
  adapter=RUN/'adapter/adapters.safetensors' if side=='candidate' else ROOT/'artifacts/craft-training-v2/adapter/adapters.safetensors'
  for c,r in zip(cases,rows):
   assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest() and r['protocol_sha256']==file_hash(RUN/'protocol.frozen.json')
   assert r['messages_count']==1 and r['prior_assistant_messages']==0 and r['usage']['prompt_tokens_details']['cached_tokens']==0
   assert r['usage']['prompt_tokens']+r['usage']['completion_tokens']<=2048 and not r['error'] and r['finish_reason']!='length'
   assert r['adapter_enabled']==(side!='base') and r['adapter_sha256']==file_hash(adapter)
  total+=len(rows)
 assert total==252
 completion=json.loads((RUN/'completion.json').read_text());progress=json.loads((RUN/'final-progress.json').read_text())
 assert completion['completed'] and completion['steps']==128 and not completion['model_promoted'] and completion['adapter_sha256']==file_hash(RUN/'adapter/adapters.safetensors')
 assert progress['is_completed'] and progress['step']==128 and not progress['error'] and not progress['warnings'] and progress['peak_memory_gb']<=10 and progress['num_tokens']==10173
 phase=json.loads((RUN/'training.phase.json').read_text());assert phase['completed'] and phase['elapsed_seconds']<=1200
 initial=json.loads((RUN/'service-initial.json').read_text());final=json.loads((RUN/'service-final.json').read_text());assert not final['experiment_error']
 assert final['http_ready'] if initial['running'] else final['port_free'] and not final['started_by_experiment']
 ballots=read_jsonl(RUN/'human-ballots.blank.jsonl');assert len(ballots)==96 and all(r['preference'] is None and r['evidence'] is None and all(v is None for v in r['ratings'].values()) for r in ballots)
 assert (RUN/'blind-key.private.json').stat().st_mode & 0o777==0o600
 assert json.loads((RUN/'experiment-complete.json').read_text())['completed']
 return dict(passed=True,matched_responses=total,primary_comparison_responses=216,extra_exposed_grounding_checks=36,unique_training_lessons=92,training_presentations=128,training_steps=128,supervised_token_exposures=10173,training_elapsed_seconds=phase['elapsed_seconds'],peak_mlx_gb=progress['peak_memory_gb'],frozen_inputs_and_prior_models_unchanged=True,base_weights_unchanged=True,selected_model_unchanged=True,initial_service_state_preserved=True,human_quality_ratings=0,model_promoted=False)
if __name__=='__main__':
 report=verify()
 with (RUN/'final-verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps(report,indent=2))
