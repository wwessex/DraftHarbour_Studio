"""One authorised128-update lower-rate stability experiment; preserve the initial service state."""
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
DATA=ROOT/'artifacts/balanced-fiction-v9'
RUN=ROOT/'artifacts/stability-v10'
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
    if len([r for r in records if r['split']=='train'])!=92:raise RuntimeError('Unexpected training membership')


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


PLAN=ROOT/'artifacts/stability-v10-plan'
def main():
 if RUN.exists():raise RuntimeError('Refuse overwrite')
 protocol=json.loads((PLAN/'protocol.proposed.frozen.json').read_text());verify(protocol)
 request=json.loads((PLAN/'request.proposed.json').read_text());old=json.loads((ROOT/'artifacts/balanced-training-v9/request.json').read_text())
 from plan_checks import validate_ablation
 assert validate_ablation(old,request,protocol)
 env={n:importlib.metadata.version(n) for n in protocol['reference_environment']};assert env==protocol['reference_environment']
 cases=read_jsonl(PLAN/'cases.frozen.jsonl');assert len(cases)==24
 references=json.loads((PLAN/'reference-provenance.json').read_text())
 for side in ['base','current-craft']:
  ref=read_jsonl(PLAN/(side+'.reference.jsonl'));assert len(ref)==24 and all(r['error'] is None and r['finish_reason']!='length' for r in ref)
  marker=json.loads((ROOT/'artifacts/balanced-training-v9'/f'{side}.complete.json').read_text());assert marker['completed'] and marker['cases']==72 and marker['response_sha256']==references[side]['source_sha256']
 RUN.mkdir();save('request.json',request);save('references-verified.json',dict(passed=True,reused_not_new_inference=True,base_cases=24,current_craft_cases=24,high_rate_cases=22,missing_high_rate_cases=2))
 protocol.update(status='execution_authorised',user_authorization='User proceeded with controlled lower-rate stability trial. Local only; no app changes, automatic promotion or paid jobs.',test_cases_path='artifacts/stability-v10-plan/cases.frozen.jsonl',stability_rules=dict(minimum_body_words=6,repeat_flag_at=2,flag_is_not_a_literary_quality_rating=True))
 for path in [PLAN/'protocol.proposed.frozen.json',RUN/'request.json',RUN/'references-verified.json',ROOT/'runtime/local/engine.py',*[HERE/n for n in ['run.py','train.py','evaluate.py','guards.py','scoring.py','plan_checks.py','stability_checks.py']]]:protocol['input_hashes'][str(path.relative_to(ROOT))]=file_hash(path)
 save('protocol.frozen.json',protocol);save('environment.json',dict(python=sys.version,packages=env,offline=True))
 service=capture_service();paused=False;error=None
 try:
  if service:service[0].terminate();paused=True;service[0].wait(timeout=30)
  phase('training',[str(HERE/'train.py')],1200)
  phase('candidate',[str(HERE/'evaluate.py')],1200)
  verify(protocol)
  score=json.loads((RUN/'candidate.complete.json').read_text())
  save('experiment-complete.json',dict(completed=True,training_steps=128,new_responses=24,reused_reference_rows=70,stability_gate_passed=score['repeated_dialogue_cases']==0,model_promoted=False))
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
   if not ready:raise RuntimeError('Legacy service failed readiness')
  else:save('service-final.json',dict(initially_running=False,started_by_experiment=False,port_free=port_free(),experiment_error=error))
if __name__=='__main__':main()
