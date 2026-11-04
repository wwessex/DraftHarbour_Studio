"""Freeze one-presentation source-only pilot; tokenise and audit installed collation."""
import os
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
import copy
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash, read_jsonl, validate_dataset
from plan_checks import validate_plan

DATA=ROOT/'artifacts/paragraph-dialogue-v12'
OUT=ROOT/'artifacts/task-matched-v13-plan'


def main():
    if OUT.exists():raise ValueError('Refuse overwrite')
    parent=json.loads((ROOT/'artifacts/stability-v10/protocol.frozen.json').read_text())
    lock_path=ROOT/'curation/paragraph-dialogue-v12/preparation.lock.json'
    lock=json.loads(lock_path.read_text())
    protected=dict(parent['input_hashes']) | dict(parent['protected_artifacts']) | dict(lock['source_hashes'])
    protected.update({str((DATA/n).relative_to(ROOT)):h for n,h in lock['artifact_hashes'].items()})
    for n in ['protocol.frozen.json','completion.json','candidate.complete.json','candidate.responses.jsonl','verification.json','adapter/adapters.safetensors','adapter/adapter_config.json']:
        p=ROOT/'artifacts/stability-v10'/n;protected[str(p.relative_to(ROOT))]=file_hash(p)
    for n,h in protected.items():assert file_hash(ROOT/n)==h,n
    records=read_jsonl(DATA/'records.proposed.jsonl')
    validate_dataset(DATA/'records.proposed.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US'])
    assert len(records)==41 and sum(r['split']=='train' for r in records)==25
    base=parent['base_path']
    assert file_hash(Path(base)/'model.safetensors')==parent['base_weights_sha256']
    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(base,None)
    from unsloth_cli._inference import ensure_studio_backend_path
    ensure_studio_backend_path()
    from transformers import AutoTokenizer
    from unsloth_zoo.mlx.utils import create_batches
    tokenizer=AutoTokenizer.from_pretrained(base,local_files_only=True,trust_remote_code=False)
    train=[];monitor=[];counts={}
    for r in records:
        prompt=tokenizer.apply_chat_template(r['messages'][:-1],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        answer=r['messages'][-1]['content'];a=tokenizer.encode(prompt,add_special_tokens=False);b=tokenizer.encode(answer,add_special_tokens=False)
        assert tokenizer.decode(b,skip_special_tokens=False)==answer
        ids=a+b+[tokenizer.eos_token_id];assert len(ids)<=2048,r['id']
        row=dict(input_ids=ids,attention_mask=[1]*len(ids),labels=[-100]*len(a)+b+[tokenizer.eos_token_id])
        (train if r['split']=='train' else monitor).append(row)
        counts[r['id']]=dict(split=r['split'],prompt=len(a),supervised=len(b)+1,total=len(ids))
    expected=Counter((tuple(r['input_ids']),tuple(r['labels'])) for r in train);actual=Counter();supervised=0
    for batch,lengths,labels in create_batches(train,tokenizer,1,2048,seed=42,append_eos=False):
        assert labels is not None
        end=int(lengths.tolist()[0][1]);ids=tuple(batch.tolist()[0][:end]);lab=labels.tolist()[0]
        assert all(x==-100 for x in lab[end:]);actual[(ids,tuple(lab[:end]))]+=1
        supervised+=sum(x!=-100 for x in lab[1:])
    assert actual==expected and len(train)==25 and len(monitor)==16 and supervised==2298
    fresh=copy.deepcopy(read_jsonl(ROOT/'artifacts/task-alignment-v11/cases.frozen.jsonl'))
    exposed=copy.deepcopy(read_jsonl(ROOT/'artifacts/stability-v10-plan/cases.frozen.jsonl'))
    cases=fresh+exposed;assert len(cases)==36 and len({r['id'] for r in cases})==36
    assert not {c['prompt'] for c in cases} & {r['messages'][0]['content'] for r in records}
    OUT.mkdir()
    def rows(n,values):
        with (OUT/n).open('x') as f:
            for r in values:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    def save(n,value):
        with (OUT/n).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
    rows('train.tokens.jsonl',train);rows('validation.tokens.jsonl',monitor);rows('cases.frozen.jsonl',cases)
    tokens=dict(passed=True,train_records=25,monitor_records=16,supervised_train_tokens=supervised,
                collated_multiset_matches=True,prompt_tokens_masked=True,targets_truncated=False,
                maximum_tokens=max(c['total'] for c in counts.values()),counts=counts)
    save('tokenizer-collation-preflight.json',tokens)
    request=json.loads((ROOT/'artifacts/stability-v10/request.json').read_text())
    request.update(project_name='Narratryx-task-matched-v13',local_datasets=[str(OUT/'train.tokens.jsonl')],
                   local_eval_datasets=[str(OUT/'validation.tokens.jsonl')],max_steps=25,num_epochs=1,save_steps=25,eval_steps=25)
    save('request.proposed.json',request)
    inputs={str(p.relative_to(ROOT)):file_hash(p) for p in [DATA/'records.proposed.jsonl',lock_path,Path(__file__),ROOT/'foundation/paragraph_lessons.py',
            ROOT/'rights/grounding-balanced-v1.scoped.jsonl',ROOT/'artifacts/task-alignment-v11/cases.frozen.jsonl',ROOT/'artifacts/stability-v10-plan/cases.frozen.jsonl',
            *[OUT/n for n in ['train.tokens.jsonl','validation.tokens.jsonl','cases.frozen.jsonl','tokenizer-collation-preflight.json','request.proposed.json']]]}
    protocol=dict(status='frozen_bounded_pilot',created_on='2026-11-01',base_path=base,base_weights_sha256=parent['base_weights_sha256'],
                  reference_environment=parent['reference_environment'],input_hashes=inputs,protected_artifacts=protected,training_steps=25,context_limit=2048,
                  training=dict(records=25,presentations=25,monitor_records=16,max_steps=25,epochs=1,batch_size=1,gradient_accumulation=1,learning_rate='5e-5',context_limit=2048),
                  evaluation=dict(cases=36,new_unrun_cases=12,exposed_cases=24,conditions=3,planned_requests=108,max_new_tokens=384,temperature=0,seed=42,repetition_penalty=1.0),
                  resource_stop=dict(max_steps=25,peak_mlx_gb=10,phase_timeout_seconds=1200,stop_on_warning_error_nonfinite=True),
                  scope='One authorised local Unsloth MLX fresh-base pilot, one presentation per training record. No generated literary teaching answers, paid jobs, remote calls, app changes, publication or promotion.',
                  limits=['Data and update budget differ from v10; not a single-variable causal study.','All training sources and Wray monitors are previously exposed.','Twelve newly authored tasks are correlated development cases; not an independent human benchmark.','Literary quality needs human review, not exact canonical continuation.'])
    assert validate_plan(protocol,request,tokens)
    save('protocol.proposed.frozen.json',protocol)
    print('Frozen25 train/16 monitor;2298 supervised tokens;36 cases;108 planned fresh-context requests.')


if __name__=='__main__':main()
