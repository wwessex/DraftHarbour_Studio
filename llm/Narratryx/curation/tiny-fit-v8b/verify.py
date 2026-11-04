"""Read-only verification of tiny fitting diagnostics, never literary release approval."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(Path(__file__).resolve().parent))
from foundation.validation import file_hash,read_jsonl,validate_dataset
from scoring import claim_match
from plan_checks import validate_plan
RUN=ROOT/'artifacts/tiny-fit-training-v8b';DATA=ROOT/'artifacts/tiny-fit-v8'
def verify():
 p=json.loads((RUN/'protocol.frozen.json').read_text());cfg=json.loads((RUN/'request.json').read_text());pre=json.loads((DATA/'preflight.json').read_text())
 assert validate_plan(p,cfg,pre)
 for group in ['input_hashes','protected_artifacts']:
  for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
 assert file_hash(Path(p['base_path'])/'model.safetensors')==p['base_weights_sha256']
 audit=json.loads((DATA/'loss-path-audit.json').read_text());assert audit['passed']
 for n,h in audit['installed_source_hashes'].items():assert file_hash(Path(n))==h
 assert len(validate_dataset(DATA/'records.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US']))==12
 tokens=read_jsonl(DATA/'train.tokens.jsonl');seen=read_jsonl(DATA/'cases.frozen.jsonl')[:12];allcases=read_jsonl(DATA/'cases.frozen.jsonl')
 masked={r['id']:sum(x==-100 for x in t['labels']) for r,t in zip(seen,tokens)};results={};response_total=0
 for side in ['base','candidate']:
  entries=read_jsonl(RUN/f'{side}.responses.jsonl');complete=json.loads((RUN/f'{side}.complete.json').read_text());assert complete['completed']
  assert file_hash(RUN/f'{side}.responses.jsonl')==complete['response_sha256']
  fitted=sum(r['exact_passed'] for r in entries[:12]);gate=fitted>=p['fit_gate']['required_seen_correct']
  expected=allcases if side=='candidate' and gate else seen
  assert [r['case_id'] for r in entries]==[c['id'] for c in expected]
  for c,r in zip(expected,entries):
   assert r['exact_passed']==claim_match(r['text'],c['expected_json'])
   assert r['protocol_sha256']==file_hash(RUN/'protocol.frozen.json')
   assert r['adapter_enabled']==(side=='candidate')
   assert r['finish_reason']!='length' and r['usage']['prompt_tokens_details']['cached_tokens']==0 and r['usage']['total_tokens']<=2048
   if r['cohort']=='seen-training':assert r['usage']['prompt_tokens']==masked[r['case_id']]
  results[side]=complete['scores'];response_total+=len(entries)
 completion=json.loads((RUN/'completion.json').read_text());progress=json.loads((RUN/'final-progress.json').read_text())
 assert completion['completed'] and completion['steps']==48 and not completion['model_promoted']
 assert completion['adapter_sha256']==file_hash(RUN/'adapter/adapters.safetensors')
 assert progress['is_completed'] and progress['step']==48 and not progress['warnings'] and not progress['error'] and progress['peak_memory_gb']<=10
 assert progress['num_tokens']==pre['expected_supervised_token_exposures']
 training=json.loads((RUN/'training.phase.json').read_text());assert training['completed'] and training['elapsed_seconds']<=1200
 final=json.loads((RUN/'service-final.json').read_text());initial=json.loads((RUN/'service-initial.json').read_text())
 assert not final['experiment_error']
 assert final['http_ready'] if initial['running'] else final['port_free'] and not final['started_by_experiment']
 assert json.loads((RUN/'experiment-complete.json').read_text())['completed']
 return dict(passed=True,scores=results,responses=response_total,training_steps=48,supervised_token_exposures=progress['num_tokens'],training_elapsed_seconds=training['elapsed_seconds'],peak_mlx_gb=progress['peak_memory_gb'],prompt_token_counts_match_training_masks=True,frozen_inputs_and_prior_artifacts_unchanged=True,base_weights_unchanged=True,app_model_unchanged=True,initial_service_state_preserved=True,no_literary_quality_claim=True,model_promoted=False)
if __name__=='__main__':
 report=verify()
 with (RUN/'final-verification.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps(report,indent=2))

def verify_transfer_control():
 import hashlib
 casepath=DATA/'cases.frozen.jsonl';cases=[c for c in read_jsonl(casepath) if c['cohort']!='seen-training']
 protocol=json.loads((RUN/'transfer-base.protocol.json').read_text());complete=json.loads((RUN/'transfer-base.complete.json').read_text());entries=read_jsonl(RUN/'transfer-base.responses.jsonl')
 assert protocol['post_hoc'] and complete['post_hoc'] and complete['completed'] and complete['cases']==24
 assert protocol['cases_sha256']==file_hash(casepath) and protocol['script_sha256']==file_hash(Path(__file__).parent/'transfer_base.py')
 assert protocol['primary_protocol_sha256']==file_hash(RUN/'protocol.frozen.json')
 assert complete['responses_sha256']==file_hash(RUN/'transfer-base.responses.jsonl')
 assert [r['case_id'] for r in entries]==[c['id'] for c in cases]
 scores={}
 for c,r in zip(cases,entries):
  assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest()
  assert r['exact_passed']==claim_match(r['text'],c['expected_json'])
  assert r['finish_reason']!='length' and r['usage']['prompt_tokens_details']['cached_tokens']==0 and r['usage']['total_tokens']<=2048
  scores.setdefault(c['cohort'],dict(passed=0,total=0));scores[c['cohort']]['total']+=1;scores[c['cohort']]['passed']+=r['exact_passed']
 assert scores==complete['scores']
 return dict(passed=True,post_hoc=True,cases=24,scores=scores,weights_and_cases_not_retuned=True)
