"""Run with python -m foundation from llm/Narratryx. All commands are offline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .evaluation import (DEFAULT_RUBRIC, benchmark, blind, freeze, responses, score, summarize_reviews,
                         write_new)
from .validation import (Invalid, clear_source, file_hash, load_ledger,
                         read_json, read_jsonl, validate_dataset, validate_schema)


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest='command', required=True)
    ledger = sub.add_parser('validate-ledger', help='structural check; --release requires recorded approval and local hash evidence')
    ledger.add_argument('ledger', type=Path)
    ledger.add_argument('--release', action='store_true')
    ledger.add_argument('--jurisdictions', nargs='+')
    ledger.add_argument('--use', choices=['training', 'evaluation', 'redistribution'], default='training')
    dataset = sub.add_parser('validate-dataset', help='fail-closed rights, provenance and cross-split checks')
    dataset.add_argument('dataset', type=Path)
    dataset.add_argument('--ledger', type=Path, required=True)
    dataset.add_argument('--jurisdictions', nargs='+', required=True)
    dataset.add_argument('--benchmark', type=Path, required=True)
    dataset.add_argument('--lock', type=Path, required=True)
    dataset.add_argument('--rubric', type=Path, default=DEFAULT_RUBRIC)
    dataset.add_argument('--output', type=Path, required=True)
    freezer = sub.add_parser('freeze', help='freeze reviewed tasks/rubric by hash; refuses pending tasks')
    freezer.add_argument('--tasks', type=Path, required=True)
    freezer.add_argument('--output', type=Path, required=True)
    freezer.add_argument('--rubric', type=Path, default=DEFAULT_RUBRIC)
    for name in ('export-prompts', 'score', 'blind', 'review-report'):
        cmd = sub.add_parser(name)
        cmd.add_argument('--tasks', type=Path, required=True)
        cmd.add_argument('--lock', type=Path)
        cmd.add_argument('--rubric', type=Path, default=DEFAULT_RUBRIC)
        cmd.add_argument('--allow-draft', action='store_true', help='development only; no promotion claim')
        if name == 'export-prompts':
            cmd.add_argument('--output', type=Path, required=True)
        elif name == 'score':
            cmd.add_argument('--responses', type=Path, required=True)
            cmd.add_argument('--run', type=Path, required=True)
            cmd.add_argument('--output', type=Path, required=True)
        elif name == 'blind':
            for side in ('left', 'right'):
                cmd.add_argument(f'--{side}', type=Path, required=True)
                cmd.add_argument(f'--{side}-run', type=Path, required=True)
            cmd.add_argument('--seed', type=int, default=42)
            cmd.add_argument('--output-dir', type=Path, required=True)
        else:
            cmd.add_argument('--packet', type=Path, required=True)
            cmd.add_argument('--key', type=Path, required=True)
            cmd.add_argument('--ballots', type=Path, required=True)
            cmd.add_argument('--output', type=Path, required=True)
    return p


def execute(args) -> dict:
    if args.command == 'validate-ledger':
        ledger = load_ledger(args.ledger)
        if args.release:
            for row in ledger.values():
                clear_source(row, args.ledger, args.jurisdictions, args.use)
        return {'records': len(ledger), 'mode': 'release-evidence' if args.release else 'structure-only',
                'approved_records': sum(r['review']['status'] == 'approved' for r in ledger.values()),
                'legal_certification': False}
    if args.command == 'validate-dataset':
        tasks = benchmark(args.benchmark, args.lock, rubric=args.rubric)
        rows = validate_dataset(args.dataset, args.ledger, args.jurisdictions, tasks)
        report = {'schema_version': '1.0', 'records': len(rows),
                  'dataset_version': rows[0]['dataset_version'],
                  'dataset_sha256': file_hash(args.dataset), 'ledger_sha256': file_hash(args.ledger),
                  'benchmark_sha256': file_hash(args.benchmark),
                  'jurisdictions': args.jurisdictions,
                  'record_ids': [r['id'] for r in rows],
                  'rights_record_ids': sorted({i for r in rows for i in r['rights_record_ids']}),
                  'split_counts': {s: sum(r['split'] == s for r in rows) for s in ('train', 'validation', 'test')},
                  'lexical_overlap_screen': 'passed; not semantic or pretraining-contamination clearance',
                  'legal_certification': False}
        write_new(args.output, report)
        return report
    if args.command == 'freeze':
        return freeze(args.tasks, args.output, args.rubric)
    tasks = benchmark(args.tasks, args.lock, args.allow_draft, args.rubric)
    if args.command == 'export-prompts':
        # Targets, checks, rubrics and review metadata are intentionally withheld.
        prompts = [{'task_id': t['id'], 'messages': [
            {'role': 'user', 'content': f'Context:\n{t["context"]}\n\nTask:\n{t["prompt"]}'}
        ]} for t in tasks]
        write_new(args.output, prompts, jsonl=True)
        return {'exported': len(prompts), 'benchmark_sha256': file_hash(args.tasks),
                'draft_benchmark': args.allow_draft, 'inference_calls': 0}
    if args.command == 'score':
        report = score(tasks, responses(args.responses, tasks), read_json(args.run),
                       args.tasks, args.allow_draft)
        report['responses_sha256'] = file_hash(args.responses)
        write_new(args.output, report)
        return {k: v for k, v in report.items() if k != 'results'}
    if args.command == 'blind':
        runs = {s: read_json(getattr(args, f'{s}_run')) for s in ('left', 'right')}
        for run in runs.values():
            validate_schema(run, 'eval-run')
            if run['benchmark_sha256'] != file_hash(args.tasks):
                raise Invalid('comparison run benchmark mismatch')
        if runs['left']['run_id'] == runs['right']['run_id']:
            raise Invalid('comparison requires distinct run IDs')
        packets, key = blind(tasks, responses(args.left, tasks), responses(args.right, tasks), args.seed)
        key.update({'runs': runs, 'benchmark_sha256': file_hash(args.tasks),
                    'response_hashes': {'left': file_hash(args.left), 'right': file_hash(args.right)},
                    'draft_benchmark': args.allow_draft})
        # Exclusive directory prevents accidental replacement of review artifacts.
        args.output_dir.mkdir(parents=True, exist_ok=False)
        write_new(args.output_dir / 'review.jsonl', packets, jsonl=True)
        write_new(args.output_dir / 'private-key.json', key)
        (args.output_dir / 'private-key.json').chmod(0o600)
        return {'review_tasks': len(packets), 'draft_benchmark': args.allow_draft,
                'instruction': 'share only review.jsonl and the rubric; keep private-key.json private'}
    key = read_json(args.key)
    if key.get('benchmark_sha256') != file_hash(args.tasks):
        raise Invalid('review key benchmark mismatch')
    report = summarize_reviews(tasks, read_jsonl(args.packet), key, read_jsonl(args.ballots))
    report.update({'draft_benchmark': args.allow_draft or key['draft_benchmark'],
                   'runs': key['runs'], 'response_hashes': key['response_hashes']})
    write_new(args.output, report)
    return report


def main() -> int:
    args = parser().parse_args()
    try:
        result = execute(args)
    except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps({'ok': True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
