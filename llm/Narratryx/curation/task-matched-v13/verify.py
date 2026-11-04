"""Verify completed or stopped fresh-context evidence without literary approval."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from foundation.validation import file_hash,read_jsonl,validate_dataset
from plan_checks import validate_plan
RUN=ROOT/'artifacts/task-matched-training-v13'
PLAN=ROOT/'artifacts/task-matched-v13-plan'


def verify():
    p=json.loads((RUN/'protocol.frozen.json').read_text());request=json.loads((RUN/'request.json').read_text())
    assert validate_plan(p,request,json.loads((PLAN/'tokenizer-collation-preflight.json').read_text()))
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    assert file_hash(Path(p['base_path'])/'model.safetensors')==p['base_weights_sha256']
    validated=validate_dataset(ROOT/'artifacts/paragraph-dialogue-v12/records.proposed.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US'])
    assert sum(r['split']=='train' for r in validated)==25
    cases=read_jsonl(PLAN/'cases.frozen.jsonl');counts={};truncated=0;failures=0;all_complete=True;candidate_complete=False
    for side in ['base','current-craft','candidate']:
        output=RUN/(side+'.responses.jsonl');rows=read_jsonl(output) if output.exists() else []
        assert [r['case_id'] for r in rows]==[c['id'] for c in cases[:len(rows)]]
        for c,r in zip(cases,rows):
            assert r['condition']==side and r['kind']==c['kind']
            assert r['messages_count']==1 and r['prior_assistant_messages']==0 and r['adapter_enabled']==(side!='base')
            assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest() and r['protocol_sha256']==file_hash(RUN/'protocol.frozen.json')
            adapter=RUN/'adapter' if side=='candidate' else ROOT/'artifacts/craft-training-v2/adapter'
            assert r['adapter_sha256']==file_hash(adapter/'adapters.safetensors')
            if not r['error']:
                assert r['usage']['prompt_tokens_details']['cached_tokens']==0
                assert r['usage']['prompt_tokens']+r['usage']['completion_tokens']<=2048
            truncated+=r['finish_reason']=='length';failures+=bool(r['error']) or r['finish_reason']=='length'
        marker=RUN/(side+'.complete.json')
        if marker.exists():
            m=json.loads(marker.read_text());assert m['completed'] and m['cases']==len(rows)==36 and m['response_sha256']==file_hash(output)
            assert not any(r['error'] or r['finish_reason']=='length' for r in rows)
        else:all_complete=False
        if side=='candidate':candidate_complete=marker.exists()
        counts[side]=len(rows)
    trained=(RUN/'completion.json').exists()
    training_summary={}
    if trained:
        final=json.loads((RUN/'final-progress.json').read_text());model=json.loads((RUN/'completion.json').read_text());phase=json.loads((RUN/'training.phase.json').read_text())
        assert final['is_completed'] and final['step']==25 and final['num_tokens']==2298 and final['peak_memory_gb']<=10 and not final['warnings'] and not final['error']
        assert model['completed'] and model['steps']==25 and not model['model_promoted'] and model['adapter_sha256']==file_hash(RUN/'adapter/adapters.safetensors')
        assert phase['completed'] and phase['elapsed_seconds']<=1200
        training_summary=dict(training_steps=25,worker_elapsed_seconds=final['elapsed_seconds'],training_phase_seconds=phase['elapsed_seconds'],peak_mlx_gb=final['peak_memory_gb'])
        assert all((RUN/(side+'.complete.json')).exists() for side in ['base','current-craft'])
    completed=(RUN/'experiment-complete.json').exists()
    assert completed==all_complete
    if completed:
        assert trained and sum(counts.values())==108 and not failures
    else:
        assert (RUN/'experiment-failed.json').exists()
        assert truncated<=1 and failures<=1
    initial=json.loads((RUN/'service-initial.json').read_text());final_service=json.loads((RUN/'service-final.json').read_text())
    if initial['running']:assert final_service['restored'] and final_service['http_ready']
    else:assert final_service['port_free'] and not final_service['started_by_experiment']
    assert (RUN/'blind-key.private.json').stat().st_mode & 0o777==0o600
    key=json.loads((RUN/'blind-key.private.json').read_text());ballots=read_jsonl(RUN/'human-ballots.blank.jsonl') if key else []
    assert len(ballots)==2*len(key) and all(r['preference'] is None and r['evidence'] is None and all(v is None for v in r['ratings'].values()) for r in ballots)
    return dict(evidence_integrity_passed=True,training_completed=trained,**training_summary,evaluation_complete=all_complete,candidate_evaluation_complete=candidate_complete,
                attempted_requests=counts,total_attempts=sum(counts.values()),truncated_responses=truncated,request_failures=failures,planned_requests=108,
                unique_training_lessons=25,presentations=25,protected_inputs_and_models_unchanged=True,initial_service_state_preserved=True,
                human_review_pairs=len(key),human_quality_ratings=0,model_promoted=False)


if __name__=='__main__':
    result=verify()
    with (RUN/'verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
