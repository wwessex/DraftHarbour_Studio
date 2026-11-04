"""Build a deterministic editorial packet with model labels held separately."""
from hashlib import sha256
import json
from pathlib import Path
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'artifacts/rewrite-specialist-v57'
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl


def main():
    cases = read_jsonl(RUN / 'cases.frozen.jsonl')
    responses = {}
    for side in ('base', 'current-craft', 'candidate'):
        path = RUN / f'{side}.responses.jsonl'
        stamp = json.loads((RUN / f'{side}.complete.json').read_text())
        rows = read_jsonl(path)
        if not stamp['completed'] or stamp['response_sha256'] != file_hash(path):
            raise ValueError(f'{side} responses failed integrity check')
        if [row['case_id'] for row in rows] != [case['id'] for case in cases]:
            raise ValueError(f'{side} cases differ from the frozen set')
        responses[side] = rows
    packet, key = [], {}
    for index, case in enumerate(cases):
        order = sorted(responses)
        seed = sha256(case['id'].encode()).digest()
        random.Random(seed).shuffle(order)
        labels = dict(zip('ABC', order))
        packet.append(dict(id=case['id'], prompt=case['prompt'],
                           responses={label: responses[side][index]['text'] for label, side in labels.items()}))
        key[case['id']] = labels
    for name, data in [('blind-packet.json', packet), ('blind-key.json', key)]:
        with (RUN / name).open('x') as stream:
            json.dump(data, stream, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
