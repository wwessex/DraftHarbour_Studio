"""Explicit, offline engineering comparison of a GGUF export; never trains.

Requires the original frozen craft pilot artifacts and cached source tokenizer.
Writes a new output directory; never rewrites the original experiment.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from .bundle import RuntimeSession, digest

ROOT = Path(__file__).resolve().parents[2]


def summarize(cases, rows):
    by_id = {case['id']: case for case in cases}
    result = dict(cases=len(rows), errors=0, truncated=0, exact_minimal_repairs=0,
                  word_limits_by_kind={}, quality_ratings=None)
    for row in rows:
        case = by_id[row['case_id']]
        words = len(row['text'].split())
        entry = result['word_limits_by_kind'].setdefault(case['kind'], dict(passed=0, total=0))
        entry['total'] += 1
        entry['passed'] += int((not case.get('word_count_min') or words >= case['word_count_min'])
                              and (not case.get('word_count_max') or words <= case['word_count_max']))
        result['errors'] += int(bool(row.get('error')))
        result['truncated'] += int(row['stats'].get('finish_reason') == 'length')
        result['exact_minimal_repairs'] += int(case['kind'] == 'editing' and row['text'].strip() == case['exact_reference'])
    return result


def evaluate(bundle, manifest_hash, protocol_path, tokenizer_path, output):
    # Transformers is imported only for an explicit offline comparison, never on app startup.
    from transformers import AutoTokenizer
    protocol = json.loads(protocol_path.read_text())
    for name, expected in protocol['input_hashes'].items():
        if digest(ROOT / name) != expected:
            raise ValueError('Original frozen input changed: ' + name)
    expected_generation = dict(temperature=0, top_p=1, top_k=20, min_p=0,
        presence_penalty=0, repetition_penalty=1, seed=42, max_new_tokens=512, enable_thinking=False)
    if protocol['generation'] != expected_generation or protocol['system_prompt'] or protocol['tools']:
        raise ValueError('This runner supports only the frozen craft pilot generation contract')
    pin = json.loads((ROOT / 'configs/narratryx-craft-v1.json').read_text())
    for name, expected in pin['base_metadata'].items():
        if digest(tokenizer_path / name) != expected:
            raise ValueError('Source tokenizer metadata changed: ' + name)
    tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), local_files_only=True)
    cases = [json.loads(line) for line in (ROOT / protocol['test_cases_path']).read_text().splitlines()]
    if len(cases) != protocol['test_cases']:
        raise ValueError('Frozen case count changed')
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    with RuntimeSession(bundle, manifest_hash) as session:
        with (output / 'responses.jsonl').open('x') as target:
            for case in cases:
                messages = [dict(role='user', content=case['prompt'])]
                expected = tokenizer.apply_chat_template(messages, tokenize=False,
                    add_generation_prompt=True, enable_thinking=False)
                rendered = session.request('/apply-template', dict(messages=messages,
                    add_generation_prompt=True, chat_template_kwargs={'enable_thinking': False}))
                if rendered.get('prompt') != expected:
                    (output / 'template-mismatch.json').write_text(json.dumps(dict(
                        case_id=case['id'], source_prompt=expected, runtime=rendered), indent=2))
                    raise ValueError('Export chat template differs; comparison stopped')
                started = time.monotonic()
                response = session.complete(messages, max_tokens=512)
                if response['usage'].get('prompt_tokens_details', {}).get('cached_tokens', 0):
                    raise ValueError('Expected independent requests without reused prompt cache')
                choice = response['choices'][0]
                row = dict(case_id=case['id'], condition='gguf-q4-k-m', kind=case['kind'],
                    text=choice['message']['content'], error=None,
                    elapsed_seconds=round(time.monotonic()-started, 2),
                    stats=dict(usage=response['usage'], finish_reason=choice['finish_reason']),
                    prompt_sha256=hashlib.sha256(case['prompt'].encode()).hexdigest(),
                    protocol_sha256=digest(protocol_path), manifest_sha256=manifest_hash,
                    chat_template_exact=True, messages_count=1, prior_assistant_messages=0)
                target.write(json.dumps(row) + '\n'); target.flush()
                rows.append(row)
                print(case['id'], choice['finish_reason'], row['elapsed_seconds'], flush=True)
    report = dict(completed=True, cases=len(rows), manifest_sha256=manifest_hash,
        protocol_sha256=digest(protocol_path), summary=summarize(cases, rows),
        meaning='Export engineering comparison; different engines/quantization, no literary quality claim.')
    (output / 'complete.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--manifest-sha256', required=True)
    parser.add_argument('--tokenizer', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, default=ROOT / 'artifacts/craft-training-v2/protocol.frozen.json')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    evaluate(args.bundle, args.manifest_sha256, args.protocol, args.tokenizer, args.output)


if __name__ == '__main__':
    main()
