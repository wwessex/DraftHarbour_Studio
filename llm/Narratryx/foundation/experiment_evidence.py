"""Validate saved fresh-context inference evidence before reporting scores."""
import argparse
import hashlib
import json
from pathlib import Path

from .validation import Invalid, file_hash, read_json, read_jsonl


def verify(run: Path, sides: list[str]) -> dict:
    protocol = run / 'protocol.frozen.json'
    protocol_hash = file_hash(protocol)
    case_path = run / 'cases.frozen.jsonl'
    plan = read_json(protocol)
    locked_cases = Path(plan['test_cases_path'])
    if (locked_cases.name != case_path.name or locked_cases.parent.name != run.name
            or plan['input_hashes'].get(str(locked_cases)) != file_hash(case_path)):
        raise Invalid('Frozen case bytes differ from the protocol')
    cases = read_jsonl(case_path)
    ids = [case['id'] for case in cases]
    if len(set(ids)) != len(ids) or any(case['training_eligible'] is not False for case in cases):
        raise Invalid('Expected unique evaluation-only cases')
    craft_pin = plan['input_hashes']['artifacts/craft-training-v2/adapter/adapters.safetensors']
    result = {}
    for side in sides:
        adapter_pin = craft_pin
        if side == 'candidate':
            training = read_json(run / 'completion.json')
            if training['completed'] is not True:
                raise Invalid('Candidate training lacks a completion record')
            adapter_pin = training['adapter_sha256']
            if file_hash(run / 'adapter/adapters.safetensors') != adapter_pin:
                raise Invalid('Candidate adapter differs from the completed checkpoint')
        response_path = run / f'{side}.responses.jsonl'
        stamp = read_json(run / f'{side}.complete.json')
        if (stamp['completed'] is not True or stamp['cases'] != len(cases)
                or stamp['response_sha256'] != file_hash(response_path)
                or stamp['models_unloaded'] is not True or stamp['adapter_unchanged'] is not True):
            raise Invalid(f'{side}: incomplete or mismatched response evidence')
        rows = read_jsonl(response_path)
        if [row['case_id'] for row in rows] != ids:
            raise Invalid(f'{side}: response order or membership differs from frozen cases')
        for case, row in zip(cases, rows):
            expected_prompt = hashlib.sha256(case['prompt'].encode()).hexdigest()
            if (row['prompt_sha256'] != expected_prompt or row['protocol_sha256'] != protocol_hash
                    or row['adapter_sha256'] != adapter_pin or row['condition'] != side or row['kind'] != case['kind']
                    or row['prior_assistant_messages'] != 0 or row['messages_count'] != 1
                    or row['adapter_enabled'] is not (side != 'base')
                    or row['usage'].get('prompt_tokens_details', {}).get('cached_tokens', 0) != 0
                    or row['finish_reason'] != 'stop' or row['error'] is not None or not row['text'].strip()):
                raise Invalid(f'{side}/{case["id"]}: response is incomplete or differs from the frozen protocol')
        result[side] = dict(cases=len(rows), response_sha256=stamp['response_sha256'])
    return dict(protocol_sha256=protocol_hash, conditions=result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    parser.add_argument('sides', nargs='+', choices=('base', 'current-craft', 'candidate'))
    args = parser.parse_args()
    print(json.dumps(verify(args.run, args.sides), indent=2))


if __name__ == '__main__':
    main()
