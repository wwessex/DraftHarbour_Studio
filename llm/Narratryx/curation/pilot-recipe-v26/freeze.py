"""Freeze the audited one-pass pilot and its comparison."""
import json
import os
from pathlib import Path
import sys

os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl
from foundation.trainer_recipe import validate_token_row

OUT = ROOT / 'artifacts/pilot-recipe-v26'
PREVIOUS = ROOT / 'artifacts/trainer-recipe-v21b'
AUDIT = ROOT / 'artifacts/trainer-audit-v25/installed-audit.json'
DATA = ROOT / 'artifacts/curriculum-fit-v24/records.review-only.jsonl'
MANIFEST = ROOT / 'curation/trainer-audit-v25/manifest.json'


def save(path, value):
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2) + '\n')


def main():
    assert not OUT.exists(), OUT
    audit = json.loads(AUDIT.read_text())
    evidence = json.loads(MANIFEST.read_text())
    for name, expected in (evidence['input_hashes'] | evidence['completion_hashes']).items():
        assert file_hash(ROOT / name) == expected, name
    for name, expected in (audit['installed_source_hashes'] | audit['model_metadata_hashes']).items():
        assert file_hash(Path(name)) == expected, name
    assert audit['passed']
    prior_plan = json.loads((PREVIOUS / 'protocol.proposed.frozen.json').read_text())
    request = json.loads((PREVIOUS / 'request.proposed.json').read_text())
    base = prior_plan['base_path']
    assert file_hash(Path(base) / 'model.safetensors') == prior_plan['base_weights_sha256']

    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(base, None)
    from transformers import AutoTokenizer, __version__
    assert __version__ == audit['active_tokenizer_transformers']
    tokenizer = AutoTokenizer.from_pretrained(base, local_files_only=True, trust_remote_code=False)
    rows = {'train': [], 'validation': []}
    records = read_jsonl(DATA)
    assert all(record['teacher'] is None and record['origin'] == 'derived' for record in records)
    for record in records:
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
        row = dict(input_ids=ids, labels=[-100] * len(prefix) + target,
                   attention_mask=[1] * len(ids))
        count = dict(split=record['split'], prompt=len(prefix), supervised=validate_token_row(
            row, tokenizer.eos_token_id), total=len(ids))
        assert count == audit['record_counts'][record['id']]
        rows[record['split']].append(row)
    assert tuple(map(len, rows.values())) == (34, 16)
    for split, total in [('train', 3706), ('validation', 1709)]:
        assert sum(label != -100 for row in rows[split] for label in row['labels']) == total
        original = read_jsonl(PREVIOUS / f'{split}.tokens.jsonl')
        assert rows[split][:len(original)] == original
    primary_path = PREVIOUS / 'primary.cases.frozen.jsonl'
    seen_path = PREVIOUS / 'seen-fit.cases.frozen.jsonl'
    primary, seen = read_jsonl(primary_path), read_jsonl(seen_path)
    prompts = {r['messages'][0]['content'] for r in records if r['split'] == 'train'}
    assert len(primary) == 44 and len(seen) == 5
    assert len({c['id'] for c in primary + seen}) == 49
    assert all(c['prompt'] not in prompts for c in primary)
    assert all(c['prompt'] in prompts for c in seen)
    request.update(project_name='Narratryx-source-pilot-v26', max_steps=34, save_steps=34,
                   eval_steps=34, local_datasets=[str(OUT / 'train.tokens.jsonl')],
                   local_eval_datasets=[str(OUT / 'validation.tokens.jsonl')])
    assert request['num_epochs'] == request['batch_size'] == request['gradient_accumulation_steps'] == 1
    assert not request['packing'] and request['resume_from_checkpoint'] is None
    assert request['train_on_completions'] and request['max_seq_length'] == 2048
    OUT.mkdir()
    for split, values in rows.items():
        with (OUT / f'{split}.tokens.jsonl').open('x') as stream:
            for row in values:
                stream.write(json.dumps(row) + '\n')
    save(OUT / 'request.json', request)
    craft = ROOT / 'artifacts/craft-training-v2/adapter'
    pins = [Path(__file__), AUDIT, DATA, MANIFEST, primary_path, seen_path,
            ROOT / 'configs/narratryx-craft-v1.json',
            craft / 'adapters.safetensors', craft / 'adapter_config.json',
            *OUT.iterdir()]
    plan = dict(status='frozen-before-execution', training_steps=34,
                base_path=base, base_weights_sha256=prior_plan['base_weights_sha256'],
                input_hashes={str(p.relative_to(ROOT)): file_hash(p) for p in pins},
                installed_source_hashes=audit['installed_source_hashes'],
                model_metadata_hashes=audit['model_metadata_hashes'],
                reference_environment=audit['versions'],
                active_tokenizer_transformers=__version__,
                resource_stop=prior_plan['resource_stop'] | {'max_steps': 34},
                evaluation=prior_plan['evaluation'],
                primary_cases_path=str(primary_path.relative_to(ROOT)),
                seen_cases_path=str(seen_path.relative_to(ROOT)),
                execution_requirements=prior_plan['execution_requirements'],
                quality_gates=prior_plan['quality_gates'])
    save(OUT / 'protocol.frozen.json', plan)
    print('Frozen 34 training rows, 16 monitors, and 147 proposed comparison requests.')


if __name__ == '__main__':
    main()
