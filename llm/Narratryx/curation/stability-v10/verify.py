"""Verify completed or stopped small-suite evidence without claiming literary approval."""
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(Path(__file__).resolve().parent))
from foundation.validation import file_hash,read_jsonl,validate_dataset
from plan_checks import validate_ablation
from stability_checks import repeated_dialogue
RUN=ROOT/'artifacts/stability-v10';PLAN=ROOT/'artifacts/stability-v10-plan'
def verify():
 p=json.loads((RUN/'protocol.frozen.json').read_text());cfg=json.loads((RUN/'request.json').read_text());old=json.loads((ROOT/'artifacts/balanced-training-v9/request.json').read_text())
 assert validate_ablation(old,cfg,p)
 for group in ['input_hashes','protected_artifacts']:
  for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
 assert file_hash(Path(p['base_path'])/'model.safetensors')==p['base_weights_sha256']
 data=ROOT/'artifacts/balanced-fiction-v9';assert len([r for r in validate_dataset(data/'records.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US']) if r['split']=='train'])==92
 cases=read_jsonl(PLAN/'cases.frozen.jsonl');rows=read_jsonl(RUN/'candidate.responses.jsonl') if (RUN/'candidate.responses.jsonl').exists() else []
 assert len(cases)==24 and [r['case_id'] for r in rows]==[c['id'] for c in cases[:len(rows)]]
 truncated=0
 for c,r in zip(cases,rows):
  assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest() and r['protocol_sha256']==file_hash(RUN/'protocol.frozen.json')
  assert r['messages_count']==1 and r['prior_assistant_messages']==0 and r['adapter_enabled'] and r['error'] is None
  assert r['usage']['prompt_tokens_details']['cached_tokens']==0 and r['usage']['prompt_tokens']+r['usage']['completion_tokens']<=2048
  assert r['adapter_sha256']==file_hash(RUN/'adapter/adapters.safetensors')
  truncated+=r['finish_reason']=='length'
  if c['kind']=='dialogue':assert r['maximum_identical_dialogue_body_repetitions']==repeated_dialogue(r['text'])
 complete=(RUN/'candidate.complete.json').exists()
 if complete:
  marker=json.loads((RUN/'candidate.complete.json').read_text());assert marker['completed'] and marker['cases']==24 and len(rows)==24 and truncated==0 and marker['responses_sha256']==file_hash(RUN/'candidate.responses.jsonl')
  assert (RUN/'experiment-complete.json').exists()
 else:
  assert (RUN/'experiment-failed.json').exists() and not (RUN/'experiment-complete.json').exists()
  assert truncated<=1 and (not truncated or rows[-1]['finish_reason']=='length')
 references=json.loads((PLAN/'reference-provenance.json').read_text())
 for side in ['base','current-craft','high-lr']:
  ref=read_jsonl(PLAN/(side+'.reference.jsonl'));assert len(ref)==references[side]['rows'] and references[side]['reused_not_fresh']
  assert file_hash(ROOT/references[side]['source_path'])==references[side]['source_sha256']
  for r in ref:
   c=next(c for c in cases if c['id']==r['case_id']);assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest() and r['protocol_sha256']==references[side]['source_protocol_sha256']
 assert references['high-lr']['rows']==22 and len(references['high-lr']['missing'])==2
 progress=json.loads((RUN/'final-progress.json').read_text());model=json.loads((RUN/'completion.json').read_text());phase=json.loads((RUN/'training.phase.json').read_text())
 assert progress['is_completed'] and progress['step']==128 and progress['num_tokens']==10173 and progress['peak_memory_gb']<=10 and not progress['warnings'] and not progress['error']
 assert model['completed'] and model['steps']==128 and not model['model_promoted'] and model['adapter_sha256']==file_hash(RUN/'adapter/adapters.safetensors')
 assert phase['completed'] and phase['elapsed_seconds']<=1200
 initial=json.loads((RUN/'service-initial.json').read_text());final=json.loads((RUN/'service-final.json').read_text())
 assert not final['experiment_error'] if complete else final['experiment_error']
 assert final['http_ready'] if initial['running'] else final['port_free'] and not final['started_by_experiment']
 writing=[r for r in rows if r['kind'] in ['dialogue','continue','write'] and r['finish_reason']!='length'];ballots=read_jsonl(RUN/'human-ballots.blank.jsonl') if writing else []
 assert len(ballots)==2*len(writing) and all(r['preference'] is None and r['evidence'] is None and all(v is None for v in r['ratings'].values()) for r in ballots)
 assert (RUN/'blind-key.private.json').stat().st_mode & 0o777==0o600
 return dict(evidence_integrity_passed=True,training_completed=True,training_steps=128,unique_training_lessons=92,training_presentations=128,only_changed_request_field='learning_rate',old_rate='2e-4',new_rate='5e-5',training_elapsed_seconds=phase['elapsed_seconds'],peak_mlx_gb=progress['peak_memory_gb'],evaluation_complete=complete,new_requests=len(rows),truncated_responses=truncated,planned_requests=24,reused_base_rows=24,reused_current_craft_rows=24,reused_high_rate_rows=22,missing_high_rate_reference_rows=2,frozen_inputs_and_prior_models_unchanged=True,selected_model_unchanged=True,initial_service_state_preserved=True,human_quality_ratings=0,model_promoted=False)
if __name__=='__main__':
 report=verify()
 with (RUN/'verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps(report,indent=2))
