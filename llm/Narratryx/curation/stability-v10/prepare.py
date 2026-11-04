"""Freeze a one-training-parameter stability ablation and explicit reused references."""
import copy,importlib.metadata,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl,validate_dataset
OLD=ROOT/'artifacts/balanced-training-v9';DATA=ROOT/'artifacts/balanced-fiction-v9';PLAN=ROOT/'artifacts/stability-v10-plan'
def save(name,value):
 with (PLAN/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def rows(name,values):
 with (PLAN/name).open('x') as f:
  for r in values:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def main():
 if PLAN.exists():raise ValueError('Refuse overwrite')
 parent=json.loads((OLD/'protocol.frozen.json').read_text())
 for group in ['input_hashes','protected_artifacts']:
  for n,h in parent[group].items():assert file_hash(ROOT/n)==h,n
 assert json.loads((OLD/'completion.json').read_text())['completed'] and (OLD/'experiment-failed.json').exists()
 environment=json.loads((OLD/'environment.json').read_text())
 current={n:importlib.metadata.version(n) for n in environment['packages']};assert current==environment['packages'],'References require matched recorded package versions'
 validated=validate_dataset(DATA/'records.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US']);assert sum(r['split']=='train' for r in validated)==92
 oldcfg=json.loads((OLD/'request.json').read_text());cfg=dict(oldcfg,learning_rate='5e-5')
 assert {k for k in cfg if cfg[k]!=oldcfg[k]}=={'learning_rate'}
 primary=read_jsonl(DATA/'primary.cases.frozen.jsonl');by={c['id']:c for c in primary}
 writing=['bf-craft-coat-dialogue','bf-craft-reel-dialogue','bf-craft-reel-continue','bf-craft-reel-write','bf-conservatory-continue','bf-rope-workshop-continue','bf-craft-coat-continue','bf-craft-coat-write']
 selected=[]
 for ident in writing:
  c=copy.deepcopy(by[ident]);c['original_evaluation_role']=c['evaluation_role'];c['evaluation_role']='exposed-writing-stability';selected.append(c)
 # Predeclared state positions cover future absent, past absent, past unknown,
 # due now, future unknown and known arrival across both schedule families.
 for kind in ['clock-state','arrival-claim']:
  pool=[c for c in primary if c['kind']==kind]
  for index in [0,2,4,7,9,11]:
   c=copy.deepcopy(pool[index]);c['original_evaluation_role']=c['evaluation_role'];c['evaluation_role']='exposed-'+kind;selected.append(c)
 edits=[c for c in primary if c['kind']=='selected-edit'];assert len(edits)==4
 for c in edits:
  c=copy.deepcopy(c);c['original_evaluation_role']=c['evaluation_role'];c['evaluation_role']='exposed-selected-edit';selected.append(c)
 assert len(selected)==24 and len({c['id'] for c in selected})==24
 PLAN.mkdir();save('request.proposed.json',cfg);rows('cases.frozen.jsonl',selected)
 inputs=dict(parent['input_hashes']);protected=dict(parent['protected_artifacts']);reference_summary={}
 for side,source in [('base','base'),('current-craft','current-craft'),('high-lr','candidate')]:
  path=OLD/f'{source}.responses.jsonl';answers={r['case_id']:r for r in read_jsonl(path)};subset=[]
  for c in selected:
   if c['id'] not in answers:continue
   r=answers[c['id']]
   import hashlib
   assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest()
   assert r['protocol_sha256']==file_hash(OLD/'protocol.frozen.json')
   assert r['messages_count']==1 and r['prior_assistant_messages']==0 and r['usage']['prompt_tokens_details']['cached_tokens']==0
   subset.append(r)
  rows(side+'.reference.jsonl',subset);reference_summary[side]=dict(rows=len(subset),missing=[c['id'] for c in selected if c['id'] not in answers],truncated=sum(r['finish_reason']=='length' for r in subset),source_path=str(path.relative_to(ROOT)),source_sha256=file_hash(path),source_protocol_sha256=file_hash(OLD/'protocol.frozen.json'),reused_not_fresh=True)
  inputs[str(path.relative_to(ROOT))]=file_hash(path)
 assert reference_summary['base']['rows']==24 and reference_summary['current-craft']['rows']==24 and reference_summary['high-lr']['rows']==22
 save('reference-provenance.json',reference_summary)
 for name in ['adapter/adapters.safetensors','adapter/adapter_config.json','completion.json','partial-verification.json','protocol.frozen.json']:
  p=OLD/name;protected[str(p.relative_to(ROOT))]=file_hash(p)
 paths=[PLAN/n for n in ['request.proposed.json','cases.frozen.jsonl','reference-provenance.json','base.reference.jsonl','current-craft.reference.jsonl','high-lr.reference.jsonl']]+[Path(__file__)]
 inputs.update({str(p.relative_to(ROOT)):file_hash(p) for p in paths})
 training=copy.deepcopy(parent['training']);training['learning_rate']='5e-5'
 protocol=dict(status='stability_ablation_prepared',created_on='2026-11-01',input_hashes=inputs,protected_artifacts=protected,base_path=parent['base_path'],base_weights_sha256=parent['base_weights_sha256'],training_steps=128,context_limit=2048,training=training,evaluation=dict(cases=24,writing_first=8,clock_cases=6,claim_cases=6,selected_edits=4,max_new_tokens=384,temperature=0,seed=42,repetition_penalty=1.0,all_cases_exposed=True,references_reused=True),ablation=dict(parameter='learning_rate',before='2e-4',after='5e-5',other_request_fields_unchanged=True),resource_stop=copy.deepcopy(parent['resource_stop']),scope='One local lower-rate stability ablation; no app changes, new teaching targets, paid jobs, corpus uploads, promotion or publication.',limitations=['Failure-enriched exposed suite, not a fresh benchmark.','High-rate reference has22 attempted cases; two remain missing, not silently completed.','One reduced-rate model cannot establish optimal rate or literary quality.','Exact speaker-line repetition and word limits are proxies, not human craft ratings.'],reference_environment=current)
 save('protocol.proposed.frozen.json',protocol)
 print('Frozen24 exposed tests, verified references and128-update request; learning rate is the only changed request field.')
if __name__=='__main__':main()
