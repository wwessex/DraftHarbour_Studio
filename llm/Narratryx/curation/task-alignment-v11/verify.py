"""Read-only audit verification; does not train, infer, grant rights or approve prose."""
import json
import sys
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl, validate_dataset
from foundation.task_alignment import verify_unchanged_target
from foundation.anchored_edits import AnchorEdit, apply_anchor_edits


def verify():
    out = ROOT / 'artifacts/task-alignment-v11'
    proof = json.loads((out / 'verification.json').read_text())
    parent = json.loads((ROOT / 'artifacts/stability-v10/protocol.frozen.json').read_text())
    assert file_hash(Path(parent['base_path']) / 'model.safetensors') == parent['base_weights_sha256']
    for group in ['protected_hashes', 'input_hashes']:
        for name, expected in proof[group].items():
            assert file_hash(ROOT / name) == expected, name
    for name, expected in proof['output_hashes'].items():
        assert file_hash(out / name) == expected, name
    old = {r['id']:r for r in read_jsonl(ROOT / 'artifacts/balanced-fiction-v9/records.jsonl')}
    new = read_jsonl(out / 'records.proposed.jsonl')
    validate_dataset(out / 'records.proposed.jsonl', ROOT / 'rights/grounding-balanced-v1.scoped.jsonl', ['GB', 'US'])
    changes, edits = [], 0
    for r in new:
        verify_unchanged_target(old[r['id']], r)
        if r['messages'][0] != old[r['id']]['messages'][0]:
            changes.append(r['id'])
        if r['split'] == 'train' and r['task'] == 'editing' and r['messages'][-1]['content'].startswith('{'):
            target = r['messages'][0]['content'].split('\nTARGET:\n')[1]
            es = json.loads(r['messages'][-1]['content'])['edits']
            result = apply_anchor_edits(target, target, [AnchorEdit(**e) for e in es])
            expected = old[r['id']]['source_spans'][0]['text']
            # Existing derived targets normalise scan line wraps. Edits are applied
            # exactly above; only this source-suffix comparison normalises whitespace.
            assert ' '.join(expected.split()).endswith(' '.join(result.split())), r['id']
            edits += 1
    assert set(changes) == {'gb-v2-directed-opie-0256', 'gb-v2-directed-opie-0262'} and edits == 8
    assert sum(r['split'] == 'train' for r in new) == 25 and sum(r['split'] == 'validation' for r in new) == 16
    audit = read_jsonl(out / 'audit.jsonl')
    assert {r['id'] for r in audit} == {r['id'] for r in old.values() if r['split'] == 'train'}
    assert dict(Counter(r['decision'] for r in audit)) == proof['decisions']
    cases = read_jsonl(out / 'cases.frozen.jsonl')
    assert len(cases) == len({c['id'] for c in cases}) == 12
    assert not {c['prompt'] for c in cases} & {r['messages'][0]['content'] for r in new}
    assert Counter(c['kind'] for c in cases) == {'dialogue':3, 'continue':3, 'rewrite':3, 'selected-edit':3}
    assert all(c['word_count_min'] is None for c in cases if c['kind'] in ['rewrite', 'selected-edit'])
    tokens = json.loads((out / 'tokenizer-preflight.json').read_text())
    for name, expected in tokens['input_hashes'].items():
        assert file_hash(ROOT / name) == expected, name
    assert tokens['passed'] and tokens['records'] == 41 and tokens['train_records'] == 25 and tokens['maximum_tokens'] <= 2048
    return dict(passed=True, audited_train_records=92, proposal_train_records=25,
                unchanged_answers_and_source_spans=41, repaired_briefs=len(changes), anchored_edit_controls_verified=edits,
                new_unrun_evaluation_cases=12, old_models_and_inputs_unchanged=True,
                preparation_only=True, human_quality_ratings=0, model_promoted=False)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
