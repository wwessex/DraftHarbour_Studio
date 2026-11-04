"""Token masks, provenance and frozen bounded recipe before any model load/training."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import copy,json,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,validate_dataset
OUT=ROOT/'artifacts/arrival-claims-v1'
def save(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 build=json.loads((OUT/'build-verification.json').read_text())
 for n,h in build['input_hashes'].items():assert file_hash(ROOT/n)==h,n
 previous=ROOT/'artifacts/grounding-training-v6'
 protocol=copy.deepcopy(json.loads((previous/'protocol.frozen.json').read_text()))
 for group in ['input_hashes','protected_artifacts']:
  for n,h in protocol[group].items():assert file_hash(ROOT/n)==h,n
 base=Path(protocol['base_path'])
 from unsloth_cli.commands.train import _activate_mlx_transformers
 _activate_mlx_transformers(str(base),None)
 from unsloth_cli._inference import ensure_studio_backend_path
 ensure_studio_backend_path()
 from transformers import AutoTokenizer
 tokenizer=AutoTokenizer.from_pretrained(str(base),local_files_only=True,trust_remote_code=False)
 records=validate_dataset(OUT/'records.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US'])
 train=[r for r in records if r['split']=='train'];monitor=[r for r in records if r['split']=='validation'];random.Random(42).shuffle(train)
 totals={'prose':0,'structural':0};counts=[]
 for split,rows in [('train',train),('validation',monitor)]:
  with (OUT/(split+'.tokens.jsonl')).open('x') as f:
   for row in rows:
    prompt=tokenizer.apply_chat_template(row['messages'][:-1],tokenize=False,add_generation_prompt=True,enable_thinking=False)
    answer=row['messages'][-1]['content'];a=tokenizer.encode(prompt,add_special_tokens=False);b=tokenizer.encode(answer,add_special_tokens=False)
    assert tokenizer.decode(b,skip_special_tokens=False)==answer
    ids=a+b+[tokenizer.eos_token_id];assert len(ids)<=2048,row['id']
    f.write(json.dumps(dict(input_ids=ids,attention_mask=[1]*len(ids),labels=[-100]*len(a)+b+[tokenizer.eos_token_id]))+'\n')
    counts.append(dict(id=row['id'],split=split,total=len(ids),supervised=len(b)+1))
    if split=='train':totals['structural' if answer.lstrip().startswith('{') else 'prose']+=len(b)+1
 save('tokenizer-preflight.json',dict(passed=True,training_records=len(train),monitor_records=len(monitor),supervised_train_tokens=sum(totals.values()),supervised_by_kind=totals,maximum_tokens=max(c['total'] for c in counts),all_prompt_tokens_masked=True,all_answers_roundtrip=True,targets_truncated=False,counts=counts,training_record_order=[r['id'] for r in train]))
 request=json.loads((previous/'request.json').read_text());request.update(project_name='Narratryx-arrival-claims-v1',local_datasets=[str(OUT/'train.tokens.jsonl')],local_eval_datasets=[str(OUT/'validation.tokens.jsonl')],max_steps=26,save_steps=26,eval_steps=13)
 save('request.proposed.json',request)
 for name in ['adapter/adapters.safetensors','adapter/adapter_config.json','protocol.frozen.json','completion.json','request.json']:
  p=previous/name;protocol['protected_artifacts'][str(p.relative_to(ROOT))]=file_hash(p)
 protocol['input_hashes'].update(build['input_hashes'])
 paths=[OUT/name for name in ['records.jsonl','trace.jsonl','evaluation.cases.frozen.jsonl','build-verification.json','train.tokens.jsonl','validation.tokens.jsonl','tokenizer-preflight.json','request.proposed.json']]+[Path(__file__)]
 protocol['input_hashes'].update({str(p.relative_to(ROOT)):file_hash(p) for p in paths})
 protocol.pop('ablation',None)
 protocol.update(status='source_backed_claim_curriculum_ready',created_on='2026-10-31',training=dict(records=104,prose_records=56,structural_records=48,max_steps=26,learning_rate='5e-5',context_limit=2048,seed=42),scope='One local104-record,26-update source-backed claim-curriculum experiment. No generated literary teaching targets, paid jobs, corpus uploads, app changes or automatic promotion.',limitations=['Not a single-parameter ablation:24 lessons and six updates added.','Two correlated source schedule families, not24 independent works.','Original40 diagnostic cases now replaced with40 fresh cases, plus24 exposed retention.','Source-prose teaching retained unchanged; new targets are deterministic structural JSON only.'])
 save('protocol.proposed.frozen.json',protocol)
 print(json.dumps(dict(records=len(train),maximum=max(c['total'] for c in counts),supervised_tokens=totals,steps=26)))
if __name__=='__main__':main()
