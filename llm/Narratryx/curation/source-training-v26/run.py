"""Check or execute the frozen 34-update pilot with the existing process guards."""
import argparse
import importlib.metadata
import json
from pathlib import Path
import runpy
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl

HERE = Path(__file__).resolve().parent
PLAN = ROOT / 'artifacts/pilot-recipe-v26'
RUN = ROOT / 'artifacts/source-training-v26'
HELPERS = ROOT / 'curation/stability-v10/run.py'


def verify_inputs(plan):
    for name, expected in plan['input_hashes'].items():
        assert file_hash(ROOT / name) == expected, name
    for name, expected in (plan['installed_source_hashes'] | plan['model_metadata_hashes']).items():
        assert file_hash(Path(name)) == expected, name
    assert file_hash(Path(plan['base_path']) / 'model.safetensors') == plan['base_weights_sha256']
    assert {n: importlib.metadata.version(n) for n in plan['reference_environment']} == plan['reference_environment']


def load_plan():
    path = PLAN / 'protocol.frozen.json'
    manifest = json.loads((ROOT / 'curation/pilot-recipe-v26/manifest.json').read_text())
    assert file_hash(path) == manifest['protocol_sha256']
    plan = json.loads(path.read_text())
    amendment_dir = ROOT / 'artifacts/pilot-recipe-v26-install-audit'
    amendment_path = amendment_dir / 'amendment.json'
    lock_path = HERE / 'installation.lock.json'
    lock = json.loads(lock_path.read_text())
    assert file_hash(amendment_path) == lock['amendment_sha256']
    amendment = json.loads(amendment_path.read_text())
    assert amendment['protocol_sha256'] == manifest['protocol_sha256']
    assert not amendment['training_started']
    assert file_hash(HERE / 'audit_install.py') == amendment['audit_sha256']
    worker_path = amendment_dir / 'worker-config.json'
    assert file_hash(worker_path) == amendment['worker_config_sha256']
    plan.update(reference_environment=amendment['reference_environment'],
                installed_source_hashes=amendment['installed_source_hashes'],
                worker_config_path=str(worker_path.relative_to(ROOT)))
    plan['input_hashes'].update({str(p.relative_to(ROOT)): file_hash(p)
                                for p in (amendment_path, worker_path, lock_path)})
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute', action='store_true', help='Launch the local pilot')
    args = parser.parse_args()
    if not __debug__:
        raise RuntimeError('Pilot requires Python assertions')
    if RUN.exists():
        raise RuntimeError('Run directory already exists')
    path = PLAN / 'protocol.frozen.json'
    plan = load_plan()
    verify_inputs(plan)
    request = json.loads((PLAN / 'request.json').read_text())
    assert request['max_steps'] == plan['training_steps'] == 34
    assert plan['resource_stop'] == dict(max_steps=34, peak_mlx_gb=10,
                                       process_tree_rss_bytes=10_000_000_000,
                                       phase_deadline_seconds=1200,
                                       stop_on_warning_error_nonfinite_or_truncation=True)
    cases = read_jsonl(ROOT / plan['primary_cases_path']) + read_jsonl(ROOT / plan['seen_cases_path'])
    assert len(cases) == len({c['id'] for c in cases}) == 49
    subprocess.run([sys.executable, str(HERE / 'train.py'), '--check'], check=True, timeout=120)
    if not args.execute:
        return
    helpers = runpy.run_path(str(HELPERS))
    helpers['phase'].__globals__.update(RUN=RUN, PYTHON=Path(sys.executable))
    if not helpers['port_free']():
        raise RuntimeError('Port 8890 is occupied. Release its model memory before the pilot.')
    RUN.mkdir()
    save, phase = helpers['save'], helpers['phase']
    save('request.json', request)
    case_path = RUN / 'cases.frozen.jsonl'
    with case_path.open('x') as stream:
        for case in cases:
            stream.write(json.dumps(case, ensure_ascii=False) + '\n')
    paths = [path, case_path, RUN / 'request.json', HELPERS, *HERE.glob('*.py'),
             ROOT / 'runtime/local/engine.py']
    plan['input_hashes'].update({str(p.relative_to(ROOT)): file_hash(p) for p in paths})
    plan.update(test_cases_path=str(case_path.relative_to(ROOT)), context_limit=2048,
                status='execution-started')
    save('protocol.frozen.json', plan)
    deadline = plan['resource_stop']['phase_deadline_seconds']
    try:
        for side in ('base', 'current-craft'):
            phase(side, [str(HERE / 'evaluate.py'), side], deadline)
        phase('training', [str(HERE / 'train.py')], deadline)
        phase('candidate', [str(HERE / 'evaluate.py'), 'candidate'], deadline)
        phase('report', [str(HERE / 'report.py')], deadline)
        verify_inputs(plan)
        save('experiment-complete.json', dict(training_steps=34, new_responses=147))
    except BaseException as error:
        save('experiment-failed.json', dict(error=repr(error)))
        raise


if __name__ == '__main__':
    main()
