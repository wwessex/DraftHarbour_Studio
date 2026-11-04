"""Freeze 32 matched question cases after the v17b findings."""
import json
import os
import random
import sys
from pathlib import Path
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from foundation.question_ablation import cases as factor_cases
OUT=ROOT/'artifacts/question-ablation-v18-plan'


def main():
    if OUT.exists():raise ValueError('Refuse overwrite')
    lock_path=ROOT/'curation/mixed-training-v16-ai-review/review.lock.json'
    lock=json.loads(lock_path.read_text());protected=dict(lock['source_hashes'])|dict(lock['artifact_hashes'])
    prior=json.loads((ROOT/'artifacts/mixed-training-v16-ai-review/verification.json').read_text());protected.update(prior['protected_hashes'])
    for n,h in protected.items():assert file_hash(ROOT/n)==h,n
    cases=factor_cases();assert len(cases)==32
    source=ROOT/'artifacts/semantic-restoration-v14/cases.frozen.jsonl'
    original=next(c for c in read_jsonl(source) if c['id']=='sr14-binding')
    assert sum(c['prompt']==original['prompt'] for c in cases)==1
    for name in ['protocol.frozen.json','scores.json','experiment-complete.json']:
        
        for prior_run in ['format-diagnostic-v17','binding-ablation-v17b']:
            path=ROOT/'artifacts'/prior_run/name;protected[str(path.relative_to(ROOT))]=file_hash(path)
    parent=json.loads((ROOT/'artifacts/mixed-training-v16/protocol.frozen.json').read_text());base=parent['base_path']
    assert file_hash(Path(base)/'model.safetensors')==parent['base_weights_sha256']
    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(base,None)
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(base,local_files_only=True,trust_remote_code=False)
    sizes={}
    for c in cases:
        prompt=tokenizer.apply_chat_template([dict(role='user',content=c['prompt'])],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        sizes[c['id']]=len(tokenizer.encode(prompt,add_special_tokens=False));assert sizes[c['id']]+64<=2048
    OUT.mkdir()
    with (OUT/'cases.frozen.jsonl').open('x') as f:
        for c in cases:f.write(json.dumps(c,ensure_ascii=False)+'\n')
    p=dict(status='evaluation-only-frozen',created_on='2026-11-01',base_path=base,base_weights_sha256=parent['base_weights_sha256'],reference_environment=parent['reference_environment'],
           protected_artifacts=protected,input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in [lock_path,source,Path(__file__),ROOT/'foundation/format_diagnostic.py',ROOT/'foundation/binding_ablation.py',ROOT/'foundation/question_ablation.py',OUT/'cases.frozen.jsonl']},
           context_limit=2048,conditions=['base','current-craft','mixed-v16'],evaluation=dict(cases_per_condition=32,total_requests=96,max_new_tokens=64,temperature=0,seed=42,repetition_penalty=1.0),
           tokenizer_preflight=dict(passed=True,maximum_prompt_tokens=max(sizes.values()),counts=sizes,model_weights_loaded=False),
           resource_stop=dict(process_tree_rss_bytes=10000000000,phase_deadline_seconds=1200,stop_on_error_or_truncation=True),
           scope='Exploratory matched direct-question evaluation-only follow-up. No training, app changes, source acquisition, publication or promotion.',
           limits=['Designed after seeing v17/v17b results; not independent confirmation.','Two logical role states repeated across32 cells; not32 independent problems.','Only the addition of a direct question differs within each pair; unknown cue, field count and role/order are balanced backgrounds. No literary-quality claim.'])
    with (OUT/'protocol.proposed.frozen.json').open('x') as f:json.dump(p,f,indent=2);f.write('\n')
    print('Frozen32 matched cells;96 planned responses; no training.')


if __name__=='__main__':main()
