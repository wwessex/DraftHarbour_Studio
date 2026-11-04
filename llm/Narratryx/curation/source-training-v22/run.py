"""One 28-update local mixed pilot with 147 planned fresh-context control/candidate calls."""
import importlib.metadata
import importlib.util
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash, read_jsonl, validate_dataset
from foundation.trainer_recipe import validate_plan
HERE=Path(__file__).resolve().parent
PLAN=ROOT/'artifacts/trainer-recipe-v21b'
RUN=ROOT/'artifacts/source-training-v22'


def helpers():
    path=ROOT/'curation/stability-v10/run.py'
    spec=importlib.util.spec_from_file_location('frozen_v10_resource_helpers',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.RUN=RUN
    return module


def verify(p):
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    for n,h in p['installed_source_hashes'].items():assert file_hash(Path(n))==h,n
    pins=json.loads((PLAN/'model-metadata.pins.json').read_text())
    for n,h in pins['model_metadata_hashes'].items():assert file_hash(Path(n))==h,n
    assert file_hash(Path(p['base_path'])/'model.safetensors')==p['base_weights_sha256']
    records=validate_dataset(ROOT/'artifacts/source-candidates-v20/records.proposed.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US'])
    assert sum(r['split']=='train' for r in records)==28


def main():
    if RUN.exists():raise RuntimeError('Refuse overwrite or automatic resume')
    p=json.loads((PLAN/'protocol.proposed.frozen.json').read_text());verify(p)
    request=json.loads((PLAN/'request.proposed.json').read_text())
    assert validate_plan(p,request,json.loads((PLAN/'installed-audit.json').read_text()))
    env={n:importlib.metadata.version(n) for n in p['reference_environment']}
    assert env==p['reference_environment']
    cases=read_jsonl(PLAN/'primary.cases.frozen.jsonl')+read_jsonl(PLAN/'seen-fit.cases.frozen.jsonl')
    assert len(cases)==49 and len({c['id'] for c in cases})==49
    import runpy
    assert runpy.run_path(str(ROOT/'curation/trainer-recipe-v21b/verify.py'))['verify']()['passed']
    lock_path=ROOT/'curation/trainer-recipe-v21b/preparation.lock.json'
    previous=json.loads(lock_path.read_text())
    p['protected_artifacts'][str(lock_path.relative_to(ROOT))]=file_hash(lock_path)
    for group in ['source_hashes','artifact_hashes']:
        for n,hsh in previous[group].items():
            assert file_hash(ROOT/n)==hsh,n
            p['protected_artifacts'][n]=hsh
    RUN.mkdir();h=helpers();h.save('request.json',request)
    with (RUN/'cases.frozen.jsonl').open('x') as f:
        for c in cases:f.write(json.dumps(c,ensure_ascii=False)+'\n')
    p.update(status='execution_authorised',user_authorization='User proceeded with bounded pilot on frozen28 mixed source-only examples; no app default changes or model promotion.',test_cases_path='artifacts/source-training-v22/cases.frozen.jsonl')
    paths=[PLAN/'protocol.proposed.frozen.json',RUN/'request.json',RUN/'cases.frozen.jsonl',ROOT/'foundation/mixed_curriculum.py',ROOT/'foundation/trainer_recipe.py',ROOT/'runtime/local/engine.py',ROOT/'curation/stability-v10/run.py',*[HERE/n for n in ['run.py','train.py','evaluate.py','guards.py','report.py','verify.py','scoring.py']]]
    p['input_hashes'].update({str(path.relative_to(ROOT)):file_hash(path) for path in paths})
    h.save('protocol.frozen.json',p);h.save('environment.json',dict(python=sys.version,packages=env,offline=True))
    service=h.capture_service();paused=False;error=None
    try:
        if service:service[0].terminate();paused=True;service[0].wait(timeout=30)
        for side in ['base','current-craft']:
            h.phase(side,[str(HERE/'evaluate.py'),side],1200)
        h.phase('training',[str(HERE/'train.py')],1200)
        h.phase('candidate',[str(HERE/'evaluate.py'),'candidate'],1200)
        verify(p)
        h.save('experiment-complete.json',dict(completed=True,training_steps=28,new_responses=147,reused_responses=0,model_promoted=False))
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
