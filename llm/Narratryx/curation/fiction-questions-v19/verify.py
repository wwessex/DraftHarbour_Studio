"""Read-only evidence and mechanical-score audit. No model calls or quality judge."""
import hashlib
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import read_jsonl, file_hash
from foundation.fiction_questions import cases as build_cases, mechanics
RUN=ROOT/'artifacts/fiction-questions-v19'
PLAN=ROOT/'artifacts/fiction-questions-v19-plan'


def verify():
    p=json.loads((RUN/'protocol.frozen.json').read_text())
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    assert file_hash(Path(p['base_path'])/'model.safetensors')==p['base_weights_sha256']
    cases=read_jsonl(PLAN/'cases.frozen.jsonl')
    assert cases==build_cases(read_jsonl(ROOT/'artifacts/mixed-training-v16/cases.frozen.jsonl')) and len(cases)==12
    assert all(c['training_eligible'] is False for c in cases)
    scores=json.loads((RUN/'scores.json').read_text())
    details={(d['condition'],d['case_id']):d for d in scores['details']}
    assert len(details)==36
    for side in p['conditions']:
        path=RUN/(side+'.responses.jsonl');rows=read_jsonl(path)
        assert [r['case_id'] for r in rows]==[c['id'] for c in cases]
        adapter=ROOT/('artifacts/mixed-training-v16/adapter' if side=='mixed-v16' else 'artifacts/craft-training-v2/adapter')
        for c,r in zip(cases,rows):
            assert r['condition']==side and r['messages_count']==1 and r['prior_assistant_messages']==0 and r['adapter_enabled']==(side!='base')
            assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest()
            assert r['protocol_sha256']==file_hash(RUN/'protocol.frozen.json')
            assert r['adapter_sha256']==file_hash(adapter/'adapters.safetensors')
            assert not r['error'] and r['finish_reason']!='length'
            assert r['usage']['prompt_tokens_details']['cached_tokens']==0
            assert r['usage']['completion_tokens']<=384 and r['usage']['prompt_tokens']+r['usage']['completion_tokens']<=2048
            expected=dict(condition=side,case_id=c['id'],parent_case_id=c['parent_case_id'],variant=c['variant'],kind=c['kind'],**mechanics(r['text'],c))
            assert details[side,c['id']]==expected
        for variant in ['original','clarified']:
            for kind in ['rewrite','continue','dialogue']:
                subset=[details[side,c['id']] for c in cases if c['variant']==variant and c['kind']==kind]
                assert scores['summary'][side][variant][kind]==dict(cases=2,word_limit_passed=sum(d['word_limit_passed'] for d in subset),one_paragraph_passed=sum(d['one_paragraph_passed'] is True for d in subset) if kind!='dialogue' else None)
        m=json.loads((RUN/(side+'.complete.json')).read_text())
        assert m['completed'] and m['cases']==12 and m['response_sha256']==file_hash(path)
    assert json.loads((RUN/'experiment-complete.json').read_text())['new_responses']==36
    initial=json.loads((RUN/'service-initial.json').read_text());final=json.loads((RUN/'service-final.json').read_text())
    if initial['running']:assert final['restored'] and final['http_ready']
    else:assert final['port_free'] and not final['started_by_experiment']
    assert not (RUN/'adapter').exists() and not scores['training_executed'] and not scores['model_promoted']
    return dict(passed=True,new_responses=36,paired_scenarios=6,model_conditions=3,all_mechanical_scores_recomputed=True,prior_models_and_evidence_unchanged=True,initial_service_state_preserved=True,training_executed=False,human_quality_ratings=0,model_promoted=False)


if __name__=='__main__':
    result=verify()
    with (RUN/'verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
