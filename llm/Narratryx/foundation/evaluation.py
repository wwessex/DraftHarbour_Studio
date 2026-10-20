"""Offline objective checks and blinded human review, without inference calls."""

from __future__ import annotations

import json
import random
import re
import statistics
from pathlib import Path

from .validation import (Invalid, ROOT, approved, digest, file_hash, index_rows,
                         read_json, read_jsonl, validate_schema)


def write_new(path: Path, value, *, jsonl: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        if jsonl:
            for row in value:
                handle.write(json.dumps(row, ensure_ascii=False) + '\n')
        else:
            handle.write(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


DEFAULT_RUBRIC = ROOT / 'evaluation' / 'rubric.json'


def benchmark(path: Path, lock: Path | None = None, allow_draft: bool = False,
              rubric: Path = DEFAULT_RUBRIC) -> list[dict]:
    tasks = list(index_rows(read_jsonl(path), 'eval-task').values())
    for task in tasks:
        for check in task['checks']:
            if check['type'] in ('word_count', 'line_count') and check['min'] > check['max']:
                raise Invalid(f'{task["id"]}: invalid word-count range')
    if not allow_draft:
        for task in tasks:
            approved(task['review'], task['id'])
        if lock is None:
            raise Invalid('a frozen benchmark lock is required (or explicitly use --allow-draft)')
        expected = freeze_manifest(path, tasks, rubric)
        if read_json(lock) != expected:
            raise Invalid('benchmark lock mismatch: tasks, schemas or rubric changed')
    return tasks


def freeze_manifest(path: Path, tasks: list[dict], rubric: Path = DEFAULT_RUBRIC) -> dict:
    rubric_record = read_json(rubric)
    validate_schema(rubric_record, 'eval-rubric')
    approved(rubric_record['review'], 'editorial rubric')
    return {'schema_version': '1.0', 'benchmark_sha256': file_hash(path),
            'task_count': len(tasks), 'task_ids': [t['id'] for t in tasks],
            'rubric_sha256': file_hash(rubric),
            'rubric_schema_sha256': file_hash(ROOT / 'schemas' / 'eval-rubric.schema.json'),
            'task_schema_sha256': file_hash(ROOT / 'schemas' / 'eval-task.schema.json')}


def freeze(path: Path, output: Path, rubric: Path = DEFAULT_RUBRIC) -> dict:
    tasks = benchmark(path, allow_draft=True)
    for task in tasks:
        approved(task['review'], task['id'])
    manifest = freeze_manifest(path, tasks, rubric)
    write_new(output, manifest)
    return manifest


def responses(path: Path, tasks: list[dict]) -> dict:
    rows = index_rows(read_jsonl(path), 'eval-response', 'task_id')
    unexpected = set(rows) - {t['id'] for t in tasks}
    if unexpected:
        raise Invalid(f'unknown response task IDs: {sorted(unexpected)}')
    return rows


def objective(check: dict, text: str, context: str) -> bool:
    kind = check['type']
    if kind == 'word_count':
        return check['min'] <= len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b", text)) <= check['max']
    if kind == 'exact':
        return text == check['value']
    if kind == 'line_count':
        return check['min'] <= len([line for line in text.splitlines() if line.strip()]) <= check['max']
    if kind == 'contains':
        return check['value'] in text
    if kind == 'excludes':
        return check['value'] not in text
    if kind == 'json':
        try:
            json.loads(text, parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))
            return True
        except ValueError:
            return False
    if kind == 'quotes_from_context':
        # Explicit convention: analytical evidence uses double quotes, not dialogue marks.
        quotes = re.findall(r'"([^"\n]+)"|“([^”\n]+)”', text)
        return (len({a or b for a, b in quotes}) >= check['min_quotes']
                and all((a or b) in context for a, b in quotes))
    raise Invalid(f'unknown objective check: {kind}')


def score(tasks: list[dict], rows: dict, run: dict, benchmark_path: Path,
          allow_draft: bool = False) -> dict:
    validate_schema(run, 'eval-run')
    if run['benchmark_sha256'] != file_hash(benchmark_path):
        raise Invalid('run metadata references a different benchmark hash')
    results = []
    for task in tasks:
        row = rows.get(task['id'])
        failure = 'missing response' if row is None else row['error']
        if row and not row['text'].strip():
            failure = failure or 'empty response'
        checks = [{'type': c['type'], 'passed': not failure and objective(
            c, row['text'] if row else '', task['context'])} for c in task['checks']]
        results.append({'task_id': task['id'], 'task': task['task'],
                        'error': failure, 'checks': checks,
                        'passed': not failure and all(c['passed'] for c in checks)})
    per_skill = {}
    for skill in sorted({t['task'] for t in tasks}):
        subset = [r for r in results if r['task'] == skill]
        per_skill[skill] = {'tasks': len(subset), 'passed': sum(r['passed'] for r in subset)}
    latencies = [r['latency_ms'] for r in rows.values() if r['error'] is None and r['text'].strip()]
    return {'schema_version': '1.0', 'run': run, 'draft_benchmark': allow_draft,
            'literary_quality': 'requires blind human review; objective checks are not literary scores',
            'promotion': 'not assessed', 'task_count': len(tasks),
            'objective_pass_rate': sum(r['passed'] for r in results) / len(results),
            'per_skill': per_skill, 'missing_responses': len(tasks) - len(rows),
            'mean_completion_latency_ms': statistics.mean(latencies) if latencies else None,
            'results': results}


def blind(tasks: list[dict], left: dict, right: dict, seed: int) -> tuple[list, dict]:
    expected = {t['id'] for t in tasks}
    if set(left) != expected or set(right) != expected:
        raise Invalid('blind review requires exactly one response per task in both runs')
    rng = random.Random(seed)
    packets, assignments = [], {}
    for task in tasks:
        swap = rng.choice([False, True])
        mapping = {'A': 'right' if swap else 'left', 'B': 'left' if swap else 'right'}
        assignments[task['id']] = mapping
        candidates = {'left': left[task['id']], 'right': right[task['id']]}
        packets.append({'task_id': task['id'], 'task': task['task'],
                        'context': task['context'], 'prompt': task['prompt'],
                        'rubric': task['rubric'],
                        'answers': {label: {'text': candidates[side]['text'],
                                           'failed': bool(candidates[side]['error'] or not candidates[side]['text'].strip())}
                                    for label, side in mapping.items()}})
    rng.shuffle(packets)
    return packets, {'schema_version': '1.0', 'seed': seed,
                     'assignments': assignments, 'packet_hash': digest(packets)}


def summarize_reviews(tasks: list[dict], packets: list[dict], key: dict,
                      ballots: list[dict], seed: int = 42) -> dict:
    task_map = {t['id']: t for t in tasks}
    if digest(packets) != key['packet_hash']:
        raise Invalid('review packet hash mismatch')
    if set(key['assignments']) != set(task_map) or {p['task_id'] for p in packets} != set(task_map):
        raise Invalid('review tasks do not match benchmark')
    scores, seen = {}, set()
    for task_id, mapping in key['assignments'].items():
        if set(mapping) != {'A', 'B'} or set(mapping.values()) != {'left', 'right'}:
            raise Invalid(f'invalid blind assignment: {task_id}')
    for ballot in ballots:
        validate_schema(ballot, 'review-ballot')
        ident = ballot['task_id']
        reviewer = ballot['reviewer'].strip().casefold()
        if ident not in task_map or (ident, reviewer) in seen:
            raise Invalid('unknown task or duplicate reviewer/task ballot')
        seen.add((ident, reviewer))
        choice = ballot['choice']
        value = .5 if choice == 'tie' else float(key['assignments'][ident][choice] == 'right')
        scores.setdefault(ident, []).append(value)
    if not scores:
        raise Invalid('no review ballots')
    # Average reviewers within task, tasks within scenario; bootstrap scenarios to
    # avoid treating six related skill tasks as six independent observations.
    scenarios = {}
    for ident, values in scores.items():
        scenarios.setdefault(task_map[ident]['scenario_id'], []).append(statistics.mean(values))
    values = [statistics.mean(v) for v in scenarios.values()]
    rng = random.Random(seed)
    boot = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(2000))
    per_skill = {}
    for skill in sorted({t['task'] for t in tasks}):
        items = [statistics.mean(scores[t['id']]) for t in tasks if t['task'] == skill and t['id'] in scores]
        per_skill[skill] = {'reviewed_tasks': len(items),
                            'right_win_rate_ties_half': statistics.mean(items) if items else None}
    return {'promotion': 'not assessed', 'right_win_rate_ties_half': statistics.mean(values),
            'scenario_bootstrap_95_ci': [boot[49], boot[1949]] if len(values) >= 2 else None,
            'reviewed_scenarios': len(values), 'reviewed_tasks': len(scores),
            'total_tasks': len(tasks), 'tasks_with_two_reviewers': sum(len(v) >= 2 for v in scores.values()),
            'missing_task_ids': sorted(set(task_map) - set(scores)), 'per_skill': per_skill,
            'note': 'Incomplete review or a wide interval cannot establish improvement. Ratings remain in ballots for editorial review.'}
