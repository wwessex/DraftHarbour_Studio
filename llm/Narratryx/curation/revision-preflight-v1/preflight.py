"""CPU tokenizer preflight and frozen prospective recipe; never loads model weights."""
import os
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
from collections import Counter
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import Invalid, check_leakage, load_ledger, read_jsonl, validate_dataset
from build import HERE, OUT, LEDGER, save, save_rows, sha, verify_files

BASE = Path('/Users/williamwessex/.cache/huggingface/hub/models--mlx-community--Qwen3.5-4B-MLX-8bit/snapshots/5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d')
LIMIT = 2048


def encode_example(tokenizer, messages, limit=LIMIT):
    if tokenizer.eos_token_id is None:
        raise Invalid('explicit EOS token required')
    prompt = tokenizer.apply_chat_template(messages[:-1], tokenize=False,
                                           add_generation_prompt=True, enable_thinking=False)
    answer = messages[-1]['content']
    a = tokenizer.encode(prompt, add_special_tokens=False)
    b = tokenizer.encode(answer, add_special_tokens=False)
    if tokenizer.decode(b, skip_special_tokens=False) != answer:
        raise Invalid('answer tokenization does not round-trip')
    ids = a + b + [tokenizer.eos_token_id]
    if len(ids) > limit:
        raise Invalid('untruncated example exceeds context allowance')
    return dict(input_ids=ids, attention_mask=[1]*len(ids), labels=[-100]*len(a)+b+[tokenizer.eos_token_id]), len(a), len(b)+1


def main():
    verify_files(json.loads((HERE / 'source-lock.json').read_text())['files'])
    verify_files(json.loads((HERE / 'dataset-lock.json').read_text())['files'])
    records = validate_dataset(OUT / 'records.jsonl', LEDGER, ['GB', 'US'])
    cases = read_jsonl(OUT / 'test.cases.jsonl')
    check_leakage(records, [dict(id=c['id'], split_group=c['scenario_id'], context=c['prompt']) for c in cases])
    if any(c['word_count_min'] is not None for c in cases if c['task'] == 'editing'):
        raise Invalid('editing diagnostic acquired a minimum length')
    # Installed Unsloth tokenizer compatibility only; no Trainer or model load call.
    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(str(BASE), None)
    from unsloth_cli._inference import ensure_studio_backend_path
    ensure_studio_backend_path()
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(str(BASE), local_files_only=True, trust_remote_code=False)
    tokens = {'train': [], 'validation': []}
    counts = []
    ledger = load_ledger(LEDGER)
    author_tokens = Counter()
    for row in records:
        encoded, prompt, answer = encode_example(tokenizer, row['messages'])
        tokens[row['split']].append(encoded)
        counts.append(dict(id=row['id'], split=row['split'], total=prompt+answer,
                           prompt=prompt, supervised=answer))
        if row['split'] == 'train':
            for author in {a for rid in row['rights_record_ids'] for a in ledger[rid]['author_ids']}:
                author_tokens[author] += answer
    supervised = sum(c['supervised'] for c in counts if c['split'] == 'train')
    if max(author_tokens.values()) / supervised > .4:
        raise Invalid('author exceeds40percent of supervised tokens')
    for split, rows in tokens.items():
        save_rows(OUT / f'{split}.tokens.jsonl', rows)
    report = dict(counts=counts, maximum_tokens=max(c['total'] for c in counts),
                  supervised_train_tokens=supervised, author_supervised_tokens=dict(author_tokens),
                  all_prompt_tokens_ignored=True, all_answers_roundtrip=True, targets_truncated=False,
                  model_weights_loaded=False, inference_run=False, training_launched=False,
                  memory_training_certified=False, context_allowance=LIMIT)
    save(OUT / 'tokenizer-preflight.json', report)
    request = json.loads((ROOT / 'artifacts/task-matched-training-v3/request.json').read_text())
    request.update(project_name='Narratryx-revision-pilot-v4', max_seq_length=LIMIT,
                   local_datasets=[str(OUT / 'train.tokens.jsonl')],
                   local_eval_datasets=[str(OUT / 'validation.tokens.jsonl')],
                   max_steps=8, save_steps=8, eval_steps=4, learning_rate='5e-6',
                   num_epochs=1, early_stopping_patience=0, resume_from_checkpoint=None)
    save(OUT / 'request.proposed.json', request)
    paths = [HERE / name for name in ['build.py', 'evaluation_cases.py', 'preflight.py', 'dataset-lock.json', 'source-lock.json']]
    paths += [OUT / name for name in ['records.jsonl', 'membership.json', 'selection.json', 'test.cases.jsonl', 'train.tokens.jsonl', 'validation.tokens.jsonl', 'tokenizer-preflight.json', 'request.proposed.json']]
    paths += [LEDGER, ROOT / 'configs/narratryx-craft-v1.json']
    old_protocol = json.loads((ROOT / 'artifacts/task-matched-training-v3/protocol.frozen.json').read_text())
    save(OUT / 'protocol.proposed.frozen.json', dict(
        status='preflight_complete_not_launched', input_hashes={str(p.relative_to(ROOT)): sha(p) for p in paths},
        base_path=str(BASE), base_weights_sha256=old_protocol['base_weights_sha256'],
        protected_artifacts=old_protocol['protected_artifacts'],
        training=dict(max_steps=8, learning_rate='5e-6', lora_rank=8, lora_alpha=16,
                      batch_size=1, gradient_accumulation=4, seed=42, context=LIMIT),
        resource_stop=dict(peak_mlx_gb=10, timeout_seconds=1200, stop_on_memory_or_runtime_error=True),
        evaluation=dict(cases=24, scenarios=8, conditions=['base', 'current-craft', 'candidate'],
                        baseline_before_training=True, fresh_context_each_request=True, cached_tokens=0,
                        temperature=0, seed=42, max_new_tokens=384, enable_thinking=False),
        gates=['verify_all_inputs_and_weights', 'complete_both_serial_baselines_before_training',
               'respect10GB_and20minute_limits', 'run_candidate_comparison',
               'report_failures_and_semantic_review_separately', 'no_automatic_promotion'],
        validation='Sixteen exposed Wray development-monitor records retained; not independent project-wide test material.',
        limits='Small source-only pilot, not broad genre competence or Muse equivalence. No human quality ratings. Longer-context training memory unmeasured; fail closed if unsupported. No paid jobs, uploads, app changes or service restart in this preflight.'))
    print(json.dumps({k: v for k, v in report.items() if k not in ['counts', 'author_supervised_tokens']}, indent=2))


if __name__ == '__main__':
    main()
