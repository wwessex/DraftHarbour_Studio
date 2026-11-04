"""Post-hoc immutable-base control on previously frozen transfer prompts."""
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
 assert json.loads((RUN/'experiment-complete.json').read_text())['completed']
 p=json.loads((RUN/'protocol.frozen.json').read_text())
 for group in ['input_hashes','protected_artifacts']:
  for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
 pin=json.loads((ROOT/'configs/narratryx-craft-v1.json').read_text());pin['context_limit']=2048
 adapter=ROOT/'artifacts/craft-training-v2/adapter'
 cases=[c for c in read_jsonl(DATA/'cases.frozen.jsonl') if c['cohort']!='seen-training'];assert len(cases)==24
 with (RUN/'transfer-base.protocol.json').open('x') as f:json.dump(dict(post_hoc=True,reason='Candidate transfer looked promising; add immutable-base comparison without changing data or weights.',cases_sha256=file_hash(DATA/'cases.frozen.jsonl'),script_sha256=file_hash(Path(__file__)),primary_protocol_sha256=file_hash(RUN/'protocol.frozen.json'),max_new_tokens=96,temperature=0,seed=42),f,indent=2)
 engine=MLXEngine(pin,Path(p['base_path']),adapter);scores={}
 try:
  with (RUN/'transfer-base.responses.jsonl').open('x') as f:
   for c in cases:
    cancel=threading.Event();timer=threading.Timer(120,cancel.set);timer.start()
    try:r=engine.generate([dict(role='user',content=c['prompt'])],'adapter-off-base',96,0,cancel)
    finally:timer.cancel()
    assert r['finish_reason']!='length' and r['usage']['prompt_tokens_details']['cached_tokens']==0
    ok=claim_match(r['text'],c['expected_json']);scores.setdefault(c['cohort'],dict(passed=0,total=0));scores[c['cohort']]['total']+=1;scores[c['cohort']]['passed']+=ok
    f.write(json.dumps(dict(case_id=c['id'],cohort=c['cohort'],text=r['text'],exact_passed=ok,usage=r['usage'],finish_reason=r['finish_reason'],prompt_sha256=hashlib.sha256(c['prompt'].encode()).hexdigest()),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
    print(c['id'],ok,flush=True)
 finally:engine.close()
 assert file_hash(adapter/'adapters.safetensors')==pin['adapter_sha256']
 with (RUN/'transfer-base.complete.json').open('x') as f:json.dump(dict(completed=True,cases=24,scores=scores,post_hoc=True,responses_sha256=file_hash(RUN/'transfer-base.responses.jsonl'),adapter_disabled=True,prior_adapter_unchanged=True),f,indent=2)
 print(json.dumps(scores),flush=True)
if __name__=='__main__':main()
