"""Exported CUDA SFT recipe; not invoked by the offline runner.

Requires a separately provisioned/pinned Unsloth/TRL/datasets/trackio environment.
Hardware integration is untested. Outputs are local: ephemeral workers must be
configured to persist them before anyone authorizes a cloud job.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re


def check_plan(plan, train_path, script_path):
    if plan['train_sha256'] != hashlib.sha256(train_path.read_bytes()).hexdigest():
        raise ValueError('training file hash mismatch')
    if plan['script_sha256'] != hashlib.sha256(script_path.read_bytes()).hexdigest():
        raise ValueError('training script hash mismatch')
    model = plan['model']
    if not model or model['license_review']['status'] != 'approved':
        raise ValueError('a separately reviewed base model is required')
    if not model['license_review']['reviewer'].strip() or not model['license_review']['reviewed_on']:
        raise ValueError('model license review attribution is required')
    if not re.fullmatch(r'[a-f0-9]{40}', model['revision']):
        raise ValueError('pin the base model to a full Hub commit hash')
    settings = plan['training']
    for key, low, high in [('max_steps', 1, 1000), ('max_length', 128, 4096),
                           ('save_steps', 1, 100), ('seed', 0, 2147483647)]:
        if type(settings[key]) is not int or not low <= settings[key] <= high:
            raise ValueError(f'invalid bounded setting: {key}')
    return model, settings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--execute', action='store_true', help='explicit GPU execution, separately authorized')
    args = parser.parse_args()
    if not args.execute:
        parser.error('export-only by default; GPU execution requires --execute and separate authorization')
    plan = json.loads(args.plan.read_text())
    train_path = args.plan.parent / 'train.jsonl'
    model_spec, settings = check_plan(plan, train_path, Path(__file__))
    if args.output.exists():
        raise ValueError('choose a new output directory; this recipe does not silently overwrite or resume')
    # Import Unsloth first. No ML imports, model downloads or allocation before gates.
    from unsloth import FastLanguageModel
    import torch
    from datasets import load_dataset
    from trl import SFTConfig, SFTTrainer

    if not torch.cuda.is_available():
        raise RuntimeError('this recipe requires a CUDA GPU; do not run on the MacBook Air')
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_spec['id'], revision=model_spec['revision'],
        max_seq_length=settings['max_length'], load_in_4bit=True,
        trust_remote_code=False)
    dataset = load_dataset('json', data_files=str(train_path), split='train')
    # Assistant-only loss needs a compatible generation-mask chat template. Refuse
    # unsupported templates or truncation instead of training on user instructions.
    for row in dataset:
        tokens = tokenizer.apply_chat_template(row['messages'], tokenize=True,
            return_dict=True, return_assistant_tokens_mask=True)
        if not any(tokens.get('assistant_masks', [])):
            raise ValueError('chat template lacks assistant generation masks; select/verify a compatible template')
        if len(tokens['input_ids']) > settings['max_length']:
            raise ValueError('example exceeds max_length; review segmentation before training')
    model = FastLanguageModel.get_peft_model(model, r=16, lora_alpha=16,
        target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
        lora_dropout=0, bias='none', use_gradient_checkpointing='unsloth',
        random_state=settings['seed'])
    trainer = SFTTrainer(model=model, processing_class=tokenizer, train_dataset=dataset,
        args=SFTConfig(output_dir=str(args.output), max_steps=settings['max_steps'],
            max_length=settings['max_length'], assistant_only_loss=True,
            per_device_train_batch_size=1, gradient_accumulation_steps=4,
            learning_rate=2e-4, seed=settings['seed'], logging_steps=1,
            save_steps=settings['save_steps'], save_total_limit=2,
            report_to='trackio', trackio_space_id=None,
            push_to_hub=False, packing=False))
    trainer.train()
    model.save_pretrained(str(args.output / 'adapter'))
    tokenizer.save_pretrained(str(args.output / 'adapter'))
    (args.output / 'training-plan.json').write_text(json.dumps(plan, indent=2) + '\n')


if __name__ == '__main__':
    main()
