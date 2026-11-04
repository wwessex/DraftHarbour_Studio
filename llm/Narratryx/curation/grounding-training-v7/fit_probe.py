"""Post-training diagnostic on eligible training rows, never held-out quality evidence."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
import json,sys,threading,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import read_jsonl,file_hash,load_ledger,clear_source
from runtime.local.engine import MLXEngine
from scoring import claim_match
RUN=ROOT/'artifacts/grounding-training-v7';DATA=ROOT/'artifacts/arrival-claims-v1'
def save(name,value):
 with (RUN/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 assert json.loads((RUN/'experiment-complete.json').read_text())['completed']
 protocol=json.loads((RUN/'protocol.frozen.json').read_text())
 for group in ['input_hashes','protected_artifacts']:
  for n,h in protocol[group].items():assert file_hash(ROOT/n)==h,n
 ledger_path=ROOT/'rights/grounding-balanced-v1.scoped.jsonl';ledger=load_ledger(ledger_path)
 eligible=[];excluded=[]
 for r in read_jsonl(DATA/'records.jsonl'):
  if not r['id'].startswith('claim-'):continue
  allowed=all(any(c['jurisdiction']==j and 'evaluation' in c['uses'] for c in ledger[rid]['clearances']) for rid in r['rights_record_ids'] for j in ['GB','US'])
  (eligible if allowed else excluded).append(r)
 assert len(eligible)==24 and len(excluded)==0
 eligible=[r for r in eligible if int(r['id'].rsplit('-',1)[1]) in {0,1,3,6,7,8}]
 assert len(eligible)==12
 for rid in {rid for r in eligible for rid in r['rights_record_ids']}:clear_source(ledger[rid],ledger_path,['GB','US'],'evaluation')
 adapter=RUN/'adapter';pin=json.loads((ROOT/'configs/narratryx-craft-v1.json').read_text())
 pin.update(adapter_sha256=file_hash(adapter/'adapters.safetensors'),adapter_config_sha256=file_hash(adapter/'adapter_config.json'),context_limit=2048)
 audit=dict(purpose='Seen-training fit diagnostic only; not new benchmark or literary-quality evidence',cases=12,excluded_without_evaluation_use=0,eligible_not_probed=12,source_schedule_families=2,max_new_tokens=96,temperature=0,seed=42,cached_tokens=0,training_records_sha256=file_hash(DATA/'records.jsonl'),adapter_sha256=pin['adapter_sha256'],script_sha256=file_hash(Path(__file__)),primary_protocol_sha256=file_hash(RUN/'protocol.frozen.json'))
 save('fit-probe.protocol.json',audit)
 engine=MLXEngine(pin,Path(protocol['base_path']),adapter);passed=0
 try:
  with (RUN/'fit-probe.responses.jsonl').open('x') as f:
   for row in eligible:
    cancel=threading.Event();timer=threading.Timer(120,cancel.set);timer.start()
    try:answer=engine.generate([dict(role='user',content=row['messages'][0]['content'])],pin['model_id'],96,0,cancel)
    finally:timer.cancel()
    assert answer['finish_reason']!='length' and answer['usage']['prompt_tokens_details']['cached_tokens']==0
    expected=json.loads(row['messages'][-1]['content']);ok=claim_match(answer['text'],expected);passed+=ok
    f.write(json.dumps(dict(record_id=row['id'],text=answer['text'],expected=expected,exact_passed=ok,usage=answer['usage'],finish_reason=answer['finish_reason']),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
    print(row['id'],ok,flush=True)
 finally:engine.close()
 assert file_hash(adapter/'adapters.safetensors')==pin['adapter_sha256']
 save('fit-probe.complete.json',dict(completed=True,passed=passed,total=12,excluded_without_evaluation_use=0,eligible_not_probed=12,source_schedule_families=2,training_seen=True,quality_upgrade_assessed=False,adapter_unchanged=True,responses_sha256=file_hash(RUN/'fit-probe.responses.jsonl')))
 print('Training-fit probe:',passed,'/12',flush=True)
if __name__=='__main__':main()
