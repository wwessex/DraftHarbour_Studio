"""Read-only verification for evaluation-only entity-binding evidence."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from foundation.question_ablation import cases as factor_cases,diagnose as score
RUN=ROOT/'artifacts/question-ablation-v18'
PLAN=ROOT/'artifacts/question-ablation-v18-plan'


def verify():
    p=json.loads((RUN/'protocol.frozen.json').read_text())
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    assert file_hash(Path(p['base_path'])/'model.safetensors')==p['base_weights_sha256']
    cases=read_jsonl(PLAN/'cases.frozen.jsonl')
    assert len(cases)==32 and {c['id']:c for c in cases}=={c['id']:c for c in factor_cases()}
    assert Counter(c['expected_entity'] for c in cases)=={'original':16,'duplicate':16}
    assert all(c['training_eligible'] is False for c in cases)
    original=next(c for c in read_jsonl(ROOT/'artifacts/semantic-restoration-v14/cases.frozen.jsonl') if c['id']=='sr14-binding')
    assert sum(c['prompt']==original['prompt'] for c in cases)==1
    for pair_id in {c['pair_id'] for c in cases}:
        pair={c['direct_question']:c for c in cases if c['pair_id']==pair_id}
        assert set(pair)=={False,True}
        assert pair[True]['prompt'].replace("Which register's legibility is unknown? ",'',1)==pair[False]['prompt']
        assert pair[True]['expected_json']==pair[False]['expected_json']
    total=0;truncated=0;complete=True
    scores=json.loads((RUN/'scores.json').read_text());lookup={(d['condition'],d['case_id']):d for d in scores['details']}
    for side in p['conditions']:
        path=RUN/(side+'.responses.jsonl');rows=read_jsonl(path) if path.exists() else []
        assert [r['case_id'] for r in rows]==[c['id'] for c in cases[:len(rows)]]
        adapter=ROOT/'artifacts/mixed-training-v16/adapter' if side=='mixed-v16' else ROOT/'artifacts/craft-training-v2/adapter'
        for c,r in zip(cases,rows):
            assert r['condition']==side and r['messages_count']==1 and r['prior_assistant_messages']==0 and r['adapter_enabled']==(side!='base')
            assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest() and r['protocol_sha256']==file_hash(RUN/'protocol.frozen.json')
            assert r['adapter_sha256']==file_hash(adapter/'adapters.safetensors')
            if not r['error']:
                assert r['usage']['prompt_tokens_details']['cached_tokens']==0 and r['usage']['completion_tokens']<=64
                assert r['usage']['prompt_tokens']+r['usage']['completion_tokens']<=2048
            d=lookup[side,c['id']]
            if not r['error'] and r['finish_reason']!='length':
                for k,v in score(r['text'],c).items():assert d[k]==v,(side,c['id'],k)
            truncated+=r['finish_reason']=='length'
        ds=[lookup[side,c['id']] for c in cases[:len(rows)]]
        summary=scores['summary'][side]
        for q in [False,True]:
            subset=[d for d in ds if d['direct_question']==q]
            expected=dict(attempted=len(subset),entity_correct=sum(d['entity_correct'] is True for d in subset),entity_assessable=sum(d['entity_correct'] is not None for d in subset),format_compliant=sum(d['format_compliant'] for d in subset),exact_task_correct=sum(d['exact_task_correct'] for d in subset))
            assert summary['by_question'][str(q)]==expected
        pairs=[]
        for pair_id in {d['pair_id'] for d in ds}:
            pair={d['direct_question']:d for d in ds if d['pair_id']==pair_id}
            if len(pair)==2:pairs.append((pair[False]['entity_correct'],pair[True]['entity_correct']))
        assert summary['paired']==dict(both_correct=sum(a is True and b is True for a,b in pairs),question_only_correct=sum(a is not True and b is True for a,b in pairs),no_question_only_correct=sum(a is True and b is not True for a,b in pairs),neither_correct=sum(a is not True and b is not True for a,b in pairs))
        total+=len(rows);marker=RUN/(side+'.complete.json')
        if marker.exists():
            m=json.loads(marker.read_text());assert m['completed'] and m['cases']==len(rows)==32 and m['response_sha256']==file_hash(path)
            assert all(not r['error'] and r['finish_reason']!='length' for r in rows)
        else:complete=False
    if complete:assert (RUN/'experiment-complete.json').exists() and total==96 and truncated==0
    else:assert (RUN/'experiment-failed.json').exists()
    initial=json.loads((RUN/'service-initial.json').read_text());final=json.loads((RUN/'service-final.json').read_text())
    if initial['running']:assert final['restored'] and final['http_ready']
    else:assert final['port_free'] and not final['started_by_experiment']
    assert not (RUN/'adapter').exists() and not scores['training_executed'] and not scores['model_promoted']
    return dict(evidence_integrity_passed=True,evaluation_complete=complete,new_requests=total,exploratory_cases=32,original_prompt_repeats=1,conditions=3,
                truncations=truncated,all_scores_recomputed=True,original_models_and_artifacts_unchanged=True,initial_service_state_preserved=True,
                training_executed=False,human_quality_ratings=0,model_promoted=False)


if __name__=='__main__':
    result=verify()
    with (RUN/'verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
