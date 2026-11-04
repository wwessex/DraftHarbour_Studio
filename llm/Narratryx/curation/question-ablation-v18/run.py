"""One exploratory evaluation-only96-request run; existing models and service state preserved."""
import importlib.metadata
import importlib.util
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
RUN=ROOT/'artifacts/question-ablation-v18'
PLAN=ROOT/'artifacts/question-ablation-v18-plan'
HERE=Path(__file__).resolve().parent


def verify(p):
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    assert file_hash(Path(p['base_path'])/'model.safetensors')==p['base_weights_sha256']


def main():
    if RUN.exists():raise RuntimeError('Refuse overwrite or automatic retry')
    p=json.loads((PLAN/'protocol.proposed.frozen.json').read_text());verify(p)
    assert p['conditions']==['base','current-craft','mixed-v16'] and p['evaluation']['total_requests']==96 and p['evaluation']['max_new_tokens']==64
    cases=read_jsonl(PLAN/'cases.frozen.jsonl');assert len(cases)==32 and len({c['id'] for c in cases})==32
    assert all(c['training_eligible'] is False for c in cases)
    env={n:importlib.metadata.version(n) for n in p['reference_environment']};assert env==p['reference_environment']
    path=ROOT/'curation/stability-v10/run.py';spec=importlib.util.spec_from_file_location('frozen_resource_helpers17',path);h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h);h.RUN=RUN
    previous=ROOT/'curation/format-diagnostic-v17/diagnostic.lock.json'
    previous_lock=json.loads(previous.read_text())
    p['protected_artifacts'][str(previous.relative_to(ROOT))]=file_hash(previous)
    for group in ['source_hashes','artifact_hashes']:
        for n,hsh in previous_lock.get(group,{}).items():
            assert file_hash(ROOT/n)==hsh,n
            p['protected_artifacts'][n]=hsh
    RUN.mkdir();p.update(status='execution_authorised_evaluation_only',test_cases_path='artifacts/question-ablation-v18-plan/cases.frozen.jsonl',user_authorization='User proceeded with evaluation-only matched direct-question diagnostic. No training or app changes.')
    paths=[PLAN/'protocol.proposed.frozen.json',path,ROOT/'runtime/local/engine.py',HERE/'run.py',HERE/'evaluate.py',ROOT/'foundation/format_diagnostic.py',ROOT/'foundation/binding_ablation.py',ROOT/'foundation/question_ablation.py']
    p['input_hashes'].update({str(path.relative_to(ROOT)):file_hash(path) for path in paths})
    h.save('protocol.frozen.json',p);h.save('environment.json',dict(python=sys.version,packages=env,offline=True))
    service=h.capture_service();paused=False;error=None
    try:
        if service:service[0].terminate();paused=True;service[0].wait(timeout=30)
        for side in p['conditions']:h.phase(side,[str(HERE/'evaluate.py'),side],1200)
        verify(p);h.save('experiment-complete.json',dict(completed=True,new_responses=96,reused_responses=0,training_executed=False,model_promoted=False))
    except BaseException as exc:
        error=repr(exc);h.save('experiment-failed.json',dict(error=error,automatic_retry=False));raise
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
            h.save('service-final.json',dict(initially_running=True,restored=True,http_ready=ready,experiment_error=error))
            if not ready:raise RuntimeError('Legacy service failed readiness')
        else:h.save('service-final.json',dict(initially_running=False,started_by_experiment=False,port_free=h.port_free(),experiment_error=error))


if __name__=='__main__':main()
