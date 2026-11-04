"""Reject changed supervision, stale recipe caps and reclassified evaluation cohorts."""
from collections import Counter


def token_multiset(rows):
    return Counter((tuple(r['input_ids']), tuple(r['labels'])) for r in rows)


def validate_token_row(row, eos_id):
    ids, labels = row['input_ids'], row['labels']
    if not ids or len(ids) != len(labels) or row['attention_mask'] != [1] * len(ids):
        raise ValueError('token/label/mask length mismatch')
    if len(ids) > 2048 or ids[-1] != eos_id or labels[-1] != eos_id:
        raise ValueError('context/EOS mismatch')
    first = next((i for i, x in enumerate(labels) if x != -100), len(ids))
    if first == 0 or first == len(ids) or labels[first:] != ids[first:]:
        raise ValueError('prompt mask or complete answer labels missing')
    if any(x != -100 for x in labels[:first]):
        raise ValueError('prompt supervision detected')
    return len(labels) - first


def validate_plan(protocol, request, audit):
    expected = dict(records=28, presentations=28, broader_prose=20, semantic_repairs=5, structural_edits=3, monitor_records=16,
                    epochs=1, batch_size=1, gradient_accumulation=1, learning_rate='5e-5', lora_rank=8, lora_alpha=16, lora_dropout=0, seed=42)
    if protocol['training'] != expected or protocol['training_steps'] != 28 or protocol['context_limit'] != 2048:
        raise ValueError('training proposal mismatch')
    for key, value in dict(max_steps=28, num_epochs=1, batch_size=1, gradient_accumulation_steps=1, learning_rate='5e-5', save_steps=28,
                           eval_steps=28, max_seq_length=2048, warmup_steps=2, resume_from_checkpoint=None, packing=False,
                           train_on_completions=True, random_seed=42, model_random_state=42, lora_random_state=42,
                           lora_r=8, lora_alpha=16, lora_dropout=0, trust_remote_code=False, hf_dataset=None).items():
        if request[key] != value:
            raise ValueError('recipe mismatch: ' + key)
    e = protocol['evaluation']
    expected_eval = dict(primary_cases=44, exposed_primary=44, new_unrun_primary=0, seen_training_fit_cases=5,
                         conditions=['base', 'current-craft', 'candidate'], primary_requests=132, seen_fit_requests=15,
                         total_requests=147, max_new_tokens=384, temperature=0, seed=42, repetition_penalty=1.0, fresh_context=True)
    if e != expected_eval:
        raise ValueError('evaluation scope mismatch')
    if (audit['training_records'], audit['monitor_records'], audit['supervised_training_tokens']) != (28, 16, 3033):
        raise ValueError('supervision mismatch')
    if not audit['all_preprocessing_unchanged'] or not audit['collated_multiset_matches'] or not audit['worker_configuration_checked']:
        raise ValueError('installed audit incomplete')
    if protocol['resource_stop'] != dict(max_steps=28, peak_mlx_gb=10, process_tree_rss_bytes=10000000000,
                                         phase_deadline_seconds=1200, stop_on_warning_error_nonfinite_or_truncation=True):
        raise ValueError('resource caps mismatch')
    return True
