"""Freeze a proposed local recipe after offline tokenizer checks; never launch training."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
from collections import Counter
import json
from pathlib import Path
import random
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,load_ledger,validate_dataset
from build import HERE,OUT,LEDGER,save,save_rows,verify,verify_files


def main():
    verify()
    pin_path=ROOT/'configs/narratryx-craft-v1.json'
    pin=json.loads(pin_path.read_text())
    base=Path.home()/'.cache/huggingface/hub'/('models--'+pin['base_repo'].replace('/','--'))/'snapshots'/pin['base_revision']
    for name,expected in pin['base_metadata'].items():
        if file_hash(base/name)!=expected:raise ValueError('pinned tokenizer metadata mismatch')
    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(str(base),None)
    from unsloth_cli._inference import ensure_studio_backend_path
    ensure_studio_backend_path()
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(str(base),local_files_only=True,trust_remote_code=False)
    records=validate_dataset(OUT/'records.jsonl',LEDGER,['GB','US'])
    training=[r for r in records if r['split']=='train']
    monitor=[r for r in records if r['split']=='validation']
    random.Random(42).shuffle(training)
    order=training+monitor
    ledger=load_ledger(LEDGER)
    tokens={'train':[],'validation':[]}
    counts=[]
    author_tokens=Counter()
    prose_tokens=0
    structural_tokens=0
    for row in order:
        prompt=tokenizer.apply_chat_template(row['messages'][:-1],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        answer=row['messages'][-1]['content']
        a=tokenizer.encode(prompt,add_special_tokens=False)
        b=tokenizer.encode(answer,add_special_tokens=False)
        if tokenizer.decode(b,skip_special_tokens=False)!=answer or tokenizer.eos_token_id is None:
            raise ValueError('target round-trip or EOS failure')
        ids=a+b+[tokenizer.eos_token_id]
        if len(ids)>2048:raise ValueError('refusing oversized example without truncation: '+row['id'])
        tokens[row['split']].append(dict(input_ids=ids,attention_mask=[1]*len(ids),labels=[-100]*len(a)+b+[tokenizer.eos_token_id]))
        counts.append(dict(id=row['id'],split=row['split'],total=len(ids),prompt=len(a),supervised=len(b)+1))
        if row['split']=='train':
            if answer.lstrip().startswith('{'):structural_tokens+=len(b)+1
            else:prose_tokens+=len(b)+1
            for author in {a for rid in row['rights_record_ids'] for a in ledger[rid]['author_ids']}:
                author_tokens[author]+=len(b)+1
    total=prose_tokens+structural_tokens
    if max(author_tokens.values())/total>.4:raise ValueError('contributor exceeds40percent supervised-token cap')
    for split in tokens:save_rows(OUT/(split+'.tokens.jsonl'),tokens[split])
    report=dict(passed=True,training_examples=80,development_monitor=16,maximum_tokens=max(c['total'] for c in counts),
         supervised_train_tokens=total,prose_supervised_tokens=prose_tokens,structural_supervised_tokens=structural_tokens,
         prose_supervised_fraction=prose_tokens/total,contributor_supervised_tokens=dict(author_tokens),
         training_record_order=[r['id'] for r in training],counts=counts,
         all_answers_roundtrip=True,all_prompt_tokens_masked=True,targets_truncated=False,
         model_weights_loaded=False,inference_run=False,training_launched=False,
         caveat='Per-contributor credit can overlap for historical editorial transmission. Row/token shares are not proof of an optimal training balance.')
    save(OUT/'tokenizer-preflight.json',report)
    request=json.loads((ROOT/'artifacts/revision-preflight-v1/request.proposed.json').read_text())
    request.update(project_name='Narratryx-grounding-balanced-v1',local_datasets=[str(OUT/'train.tokens.jsonl')],
        local_eval_datasets=[str(OUT/'validation.tokens.jsonl')],max_seq_length=2048,max_steps=20,
        save_steps=20,eval_steps=10,num_epochs=1,resume_from_checkpoint=None)
    save(OUT/'request.proposed.json',request)
    paths=[HERE/'build.py',HERE/'preflight.py',HERE/'review-decisions.json',HERE/'dataset-lock.json',
           ROOT/'foundation/balanced_curriculum.py',ROOT/'foundation/grounding_lessons.py',LEDGER,pin_path]
    paths += [OUT/name for name in ['records.jsonl','trace.jsonl','selection.json','semantic-reviewed.records.jsonl',
             'evaluation.cases.frozen.jsonl','train.tokens.jsonl','validation.tokens.jsonl',
             'tokenizer-preflight.json','request.proposed.json']]
    prior=json.loads((ROOT/'artifacts/revision-training-v4/protocol.frozen.json').read_text())
    protected=dict(prior['protected_artifacts'])
    for name in ['adapters.safetensors','adapter_config.json']:
        rel='artifacts/revision-training-v4/adapter/'+name
        protected[rel]=file_hash(ROOT/rel)
    verify_files(protected)
    save(OUT/'protocol.proposed.frozen.json',dict(status='reviewed_preflight_complete_not_launched',
        created_on='2026-10-29',input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in paths},
        protected_artifacts=protected,base_path=str(base),base_weights_sha256=pin['base_weights_sha256'],
        training=dict(records=80,prose_records=56,structural_records=24,context_limit=2048,
             max_steps=20,epochs=1,batch_size=1,gradient_accumulation=4,learning_rate='5e-6',lora_rank=8,lora_alpha=16,seed=42),
        resource_stop=dict(peak_mlx_gb=10,timeout_seconds=1200,stop_on_warning_error_or_nonfinite=True),
        evaluation=dict(new_cases=40,clock_cases=24,prose_transfer_cases=16,prose_scenarios=4,
             baseline_before_training=True,conditions=['base','current-craft','candidate'],fresh_context_each_request=True,
             temperature=0,seed=42,max_new_tokens=384,enable_thinking=False,cached_tokens=0),
        retention=dict(path='artifacts/revision-preflight-v1/test.cases.jsonl',sha256=file_hash(ROOT/'artifacts/revision-preflight-v1/test.cases.jsonl'),
             cases=24,status='exposed development regression, not a fresh benchmark'),
        validation='Sixteen exposed Wray monitor records retained, not an independent project-wide test set.',
        promotion='No automatic promotion; human literary-quality judgements remain separate and unfilled.',
        scope='Frozen proposal only. No training runner launched, paid jobs, uploads, app changes, service action or model promotion.',
        limits=['70/30 is an experimental row balance, not an established optimal ratio.',
                'Source materials and most prose have been used before; new structural supervision is not new independent literature.',
                'Existing eight-step runner must not execute this20-step proposal without a separately checked execution wrapper.',
                'Closed JSON accuracy must be evaluated separately from semantic and literary transfer.']))
    print(json.dumps({k:report[k] for k in ['training_examples','development_monitor','maximum_tokens',
       'supervised_train_tokens','prose_supervised_tokens','structural_supervised_tokens','training_launched']},indent=2))


if __name__=='__main__':main()
