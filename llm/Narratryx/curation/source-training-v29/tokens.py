"""Audit the revised prompts against the previous token rows and installed batcher."""
import json
import runpy
from pathlib import Path
from foundation.validation import file_hash, read_jsonl, validate_dataset


def prepare(root, run, plan, request):
    from unsloth_cli.commands.train import _activate_mlx_transformers
    from unsloth_cli._inference import ensure_studio_backend_path

    proposal = root / 'artifacts/continuation-diagnostic-v28'
    path = proposal / 'records.review-only.jsonl'
    evidence = json.loads((proposal / 'proposal.json').read_text())
    assert file_hash(path) == evidence['output_sha256']
    ledger = root / 'rights/curriculum-fit-v24.scoped.jsonl'
    assert file_hash(ledger) == evidence['ledger_sha256']
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
    selected = set(evidence['changed_brief_ids'])
    changed = set()
    reports = {}
    for split, key, count, total in (
        ('train', 'local_datasets', 34, 3706),
        ('validation', 'local_eval_datasets', 16, 1709),
    ):
        previous = read_jsonl(Path(request[key][0]))
        source = [r for r in records if r['split'] == split]
        assert len(source) == len(previous) == count
        rows = []
        for record, old in zip(source, previous):
            messages = record['messages']
            prompt = tokenizer.apply_chat_template(messages[:-1], tokenize=False,
                                                   add_generation_prompt=True, enable_thinking=False)
            prefix = tokenizer.encode(prompt, add_special_tokens=False)
            answer = messages[-1]['content']
            target = tokenizer.encode(answer, add_special_tokens=False)
            assert tokenizer.decode(target, skip_special_tokens=False) == answer
            assert tokenizer.eos_token_id not in target
            target.append(tokenizer.eos_token_id)
            assert target == [label for label in old['labels'] if label != -100]
            ids = prefix + target
            row = dict(input_ids=ids, attention_mask=[1] * len(ids),
                       labels=[-100] * len(prefix) + target)
            if row != old:
                changed.add(record['id'])
            rows.append(row)
        prepared = prepare_pretokenized_dataset(Dataset.from_list(rows), max_seq_length=None,
                                                vocab_size=len(tokenizer), mlx=True)
        assert [dict(r) for r in prepared] == rows
        reports[split] = [audit(rows, prepared, tokenizer, create_batches, n) for n in (1, 2)]
        assert all(r['supervised_tokens'] == total for r in reports[split])
        output = run / f'{split}.tokens.jsonl'
        with output.open('x') as stream:
            for row in rows:
                stream.write(json.dumps(row) + '\n')
        request[key] = [str(output)]
    assert changed == selected
    return reports
