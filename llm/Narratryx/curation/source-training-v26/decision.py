"""Apply the mechanical screening gate to a completed pilot."""
import json
import re
from pathlib import Path

RUN = Path(__file__).resolve().parents[2] / 'artifacts/source-training-v26'


def writing_checks(cases, responses):
    checks = {}
    for case in cases:
        prompt = case['prompt']
        kind = case['kind']
        text = responses[case['id']].strip()
        if kind == 'dialogue' and re.search(r'(?:four to six|4[–-]6) dialogue turns', prompt):
            turns = re.findall(r"^[A-Za-z][A-Za-z .'-]{0,30}:[ \t]*\S", text, re.M)
            check, passed = 'dialogue turn limits', 4 <= len(turns) <= 6
        elif kind == 'rewrite' and re.search(r'(?:^|\n)PARAGRAPH:', prompt):
            source = re.split(r'(?:^|\n)PARAGRAPH:', prompt)[-1]
            check, passed = 'changed rewrites', bool(text) and text.split() != source.split()
        elif kind == 'continue' and re.search(r'\bone new paragraph\b', prompt):
            check, passed = 'single-paragraph continuations', bool(text) and not re.search(r'\n[ \t]*\n', text)
        else:
            continue
        row = checks.setdefault(check, dict(passed=0, total=0, failed_cases=[]))
        row['total'] += 1
        row['passed'] += passed
        if not passed:
            row['failed_cases'].append(case['id'])
    return checks


def decide(scores, writing):
    craft = scores['current-craft']
    candidate = scores['candidate']
    reasons = []
    if any(row['attempted'] != 49 or row['failures'] or row['truncated']
           for row in scores.values()):
        reasons.append('Incomplete or failed comparison')
    before, after = craft['primary'], candidate['primary']
    comparisons = {
        key: (before[key], after[key])
        for key in ('focused_closed_exact', 'clock_exact', 'claim_exact', 'selected_edits')
    }
    for cohort, tasks in before['word_limits'].items():
        for task, count in tasks.items():
            comparisons[f'{cohort} {task} word limits'] = (
                count, after['word_limits'][cohort][task])
    for name, old in writing['current-craft'].items():
        comparisons[name] = (old, writing['candidate'][name])
    gains = []
    for name, (old, new) in comparisons.items():
        if old['total'] != new['total'] or new['passed'] < old['passed']:
            reasons.append(f"{name} regressed ({old['passed']}/{old['total']} to "
                           f"{new['passed']}/{new['total']})")
        elif new['passed'] > old['passed']:
            gains.append(name)
    if after['dialogue_repeat_flags'] > before['dialogue_repeat_flags']:
        reasons.append('More repeated dialogue')
    if not gains:
        reasons.append('No measured regression-suite gain')
    return dict(decision='keep-craft' if reasons else 'advance-to-fresh-evaluation',
                reasons=reasons, gains=gains, writing_checks=writing, human_review_required=False)


if __name__ == '__main__':
    assert (RUN / 'experiment-complete.json').is_file()
    def rows(name):
        return [json.loads(line) for line in (RUN / name).read_text().splitlines()]

    cases = rows('cases.frozen.jsonl')
    writing = {
        side: writing_checks(cases, {row['case_id']: row['text']
                                    for row in rows(f'{side}.responses.jsonl')})
        for side in ('current-craft', 'candidate')
    }
    result = decide(json.loads((RUN / 'scores.json').read_text())['summary'], writing)
    with (RUN / 'automatic-decision-v2.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps(result, indent=2))
