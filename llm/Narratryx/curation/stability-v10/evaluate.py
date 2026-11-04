"""Small exposed suite, writing first; original token cap and decoding preserved."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
import hashlib,json,sys,threading
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from runtime.local.engine import MLXEngine
from stability_checks import repeated_dialogue
RUN=ROOT/'artifacts/stability-v10'
def main():
 p=json.loads((RUN/'protocol.frozen.json').read_text())
 for n,h in p['input_hashes'].items():assert file_hash(ROOT/n)==h,n
 assert json.loads((RUN/'completion.json').read_text())['completed']
 cases=read_jsonl(ROOT/p['test_cases_path']);adapter=RUN/'adapter';pin=json.loads((ROOT/'configs/narratryx-craft-v1.json').read_text())
 pin.update(adapter_sha256=file_hash(adapter/'adapters.safetensors'),adapter_config_sha256=file_hash(adapter/'adapter_config.json'),context_limit=2048)
 engine=MLXEngine(pin,Path(p['base_path']),adapter);repeated=0
 try:
  with (RUN/'candidate.responses.jsonl').open('x') as f:
   for i,c in enumerate(cases):
    cancel=threading.Event();timer=threading.Timer(120,cancel.set);timer.start()
    try:r=engine.generate([dict(role='user',content=c['prompt'])],pin['model_id'],384,0,cancel)
    finally:timer.cancel()
    repetitions=repeated_dialogue(r['text']) if c['kind']=='dialogue' else None;repeated+=repetitions is not None and repetitions>=2
    row=dict(case_id=c['id'],condition='lower-rate',kind=c['kind'],text=r['text'],usage=r['usage'],finish_reason=r['finish_reason'],error=None,messages_count=1,prior_assistant_messages=0,adapter_enabled=True,adapter_sha256=pin['adapter_sha256'],prompt_sha256=hashlib.sha256(c['prompt'].encode()).hexdigest(),protocol_sha256=file_hash(RUN/'protocol.frozen.json'),maximum_identical_dialogue_body_repetitions=repetitions)
    f.write(json.dumps(row,ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno());print(i+1,c['id'],r['finish_reason'],repetitions,flush=True)
    assert r['usage']['prompt_tokens_details']['cached_tokens']==0
    if r['finish_reason']=='length':raise RuntimeError('Output-cap stability gate; no completion or retry')
 finally:engine.close()
 assert file_hash(adapter/'adapters.safetensors')==pin['adapter_sha256']
 with (RUN/'candidate.complete.json').open('x') as f:json.dump(dict(completed=True,cases=len(cases),responses_sha256=file_hash(RUN/'candidate.responses.jsonl'),repeated_dialogue_cases=repeated,stability_threshold='At least two identical normalised dialogue bodies of six or more words is a repetition flag, not a semantic quality rating.',model_promoted=False),f,indent=2)
if __name__=='__main__':main()
