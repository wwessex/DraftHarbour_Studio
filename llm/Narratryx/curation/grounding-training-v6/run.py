"""One authorised20-update learning-rate ablation; preserve the initial service state."""
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
DATA=ROOT/'artifacts/grounding-balanced-v1'
RUN=ROOT/'artifacts/grounding-training-v6'
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
    if len([r for r in records if r['split']=='train'])!=80:raise RuntimeError('Unexpected training membership')


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
    if RUN.exists():raise RuntimeError('Refusing to overwrite an experiment')
    RUN.mkdir()
    proposed=DATA/'protocol.proposed.frozen.json';protocol=json.loads(proposed.read_text());verify(protocol)
    retention=ROOT/protocol['retention']['path']
    if file_hash(retention)!=protocol['retention']['sha256']:raise RuntimeError('Retention cases changed')
    cases=read_jsonl(DATA/'evaluation.cases.frozen.jsonl')
    for case in cases:case['evaluation_role']='new-clock' if case['kind']=='clock-state' else 'new-prose-transfer'
    prior=read_jsonl(retention)
    for case in prior:case['evaluation_role']='exposed-retention'
    cases+=prior
    if len(cases)!=64 or len({c['id'] for c in cases})!=64:raise RuntimeError('Unexpected test membership')
    with (RUN/'cases.frozen.jsonl').open('x') as f:
        for case in cases:f.write(json.dumps(case,ensure_ascii=False)+'\n')
    previous=ROOT/'artifacts/grounding-training-v5'
    if not json.loads((previous/'experiment-complete.json').read_text())['completed']:raise RuntimeError('Previous trial incomplete')
    old_request=json.loads((previous/'request.json').read_text())
    request=dict(old_request,learning_rate='5e-5')
    if {k for k in request if request[k]!=old_request[k]}!={'learning_rate'}:raise RuntimeError('Ablation changed more than learning rate')
    if float(old_request['learning_rate'])!=5e-6 or float(request['learning_rate'])!=5e-5:raise RuntimeError('Unexpected learning rates')
    save('request.json',request)
    protocol['ablation']=dict(parameter='learning_rate',previous='5e-6',candidate='5e-5',other_request_parameters_unchanged=True,previous_run='artifacts/grounding-training-v5',evaluation_status='Repeated exposed diagnostics; no independent quality claim')
    for name in ['adapter/adapters.safetensors','adapter/adapter_config.json','request.json','protocol.frozen.json','completion.json','experiment-complete.json']:
        path=previous/name
        protocol['protected_artifacts'][str(path.relative_to(ROOT))]=file_hash(path)
    protocol.update(status='execution_authorised',user_authorization='User requested next training step. One fresh-base20-update learning-rate ablation at5e-5; all data and other request parameters fixed. Local only, no promotion or app changes.',training_steps=20,
                    context_limit=2048,test_cases_path=str((RUN/'cases.frozen.jsonl').relative_to(ROOT)),
                    model_conditions=['base','current-craft','candidate'])
    paths=[proposed,RUN/'request.json',RUN/'cases.frozen.jsonl',ROOT/'runtime/local/engine.py']
    paths += [HERE/name for name in ['run.py','train.py','evaluate.py','guards.py','scoring.py']]
    for path in paths:protocol['input_hashes'][str(path.relative_to(ROOT))]=file_hash(path)
    save('protocol.frozen.json',protocol)
    packages={}
    for name in ['mlx','mlx-lm','mlx-vlm','transformers','unsloth']:
        try:packages[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:packages[name]=None
    save('environment.json',dict(python=sys.version,packages=packages,offline=True,
         transformers_note='Installed CLI selects its pinned model-compatible sidecar; actual worker import version is recorded in logs.'))
    service=capture_service();paused=False;error=None
    try:
        if service:
            service[0].terminate();paused=True;service[0].wait(timeout=30)
        for side in ['base','current-craft']:phase(side,[str(HERE/'evaluate.py'),side],3600)
        phase('training',[str(HERE/'train.py')],1200)
        phase('candidate',[str(HERE/'evaluate.py'),'candidate'],3600)
        verify(protocol)
        save('experiment-complete.json',dict(completed=True,responses=192,conditions=3,training_steps=20,model_promoted=False))
    except BaseException as exc:
        error=repr(exc);save('experiment-failed.json',dict(error=error,automatic_retry=False));raise
    finally:
        if paused:
            state=service[1]
            with (RUN/'service-restored.log').open('x') as log:
                process=subprocess.Popen(state['command'],cwd=state['cwd'],env=state['environment'],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            ready=False;deadline=time.monotonic()+120
            while process.poll() is None and time.monotonic()<deadline:
                try:
                    with urllib.request.urlopen('http://127.0.0.1:8890/health',timeout=2) as response:ready=response.status==200
                    if ready:break
                except Exception:time.sleep(1)
            save('service-final.json',dict(initially_running=True,restored=True,http_ready=ready,pid=process.pid,experiment_error=error))
            if not ready:raise RuntimeError('Legacy service did not regain readiness')
        else:
            save('service-final.json',dict(initially_running=False,started_by_experiment=False,port_free=port_free(),experiment_error=error))
        print('Initial service state preserved.',flush=True)


if __name__=='__main__':main()
