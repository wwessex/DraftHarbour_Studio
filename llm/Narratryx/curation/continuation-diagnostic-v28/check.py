"""Recheck the v27 screen against both forms of the paragraph instruction."""
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'curation/source-training-v26'))
from decision import decide, writing_checks
from foundation.validation import file_hash, read_jsonl

RUN = ROOT / 'artifacts/source-training-v27'
OUT = ROOT / 'artifacts/continuation-diagnostic-v28'
PARAGRAPH = re.compile(r'\b(?:one|a) new paragraph\b', re.I)


def main():
    lock = ROOT / 'curation/source-training-v27/results.lock.json'
    for name, digest in json.loads(lock.read_text()).items():
        assert file_hash(ROOT / name) == digest, name
    cases = read_jsonl(RUN / 'cases.frozen.jsonl')
    selected = [case for case in cases if case['kind'] == 'continue'
                and PARAGRAPH.search(case['prompt'].split('PARAGRAPH:')[0])]
    assert len(selected) == 9
    checks = {}
    for side in ('current-craft', 'candidate'):
        responses = {r['case_id']: r['text'] for r in read_jsonl(RUN / f'{side}.responses.jsonl')}
        failed = []
        for case in selected:
            text = responses[case['id']].strip()
            if not text or re.search(r'\n[ \t]*\n', text):
                failed.append(case['id'])
        checks[side] = writing_checks(cases, responses)
        checks[side]['single-paragraph continuations'] = dict(
            passed=len(selected) - len(failed), total=len(selected), failed_cases=failed)
    result = decide(json.loads((RUN / 'scores.json').read_text())['summary'], checks)
    data = ROOT / 'artifacts/curriculum-fit-v24/records.review-only.jsonl'
    lessons = []
    for row in read_jsonl(data):
        brief = row['messages'][0]['content'].splitlines()[0]
        if row['split'] == 'train' and brief.startswith('Continue') and re.search(
                r'\b(?:one|two) new paragraphs?\b', brief):
            answer = row['messages'][-1]['content'].strip()
            lessons.append(dict(id=row['id'], words=len(answer.split()),
                                paragraphs=len(re.split(r'\n[ \t]*\n', answer)),
                                explicit_word_range=bool(re.search(r'\d+\s*[–-]\s*\d+\s*words', brief))))
    result.update(lessons=lessons, source_dataset_sha256=file_hash(data))
    OUT.mkdir()
    with (OUT / 'decision.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
