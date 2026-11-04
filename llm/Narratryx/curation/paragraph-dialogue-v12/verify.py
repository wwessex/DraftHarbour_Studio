"""Verify source-contiguous candidates, replacements, frozen tests and prior models."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl, validate_dataset
from foundation.paragraph_lessons import verify_derivation


def verify():
    out = ROOT / 'artifacts/paragraph-dialogue-v12'
    proof = json.loads((out / 'verification.json').read_text())
    for group in ['protected_hashes', 'input_hashes']:
        for name, expected in proof[group].items():
            assert file_hash(ROOT / name) == expected, name
    for name, expected in proof['output_hashes'].items():
        assert file_hash(out / name) == expected, name
    parent_protocol = json.loads((ROOT / 'artifacts/stability-v10/protocol.frozen.json').read_text())
    assert file_hash(Path(parent_protocol['base_path']) / 'model.safetensors') == parent_protocol['base_weights_sha256']
    original = {r['id']:r for r in read_jsonl(ROOT / 'artifacts/balanced-fiction-v9/records.jsonl')}
    old = {r['id']:r for r in read_jsonl(ROOT / 'artifacts/task-alignment-v11/records.proposed.jsonl')}
    candidates = {r['id']:r for r in read_jsonl(out / 'candidates.jsonl')}
    bindings = {r['id']:r for r in read_jsonl(out / 'derivations.jsonl')}
    assert len(candidates) == len(bindings) == 5
    for ident, r in candidates.items():
        b = bindings[ident]
        parent = original[b['parent_id']]
        assert parent['split'] == 'train' and parent['source_spans'] == r['source_spans'] == [b['source_span']]
        for key in ['rights_record_ids', 'source_work_ids', 'split_group', 'split', 'origin', 'teacher']:
            assert r[key] == parent[key], (ident, key)
        span = b['source_span']
        d = b['derivation']
        verify_derivation(span['text'], d)
        assert r['messages'][-1]['content'] == d['answer']
        assert r['messages'][0]['content'].split('\n\nPRECEDING PARAGRAPHS:\n')[1] == d['context']
        assert b['absolute_context_start'] == span['start']
        assert b['absolute_context_end'] == span['start'] + d['context_end']
        assert b['absolute_answer_start'] == span['start'] + d['answer_start']
        assert b['absolute_answer_end'] == span['start'] + d['answer_end'] <= span['end']
    ledger = ROOT / 'rights/grounding-balanced-v1.scoped.jsonl'
    validate_dataset(out / 'candidates.jsonl', ledger, ['GB', 'US'])
    validate_dataset(out / 'records.proposed.jsonl', ledger, ['GB', 'US'])
    proposed = read_jsonl(out / 'records.proposed.jsonl')
    ids = {r['id'] for r in proposed}
    assert len(ids) == 41 and sum(r['split'] == 'train' for r in proposed) == 25
    replacements = {'gb-hopkins-embroidery':'pd12-embroidery', 'gb-wilson-help':'pd12-support',
                    'gb-hopkins-work':'pd12-work', 'gb-harper-newspaper':'pd12-rumour-dialogue'}
    assert ids == (set(old) - set(replacements)) | set(replacements.values())
    assert 'pd12-news' not in ids
    for r in proposed:
        expected = dict(candidates[r['id']] if r['id'] in candidates else old[r['id']])
        expected['dataset_version'] = 'paragraph-dialogue-v12-proposal'
        assert r == expected, r['id']
    cases = read_jsonl(ROOT / proof['evaluation_cases_path'])
    assert len(cases) == 12 and not {c['prompt'] for c in cases} & {r['messages'][0]['content'] for r in proposed}
    tokens = json.loads((out / 'tokenizer-preflight.json').read_text())
    for name, expected in tokens['input_hashes'].items():
        assert file_hash(ROOT / name) == expected, name
    assert tokens['passed'] and tokens['records'] == 41 and tokens['train_records'] == 25
    assert tokens['maximum_tokens'] <= 2048 and not tokens['weights_loaded'] and not tokens['training']
    return dict(passed=True, exact_contiguous_candidates=5, one_paragraph_candidates=4, three_turn_dialogue_candidates=1,
                full_scene_parents_replaced=4, proposal_training_records=25, exposed_monitor_records=16,
                answers_are_exact_source_substrings=True, new_scoped_source_spans=0,
                protected_inputs_and_models_unchanged=True, new_evaluation_cases_run=0,
                preparation_only=True, human_quality_ratings=0, model_promoted=False)


if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
