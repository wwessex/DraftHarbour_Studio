"""One-message, uncached local baseline/candidate evaluation. No training."""
import os
os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1';os.environ['UNSLOTH_MLX_PROMPT_CACHE_BYTES']='0'
from pathlib import Path
import hashlib,json,time,threading,sys,importlib.metadata
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'artifacts/craft-expansion-v1'
RUN=ROOT/'artifacts'/(sys.argv[2] if len(sys.argv)>2 else 'craft-training-v1')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    side=sys.argv[1];assert side in ['base','candidate']
    protocol=json.loads((RUN/'protocol.frozen.json').read_text())
    for name,h in protocol['input_hashes'].items():assert sha(ROOT/name)==h,name
    cases=[json.loads(l) for l in (ROOT/protocol.get('test_cases_path','artifacts/craft-expansion-v1/test.cases.jsonl')).read_text().splitlines()]
    assert len(cases)==16
    adapter=RUN/'adapter' if side=='candidate' else ROOT/'artifacts/source-task-training-v1/adapter'
    expected=json.loads((RUN/'completion.json').read_text())['adapter_sha256'] if side=='candidate' else '855eb01061b0b51e665ce0f5547bccfb025090b8326a7e4885149f1c53fe7e53'
    assert sha(adapter/'adapters.safetensors')==expected
    output=RUN/f'{side}.responses.jsonl'
    existing=[json.loads(l) for l in output.read_text().splitlines()] if output.exists() else []
    keys={r['case_id'] for r in existing};assert len(keys)==len(existing)
    assert all(r['condition']==side and r['protocol_sha256']==sha(RUN/'protocol.frozen.json') for r in existing)
    from unsloth_cli._inference import ensure_studio_backend_path,resolve_model_config
    ensure_studio_backend_path()
    from core.inference.mlx_inference import MLXInferenceBackend,_mlx_adapter_modules
    runtime=dict(side=side,script_sha256=sha(Path(__file__)),packages={k:importlib.metadata.version(k) for k in ['mlx','mlx-lm','mlx-vlm','transformers']},adapter_sha256=expected,
                 protocol_sha256=sha(RUN/'protocol.frozen.json'),backend_source_sha256=sha(Path(__import__('core.inference.mlx_inference',fromlist=['x']).__file__)))
    runtime_name=f'{side}.runtime-{time.time_ns()}.json'
    with (RUN/runtime_name).open('x') as f:json.dump(runtime,f,indent=2)
    backend=MLXInferenceBackend()
    assert backend.load_model(resolve_model_config(str(adapter),hf_token=None),max_seq_length=2048,load_in_4bit=False)
    modules,unsupported=_mlx_adapter_modules(backend._model);assert modules and not unsupported
    try:
        with output.open('a') as f:
            for c in cases:
                if c['id'] in keys:continue
                assert backend._prompt_cache() is None
                cancel=threading.Event();timer=threading.Timer(120,cancel.set);timer.daemon=True;timer.start()
                text='';error=None;start=time.perf_counter()
                try:
                    for chunk in backend.generate_with_adapter_control(use_adapter=side=='candidate',messages=[dict(role='user',content=c['prompt'])],system_prompt='',tools=None,cancel_event=cancel,**protocol['generation']):
                        if isinstance(chunk,str):text=str(chunk)
                    if cancel.is_set():error='120-second deadline'
                    if not text.strip():error=error or 'empty response'
                except Exception as e:error=repr(e)
                finally:timer.cancel()
                row=dict(case_id=c['id'],condition=side,kind=c['kind'],text=text,error=error,elapsed_seconds=time.perf_counter()-start,
                         stats=backend.last_generation_stats,messages_count=1,prior_assistant_messages=0,adapter_enabled=side=='candidate',
                         prompt_sha256=hashlib.sha256(c['prompt'].encode()).hexdigest(),protocol_sha256=sha(RUN/'protocol.frozen.json'),runtime_record=runtime_name)
                f.write(json.dumps(row,ensure_ascii=False,default=str)+'\n');f.flush();os.fsync(f.fileno());keys.add(c['id'])
                print(f'{side} {len(keys)}/16 {c["id"]}: {row["elapsed_seconds"]:.1f}s error={error}',flush=True)
                if error:raise RuntimeError(error)
    finally:backend.unload_model(backend.active_model_name)
    assert sha(adapter/'adapters.safetensors')==expected
    assert keys=={c['id'] for c in cases}
    with (RUN/f'{side}.complete.json').open('x') as f:json.dump(dict(completed=True,cases=16,models_unloaded=True,adapter_unchanged=True,response_sha256=sha(output)),f,indent=2)
if __name__=='__main__':main()
