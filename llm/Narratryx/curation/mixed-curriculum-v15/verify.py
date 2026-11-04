"""Read-only verification of the corrected mixed proposal; no job launch."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,load_ledger,read_jsonl,validate_dataset
from foundation.mixed_curriculum import require_distinct_source_spans,repair_diagnostics


def verify():
    out=ROOT/'artifacts/mixed-curriculum-v15b'
    p=json.loads((out/'protocol.proposed.frozen.json').read_text());proof=json.loads((out/'verification.json').read_text())
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    for n,h in proof['output_hashes'].items():assert file_hash(out/n)==h,n
    assert file_hash(Path(p['base_path'])/'model.safetensors')==p['base_weights_sha256']
    records=read_jsonl(out/'records.proposed.jsonl');train=[r for r in records if r['split']=='train'];monitor=[r for r in records if r['split']=='validation']
    ledger=ROOT/'rights/grounding-balanced-v1.scoped.jsonl'
    validate_dataset(out/'records.proposed.jsonl',ledger,['GB','US']);require_distinct_source_spans(train,load_ledger(ledger))
    assert len(train)==22 and len(monitor)==16
    assert sum(r['id'].startswith('sr14-') for r in train)==5 and sum(r['id'].startswith('gb-ge-') for r in train)==3
    old={r['id']:r for r in read_jsonl(ROOT/'artifacts/paragraph-dialogue-v12/records.proposed.jsonl')}
    semantic={r['id']:r for r in read_jsonl(ROOT/'artifacts/semantic-restoration-v14/candidates.jsonl')}
    for r in records:
        expected=dict(semantic[r['id']] if r['id'] in semantic else old[r['id']]);expected['dataset_version']='mixed-curriculum-v15-proposal';assert r==expected,r['id']
    assert {r['id'] for r in train if r['id'].startswith('sr14-')}==set(proof['selected_semantic'])
    assert len(proof['reserved_semantic'])==4 and not set(proof['reserved_semantic']) & {r['id'] for r in train}
    primary=read_jsonl(ROOT/p['primary_cases_path']);fit=read_jsonl(ROOT/p['seen_fit_cases_path'])
    assert len(primary)==44 and len(fit)==5 and len({c['id'] for c in primary+fit})==49
    by_id={r['id']:r for r in train}
    assert not {c['prompt'] for c in primary} & {r['messages'][0]['content'] for r in train}
    for c in fit:
        r=by_id[c['source_record_id']]
        assert c['evaluation_role']=='seen-training-fit-not-generalisation' and c['training_prompt_overlap_intentional']
        assert c['prompt']==r['messages'][0]['content'] and c['expected_source_answer']==r['messages'][-1]['content']
        diagnostics=repair_diagnostics(c['expected_source_answer'],c['corruption'])
        assert all(diagnostics.values()),c['id']
    tokens=json.loads((out/'tokenizer-collation-preflight.json').read_text());request=json.loads((out/'request.proposed.json').read_text())
    assert tokens['passed'] and tokens['collated_multiset_matches'] and tokens['supervised_training_tokens']==2449
    assert tokens['supervised_tokens_by_category']=={'broader-prose':1711,'semantic-repair':695,'structural-edit':43}
    assert tokens['maximum_record_tokens']<=2048 and tokens['maximum_evaluation_prompt_tokens']+384<=2048
    assert len(read_jsonl(out/'train.tokens.jsonl'))==22 and len(read_jsonl(out/'validation.tokens.jsonl'))==16
    assert p['training_steps']==request['max_steps']==request['save_steps']==request['eval_steps']==22
    assert request['num_epochs']==request['batch_size']==request['gradient_accumulation_steps']==1 and request['learning_rate']=='5e-5' and request['resume_from_checkpoint'] is None
    assert p['evaluation']['total_requests']==147 and p['evaluation']['primary_requests']==132 and p['evaluation']['seen_fit_requests']==15
    assert p['status']=='proposal-ready-not-execution'
    return dict(passed=True,corrected_proposal='mixed-curriculum-v15b',training_records=22,broader_prose=14,semantic_repairs=5,structural_edits=3,
                monitor_records=16,no_overlapping_training_source_spans=True,supervised_tokens=2449,
                primary_cases=44,new_unrun_primary_cases=8,exposed_primary_cases=36,seen_training_fit_cases=5,
                proposed_requests=147,old_models_and_artifacts_unchanged=True,training_executed=False,inference_executed=False,human_quality_ratings=0,model_promoted=False)


if __name__=='__main__':print(json.dumps(verify(),indent=2))
