"""Resumable offline preparation/export/evaluation. Never submits or launches jobs."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

from .austen_review import build_pack
from .evaluation import benchmark, blind, responses, score, write_new
from .validation import (Invalid, ROOT, clear_source, digest, file_hash, load_ledger,
                         read_json, read_jsonl, validate_dataset, validate_schema)


def atomic_json(path: Path, value: dict) -> None:
    """Publish state only after a complete write; interrupted writes are disposable."""
    fd, name = tempfile.mkstemp(prefix='.state-', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


@contextmanager
def run_lock(directory: Path):
    """OS releases the advisory lock on exit/crash; no stale PID deletion needed."""
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / '.runner.lock').open('a+b') as handle:
        if handle.tell() == 0:
            handle.write(b'0')
            handle.flush()
        handle.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise Invalid('another runner holds this run directory') from exc
        try:
            yield
        finally:
            if os.name == 'nt':
                handle.seek(0)
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle, fcntl.LOCK_UN)


def resolve_config(path: Path) -> dict:
    config = read_json(path)
    validate_schema(config, 'offline-runner')
    # Paths are relative to the configuration, never the caller's working directory.
    for name in ('ledger', 'dataset', 'tasks', 'lock', 'rubric'):
        config[name] = (path.parent / config[name]).resolve()
    if config['prepare_austen']:
        for key, value in config['prepare_austen'].items():
            config['prepare_austen'][key] = (path.parent / value).resolve()
    for side in ('baseline', 'candidate'):
        if config[side]:
            config[side] = {k: (path.parent / v).resolve() for k, v in config[side].items()}
    return config


def inputs(config: dict, config_path: Path) -> dict:
    paths = {config_path.resolve(), *ROOT.joinpath('foundation').glob('*.py'),
             *ROOT.joinpath('schemas').glob('*.json'), ROOT / 'training/unsloth_sft.py',
             ROOT / 'evaluation/tasks.draft.jsonl'}
    paths.update(config[k] for k in ('ledger', 'dataset', 'tasks', 'lock', 'rubric'))
    if config['prepare_austen']:
        paths.update(config['prepare_austen'].values())
        approval = read_json(config['prepare_austen']['approval'])
        for entry in approval['reviewed_documents'].values():
            paths.add((config['ledger'].parent / entry['snapshot_path']).resolve())
    for side in ('baseline', 'candidate'):
        if config[side]:
            paths.update(config[side].values())
    # Hash the source bytes too: a cached validation must not survive a source edit.
    ledger = load_ledger(config['ledger'])
    for row in ledger.values():
        raw = row['source'].get('raw_path')
        if raw:
            raw_path = (config['ledger'].parent / raw).resolve()
            if not raw_path.is_relative_to(config['ledger'].parent.resolve()):
                raise Invalid('raw source escapes ledger directory')
            paths.add(raw_path)
    return {str(p): file_hash(p) if p.is_file() else None for p in sorted(paths)}


def release_checks(config: dict) -> tuple[list, list, list]:
    """Collect independent gates together instead of hiding all but the first."""
    blockers, rows, tasks = [], [], []
    try:
        raw_rows = read_jsonl(config['dataset'])
        ids = {ident for row in raw_rows for ident in row['rights_record_ids']}
        ledger = load_ledger(config['ledger'])
        # Only sources used by this dataset need release. Other candidates stay pending.
        for ident in sorted(ids):
            try:
                row = ledger[ident]
                uses = {'training' if r['split'] == 'train' else 'evaluation'
                        for r in raw_rows if ident in r['rights_record_ids']}
                for use in sorted(uses):
                    clear_source(row, config['ledger'], config['jurisdictions'], use)
            except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
                blockers.append({'gate': f'source:{ident}', 'reason': str(exc)})
    except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
        blockers.append({'gate': 'dataset-input', 'reason': str(exc)})
    try:
        tasks = benchmark(config['tasks'], config['lock'], rubric=config['rubric'])
    except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
        blockers.append({'gate': 'frozen-benchmark', 'reason': str(exc)})
    try:
        # With no valid benchmark, independently check rights/reviews/provenance;
        # export remains blocked until the frozen benchmark also passes.
        rows = validate_dataset(config['dataset'], config['ledger'], config['jurisdictions'], tasks or None)
        if not any(row['split'] == 'train' for row in rows):
            raise Invalid('dataset contains no training records')
    except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
        blockers.append({'gate': 'dataset-release', 'reason': str(exc)})
    return blockers, rows, tasks


def export_bundle(config: dict, rows: list, tasks: list, output: Path) -> None:
    train = [{'messages': row['messages']} for row in rows if row['split'] == 'train']
    write_new(output / 'train.jsonl', train, jsonl=True)
    write_new(output / 'provenance.json', {
        'record_ids': [r['id'] for r in rows if r['split'] == 'train'],
        'dataset_sha256': file_hash(config['dataset']),
        'ledger_sha256': file_hash(config['ledger']),
        'benchmark_sha256': file_hash(config['tasks']),
        'jurisdictions': config['jurisdictions'], 'legal_certification': False})
    write_new(output / 'prompts.jsonl', [{'task_id': t['id'], 'messages': [
        {'role': 'user', 'content': f'Context:\n{t["context"]}\n\nTask:\n{t["prompt"]}'}
    ]} for t in tasks], jsonl=True)
    # Benchmark targets/checks/rubrics and non-training splits never enter train.jsonl.
    shutil.copyfile(ROOT / 'training/unsloth_sft.py', output / 'unsloth_sft.py')
    write_new(output / 'job-plan.json', {
        'status': 'export-only; GPU recipe unvalidated on hardware',
        'paid_execution_enabled': False, 'submitted': False,
        'model': config['model'], 'training': config['training'],
        'train_sha256': file_hash(output / 'train.jsonl'),
        'script_sha256': file_hash(output / 'unsloth_sft.py'),
        'required_before_execution': ['review base-model license and exact revision',
            'choose provider, private durable checkpoint storage and pinned GPU environment',
            'authorize a priced job and total budget, including evaluation',
            'hardware smoke test, baseline inference and candidate inference'],
        'promotion': 'disabled; blind literary review required'})


def evaluate(config: dict, tasks: list, output: Path) -> dict:
    imported = {}
    for side in ('baseline', 'candidate'):
        if config[side] is None:
            continue
        spec = config[side]
        metadata = read_json(spec['run'])
        imported[side] = responses(spec['responses'], tasks)
        report = score(tasks, imported[side], metadata, config['tasks'])
        report['responses_sha256'] = file_hash(spec['responses'])
        write_new(output / f'{side}.score.json', report)
    if len(imported) == 2:
        left, right = (read_json(config[s]['run']) for s in ('baseline', 'candidate'))
        if left['run_id'] == right['run_id']:
            raise Invalid('baseline and candidate need distinct run IDs')
        if left['artifact_sha256'] == right['artifact_sha256']:
            raise Invalid('baseline and candidate reference the same artifact')
        if left['generation'] != right['generation'] or left['prompt_version'] != right['prompt_version']:
            raise Invalid('comparison requires matching generation settings and prompt version')
        packet, key = blind(tasks, imported['baseline'], imported['candidate'], 42)
        key.update({'runs': {'left': left, 'right': right}, 'draft_benchmark': False,
                    'benchmark_sha256': file_hash(config['tasks']),
                    'response_hashes': {s: file_hash(config[s]['responses']) for s in imported}})
        write_new(output / 'review.jsonl', packet, jsonl=True)
        write_new(output / 'private-key.json', key)
        (output / 'private-key.json').chmod(0o600)
    return {'scored': sorted(imported), 'comparison_ready': len(imported) == 2,
            'promotion': 'disabled; objective pass rates do not establish literary quality'}


def run(config_path: Path, output: Path) -> dict:
    config_path, output = config_path.resolve(), output.resolve()
    config = resolve_config(config_path)
    # Do not let an output path contain input files (including future configured files).
    fingerprint_inputs = inputs(config, config_path)
    if any(Path(p).is_relative_to(output) for p in fingerprint_inputs):
        raise Invalid('run directory must be separate from all inputs')
    fingerprint = digest(fingerprint_inputs)
    with run_lock(output):
        state_path = output / 'state.json'
        if state_path.exists():
            state = read_json(state_path)
            if state['input_fingerprint'] != fingerprint:
                raise Invalid('inputs changed; choose a new run directory to preserve this run')
        else:
            if any(p.name != '.runner.lock' for p in output.iterdir()):
                raise Invalid('nonempty run directory has no runner state; choose a new directory')
            state = {'schema_version': '1.0', 'input_fingerprint': fingerprint,
                     'input_hashes': fingerprint_inputs, 'stages': {}}
            # Establish ownership before publishing stage directories. Never remove
            # an unrelated pre-existing bundle in a user-chosen output directory.
            atomic_json(state_path, state)

        def stage(name, action):
            destination = output / name
            previous = state['stages'].get(name)
            if previous and previous['status'] == 'complete':
                actual = {str(p.relative_to(destination)): file_hash(p)
                          for p in destination.rglob('*') if p.is_file()}
                if actual != previous['files']:
                    raise Invalid(f'{name}: completed output changed or missing; use a new run')
                return previous.get('result')
            # A crash before state publication may leave a complete directory. It is
            # disposable unless committed in state, and rebuilt from unchanged inputs.
            if destination.exists():
                shutil.rmtree(destination)
            temporary = Path(tempfile.mkdtemp(prefix=f'.{name}-', dir=output))
            try:
                result = action(temporary)
                files = {str(p.relative_to(temporary)): file_hash(p)
                         for p in temporary.rglob('*') if p.is_file()}
                temporary.rename(destination)
                state['stages'][name] = {'status': 'complete', 'files': files, 'result': result}
                atomic_json(state_path, state)
                return result
            finally:
                if temporary.exists():
                    shutil.rmtree(temporary)

        if config['prepare_austen']:
            spec = config['prepare_austen']

            def prepare(temp):
                # Builder requires an absent directory; parent temp is the transaction.
                build_pack(spec['spec'], config['ledger'], spec['source_manifest'],
                           spec['approval'], temp / 'pack')
                return {'status': 'drafts only; existing decisions unchanged'}

            stage('preparation', prepare)
        blockers, rows, tasks = release_checks(config)
        if digest(inputs(config, config_path)) != fingerprint:
            raise Invalid('inputs changed during validation; use a new run directory')
        evaluation = {'scored': [], 'comparison_ready': False}
        if not blockers:
            stage('bundle', lambda temp: export_bundle(config, rows, tasks, temp))
            try:
                evaluation = stage('evaluation', lambda temp: evaluate(config, tasks, temp))
            except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
                blockers.append({'gate': 'imported-evaluation', 'reason': str(exc)})
        if digest(inputs(config, config_path)) != fingerprint:
            raise Invalid('inputs changed during execution; discard this run and choose a new one')
        report = {'schema_version': '1.0', 'updated_at_utc': datetime.now(timezone.utc).isoformat(),
                  'status': 'blocked' if blockers else 'offline-stages-complete',
                  'blockers': blockers, 'stages': state['stages'], 'evaluation': evaluation,
                  'paid_execution_enabled': False, 'jobs_submitted': 0, 'inference_calls': 0,
                  'training_started': False, 'promotion': 'disabled',
                  'next_step': 'Resolve recorded gates and configure a new run; no approvals are inferred.'
                  if blockers else 'GPU execution and inference require a separately authorized provider setup.'}
        atomic_json(state_path, state)
        atomic_json(output / 'report.json', report)
        return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT / 'configs/offline-runner.json')
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    try:
        report = run(args.config, args.run_dir)
    except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if report['blockers'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
