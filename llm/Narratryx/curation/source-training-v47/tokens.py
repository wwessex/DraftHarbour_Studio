"""Audit the expanded curriculum with the installed batcher."""
import json
import runpy
from pathlib import Path
from foundation.validation import file_hash, read_jsonl, validate_dataset


def prepare(root, run, plan, request):
    from unsloth_cli.commands.train import _activate_mlx_transformers
    from unsloth_cli._inference import ensure_studio_backend_path

    proposal = root / 'artifacts/balanced-writing-v47'
    path = proposal / 'records.review-only.jsonl'
    evidence = json.loads((proposal / 'review.json').read_text())
    for name, digest in evidence['hashes'].items():
        assert file_hash(root / name) == digest, name
    ledger = root / 'rights/balanced-writing-v47.scoped.jsonl'
    records = validate_dataset(path, ledger, ['GB', 'US'],
                               benchmark=read_jsonl(root / 'evaluation/tasks.draft.jsonl'))
    assert all(r['origin'] == 'derived' and r['teacher'] is None for r in records)
    _activate_mlx_transformers(plan['base_path'], None)
    ensure_studio_backend_path()
    from datasets import Dataset
    from transformers import AutoTokenizer, __version__
    from unsloth_zoo.mlx.utils import create_batches
    from utils.datasets.pretokenized import prepare_pretokenized_dataset

    assert __version__ == plan['active_tokenizer_transformers']
    tokenizer = AutoTokenizer.from_pretrained(plan['base_path'], local_files_only=True,
                                              trust_remote_code=False)
    audit = runpy.run_path(str(root / 'curation/trainer-audit-v25/audit.py'))['audit_batches']
    reports = {}
    for split, key, count, total in (
        ('train', 'local_datasets', 61, None),
        ('validation', 'local_eval_datasets', 16, 1709),
    ):
        previous = read_jsonl(Path(request[key][0]))
        source = [r for r in records if r['split'] == split]
        assert len(source) == count
        rows = []
        for record in source:
            messages = record['messages']
            prompt = tokenizer.apply_chat_template(messages[:-1], tokenize=False,
                                                   add_generation_prompt=True, enable_thinking=False)
            prefix = tokenizer.encode(prompt, add_special_tokens=False)
            answer = messages[-1]['content']
            target = tokenizer.encode(answer, add_special_tokens=False)
            assert tokenizer.decode(target, skip_special_tokens=False) == answer
            assert tokenizer.eos_token_id not in target
            target.append(tokenizer.eos_token_id)
            ids = prefix + target
            row = dict(input_ids=ids, attention_mask=[1] * len(ids),
                       labels=[-100] * len(prefix) + target)
            rows.append(row)
        prepared = prepare_pretokenized_dataset(Dataset.from_list(rows), max_seq_length=None,
                                                vocab_size=len(tokenizer), mlx=True)
        assert [dict(r) for r in prepared] == rows
        sizes = (1,) if len(rows) % 2 else (1, 2)
        reports[split] = [audit(rows, prepared, tokenizer, create_batches, n) for n in sizes]
        if total is not None:
            assert all(r['supervised_tokens'] == total for r in reports[split])
            assert rows == previous
        output = run / f'{split}.tokens.jsonl'
        with output.open('x') as stream:
            for row in rows:
                stream.write(json.dumps(row) + '\n')
        request[key] = [str(output)]
    return reports
