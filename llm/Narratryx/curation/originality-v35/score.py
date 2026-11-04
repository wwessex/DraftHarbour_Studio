"""Measure normalized exact overlap against known source bytes and peer outputs."""
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, load_ledger, read_jsonl

OUT = ROOT / 'artifacts/originality-v35'
LEDGER = ROOT / 'rights/watsons-v33.scoped.jsonl'
THRESHOLD = 12


def words(text):
    return re.findall(r"[^\W_]+(?:'[^\W_]+)*", text.casefold().replace('’', "'"))


def grams(tokens, n):
    return {tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)}


def main():
    assert json.loads((OUT / 'originality.phase.json').read_text())['completed']
    responses = read_jsonl(OUT / 'alternatives.jsonl')
    assert len(responses) == 9
    assert all(r['finish_reason'] == 'stop' for r in responses)
    counts = Counter(r['case_id'] for r in responses)
    assert len(counts) == 3 and set(counts.values()) == {3}
    query = defaultdict(list)
    outputs = {}
    for row in responses:
        key = (row['case_id'], row['attempt'])
        assert key not in outputs
        outputs[key] = tokens = words(row['text'])
        assert tokens
        for index in range(len(tokens) - THRESHOLD + 1):
            query[tuple(tokens[index:index + THRESHOLD])].append((key, index))
    sources = {}
    matches = {}
    for rid, item in load_ledger(LEDGER).items():
        path = ROOT / 'rights' / item['source']['raw_path']
        if path in sources:
            assert item['source']['sha256'] == sources[path]
            continue
        assert file_hash(path) == item['source']['sha256']
        sources[path] = item['source']['sha256']
        tokens = words(path.read_text())
        for i in range(len(tokens) - THRESHOLD + 1):
            for key, j in query.get(tuple(tokens[i:i + THRESHOLD]), ()):
                output = outputs[key]
                length = THRESHOLD
                while i + length < len(tokens) and j + length < len(output) and tokens[i + length] == output[j + length]:
                    length += 1
                if length > matches.get(key, {}).get('words', 0):
                    matches[key] = dict(words=length, source_id=rid, output_word_index=j)
    peers = []
    for (a, x), (b, y) in combinations(outputs.items(), 2):
        if a[0] != b[0]:
            continue
        g, h = grams(x, 4), grams(y, 4)
        peers.append(dict(case_id=a[0], attempts=[a[1], b[1]], identical=x == y,
                          shared_4grams=len(g & h), jaccard_4grams=len(g & h) / max(1, len(g | h))))
    report = dict(alternatives=len(outputs), source_files=len(sources),
                  contiguous_match_threshold_words=THRESHOLD,
                  source_matches=[dict(case_id=k[0], attempt=k[1], **v) for k, v in matches.items()],
                  peer_comparisons=peers,
                  response_sha256=file_hash(OUT / 'alternatives.jsonl'),
                  source_sha256={str(p.relative_to(ROOT)): h for p, h in sources.items()},
                  training_eligible=False)
    with (OUT / 'overlap.json').open('x') as stream:
        json.dump(report, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'source_sha256'}, indent=2))


if __name__ == '__main__':
    main()
