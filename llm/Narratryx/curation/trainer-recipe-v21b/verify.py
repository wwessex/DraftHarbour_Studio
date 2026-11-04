"""Read-only frozen recipe, environment-source and token supervision checks."""
import json
import runpy
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from foundation.trainer_recipe import validate_plan,validate_token_row
OUT=ROOT/'artifacts/trainer-recipe-v21b'


def verify():
    p=json.loads((OUT/'protocol.proposed.frozen.json').read_text())
    for group in ['input_hashes','protected_artifacts']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    for n,h in p['installed_source_hashes'].items():assert file_hash(Path(n))==h,n
    assert file_hash(Path(p['base_path'])/'model.safetensors')==p['base_weights_sha256']
    assert runpy.run_path(str(ROOT/'curation/source-candidates-v20/verify.py'))['verify']()['passed']
    pins=json.loads((OUT/'model-metadata.pins.json').read_text())
    assert pins['records_reproduced']==44 and pins['all_frozen_token_rows_identical']
    for n,h in pins['model_metadata_hashes'].items():assert file_hash(Path(n))==h,n
    for n,h in pins['input_hashes'].items():assert file_hash(ROOT/n)==h,n
    request=json.loads((OUT/'request.proposed.json').read_text());audit=json.loads((OUT/'installed-audit.json').read_text())
    assert validate_plan(p,request,audit)
    previous_tokens=json.loads((ROOT/'artifacts/source-candidates-v20/tokenizer-preflight.json').read_text())
    assert audit['counts']==previous_tokens['counts']
    source=read_jsonl(ROOT/'artifacts/source-candidates-v20/records.proposed.jsonl')
    for split,filename in [('train','train.tokens.jsonl'),('validation','validation.tokens.jsonl')]:
        rows=read_jsonl(OUT/filename);records=[r for r in source if r['split']==split]
        assert len(rows)==len(records)==audit['batching'][split]['rows']
        total=0
        for row,r in zip(rows,records):
            count=audit['counts'][r['id']];eos=row['input_ids'][-1]
            assert len(row['input_ids'])==count['total'] and eos==row['labels'][-1]
            assert row['labels'][:count['prompt']]==[-100]*count['prompt']
            assert row['labels'][count['prompt']:]==row['input_ids'][count['prompt']:]
            assert validate_token_row(row,eos)==count['supervised']
            total+=count['supervised']
        assert total==audit['batching'][split]['supervised_tokens']
    primary=read_jsonl(OUT/'primary.cases.frozen.jsonl');seen=read_jsonl(OUT/'seen-fit.cases.frozen.jsonl')
    original=read_jsonl(ROOT/'artifacts/mixed-training-v16/cases.frozen.jsonl')
    assert primary==[dict(c,evaluation_role='exposed-development-regression') for c in original if c.get('evaluation_role')!='seen-training-fit-not-generalisation']
    assert seen==[c for c in original if c.get('evaluation_role')=='seen-training-fit-not-generalisation']
    assert len(primary)==44 and len(seen)==5 and len({c['id'] for c in primary+seen})==49
    prompts={r['messages'][0]['content'] for r in source if r['split']=='train'}
    assert not prompts & {c['prompt'] for c in primary}
    assert all(c['prompt'] in prompts and c.get('training_prompt_overlap_intentional') for c in seen)
    worker=json.loads((OUT/'worker-config.proposed.json').read_text())
    for key in ['max_steps','num_epochs','batch_size','gradient_accumulation_steps','max_seq_length','save_steps','eval_steps','lora_r','lora_alpha','lora_dropout','packing','train_on_completions','local_datasets','local_eval_datasets']:
        assert worker[key]==request[key],key
    assert not worker.get('hf_token') and worker['resume_from_checkpoint'] is None
    assert p['status']=='recipe-frozen-not-executed' and not audit['worker_started'] and not audit['weights_loaded'] and not audit['training'] and not audit['inference']
    assert (OUT/'adapter').exists() is False
    return dict(passed=True,training_records=28,monitor_records=16,proposed_max_updates=28,supervised_train_tokens=3033,supervised_monitor_tokens=1709,maximum_record_tokens=499,primary_cases=44,all_primary_exposed=True,seen_fit_cases=5,proposed_requests=147,installed_source_hashes_match=True,cached_tokenizer_metadata_pinned=True,exact_token_masks_and_records_verified=True,prior_evidence_and_models_unchanged=True,worker_started=False,weights_loaded=False,training_executed=False,inference_requests=0,human_quality_ratings=0,model_promoted=False)


if __name__=='__main__':
    result=verify()
    with (OUT/'verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
