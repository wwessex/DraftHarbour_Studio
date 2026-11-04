"""Audit the installed Unsloth data path without loading weights or starting training."""
import importlib.metadata
import inspect
import json
import os
from pathlib import Path
import runpy
import sys

os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1',
                  UNSLOTH_MLX_PROMPT_CACHE_BYTES='0', HF_DATASETS_OFFLINE='1')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.trainer_recipe import token_multiset, validate_token_row
from foundation.validation import file_hash, read_jsonl

DATA = ROOT / 'artifacts/curriculum-fit-v24'
REFERENCE = ROOT / 'artifacts/trainer-recipe-v21b'
OUT = ROOT / 'artifacts/trainer-audit-v25'


def audit_batches(rows, prepared, tokenizer, create_batches, size):
    actual = []
    padding = batches = 0
    for batch, lengths, labels in create_batches(
            prepared, tokenizer, size, 2048, seed=42, append_eos=False):
        assert labels is not None
        ids_rows, bounds, lab_rows = batch.tolist(), lengths.tolist(), labels.tolist()
        assert len(ids_rows) == len(bounds) == len(lab_rows) == size
        for ids, (start, end), lab in zip(ids_rows, bounds, lab_rows):
            assert start == 0 and 0 < end <= len(ids) == len(lab)
            assert lab[end:] == [-100] * (len(lab) - end)
            padding += len(lab) - end
            row = dict(input_ids=ids[:end], labels=lab[:end], attention_mask=[1] * end)
            validate_token_row(row, tokenizer.eos_token_id)
            actual.append(row)
        batches += 1
    assert token_multiset(actual) == token_multiset(rows)
    return dict(batch_size=size, batches=batches, rows=len(actual), ignored_padding_tokens=padding,
                supervised_tokens=sum(x != -100 for r in actual for x in r['labels']))


def main():
    assert not OUT.exists(), 'Refuse overwrite'
    manifest_path = ROOT / 'curation/curriculum-fit-v24/manifest.json'
    manifest = json.loads(manifest_path.read_text())
    for name, expected in manifest['completion_hashes'].items():
        assert file_hash(ROOT / name) == expected, name
    assert runpy.run_path(str(ROOT / 'curation/curriculum-fit-v24/verify.py'))['verify']()['passed']
    ref = json.loads((REFERENCE / 'installed-audit.json').read_text())
    plan = json.loads((REFERENCE / 'protocol.proposed.frozen.json').read_text())
    pins = json.loads((REFERENCE / 'model-metadata.pins.json').read_text())['model_metadata_hashes']
    versions = {name: importlib.metadata.version(name) for name in ref['reference_environment']}
    assert versions == ref['reference_environment'], 'Installed package versions differ from v21b'
    installed = ref['installed_source_hashes']
    for name, expected in (installed | pins).items():
        assert file_hash(Path(name)) == expected, name

    from unsloth_cli.commands.train import _activate_mlx_transformers
    from unsloth_cli._inference import ensure_studio_backend_path
    base = plan['base_path']
    _activate_mlx_transformers(base, None)
    ensure_studio_backend_path()
    from transformers import AutoTokenizer, __version__ as tokenizer_version
    from datasets import Dataset
    from utils.datasets.pretokenized import (
        prepare_pretokenized_dataset, has_custom_labels, is_pretokenized_dataset,
    )
    from unsloth_zoo.mlx.utils import create_batches

    assert tokenizer_version == ref['active_tokenizer_transformers']
    for fn in (_activate_mlx_transformers, prepare_pretokenized_dataset, create_batches):
        assert file_hash(Path(inspect.getsourcefile(fn))) == installed[inspect.getsourcefile(fn)]
    tokenizer = AutoTokenizer.from_pretrained(base, local_files_only=True, trust_remote_code=False)
    records = read_jsonl(DATA / 'records.review-only.jsonl')
    expected_counts = json.loads((DATA / 'tokenizer-preflight.json').read_text())['counts']
    counts, results = {}, {}
    for split, old_count, count in [('train', 28, 34), ('validation', 16, 16)]:
        rows = []
        for record in (r for r in records if r['split'] == split):
            messages = record['messages']
            prompt = tokenizer.apply_chat_template(
                messages[:-1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
            a = tokenizer.encode(prompt, add_special_tokens=False)
            answer = messages[-1]['content']
            b = tokenizer.encode(answer, add_special_tokens=False)
            eos = tokenizer.eos_token_id
            assert tokenizer.decode(b, skip_special_tokens=False) == answer
            assert eos not in b
            ids = a + b + [eos]
            row = dict(input_ids=ids, labels=[-100] * len(a) + b + [eos],
                       attention_mask=[1] * len(ids))
            supervised = validate_token_row(row, eos)
            counts[record['id']] = dict(split=split, prompt=len(a), supervised=supervised, total=len(ids))
            rows.append(row)
        assert len(rows) == count
        assert rows[:old_count] == read_jsonl(REFERENCE / f'{split}.tokens.jsonl')
        dataset = Dataset.from_list(rows)
        assert is_pretokenized_dataset(dataset) and has_custom_labels(dataset)
        prepared = prepare_pretokenized_dataset(dataset, max_seq_length=None,
                                                vocab_size=len(tokenizer), mlx=True)
        assert [dict(row) for row in prepared] == rows
        results[split] = [audit_batches(rows, prepared, tokenizer, create_batches, size) for size in (1, 2)]
        assert results[split][1]['ignored_padding_tokens'] > 0
    assert counts == expected_counts
    assert results['train'][0]['supervised_tokens'] == 3706
    report = dict(passed=True, train_records=34, exposed_monitor_records=16,
                  maximum_tokens=max(c['total'] for c in counts.values()), batches=results,
                  record_counts=counts, retained_legacy_token_rows=44, eos_per_target=1,
                  all_tokens_and_labels_preserved=True, versions=versions,
                  active_tokenizer_transformers=tokenizer_version, installed_source_hashes=installed,
                  model_metadata_hashes=pins, training=False, worker_started=False, inference_requests=0,
                  weights_loaded=False, recipe_frozen=False,
                  input_hashes={str(p.relative_to(ROOT)): file_hash(p) for p in [
                      Path(__file__), manifest_path, DATA / 'records.review-only.jsonl',
                      DATA / 'tokenizer-preflight.json', REFERENCE / 'installed-audit.json',
                      REFERENCE / 'model-metadata.pins.json', REFERENCE / 'protocol.proposed.frozen.json',
                      REFERENCE / 'train.tokens.jsonl', REFERENCE / 'validation.tokens.jsonl',
                      ROOT / 'foundation/trainer_recipe.py']})
    OUT.mkdir()
    with (OUT / 'installed-audit.json').open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
