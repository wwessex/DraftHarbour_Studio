"""One post-hoc decode diagnostic; never resumes or repairs the failed benchmark."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
import json,sys,threading,re
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import read_jsonl,file_hash
from runtime.local.engine import MLXEngine
RUN=ROOT/'artifacts/balanced-training-v9';DATA=ROOT/'artifacts/balanced-fiction-v9'
def main():
 assert (RUN/'experiment-failed.json').exists() and not (RUN/'experiment-complete.json').exists()
 p=json.loads((RUN/'protocol.frozen.json').read_text())
 for group in ['input_hashes','protected_artifacts']:
  for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
 c=next(c for c in read_jsonl(DATA/'primary.cases.frozen.jsonl') if c['id']=='bf-craft-coat-dialogue')
 old=read_jsonl(RUN/'candidate.responses.jsonl')[-1];assert old['case_id']==c['id'] and old['finish_reason']=='length'
 adapter=RUN/'adapter';pin=json.loads((ROOT/'configs/narratryx-craft-v1.json').read_text());pin.update(adapter_sha256=file_hash(adapter/'adapters.safetensors'),adapter_config_sha256=file_hash(adapter/'adapter_config.json'),context_limit=2048)
 with (RUN/'repetition-probe.protocol.json').open('x') as f:json.dump(dict(post_hoc=True,case_id=c['id'],model_weights_sha256=pin['adapter_sha256'],script_sha256=file_hash(Path(__file__)),primary_protocol_sha256=file_hash(RUN/'protocol.frozen.json'),changed_parameter='repetition_penalty',before=1.0,after=1.1,temperature=0,seed=42,max_new_tokens=384,benchmark_resumed=False),f,indent=2)
 engine=MLXEngine(pin,Path(p['base_path']),adapter)
 try:
  original=engine.backend.generate_with_adapter_control
  def with_penalty(*args,**kwargs):
   kwargs['repetition_penalty']=1.1
   return original(*args,**kwargs)
  # This affects only this private engine object, not installed code or app defaults.
  engine.backend.generate_with_adapter_control=with_penalty
  cancel=threading.Event();timer=threading.Timer(120,cancel.set);timer.start()
  try:r=engine.generate([dict(role='user',content=c['prompt'])],pin['model_id'],384,0,cancel)
  finally:timer.cancel()
 finally:engine.close()
 assert file_hash(adapter/'adapters.safetensors')==pin['adapter_sha256'] and r['usage']['prompt_tokens_details']['cached_tokens']==0
 def metrics(text,finish):
  lines=[s.strip() for s in text.splitlines() if s.strip()];counter=Counter(lines);turns=sum(bool(re.match(r'^(Cora|Devin)\s*:',s)) for s in lines)
  return dict(words=len(text.split()),max_identical_line_repetitions=max(counter.values(),default=0),named_speaker_line_proxy=turns,truncated=finish=='length',word_limit_passed=len(text.split())<=100,turn_proxy_passed=4<=turns<=6)
 result=dict(completed=True,post_hoc=True,case_id=c['id'],original=metrics(old['text'],old['finish_reason']),probe=metrics(r['text'],r['finish_reason']),probe_text=r['text'],usage=r['usage'],finish_reason=r['finish_reason'],model_unchanged=True,benchmark_resumed=False,quality_upgrade_assessed=False)
 with (RUN/'repetition-probe.complete.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in result.items() if k!='probe_text'},indent=2))
if __name__=='__main__':main()
