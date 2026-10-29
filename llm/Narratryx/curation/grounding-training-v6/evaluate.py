"""Fresh-context functional/literary diagnostic. No training or quality judgements."""
import os
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
from pathlib import Path
import hashlib, json, sys, threading, time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from runtime.local.engine import MLXEngine
RUN=ROOT/'artifacts/grounding-training-v6'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def main():
    side=sys.argv[1];assert side in ['base','current-craft','candidate']
    protocol=json.loads((RUN/'protocol.frozen.json').read_text())
    for name,value in protocol['input_hashes'].items():assert sha(ROOT/name)==value,name
    cases=[json.loads(line) for line in (ROOT/protocol['test_cases_path']).read_text().splitlines()]
    adapter=RUN/'adapter' if side=='candidate' else ROOT/'artifacts/craft-training-v2/adapter'
    if side=='candidate': assert json.loads((RUN/'completion.json').read_text())['completed']
    pin=json.loads((ROOT/'configs/narratryx-craft-v1.json').read_text())
    pin.update(adapter_sha256=sha(adapter/'adapters.safetensors'),adapter_config_sha256=sha(adapter/'adapter_config.json'),context_limit=protocol['context_limit'])
    output=RUN/f'{side}.responses.jsonl'
    assert not output.exists(), 'Refuse overwriting responses; use a new experiment or audit an interrupted run'
    engine=MLXEngine(pin,Path(protocol['base_path']),adapter)
    try:
        with output.open('x') as stream:
            for i,case in enumerate(cases):
                cancel=threading.Event();timer=threading.Timer(120,cancel.set);timer.daemon=True;timer.start()
                start=time.monotonic();result=None;error=None
                try:
                    result=engine.generate([dict(role='user',content=case['prompt'])],pin['model_id'] if side!='base' else 'adapter-off-base',384,0,cancel)
                    assert result['usage'].get('prompt_tokens_details',{}).get('cached_tokens',0)==0
                except Exception as exc:error=repr(exc)
                finally:timer.cancel()
                row=dict(case_id=case['id'],condition=side,kind=case['kind'],text=result['text'] if result else '',error=error,usage=result['usage'] if result else {},finish_reason=result['finish_reason'] if result else None,messages_count=1,prior_assistant_messages=0,adapter_enabled=side!='base',prompt_sha256=hashlib.sha256(case['prompt'].encode()).hexdigest(),protocol_sha256=sha(RUN/'protocol.frozen.json'),adapter_sha256=pin['adapter_sha256'],elapsed_seconds=time.monotonic()-start)
                stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush();os.fsync(stream.fileno())
                print(f'{side}: {i+1}/{len(cases)} {case["id"]} finish={row["finish_reason"]} error={error}',flush=True)
                if error or row['finish_reason'] == 'length':raise RuntimeError(error or 'Truncated diagnostic response')
    finally:engine.close()
    assert sha(adapter/'adapters.safetensors')==pin['adapter_sha256']
    with (RUN/f'{side}.complete.json').open('x') as f:json.dump(dict(completed=True,cases=len(cases),response_sha256=sha(output),models_unloaded=True,adapter_unchanged=True),f,indent=2)
if __name__=='__main__':main()
