"""Audit installed local preprocessing/batching and freeze a recipe without starting workers."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
import importlib.metadata
import inspect
import json
import runpy
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from foundation.trainer_recipe import token_multiset,validate_token_row,validate_plan
DATA=ROOT/'artifacts/source-candidates-v20'
OUT=ROOT/'artifacts/trainer-recipe-v21'
HERE=Path(__file__).resolve().parent


def main():
    if OUT.exists():raise ValueError('Refuse overwrite')
    assert runpy.run_path(str(ROOT/'curation/source-candidates-v20/verify.py'))['verify']()['passed']
    lock_path=ROOT/'curation/source-candidates-v20/preparation.lock.json'
    lock=json.loads(lock_path.read_text());protected={}
    for group in ['source_hashes','artifact_hashes']:protected.update(lock[group])
    source_proof=json.loads((DATA/'verification.json').read_text());protected.update(source_proof['protected_hashes'])
    protected.update(source_proof['input_hashes'])
    for n,h in protected.items():assert file_hash(ROOT/n)==h,n
    parent=json.loads((ROOT/'artifacts/mixed-training-v16/protocol.frozen.json').read_text())
    base=parent['base_path'];assert file_hash(Path(base)/'model.safetensors')==parent['base_weights_sha256']
    environment={name:importlib.metadata.version(name) for name in parent['reference_environment']}
    assert environment==parent['reference_environment']
    from unsloth_cli.commands.train import _activate_mlx_transformers,_create_cli_trainer
    _activate_mlx_transformers(base,None)
    from unsloth_cli._inference import ensure_studio_backend_path
    ensure_studio_backend_path()
    from transformers import AutoTokenizer
    from datasets import Dataset
    from utils.datasets.pretokenized import prepare_pretokenized_dataset,has_custom_labels,is_pretokenized_dataset
    from unsloth_zoo.mlx.utils import create_batches
    tokenizer=AutoTokenizer.from_pretrained(base,local_files_only=True,trust_remote_code=False)
    records=read_jsonl(DATA/'records.proposed.jsonl');splits={'train':[],'validation':[]};counts={};categories=Counter()
    for r in records:
        prompt=tokenizer.apply_chat_template(r['messages'][:-1],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        answer=r['messages'][-1]['content'];a=tokenizer.encode(prompt,add_special_tokens=False);b=tokenizer.encode(answer,add_special_tokens=False)
        assert tokenizer.decode(b,skip_special_tokens=False)==answer
        ids=a+b+[tokenizer.eos_token_id];labels=[-100]*len(a)+b+[tokenizer.eos_token_id]
        row=dict(input_ids=ids,attention_mask=[1]*len(ids),labels=labels)
        assert validate_token_row(row,tokenizer.eos_token_id)==len(b)+1 and ids[-2]!=tokenizer.eos_token_id
        splits[r['split']].append(row)
        counts[r['id']]=dict(split=r['split'],prompt=len(a),supervised=len(b)+1,total=len(ids))
        if r['split']=='train':
            category='semantic-repair' if r['id'].startswith('sr14-') else 'structural-edit' if r['id'].startswith('gb-ge-') else 'broader-prose'
            categories[category]+=len(b)+1
    assert len(splits['train'])==28 and len(splits['validation'])==16
    batching={}
    for split,rows in splits.items():
        dataset=Dataset.from_list(rows)
        assert is_pretokenized_dataset(dataset) and has_custom_labels(dataset)
        prepared=prepare_pretokenized_dataset(dataset,max_seq_length=None,vocab_size=len(tokenizer),mlx=True)
        actual_rows=[dict(r) for r in prepared]
        assert actual_rows==rows,'Installed preprocessor changed source labels/tokens'
        collated=[];supervised=0
        for batch,lengths,labels in create_batches(prepared,tokenizer,1,2048,seed=42,append_eos=False):
            assert labels is not None
            end=int(lengths.tolist()[0][1]);ids=batch.tolist()[0][:end];lab=labels.tolist()[0]
            assert all(x==-100 for x in lab[end:])
            row=dict(input_ids=ids,labels=lab[:end],attention_mask=[1]*end)
            supervised+=validate_token_row(row,tokenizer.eos_token_id)
            collated.append(row)
        assert token_multiset(collated)==token_multiset(rows)
        assert supervised==sum(sum(x!=-100 for x in r['labels']) for r in rows)
        batching[split]=dict(rows=len(rows),supervised_tokens=supervised,preprocessing_unchanged=True,collated_multiset_matches=True,append_eos=False,padding_labels_ignored=True)
    assert batching['train']['supervised_tokens']==3033
    cases_source=ROOT/'artifacts/mixed-training-v16/cases.frozen.jsonl'
    cases=read_jsonl(cases_source)
    seen=[c for c in cases if c.get('evaluation_role')=='seen-training-fit-not-generalisation']
    primary=[dict(c,evaluation_role='exposed-development-regression') for c in cases if c not in seen]
    assert len(primary)==44 and len(seen)==5 and all(c.get('training_prompt_overlap_intentional') for c in seen)
    sizes={}
    for c in primary+seen:
        prompt=tokenizer.apply_chat_template([dict(role='user',content=c['prompt'])],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        sizes[c['id']]=len(tokenizer.encode(prompt,add_special_tokens=False));assert sizes[c['id']]+384<=2048
    request=json.loads((ROOT/'artifacts/mixed-training-v16/request.json').read_text())
    request.update(project_name='Narratryx-source-candidates-v21',local_datasets=[str(OUT/'train.tokens.jsonl')],local_eval_datasets=[str(OUT/'validation.tokens.jsonl')],max_steps=28,num_epochs=1,save_steps=28,eval_steps=28)
    # Installed adapter calls queue metadata only; no start_training, process or model worker is invoked.
    trainer=_create_cli_trainer(base,None)
    assert trainer.load_model(base,max_seq_length=2048,load_in_4bit=False,trust_remote_code=False,use_gradient_checkpointing='mlx')
    assert trainer.prepare_model_for_training(use_lora=True,target_modules=request['target_modules'],lora_r=8,lora_alpha=16,lora_dropout=0,use_gradient_checkpointing='mlx',random_state=42)
    trainer.load_and_format_dataset('',format_type='auto',local_datasets=request['local_datasets'],local_eval_datasets=request['local_eval_datasets'],eval_steps=28,is_cpt=False,dataset_local_files_only=True)
    worker=trainer._build_worker_config(dict(request,output_dir=str(ROOT/'artifacts/source-training-v22/adapter'),enable_wandb=False,enable_tensorboard=False,allow_ambient=False))
    assert worker['max_steps']==28 and worker['resume_from_checkpoint'] is None and worker['max_seq_length']==2048
    assert worker['local_datasets']==request['local_datasets'] and worker['local_eval_datasets']==request['local_eval_datasets']
    assert worker['train_on_completions'] is True and worker['packing'] is False
    assert float(worker['learning_rate'])==5e-5 and worker['lora_r']==8 and worker['lora_alpha']==16
    assert not trainer.training_thread and not trainer._pump_thread
    assert not worker.get('hf_token')
    installed_paths=[Path(inspect.getsourcefile(fn)) for fn in [prepare_pretokenized_dataset,create_batches,type(trainer),_create_cli_trainer]]
    installed_paths += [Path(inspect.getsourcefile(type(trainer))).parent/'worker.py']
    installed={str(p):file_hash(p) for p in set(installed_paths)}
    audit=dict(passed=True,training_records=28,presentations=28,monitor_records=16,supervised_training_tokens=3033,supervised_tokens_by_category=dict(categories),maximum_record_tokens=max(c['total'] for c in counts.values()),all_answers_roundtrip=True,all_prompts_masked=True,targets_truncated=False,all_preprocessing_unchanged=True,collated_multiset_matches=True,worker_configuration_checked=True,worker_execution_tested=False,training=False,inference=False,weights_loaded=False,worker_started=False,batching=batching,counts=counts,evaluation_prompt_counts=sizes,installed_source_hashes=installed,reference_environment=environment,default_transformers=environment.get('transformers'),active_tokenizer_transformers=importlib.metadata.version('transformers'),limits='Actual installed preprocessing/batching plus queued metadata/config construction only; no optimizer, forward/backward pass, runtime memory measurement or full training worker execution.')
    OUT.mkdir()
    def save(n,v):
        with (OUT/n).open('x') as f:json.dump(v,f,indent=2);f.write('\n')
    def rows(n,values):
        with (OUT/n).open('x') as f:
            for row in values:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    for split,values in splits.items():rows(split+'.tokens.jsonl',values)
    rows('primary.cases.frozen.jsonl',primary);rows('seen-fit.cases.frozen.jsonl',seen)
    save('installed-audit.json',audit);save('request.proposed.json',request);save('worker-config.proposed.json',worker)
    inputs={str(p.relative_to(ROOT)):file_hash(p) for p in [Path(__file__),ROOT/'foundation/trainer_recipe.py',lock_path,DATA/'records.proposed.jsonl',cases_source,*[OUT/n for n in ['train.tokens.jsonl','validation.tokens.jsonl','primary.cases.frozen.jsonl','seen-fit.cases.frozen.jsonl','installed-audit.json','request.proposed.json','worker-config.proposed.json']]]}
    protocol=dict(status='recipe-frozen-not-executed',created_on='2026-11-01',base_path=base,base_weights_sha256=parent['base_weights_sha256'],reference_environment=environment,installed_source_hashes=installed,input_hashes=inputs,protected_artifacts=protected,training_steps=28,context_limit=2048,training=dict(records=28,presentations=28,broader_prose=20,semantic_repairs=5,structural_edits=3,monitor_records=16,epochs=1,batch_size=1,gradient_accumulation=1,learning_rate='5e-5',lora_rank=8,lora_alpha=16,lora_dropout=0,seed=42),evaluation=dict(primary_cases=44,exposed_primary=44,new_unrun_primary=0,seen_training_fit_cases=5,conditions=['base','current-craft','candidate'],primary_requests=132,seen_fit_requests=15,total_requests=147,max_new_tokens=384,temperature=0,seed=42,repetition_penalty=1.0,fresh_context=True),resource_stop=dict(max_steps=28,peak_mlx_gb=10,process_tree_rss_bytes=10000000000,phase_deadline_seconds=1200,stop_on_warning_error_nonfinite_or_truncation=True),execution_requirements=['Fresh base, no adapter resume; revalidate hashes and environment before execution.','Reference calls before training; all requests fresh, no reuse or prior assistant history.','Execution wrapper must enforce outer memory/deadline stops, preserve recognised legacy service state and never interrupt unrelated apps.','Stop on training warnings/errors/nonfinite values, cap breach, evaluation error or truncation; no automatic retry.','Keep completion, mechanical constraint scores and informed/blinded human literary review separate.','No automatic promotion, application prompt/default changes, paid/cloud job or publication.'],quality_gates=dict(human_ratings_currently=0,require_independent_human_review_for_promotion=True,mechanical_checks=['word and paragraph/turn limits are separate from prose quality','closed JSON field/type/value checks','selected text preservation','long repeated dialogue/utterance flags','seen source repairs labelled fit only'],literary_review=['object/property fidelity','chronology and claims','permissions and resource use','concrete progression','voice and repetition','distinct dialogue aims and subtext']),scope='Preparation only; no training, inference, source acquisition or app changes.',limits=['28-example historical curriculum remains tiny; no broad literary upgrade established.','All44 primary cases and16 validation monitors are exposed; no fresh-author quality evidence.','Data mixture and step count differ from v16, so this is not a single-variable causal test.','Resource caps are requirements for the future executor, not enforced by passing a raw request to Studio.'])
    assert validate_plan(protocol,request,audit)
    save('protocol.proposed.frozen.json',protocol)
    print(json.dumps({k:v for k,v in audit.items() if k not in ['counts','evaluation_prompt_counts','installed_source_hashes']},indent=2))


if __name__=='__main__':main()
