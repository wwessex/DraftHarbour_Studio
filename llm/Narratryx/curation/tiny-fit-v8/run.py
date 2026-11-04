"""One authorised26-update claim-reasoning experiment; preserve the initial service state."""
import importlib.metadata
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.request

import psutil

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl,validate_dataset

HERE=Path(__file__).resolve().parent
DATA=ROOT/'artifacts/tiny-fit-v8'
RUN=ROOT/'artifacts/tiny-fit-training-v8'
PYTHON=Path('/Users/williamwessex/.unsloth/studio/unsloth_studio/bin/python')


def save(name,value,private=False):
    fd=os.open(RUN/name,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600 if private else 0o644)
    with os.fdopen(fd,'w') as f:
        json.dump(value,f,indent=2);f.write('\n')


def verify(protocol):
    for group in ['input_hashes','protected_artifacts']:
        for relative,expected in protocol[group].items():
            if file_hash(ROOT/relative)!=expected:raise RuntimeError('Pinned artifact mismatch: '+relative)
    if file_hash(Path(protocol['base_path'])/'model.safetensors')!=protocol['base_weights_sha256']:
        raise RuntimeError('Base weight mismatch')
    records=validate_dataset(DATA/'records.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US'])
    if len([r for r in records if r['split']=='train'])!=12:raise RuntimeError('Unexpected training membership')


def port_free():
    connection=socket.socket()
    try:
        connection.bind(('127.0.0.1',8890));return True
    except OSError:return False
    finally:connection.close()


def capture_service():
    if port_free():
        save('service-initial.json',dict(running=False,action='leave stopped'))
        return None
    result=subprocess.run(['lsof','-t','-nP','-iTCP:8890','-sTCP:LISTEN'],capture_output=True,text=True,timeout=10)
    ids={int(x) for x in result.stdout.split()}
    if len(ids)!=1:raise RuntimeError('Cannot safely identify legacy service listener')
    process=psutil.Process(ids.pop())
    command=process.cmdline()
    if 'runtime.local' not in ' '.join(command):raise RuntimeError('Unrelated listener; refusing interruption')
    state=dict(command=command,cwd=process.cwd(),environment=process.environ())
    save('service-initial.json',dict(running=True,pid=process.pid))
    save('service-state.private.json',dict(pid=process.pid,command=command,cwd=state['cwd']),private=True)
    return process,state


def stop_tree(process):
    try:
        root=psutil.Process(process.pid);members=root.children(recursive=True)+[root]
    except psutil.NoSuchProcess:return
    for member in members:
        try:member.terminate()
        except psutil.NoSuchProcess:pass
    _,alive=psutil.wait_procs(members,timeout=10)
    for member in alive:
        try:member.kill()
        except psutil.NoSuchProcess:pass


def phase(name,args,timeout):
    print('Starting '+name,flush=True);started=time.monotonic()
    with (RUN/(name+'.log')).open('x') as log:
        process=subprocess.Popen([str(PYTHON),*args],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,
            start_new_session=True,env={**os.environ,'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','UNSLOTH_MLX_PROMPT_CACHE_BYTES':'0'})
        try:
            while process.poll() is None:
                if time.monotonic()-started>timeout:raise RuntimeError(name+' exceeded deadline')
                try:
                    root=psutil.Process(process.pid);members=[root]+root.children(recursive=True)
                    if sum(m.memory_info().rss for m in members if m.is_running())>10_000_000_000:
                        raise RuntimeError(name+' resident process memory exceeded10GB')
                except psutil.NoSuchProcess:pass
                time.sleep(1)
            if process.returncode:raise RuntimeError(name+' exited with code '+str(process.returncode))
        except BaseException:
            stop_tree(process);raise
    save(name+'.phase.json',dict(completed=True,elapsed_seconds=time.monotonic()-started))
    print('Completed '+name,flush=True)


def main():
 if RUN.exists():raise RuntimeError('Refusing overwrite')
 RUN.mkdir();protocol=json.loads((DATA/'protocol.proposed.frozen.json').read_text());verify(protocol)
 audit=json.loads((DATA/'loss-path-audit.json').read_text());assert audit['passed']
 for name,value in audit['installed_source_hashes'].items():assert file_hash(Path(name))==value
 save('request.json',json.loads((DATA/'request.proposed.json').read_text()))
 protocol.update(training_steps=48,context_limit=2048,model_conditions=['base','candidate'],user_authorization='User proceeded with tiny-set learning-path sanity check; local only, no model promotion or app changes.')
 for path in [DATA/'protocol.proposed.frozen.json',DATA/'loss-path-audit.json',RUN/'request.json',ROOT/'runtime/local/engine.py',*[HERE/name for name in ['audit.py','run.py','train.py','evaluate.py','guards.py','scoring.py']]]:protocol['input_hashes'][str(path.relative_to(ROOT))]=file_hash(path)
 save('protocol.frozen.json',protocol)
 save('environment.json',dict(python=sys.version,packages={n:importlib.metadata.version(n) for n in ['unsloth','mlx','mlx-lm','mlx-vlm']},offline=True))
 service=capture_service();paused=False;error=None
 try:
  if service:service[0].terminate();paused=True;service[0].wait(timeout=30)
  phase('base',[str(HERE/'evaluate.py'),'base'],600)
  phase('training',[str(HERE/'train.py')],1200)
  phase('candidate',[str(HERE/'evaluate.py'),'candidate'],600)
  verify(protocol)
  candidate=json.loads((RUN/'candidate.complete.json').read_text())
  save('experiment-complete.json',dict(completed=True,training_steps=48,fit_gate_passed=candidate['fit_gate_passed'],responses=12+candidate['cases'],model_promoted=False,literary_quality_assessed=False))
 except BaseException as exc:error=repr(exc);save('experiment-failed.json',dict(error=error,automatic_retry=False));raise
 finally:
  if paused:
   state=service[1]
   with (RUN/'service-restored.log').open('x') as log:process=subprocess.Popen(state['command'],cwd=state['cwd'],env=state['environment'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   ready=False;deadline=time.monotonic()+120
   while process.poll() is None and time.monotonic()<deadline:
    try:
     with urllib.request.urlopen('http://127.0.0.1:8890/health',timeout=2) as response:ready=response.status==200
     if ready:break
    except Exception:time.sleep(1)
   save('service-final.json',dict(initially_running=True,restored=True,http_ready=ready,experiment_error=error))
   if not ready:raise RuntimeError('Legacy service not ready after restoration')
  else:save('service-final.json',dict(initially_running=False,started_by_experiment=False,port_free=port_free(),experiment_error=error))
if __name__=='__main__':main()
