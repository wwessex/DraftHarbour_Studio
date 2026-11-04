"""Offline tokenizer/masking check only: no model weights loaded or training."""
import os
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl


def main():
    out = ROOT / 'artifacts/source-candidates-v20'
    proof = json.loads((out / 'verification.json').read_text())
    if (out / 'tokenizer-preflight.json').exists():
        raise ValueError('Refuse overwrite')
    for group in ['protected_hashes', 'input_hashes']:
        for name, expected in proof[group].items():
            assert file_hash(ROOT / name) == expected, name
    for name, expected in proof['output_hashes'].items():
        assert file_hash(out / name) == expected, name
    parent = json.loads((ROOT / 'artifacts/stability-v10/protocol.frozen.json').read_text())
    base = parent['base_path']
    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(base, None)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(base, local_files_only=True, trust_remote_code=False)
    counts = {}
    for r in read_jsonl(out / 'records.proposed.jsonl'):
        prompt = tokenizer.apply_chat_template(r['messages'][:-1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        answer = r['messages'][-1]['content']
        a = tokenizer.encode(prompt, add_special_tokens=False)
        b = tokenizer.encode(answer, add_special_tokens=False)
        assert tokenizer.decode(b, skip_special_tokens=False) == answer
        assert len(a) + len(b) + 1 <= 2048, r['id']
        labels = [-100] * len(a) + b + [tokenizer.eos_token_id]
        assert all(x == -100 for x in labels[:len(a)]) and labels[len(a):] == b + [tokenizer.eos_token_id]
        counts[r['id']] = dict(split=r['split'], prompt=len(a), supervised=len(b) + 1, total=len(labels))
    report = dict(passed=True, training=False, weights_loaded=False, records=len(counts),
                  train_records=sum(c['split'] == 'train' for c in counts.values()),
                  maximum_tokens=max(c['total'] for c in counts.values()), context_limit=2048,
                  supervised_train_tokens=sum(c['supervised'] for c in counts.values() if c['split'] == 'train'),
                  answers_roundtrip=True, prompts_masked_in_proposed_labels=True, targets_truncated=False,
                  limits='Label construction only; no saved executable token files or installed collation/trainer audit for this proposal.',
                  input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in [out / 'records.proposed.jsonl', out / 'verification.json', Path(__file__)]}, counts=counts)
    with (out / 'tokenizer-preflight.json').open('x') as f:
        json.dump(report, f, indent=2)
    print(json.dumps({k:v for k,v in report.items() if k not in ['counts', 'input_hashes']}, indent=2))


if __name__ == '__main__':
    main()
