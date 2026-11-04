"""Offline tokenizer/mask check only; no training, inference or model weight loading."""
import os
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl, validate_dataset
from build import HERE, OUT, LEDGER, save, save_rows, verify


def main():
    verify()
    pin = json.loads((ROOT/'configs/narratryx-craft-v1.json').read_text())
    base = Path.home()/'.cache/huggingface/hub'/('models--'+pin['base_repo'].replace('/','--'))/'snapshots'/pin['base_revision']
    for name, expected in pin['base_metadata'].items():
        if file_hash(base/name) != expected:
            raise ValueError('pinned tokenizer/base metadata mismatch')
    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(str(base), None)
    from unsloth_cli._inference import ensure_studio_backend_path
    ensure_studio_backend_path()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(base), local_files_only=True, trust_remote_code=False)
    records = validate_dataset(OUT/'records.jsonl', LEDGER, ['GB','US'])
    trace = {r['id']:r for r in read_jsonl(OUT/'trace.jsonl')}
    tokens, counts = [], []
    for row in records:
        prompt = tokenizer.apply_chat_template(row['messages'][:-1], tokenize=False,
                                               add_generation_prompt=True, enable_thinking=False)
        answer = row['messages'][-1]['content']
        a = tokenizer.encode(prompt, add_special_tokens=False)
        b = tokenizer.encode(answer, add_special_tokens=False)
        if tokenizer.decode(b, skip_special_tokens=False) != answer or tokenizer.eos_token_id is None:
            raise ValueError('target does not round-trip or EOS unavailable')
        ids = a+b+[tokenizer.eos_token_id]
        if len(ids)>2048:
            raise ValueError('oversized lesson; refusing truncation: '+row['id'])
        tokens.append(dict(input_ids=ids, attention_mask=[1]*len(ids), labels=[-100]*len(a)+b+[tokenizer.eos_token_id]))
        counts.append(dict(id=row['id'],kind=trace[row['id']]['kind'],prompt=len(a),supervised=len(b)+1,total=len(ids)))
    save_rows(OUT/'all.tokens.jsonl',tokens)
    save(OUT/'tokenizer-preflight.json',dict(passed=True,examples=len(counts),maximum_tokens=max(c['total'] for c in counts),
        supervised_tokens=sum(c['supervised'] for c in counts),counts=counts,all_targets_roundtrip=True,
        all_prompt_tokens_masked=True,targets_truncated=False,model_weights_loaded=False,inference_run=False,
        training_launched=False,approved_training_mixture=False,
        warning='Structural-only packet. Do not train as the entire fiction curriculum. Token count is not model-quality evidence.'))
    save(HERE/'token-lock.json',dict(files={str(p.relative_to(ROOT)):file_hash(p) for p in
         [HERE/'preflight.py',OUT/'all.tokens.jsonl',OUT/'tokenizer-preflight.json']}))
    print(json.dumps(dict(examples=len(counts),maximum_tokens=max(c['total'] for c in counts),
                         supervised_tokens=sum(c['supervised'] for c in counts),trained=False)))


if __name__ == '__main__':
    main()
