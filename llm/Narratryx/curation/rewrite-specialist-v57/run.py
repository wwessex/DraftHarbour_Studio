"""Train a source-backed rewrite specialist and compare it with base and craft."""
import json
import os
from pathlib import Path
import runpy
import sys

os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/rewrite-specialist-v57'
OLD = ROOT / 'artifacts/source-training-v48'
CURRICULUM = ROOT / 'artifacts/stylistic-writing-v48/records.review-only.jsonl'
PREVIOUS = ROOT / 'curation/source-training-v26'
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl, validate_dataset


def main():
    assert __debug__
    if sys.argv[1:] == ['--train']:
        train = runpy.run_path(str(HERE / 'train.py'))['main']
        train.__globals__['RUN'] = RUN
        sys.path.insert(0, str(HERE))
        train()
        return
    if len(sys.argv) == 3 and sys.argv[1] == '--evaluate':
        evaluate = runpy.run_path(str(PREVIOUS / 'evaluate.py'))['main']
        evaluate.__globals__['RUN'] = RUN
        sys.argv[1:] = [sys.argv[2]]
        evaluate()
        return
    assert not RUN.exists()
    previous = runpy.run_path(str(PREVIOUS / 'run.py'))
    plan = json.loads((OLD / 'protocol.frozen.json').read_text())
    previous['verify_inputs'](plan)
    from unsloth_cli.commands.train import _activate_mlx_transformers
    from foundation.trainer_recipe import validate_token_row

    cases = read_jsonl(HERE / 'cases.jsonl')
    assert len(cases) == 6 and all(not c['training_eligible'] for c in cases)
    packets = (
        ('rewrite-reserve-v52', 'stylistic-writing-v48'),
        ('shelley-rewrite-v54', 'shelley-rewrite-v54'),
        ('wilde-rewrite-v56', 'wilde-rewrite-v56'),
    )
    records, ledger, inputs = [], [], []
    for folder, scope in packets:
        data_path = ROOT / 'artifacts' / folder / 'records.review-only.jsonl'
        scope_path = ROOT / 'rights' / f'{scope}.scoped.jsonl'
        inputs.extend((data_path, scope_path))
        rows = read_jsonl(data_path)
        records.extend(dict(row, dataset_version='rewrite-specialist-v57') for row in rows)
        ids = {ident for row in rows for ident in row['rights_record_ids']}
        ledger.extend(row for row in read_jsonl(scope_path) if row['id'] in ids)
    assert len(records) == 9 and len({work for r in records for work in r['source_work_ids']}) == 3
    assert all(r['teacher'] is None and r['task'] == 'editing' and r['split'] == 'train'
               and r['messages'][-1]['content'] == r['source_spans'][-1]['text'] for r in records)
    assert not {c['prompt'] for c in cases} & {r['messages'][0]['content'] for r in records}
    inputs.extend(ROOT / 'rights' / r['source']['raw_path'] for r in ledger)
    _activate_mlx_transformers(plan['base_path'], None)
    from transformers import AutoTokenizer, __version__
    assert __version__ == plan['active_tokenizer_transformers']
    tokenizer = AutoTokenizer.from_pretrained(plan['base_path'], local_files_only=True, trust_remote_code=False)
    selected = []
    for row in records:
        prompt = tokenizer.apply_chat_template(row['messages'][:-1], tokenize=False,
                                               add_generation_prompt=True, enable_thinking=False)
        prefix = tokenizer.encode(prompt, add_special_tokens=False)
        answer = row['messages'][-1]['content']
        target = tokenizer.encode(answer, add_special_tokens=False)
        assert tokenizer.decode(target, skip_special_tokens=False) == answer
        ids = prefix + target + [tokenizer.eos_token_id]
        assert len(ids) <= plan['context_limit']
        selected.append(dict(input_ids=ids, attention_mask=[1]*len(ids),
                             labels=[-100]*len(prefix)+target+[tokenizer.eos_token_id]))
    ids = {r['id'] for r in records}
    helper = runpy.run_path(str(previous['HELPERS']))
    helper['phase'].__globals__.update(RUN=RUN, PYTHON=Path(sys.executable))
    assert helper['port_free']()
    RUN.mkdir()
    save, phase = helper['save'], helper['phase']
    for name, rows in [('train.tokens.jsonl', selected), ('cases.frozen.jsonl', cases), ('records.jsonl', records), ('ledger.jsonl', ledger)]:
        with (RUN / name).open('x') as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    # The local ledger sits beside the packet. Rebase paths to the same checked files.
    # Foundation confines paths to the ledger directory, so stage just the scoped files.
    for entry in ledger:
        relative = Path(entry['source']['raw_path'])
        target = RUN / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / 'rights' / relative).read_bytes())
        inputs.append(target)
    validate_dataset(RUN / 'records.jsonl', RUN / 'ledger.jsonl', ['GB', 'US'],
                     benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    request = json.loads((OLD / 'request.json').read_text())
    request.update(project_name='Narratryx-rewrite-v57', max_steps=9, save_steps=9, eval_steps=9,
                   local_datasets=[str(RUN / 'train.tokens.jsonl')])
    worker = json.loads((OLD / 'worker-config.json').read_text())
    for key in ('project_name', 'max_steps', 'save_steps', 'eval_steps', 'local_datasets'):
        worker[key] = request[key]
    worker['output_dir'] = str(RUN / 'adapter')
    save('request.json', request)
    save('worker-config.expected.json', worker)
    total = sum(validate_token_row(r, r['input_ids'][-1]) for r in selected)
    plan.update(training_steps=9, supervised_training_tokens=total, selected_ids=sorted(ids),
                test_cases_path=str((RUN / 'cases.frozen.jsonl').relative_to(ROOT)),
                worker_config_path=str((RUN / 'worker-config.expected.json').relative_to(ROOT)))
    plan['resource_stop']['max_steps'] = 9
    paths = [Path(__file__), HERE / 'guards.py', HERE / 'cases.jsonl', HERE / 'train.py', *inputs, *RUN.glob('*.json*')]
    plan['input_hashes'].update({str(p.relative_to(ROOT)): file_hash(p) for p in paths})
    save('protocol.frozen.json', plan)
    for side in ('base', 'current-craft'):
        phase(side, [str(Path(__file__)), '--evaluate', side], 1200)
    phase('training', [str(Path(__file__)), '--train'], 1200)
    try:
        phase('candidate', [str(Path(__file__)), '--evaluate', 'candidate'], 1200)
    except RuntimeError as error:
        save('automatic-decision.json', dict(decision='keep-craft', reason=str(error)))
        raise
    changed = {}
    for side in ('base', 'current-craft', 'candidate'):
        rows = read_jsonl(RUN / f'{side}.responses.jsonl')
        assert [r['case_id'] for r in rows] == [c['id'] for c in cases]
        changed[side] = [r['case_id'] for r, c in zip(rows, cases)
                         if ' '.join(r['text'].split()) != ' '.join(c['prompt'].split('PASSAGE:\n', 1)[1].split())]
    save('automatic-decision.json', dict(decision='keep-craft-pending-editorial-comparison',
                                        changed=changed, training_eligible=False))


if __name__ == '__main__':
    main()
