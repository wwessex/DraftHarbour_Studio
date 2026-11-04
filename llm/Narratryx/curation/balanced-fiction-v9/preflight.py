"""Verify exact token targets/masks and freeze a coherent balanced execution plan."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
from collections import Counter
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl,validate_dataset
DATA=ROOT/'artifacts/balanced-fiction-v9';HERE=Path(__file__).resolve().parent
LEDGER=ROOT/'rights/grounding-balanced-v1.scoped.jsonl'
def save(name,value):
 with (DATA/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def rows(name,values):
 with (DATA/name).open('x') as f:
  for r in values:f.write(json.dumps(r)+'\n')
def main():
 build=json.loads((DATA/'build-verification.json').read_text());selection=json.loads((DATA/'selection.json').read_text())
 for n,h in build['input_hashes'].items():assert file_hash(ROOT/n)==h,n
 proof=ROOT/'artifacts/tiny-fit-training-v8b';parent=json.loads((proof/'protocol.frozen.json').read_text())
 for group in ['input_hashes','protected_artifacts']:
  for n,h in parent[group].items():assert file_hash(ROOT/n)==h,n
 base=Path(parent['base_path'])
 from unsloth_cli.commands.train import _activate_mlx_transformers
 _activate_mlx_transformers(str(base),None)
 from unsloth_cli._inference import ensure_studio_backend_path
 ensure_studio_backend_path()
 from transformers import AutoTokenizer
 from unsloth_zoo.mlx.utils import create_batches
 from unsloth_zoo.mlx.trainer import MLXTrainingConfig
 tokenizer=AutoTokenizer.from_pretrained(str(base),local_files_only=True,trust_remote_code=False)
 records=read_jsonl(DATA/'records.jsonl');validate_dataset(DATA/'records.jsonl',LEDGER,['GB','US'])
 by_id={r['id']:r for r in records};tokens={};counts={}
 for r in records:
  prompt=tokenizer.apply_chat_template(r['messages'][:-1],tokenize=False,add_generation_prompt=True,enable_thinking=False);answer=r['messages'][-1]['content']
  a=tokenizer.encode(prompt,add_special_tokens=False);b=tokenizer.encode(answer,add_special_tokens=False)
  assert tokenizer.decode(b,skip_special_tokens=False)==answer
  ids=a+b+[tokenizer.eos_token_id];assert len(ids)<=2048,r['id']
  tokens[r['id']]=dict(input_ids=ids,attention_mask=[1]*len(ids),labels=[-100]*len(a)+b+[tokenizer.eos_token_id]);counts[r['id']]=dict(prompt=len(a),supervised=len(b)+1,total=len(ids))
 presentations=[tokens[n] for n in selection['presentation_order']];monitor=[tokens[r['id']] for r in records if r['split']=='validation']
 assert len(presentations)==128 and len(monitor)==16
 rows('train.tokens.jsonl',presentations);rows('validation.tokens.jsonl',monitor)
 # Audit the shared collation path's full multiset, not a claimed optimiser sequence.
 expected=Counter((tuple(r['input_ids']),tuple(r['labels'])) for r in presentations);actual=Counter();supervised=0
 for batch,lengths,labels in create_batches(presentations,tokenizer,1,2048,seed=42,append_eos=False):
  assert labels is not None
  end=int(lengths.tolist()[0][1]);ids=tuple(batch.tolist()[0][:end]);lab=labels.tolist()[0]
  assert all(x==-100 for x in lab[end:]);actual[(ids,tuple(lab[:end]))]+=1;supervised+=sum(x!=-100 for x in lab[1:])
 assert actual==expected
 prose=sum(counts[n]['supervised'] for n in selection['presentation_order'] if not by_id[n]['messages'][-1]['content'].lstrip().startswith('{'))
 assert prose==8686 and supervised==10173
 save('tokenizer-preflight.json',dict(passed=True,unique_training_records=92,training_presentations=128,monitor_records=16,supervised_train_tokens=supervised,prose_supervised_tokens=prose,structural_supervised_tokens=supervised-prose,maximum_tokens=max(c['total'] for c in counts.values()),all_answers_roundtrip=True,all_prompt_tokens_masked=True,targets_truncated=False,collated_multiset_matches=True,collated_supervised_tokens=supervised,worker_supports_torch_randperm='dataset_order' in MLXTrainingConfig.__dataclass_fields__,sampler_note='Installed worker selects torch_randperm; file order is not asserted as optimiser order.',counts=counts))
 cfg=json.loads((proof/'request.json').read_text());cfg.update(project_name='Narratryx-balanced-fiction-v9',local_datasets=[str(DATA/'train.tokens.jsonl')],local_eval_datasets=[str(DATA/'validation.tokens.jsonl')],max_steps=128,num_epochs=1,save_steps=128,eval_steps=32,batch_size=1,gradient_accumulation_steps=1,learning_rate='2e-4',warmup_steps=2)
 save('request.proposed.json',cfg)
 protected=dict(parent['protected_artifacts'])
 for name in ['adapter/adapters.safetensors','adapter/adapter_config.json','completion.json','protocol.frozen.json','combined-verification.json']:
  p=proof/name;protected[str(p.relative_to(ROOT))]=file_hash(p)
 inputs=dict(parent['input_hashes']);inputs.update(build['input_hashes'])
 paths=[DATA/n for n in ['records.jsonl','selection.json','build-verification.json','fresh.cases.frozen.jsonl','primary.cases.frozen.jsonl','candidate-extra.cases.frozen.jsonl','train.tokens.jsonl','validation.tokens.jsonl','tokenizer-preflight.json','request.proposed.json']]+[Path(__file__)]
 inputs.update({str(p.relative_to(ROOT)):file_hash(p) for p in paths})
 protocol=dict(status='balanced_preflight_ready',created_on='2026-11-01',input_hashes=inputs,protected_artifacts=protected,base_path=str(base),base_weights_sha256=parent['base_weights_sha256'],training_steps=128,context_limit=2048,training=dict(records=92,presentations=128,prose_records=56,structural_records=36,focused_unique_records=12,focused_exposures=4,prose_presentations=56,structural_presentations=72,max_steps=128,epochs=1,batch_size=1,gradient_accumulation=1,learning_rate='2e-4',context_limit=2048,lora_rank=8,lora_alpha=16,seed=42),evaluation=dict(primary_cases=72,fresh_cases=48,exposed_writing_retention=24,candidate_extra_exposed=36,base_requests=72,current_craft_requests=72,candidate_requests=108,max_new_tokens=384,temperature=0,seed=42,cached_tokens=0,human_literary_ratings=0),resource_stop=dict(max_steps=128,peak_mlx_gb=10,timeout_seconds=1200,stop_on_warning_error_nonfinite=True),validation='Sixteen previously exposed Wray records monitor prose loss. Grounding/fiction tasks scored separately after training; not independent literary approval.',scope='One local balanced source-only trial. No generated literary teaching targets, paid jobs, corpus uploads, model promotion, app changes or silent replacement of uploaded models.',limits=['Multiple recipe changes from broad v7; no single-factor causal claim.','Focused repetitions do not add independent authors or literary passages.','Original tiny proof/retention checks are exposed diagnostics.','No app release or model promotion without independent literary evaluation.'])
 save('protocol.proposed.frozen.json',protocol)
 print(json.dumps(dict(unique_records=92,presentations=128,supervised_tokens=supervised,prose_tokens=prose,max_tokens=protocol['context_limit'],steps=128)))
if __name__=='__main__':main()
