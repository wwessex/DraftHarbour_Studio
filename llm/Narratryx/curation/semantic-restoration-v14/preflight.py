"""Offline tokenizer-only check for nine exact-source repairs and eight test prompts."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
OUT=ROOT/'artifacts/semantic-restoration-v14'


def main():
    if (OUT/'tokenizer-preflight.json').exists():raise ValueError('Refuse overwrite')
    proof=json.loads((OUT/'verification.json').read_text())
    for group in ['protected_hashes','input_hashes']:
        for n,h in proof[group].items():assert file_hash(ROOT/n)==h,n
    for n,h in proof['output_hashes'].items():assert file_hash(OUT/n)==h,n
    parent=json.loads((ROOT/'artifacts/task-matched-training-v13/protocol.frozen.json').read_text())
    base=parent['base_path']
    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(base,None)
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(base,local_files_only=True,trust_remote_code=False)
    counts={}
    for r in read_jsonl(OUT/'candidates.jsonl'):
        prompt=tokenizer.apply_chat_template(r['messages'][:-1],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        answer=r['messages'][-1]['content'];a=tokenizer.encode(prompt,add_special_tokens=False);b=tokenizer.encode(answer,add_special_tokens=False)
        assert tokenizer.decode(b,skip_special_tokens=False)==answer
        labels=[-100]*len(a)+b+[tokenizer.eos_token_id]
        assert len(labels)<=2048 and all(t==-100 for t in labels[:len(a)]) and labels[len(a):]==b+[tokenizer.eos_token_id]
        counts[r['id']]=dict(prompt=len(a),supervised=len(b)+1,total=len(labels))
    case_counts={}
    for c in read_jsonl(OUT/'cases.frozen.jsonl'):
        prompt=tokenizer.apply_chat_template([dict(role='user',content=c['prompt'])],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        size=len(tokenizer.encode(prompt,add_special_tokens=False));assert size+384<=2048,c['id'];case_counts[c['id']]=size
    result=dict(passed=True,candidates=9,evaluation_prompts=8,maximum_training_tokens=max(c['total'] for c in counts.values()),
                supervised_tokens_for_one_presentation=sum(c['supervised'] for c in counts.values()),maximum_evaluation_prompt_tokens=max(case_counts.values()),
                context_limit=2048,answers_roundtrip=True,prompts_masked_in_proposed_labels=True,targets_truncated=False,
                weights_loaded=False,training_executed=False,inference_executed=False,
                limits='Tokenizer/label construction only. No executable token dataset, installed collation audit or training recipe supplied.',counts=counts,evaluation_prompt_counts=case_counts,
                input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in [OUT/'verification.json',OUT/'candidates.jsonl',OUT/'cases.frozen.jsonl',Path(__file__)]})
    with (OUT/'tokenizer-preflight.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['counts','evaluation_prompt_counts','input_hashes']},indent=2))


if __name__=='__main__':main()
