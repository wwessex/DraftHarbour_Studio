"""Read-only verification; source restoration is not human approval or story quality."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl,validate_dataset
from foundation.source_restoration import verify_corruption


def verify():
    out=ROOT/'artifacts/semantic-restoration-v14';proof=json.loads((out/'verification.json').read_text())
    for group in ['protected_hashes','input_hashes']:
        for n,h in proof[group].items():assert file_hash(ROOT/n)==h,n
    for n,h in proof['output_hashes'].items():assert file_hash(out/n)==h,n
    parent_protocol=json.loads((ROOT/'artifacts/task-matched-training-v13/protocol.frozen.json').read_text())
    assert file_hash(Path(parent_protocol['base_path'])/'model.safetensors')==parent_protocol['base_weights_sha256']
    original={r['id']:r for r in read_jsonl(ROOT/'artifacts/balanced-fiction-v9/records.jsonl')}
    candidates={r['id']:r for r in read_jsonl(out/'candidates.jsonl')};bindings=read_jsonl(out/'derivations.jsonl')
    assert len(candidates)==len(bindings)==len({b['parent_id'] for b in bindings})==9
    for b in bindings:
        r=candidates[b['id']];parent=original[b['parent_id']]
        for key in ['source_spans','rights_record_ids','source_work_ids','split','split_group','origin','teacher']:assert r[key]==parent[key],key
        assert r['split']=='train' and r['task']=='editing' and r['teacher'] is None
        span=r['source_spans'][b['source_span_index']]
        text=span['text'][b['source_relative_start']:b['source_relative_end']]
        assert b['absolute_start']==span['start']+b['source_relative_start'] and b['absolute_end']==span['start']+b['source_relative_end']<=span['end']
        verify_corruption(text,b['corruption'])
        assert r['messages'][-1]['content']==text and r['messages'][0]['content'].split('\n\nPASSAGE:\n')[1]==b['corruption']['damaged_input']
        assert 'No minimum output length.' in r['messages'][0]['content']
    assert len({r['messages'][-1]['content'] for r in candidates.values()})==9
    validate_dataset(out/'candidates.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US'])
    cases=read_jsonl(out/'cases.frozen.jsonl')
    assert len(cases)==len({c['id'] for c in cases})==8
    assert all(c['training_eligible'] is False for c in cases)
    assert not {c['prompt'] for c in cases} & {r['messages'][0]['content'] for r in candidates.values()}
    assert sum('expected_json' in c for c in cases)==4
    assert next(c for c in cases if c['id']=='sr14-future')['expected_json']['minutes_to_schedule']==35
    tokens=json.loads((out/'tokenizer-preflight.json').read_text())
    for n,h in tokens['input_hashes'].items():assert file_hash(ROOT/n)==h,n
    assert tokens['passed'] and tokens['candidates']==9 and tokens['evaluation_prompts']==8 and tokens['maximum_training_tokens']<=2048
    assert tokens['maximum_evaluation_prompt_tokens']+384<=2048 and not tokens['weights_loaded'] and not tokens['inference_executed'] and not tokens['training_executed']
    return dict(passed=True,source_exact_repair_candidates=9,unique_parent_lessons=9,new_source_spans=0,new_literary_teaching_answers_authored=0,
                new_unrun_evaluation_cases=8,old_models_and_experiments_unchanged=True,human_quality_ratings=0,preparation_only=True,model_promoted=False)


if __name__=='__main__':print(json.dumps(verify(),indent=2))
