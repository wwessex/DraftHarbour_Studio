"""Measure repeated dialogue in saved outputs, including incomplete evaluations."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl


def analyse(text):
    lines = [' '.join(m.group(1).casefold().split()).strip('“”"')
             for m in re.finditer(r"^(?:\*\*)?[\w .'-]+:(?:\*\*)?\s*(\S.*)$", text, re.M)]
    for i in range(len(lines)):
        for width in (1, 2, 3):
            block = lines[i:i + width]
            if i + 3 * width <= len(lines) and lines[i:i + 3 * width] == block * 3:
                return dict(turns=len(lines), loop_start_turn=i + 1, period=width)
    return dict(turns=len(lines), loop_start_turn=None, period=None)


if __name__ == '__main__':
    paths = [ROOT / 'artifacts' / run / 'candidate.responses.jsonl'
             for run in ('source-training-v48', 'stylistic-screen-v48')]
    result = []
    for path in paths:
        for row in read_jsonl(path):
            if row['finish_reason'] == 'length':
                result.append(dict(case=row['case_id'], source_sha256=file_hash(path),
                                   **analyse(row['text'])))
    assert len(result) == 2
    out = ROOT / 'artifacts/dialogue-loop-v49'
    out.mkdir()
    with (out / 'replay.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(result)
