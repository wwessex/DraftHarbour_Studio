"""Pin the source-only mixture, explicit loss masks and bounded local recipe."""
import os
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
from pathlib import Path
import hashlib, json, math, random, sys, importlib.metadata
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import validate_dataset, check_leakage
P = ROOT/'artifacts/task-matched-v3'
RUN = ROOT/'artifacts/task-matched-training-v3'
BASE = Path('/Users/williamwessex/.cache/huggingface/hub/models--mlx-community--Qwen3.5-4B-MLX-8bit/snapshots/5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d')

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''): h.update(block)
    return h.hexdigest()
def save(p, value):
    with p.open('x') as f: json.dump(value, f, indent=2);f.write('\n')
def rows(p, values):
    with p.open('x') as f:
        for value in values:f.write(json.dumps(value)+'\n')

def main():
    RUN.mkdir(exist_ok=False)
    records=validate_dataset(P/'records.jsonl',ROOT/'rights/literary-mix-v2.scoped.jsonl',['GB','US'])
    cases=[json.loads(line) for line in (P/'test.cases.jsonl').read_text().splitlines()]
    check_leakage(records,[dict(id=case['id'],split_group=case['scenario_id'],context=case['context']) for case in cases])
    assert all(not case['word_count_min'] for case in cases if case['task']=='editing')
    assert all(case['context'] not in record['messages'][-1]['content'] for case in cases for record in records if record['split']=='train')
    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(str(BASE), None)
    from unsloth_cli._inference import ensure_studio_backend_path
    ensure_studio_backend_path()
    from transformers import AutoTokenizer
    from datasets import Dataset
    from utils.datasets.pretokenized import has_custom_labels
    tok=AutoTokenizer.from_pretrained(str(BASE),local_files_only=True,trust_remote_code=False)
    tokens={'train':[], 'validation':[]}; ids={'train':[], 'validation':[]}; counts=[]
    for record in records:
        prompt=tok.apply_chat_template([record['messages'][0]],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        answer=record['messages'][1]['content']
        a=tok.encode(prompt,add_special_tokens=False);b=tok.encode(answer,add_special_tokens=False)
        assert tok.decode(b,skip_special_tokens=False)==answer and tok.eos_token_id is not None
        input_ids=a+b+[tok.eos_token_id];labels=[-100]*len(a)+b+[tok.eos_token_id]
        assert len(input_ids)<=1024 and labels[:len(a)]==[-100]*len(a) and labels[len(a):]==input_ids[len(a):]
        row=dict(input_ids=input_ids,attention_mask=[1]*len(input_ids),labels=labels)
        tokens[record['split']].append(row);ids[record['split']].append(record['id'])
        counts.append(dict(id=record['id'],split=record['split'],total=len(input_ids),supervised=len(b)+1))
    # Fixed, evenly spaced validation subset, selected before any model response/loss.
    indices=sorted({round(i*(len(tokens['validation'])-1)/15) for i in range(16)})
    pairs=list(zip(tokens['train'],ids['train']));random.Random(42).shuffle(pairs)
    tokens['train'],ids['train']=map(list,zip(*pairs))
    for split in tokens:
        assert has_custom_labels(Dataset.from_list(tokens[split])), 'Installed worker must recognise explicit labels'
        rows(P/f'{split}.tokens.jsonl',tokens[split])
    rows(P/'validation-monitor.tokens.jsonl',[tokens['validation'][i] for i in indices])
    save(P/'tokenizer-preflight.json',dict(counts=counts,maximum_tokens=max(c['total'] for c in counts),supervised_train_tokens=sum(c['supervised'] for c in counts if c['split']=='train'),all_prompt_tokens_ignored=True,all_targets_roundtrip=True,installed_custom_label_detection=True,validation_monitor_ids=[ids['validation'][i] for i in indices],training_ids=ids['train']))
    cfg=json.loads((ROOT/'artifacts/craft-training-v2/request.json').read_text())
    steps=math.ceil(len(tokens['train'])/4)
    cfg.update(project_name='Narratryx-task-matched-v3',local_datasets=[str(P/'train.tokens.jsonl')],local_eval_datasets=[str(P/'validation-monitor.tokens.jsonl')],eval_steps=6,learning_rate='5e-6',num_epochs=1,max_steps=steps,save_steps=steps,warmup_steps=1,early_stopping_patience=0)
    save(RUN/'request.json',cfg)
    paths=[P/'records.jsonl',P/'trace.jsonl',P/'train.tokens.jsonl',P/'validation.tokens.jsonl',P/'validation-monitor.tokens.jsonl',P/'validation.json',P/'tokenizer-preflight.json',P/'test.cases.jsonl',ROOT/'rights/literary-mix-v2.scoped.jsonl',RUN/'request.json']
    paths += [ROOT/'runtime/local/engine.py', ROOT/'foundation/anchored_edits.py', ROOT/'foundation/literary_diagnostics.py']
    paths += [ROOT/'curation/task-matched-v3'/name for name in ['build.py','evaluation_cases.py','prepare.py','train.py','evaluate.py','review.py','audit.py']]
    old=['literary-mix-training-v1','literary-mix-training-v2','craft-training-v2','source-task-training-v1','clean-source-training-v1','clean-source-training-v2']
    protected={str((ROOT/'artifacts'/n/'adapter'/file).relative_to(ROOT)):sha(ROOT/'artifacts'/n/'adapter'/file) for n in old for file in ['adapters.safetensors','adapter_config.json']}
    save(RUN/'protocol.frozen.json',dict(experiment='task-matched-training-v3',user_authorization='User proceeded with the plan to curate source-only task-matched data, freeze fresh comparisons and run a bounded local candidate; no paid job, uploads, application default changes or promotion',frozen_before_baselines_and_training=True,input_hashes={str(p.relative_to(ROOT)):sha(p) for p in paths},base_path=str(BASE),base_weights_sha256=sha(BASE/'model.safetensors'),protected_artifacts=protected,training_steps=steps,resource_stop=dict(peak_mlx_gb=10,training_timeout_seconds=1200),model_conditions=['base','current-craft','candidate'],generation=dict(temperature=0,top_p=1,top_k=20,min_p=0,presence_penalty=0,repetition_penalty=1,seed=42,max_new_tokens=384,enable_thinking=False),test_cases_path=str((P/'test.cases.jsonl').relative_to(ROOT)),context_limit=2048,independent_requests=True,no_prompt_cache=True,packages={k:importlib.metadata.version(k) for k in ['mlx','mlx-lm','mlx-vlm','transformers']},promotion='No automatic promotion. Human blind ratings required; source-only small-model experiment is not Muse equivalence.',validation='Sixteen fixed evenly spaced Wray records; author/work excluded from this candidate training, previously seen in other exploratory adapters. Not independent project-wide test material.',evaluation_provenance='New original Codex AI-authored diagnostic fiction, evaluation only; not training data or a human-approved formal benchmark. Previous 24 cases are exposed development diagnostics.',limitations=json.loads((P/'validation.json').read_text())['limitations']))
    print(json.dumps(dict(train=len(tokens['train']),validation=len(tokens['validation']),monitor=len(indices),steps=steps,maximum_tokens=max(c['total'] for c in counts)),indent=2))
if __name__=='__main__':main()
