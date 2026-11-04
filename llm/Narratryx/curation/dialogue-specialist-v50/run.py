"""Train a dialogue-only task mixture and compare it with base and craft."""
import json
import os
from pathlib import Path
import runpy
import sys

os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_DATASETS_OFFLINE='1')
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/dialogue-specialist-v50'
OLD = ROOT / 'artifacts/source-training-v48'
CURRICULUM = ROOT / 'artifacts/stylistic-writing-v48/records.review-only.jsonl'
PREVIOUS = ROOT / 'curation/source-training-v26'
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl, validate_dataset


def main():
    assert __debug__
    if sys.argv[1:] == ['--train']:
        train = runpy.run_path(str(ROOT / 'curation/source-training-v48/train.py'))['main']
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
    records = validate_dataset(CURRICULUM, ROOT / 'rights/stylistic-writing-v48.scoped.jsonl',
                               ['GB', 'US'], benchmark=read_jsonl(ROOT / 'evaluation/tasks.draft.jsonl'))
    train = [r for r in records if r['split'] == 'train']
    ids = {r['id'] for r in train if r['task'] == 'dialogue' and not r['id'].startswith('gb-v3-')}
    assert len(ids) == 9
    tokens = read_jsonl(OLD / 'train.tokens.jsonl')
    assert len(tokens) == len(train) == 58
    selected = [t for r, t in zip(train, tokens) if r['id'] in ids]
    cases = read_jsonl(HERE / 'cases.jsonl')
    assert len(cases) == 4 and all(not c['training_eligible'] for c in cases)
    assert not {c['prompt'] for c in cases} & {r['messages'][0]['content'] for r in records}
    helper = runpy.run_path(str(previous['HELPERS']))
    helper['phase'].__globals__.update(RUN=RUN, PYTHON=Path(sys.executable))
    assert helper['port_free']()
    RUN.mkdir()
    save, phase = helper['save'], helper['phase']
    for name, rows in [('train.tokens.jsonl', selected), ('cases.frozen.jsonl', cases)]:
        with (RUN / name).open('x') as stream:
            for row in rows:
                stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    request = json.loads((OLD / 'request.json').read_text())
    request.update(project_name='Narratryx-dialogue-v50', max_steps=9, save_steps=9, eval_steps=9,
                   local_datasets=[str(RUN / 'train.tokens.jsonl')])
    worker = json.loads((OLD / 'worker-config.json').read_text())
    for key in ('project_name', 'max_steps', 'save_steps', 'eval_steps', 'local_datasets'):
        worker[key] = request[key]
    worker['output_dir'] = str(RUN / 'adapter')
    save('request.json', request)
    save('worker-config.expected.json', worker)
    from foundation.trainer_recipe import validate_token_row
    total = sum(validate_token_row(r, r['input_ids'][-1]) for r in selected)
    plan.update(training_steps=9, supervised_training_tokens=total, selected_ids=sorted(ids),
                test_cases_path=str((RUN / 'cases.frozen.jsonl').relative_to(ROOT)),
                worker_config_path=str((RUN / 'worker-config.expected.json').relative_to(ROOT)))
    plan['resource_stop']['max_steps'] = 9
    paths = [Path(__file__), HERE / 'guards.py', HERE / 'cases.jsonl', *RUN.glob('*.json*')]
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
    check = runpy.run_path(str(ROOT / 'curation/holdout-v36/constraints.py'))['checks']
    scores = {}
    for side in ('base', 'current-craft', 'candidate'):
        rows = read_jsonl(RUN / f'{side}.responses.jsonl')
        assert [r['case_id'] for r in rows] == [c['id'] for c in cases]
        scores[side] = []
        for i, (case, row) in enumerate(zip(cases, rows)):
            turns = (4, 5, 4, 5)[i]
            flags = check(dict(case, constraints=dict(min_turns=turns, max_turns=turns,
                               max_words=(100, 110, 100, 110)[i])), row['text'])
            scores[side].append(dict(id=case['id'], passed=all(flags.values()), checks=flags))
    save('automatic-decision.json', dict(decision='keep-craft-pending-broader-evaluation', scores=scores,
                                        training_eligible=False))


if __name__ == '__main__':
    main()
