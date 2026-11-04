"""Freeze tokens, installed collation, executable proposed request and descriptors."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl,validate_dataset
OUT=ROOT/'artifacts/mixed-curriculum-v15b'


def main():
    if (OUT/'tokenizer-collation-preflight.json').exists():raise ValueError('Refuse overwrite')
    proof=json.loads((OUT/'verification.json').read_text())
    for group in ['protected_hashes','input_hashes']:
        for n,h in proof[group].items():assert file_hash(ROOT/n)==h,n
    for n,h in proof['output_hashes'].items():assert file_hash(OUT/n)==h,n
    parent=json.loads((ROOT/'artifacts/task-matched-training-v13/protocol.frozen.json').read_text())
    base=parent['base_path']
    assert file_hash(Path(base)/'model.safetensors')==parent['base_weights_sha256']
    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(base,None)
    from unsloth_cli._inference import ensure_studio_backend_path
    ensure_studio_backend_path()
    from transformers import AutoTokenizer
    from unsloth_zoo.mlx.utils import create_batches
    tokenizer=AutoTokenizer.from_pretrained(base,local_files_only=True,trust_remote_code=False)
    records=read_jsonl(OUT/'records.proposed.jsonl')
    validate_dataset(OUT/'records.proposed.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US'])
    train=[];monitor=[];counts={};categories=Counter()
    for r in records:
        prompt=tokenizer.apply_chat_template(r['messages'][:-1],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        answer=r['messages'][-1]['content'];a=tokenizer.encode(prompt,add_special_tokens=False);b=tokenizer.encode(answer,add_special_tokens=False)
        assert tokenizer.decode(b,skip_special_tokens=False)==answer
        ids=a+b+[tokenizer.eos_token_id];assert len(ids)<=2048,r['id']
        labels=[-100]*len(a)+b+[tokenizer.eos_token_id]
        row=dict(input_ids=ids,attention_mask=[1]*len(ids),labels=labels)
        (train if r['split']=='train' else monitor).append(row)
        counts[r['id']]=dict(split=r['split'],prompt=len(a),supervised=len(b)+1,total=len(ids))
        if r['split']=='train':
            category='semantic-repair' if r['id'].startswith('sr14-') else 'structural-edit' if r['id'].startswith('gb-ge-') else 'broader-prose'
            categories[category]+=len(b)+1
    expected=Counter((tuple(r['input_ids']),tuple(r['labels'])) for r in train);actual=Counter();supervised=0
    for batch,lengths,labels in create_batches(train,tokenizer,1,2048,seed=42,append_eos=False):
        assert labels is not None
        end=int(lengths.tolist()[0][1]);ids=tuple(batch.tolist()[0][:end]);lab=labels.tolist()[0]
        assert all(x==-100 for x in lab[end:]);actual[(ids,tuple(lab[:end]))]+=1
        supervised+=sum(x!=-100 for x in lab[1:])
    assert actual==expected and len(train)==22 and len(monitor)==16 and supervised==sum(categories.values())
    evaluation_counts={}
    cases=read_jsonl(OUT/'primary.cases.frozen.jsonl')+read_jsonl(OUT/'seen-fit.cases.frozen.jsonl')
    for c in cases:
        prompt=tokenizer.apply_chat_template([dict(role='user',content=c['prompt'])],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        size=len(tokenizer.encode(prompt,add_special_tokens=False));assert size+384<=2048,c['id'];evaluation_counts[c['id']]=size
    def save(n,value):
        with (OUT/n).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
    for name,values in [('train.tokens.jsonl',train),('validation.tokens.jsonl',monitor)]:
        with (OUT/name).open('x') as f:
            for r in values:f.write(json.dumps(r)+'\n')
    tokens=dict(passed=True,training_records=22,presentations=22,monitor_records=16,supervised_training_tokens=supervised,
                supervised_tokens_by_category=dict(categories),maximum_record_tokens=max(c['total'] for c in counts.values()),
                all_answers_roundtrip=True,all_prompts_masked=True,targets_truncated=False,collated_multiset_matches=True,
                evaluation_cases=49,maximum_evaluation_prompt_tokens=max(evaluation_counts.values()),counts=counts,evaluation_prompt_counts=evaluation_counts)
    save('tokenizer-collation-preflight.json',tokens)
    request=json.loads((ROOT/'artifacts/task-matched-training-v13/request.json').read_text())
    request.update(project_name='Narratryx-mixed-curriculum-v15',local_datasets=[str(OUT/'train.tokens.jsonl')],local_eval_datasets=[str(OUT/'validation.tokens.jsonl')],max_steps=22,num_epochs=1,save_steps=22,eval_steps=22)
    save('request.proposed.json',request)
    inputs=dict(proof['input_hashes'])
    paths=[Path(__file__),OUT/'verification.json',*[OUT/n for n in ['records.proposed.jsonl','selection.jsonl','primary.cases.frozen.jsonl','seen-fit.cases.frozen.jsonl','train.tokens.jsonl','validation.tokens.jsonl','tokenizer-collation-preflight.json','request.proposed.json']]]
    inputs.update({str(p.relative_to(ROOT)):file_hash(p) for p in paths})
    protocol=dict(status='proposal-ready-not-execution',created_on='2026-11-01',base_path=base,base_weights_sha256=parent['base_weights_sha256'],reference_environment=parent['reference_environment'],
                  input_hashes=inputs,protected_artifacts=proof['protected_hashes'],training_steps=22,context_limit=2048,
                  training=dict(records=22,presentations=22,broader_prose=14,semantic_repairs=5,structural_edits=3,monitor_records=16,
                                epochs=1,batch_size=1,gradient_accumulation=1,learning_rate='5e-5',lora_rank=8,lora_alpha=16,lora_dropout=0,seed=42),
                  evaluation=dict(primary_cases=44,new_unrun_primary=8,exposed_primary=36,seen_training_fit_cases=5,conditions=['base','current-craft','candidate'],primary_requests=132,seen_fit_requests=15,total_requests=147,
                                  max_new_tokens=384,temperature=0,seed=42,repetition_penalty=1.0,fresh_context=True),
                  primary_cases_path=str((OUT/'primary.cases.frozen.jsonl').relative_to(ROOT)),seen_fit_cases_path=str((OUT/'seen-fit.cases.frozen.jsonl').relative_to(ROOT)),
                  resource_stop=dict(max_steps=22,peak_mlx_gb=10,process_tree_rss_bytes=10000000000,phase_deadline_seconds=1200,stop_on_warning_error_nonfinite_or_truncation=True),
                  scope='Preparation only. No training/inference, generated literary answers, paid jobs, publication, app changes or promotion.',
                  limits=['No source diversity added.','Monitors and36 regressions are exposed; five fit prompts intentionally equal training prompts and cannot measure generalisation.','Data mixture and update count differ from v13; not a single-factor experiment.','Repair anchor checks are proxies; prose quality needs human review.'])
    assert request['max_steps']==protocol['training_steps']==len(train)==22 and request['resume_from_checkpoint'] is None
    assert protocol['evaluation']['total_requests']==3*len(cases)==147
    save('protocol.proposed.frozen.json',protocol)
    print(json.dumps({k:v for k,v in tokens.items() if k not in ['counts','evaluation_prompt_counts']},indent=2))


if __name__=='__main__':main()
