"""Resume a prefix-only interrupted evaluation; preserve original bytes and frozen inputs."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
from pathlib import Path
import hashlib,json,sys,threading,time,shutil
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from runtime.local.engine import MLXEngine
RUN=ROOT/'artifacts/task-matched-training-v3'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 side=sys.argv[1];assert side=='current-craft'
 protocol=json.loads((RUN/'protocol.frozen.json').read_text());protocol_hash=sha(RUN/'protocol.frozen.json')
 for rel,value in protocol['input_hashes'].items():assert sha(ROOT/rel)==value,rel
 cases=[json.loads(l) for l in (ROOT/protocol['test_cases_path']).read_text().splitlines()]
 output=RUN/f'{side}.responses.jsonl';original=output.read_bytes();assert original.endswith(b'\n')
 prior=[json.loads(l) for l in original.splitlines()];assert 0<len(prior)<len(cases)
 assert [r['case_id'] for r in prior]==[c['id'] for c in cases[:len(prior)]]
 for row,case in zip(prior,cases):
  assert row['protocol_sha256']==protocol_hash and row['condition']==side and not row['error']
  assert row['prompt_sha256']==hashlib.sha256(case['prompt'].encode()).hexdigest()
  assert row['messages_count']==1 and row['prior_assistant_messages']==0
  assert row['usage'].get('prompt_tokens_details',{}).get('cached_tokens',0)==0
 backup=RUN/f'{side}.pre-resume-2026-10-26.jsonl';assert not backup.exists();shutil.copy2(output,backup)
 adapter=ROOT/'artifacts/craft-training-v2/adapter';pin=json.loads((ROOT/'configs/narratryx-craft-v1.json').read_text())
 pin.update(adapter_sha256=sha(adapter/'adapters.safetensors'),adapter_config_sha256=sha(adapter/'adapter_config.json'),context_limit=protocol['context_limit'])
 for row in prior:assert row['adapter_sha256']==pin['adapter_sha256']
 (RUN/'resume-audit-2026-10-26.json').write_text(json.dumps(dict(condition=side,retained_requests=len(prior),remaining=len(cases)-len(prior),original_sha256=sha(backup),resume_script_sha256=sha(Path(__file__)),protocol_unchanged=True,reason='Process interrupted after four durable completed requests; base baseline complete, training not started.',human_ratings=0),indent=2)+'\n')
 engine=MLXEngine(pin,Path(protocol['base_path']),adapter)
 try:
  with output.open('a') as stream:
   for i,case in enumerate(cases[len(prior):],start=len(prior)):
    cancel=threading.Event();timer=threading.Timer(120,cancel.set);timer.daemon=True;timer.start();start=time.monotonic();result=None;error=None
    try:
     result=engine.generate([dict(role='user',content=case['prompt'])],pin['model_id'],384,0,cancel)
     assert result['usage'].get('prompt_tokens_details',{}).get('cached_tokens',0)==0
    except Exception as exc:error=repr(exc)
    finally:timer.cancel()
    row=dict(case_id=case['id'],condition=side,kind=case['kind'],text=result['text'] if result else '',error=error,usage=result['usage'] if result else {},finish_reason=result['finish_reason'] if result else None,messages_count=1,prior_assistant_messages=0,adapter_enabled=True,prompt_sha256=hashlib.sha256(case['prompt'].encode()).hexdigest(),protocol_sha256=protocol_hash,adapter_sha256=pin['adapter_sha256'],elapsed_seconds=time.monotonic()-start)
    stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush();os.fsync(stream.fileno())
    print(f'{side}: {i+1}/{len(cases)} finish={row["finish_reason"]} error={error}',flush=True)
    if error:raise RuntimeError(error)
 finally:engine.close()
 assert output.read_bytes().startswith(original) and sha(adapter/'adapters.safetensors')==pin['adapter_sha256']
 with (RUN/f'{side}.complete.json').open('x') as f:json.dump(dict(completed=True,cases=len(cases),response_sha256=sha(output),models_unloaded=True,adapter_unchanged=True,resumed_without_replacing_completed_requests=True),f,indent=2)
if __name__=='__main__':main()
