"""Seen-set baseline/candidate fitting, followed only on success by transfer diagnostics."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
import hashlib,json,sys,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from runtime.local.engine import MLXEngine
from scoring import claim_match
RUN=ROOT/'artifacts/tiny-fit-training-v8b';DATA=ROOT/'artifacts/tiny-fit-v8'
def main():
 side=sys.argv[1];assert side in ['base','candidate'];p=json.loads((RUN/'protocol.frozen.json').read_text())
 for n,h in p['input_hashes'].items():assert file_hash(ROOT/n)==h,n
 if side=='candidate':assert json.loads((RUN/'completion.json').read_text())['completed']
 adapter=RUN/'adapter' if side=='candidate' else ROOT/'artifacts/craft-training-v2/adapter'
 pin=json.loads((ROOT/'configs/narratryx-craft-v1.json').read_text());pin.update(adapter_sha256=file_hash(adapter/'adapters.safetensors'),adapter_config_sha256=file_hash(adapter/'adapter_config.json'),context_limit=2048)
 cases=read_jsonl(DATA/'cases.frozen.jsonl');engine=MLXEngine(pin,Path(p['base_path']),adapter);counts={};completed=0;gate=False
 try:
  with (RUN/f'{side}.responses.jsonl').open('x') as f:
   for c in cases:
    if c['cohort']!='seen-training' and (side=='base' or not gate):break
    cancel=threading.Event();timer=threading.Timer(120,cancel.set);timer.start()
    try:r=engine.generate([dict(role='user',content=c['prompt'])],pin['model_id'] if side=='candidate' else 'adapter-off-base',96,0,cancel)
    finally:timer.cancel()
    assert r['finish_reason']!='length' and r['usage']['prompt_tokens_details']['cached_tokens']==0
    ok=claim_match(r['text'],c['expected_json']);counts.setdefault(c['cohort'],dict(passed=0,total=0));counts[c['cohort']]['total']+=1;counts[c['cohort']]['passed']+=ok;completed+=1
    f.write(json.dumps(dict(case_id=c['id'],cohort=c['cohort'],text=r['text'],expected=c['expected_json'],exact_passed=ok,usage=r['usage'],finish_reason=r['finish_reason'],prompt_sha256=hashlib.sha256(c['prompt'].encode()).hexdigest(),protocol_sha256=file_hash(RUN/'protocol.frozen.json'),adapter_enabled=side=='candidate'),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
    if completed==12:gate=counts['seen-training']['passed']>=p['fit_gate']['required_seen_correct']
    print(side,completed,c['id'],ok,flush=True)
 finally:engine.close()
 assert file_hash(adapter/'adapters.safetensors')==pin['adapter_sha256']
 with (RUN/f'{side}.complete.json').open('x') as f:json.dump(dict(completed=True,cases=completed,response_sha256=file_hash(RUN/f'{side}.responses.jsonl'),scores=counts,fit_gate_passed=gate,transfer_skipped=(side=='candidate' and not gate),adapter_unchanged=True),f,indent=2)
if __name__=='__main__':main()
