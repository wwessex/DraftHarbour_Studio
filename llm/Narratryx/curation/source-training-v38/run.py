"""Run one expanded-curriculum pilot and automatically screen the candidate."""
import json
import os
os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", HF_DATASETS_OFFLINE="1")
from pathlib import Path
import runpy
import shutil
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PREVIOUS = ROOT / 'curation/source-training-v26'
REFERENCE = ROOT / 'artifacts/source-training-v26'
RUN = ROOT / 'artifacts/source-training-v38'
sys.path.insert(0, str(PREVIOUS))
previous_runner = runpy.run_path(str(PREVIOUS / 'run.py'))
HELPERS = previous_runner['HELPERS']
load_plan = previous_runner['load_plan']
verify_inputs = previous_runner['verify_inputs']
from decision import decide, writing_checks
from foundation.validation import file_hash, read_jsonl
from tokens import prepare
import re


def main():
    assert __debug__
    if RUN.exists():
        raise RuntimeError('Run directory already exists')
    plan = load_plan()
    verify_inputs(plan)
    old = json.loads((REFERENCE / 'protocol.frozen.json').read_text())
    verify_inputs(old)
    lock = json.loads((PREVIOUS / 'results.lock.json').read_text())
    for name, expected in lock.items():
        assert file_hash(ROOT / name) == expected, name
    helpers = runpy.run_path(str(HELPERS))
    helpers['phase'].__globals__.update(RUN=RUN, PYTHON=Path(sys.executable))
    if not helpers['port_free']():
        raise RuntimeError('Port 8890 is occupied')
    request = json.loads((REFERENCE / 'request.json').read_text())
    request.update(learning_rate='2.5e-5', project_name='Narratryx-source-pilot-v38',
                   max_steps=50, save_steps=50, eval_steps=50)
    worker = json.loads((ROOT / plan['worker_config_path']).read_text())
    worker.update(learning_rate=request['learning_rate'], project_name=request['project_name'],
                  output_dir=str(RUN / 'adapter'))
    RUN.mkdir()
    save, phase = helpers['save'], helpers['phase']
    try:
        audit = prepare(ROOT, RUN, plan, request)
        save('batch-audit.json', audit)
        for key in ('local_datasets', 'local_eval_datasets', 'max_steps', 'save_steps', 'eval_steps'):
            worker[key] = request[key]
        save('request.json', request)
        save('worker-config.expected.json', worker)
        for side in ('base', 'current-craft'):
            for suffix in ('responses.jsonl', 'complete.json'):
                name = f'{side}.{suffix}'
                shutil.copyfile(REFERENCE / name, RUN / name)
            assert file_hash(RUN / f'{side}.responses.jsonl') == lock[
                str((REFERENCE / f'{side}.responses.jsonl').relative_to(ROOT))]
        cases = RUN / 'cases.frozen.jsonl'
        shutil.copyfile(REFERENCE / cases.name, cases)
        expected_cases = (read_jsonl(ROOT / plan['primary_cases_path'])
                          + read_jsonl(ROOT / plan['seen_cases_path']))
        assert read_jsonl(cases) == expected_cases
        plan['resource_stop']['max_steps'] = 50
        plan.update(training_steps=50, supervised_training_tokens=audit['train'][0]['supervised_tokens'],
                    context_limit=2048, status='execution-started', reference_responses_reused=98,
                    test_cases_path=str(cases.relative_to(ROOT)),
                    worker_config_path=str((RUN / 'worker-config.expected.json').relative_to(ROOT)))
        paths = [*HERE.glob('*.py'), PREVIOUS / 'decision.py', cases, RUN / 'request.json',
                 RUN / 'worker-config.expected.json', RUN / 'batch-audit.json',
                 ROOT / 'artifacts/short-fiction-v37/records.review-only.jsonl',
                 *(RUN.glob('*.tokens.jsonl')), *(RUN.glob('*.responses.jsonl'))]
        plan['input_hashes'].update(old['input_hashes'])
        plan['input_hashes'].update({str(p.relative_to(ROOT)): file_hash(p) for p in paths})
        save('protocol.frozen.json', plan)
        deadline = plan['resource_stop']['phase_deadline_seconds']
        assert plan['resource_stop'] == dict(max_steps=50, peak_mlx_gb=10,
                                           process_tree_rss_bytes=10_000_000_000,
                                           phase_deadline_seconds=1200,
                                           stop_on_warning_error_nonfinite_or_truncation=True)
        phase('training', [str(HERE / 'phase.py'), 'train'], deadline)
        phase('candidate', [str(HERE / 'phase.py'), 'evaluate', 'candidate'], deadline)
        phase('report', [str(HERE / 'phase.py'), 'report'], deadline)
        # The audit selected the tokenizer tier. Verify the default environment
        # in a separate process before the audit, and recheck file pins here.
        for name, digest in plan['input_hashes'].items():
            assert file_hash(ROOT / name) == digest, name
        writing = {}
        paragraph_cases = [c for c in expected_cases if c['kind'] == 'continue'
                           and re.search(r'\b(?:one|a) new paragraph\b', c['prompt'])]
        assert len(paragraph_cases) == 9
        for side in ('current-craft', 'candidate'):
            rows = read_jsonl(RUN / f'{side}.responses.jsonl')
            assert [r['case_id'] for r in rows] == [c['id'] for c in expected_cases]
            responses = {r['case_id']: r['text'].strip() for r in rows}
            checks = writing_checks(expected_cases, responses)
            failed = [c['id'] for c in paragraph_cases
                      if not responses[c['id']] or re.search(r'\n[ \t]*\n', responses[c['id']])]
            checks['single-paragraph continuations'] = dict(
                passed=len(paragraph_cases) - len(failed), total=len(paragraph_cases),
                failed_cases=failed)
            writing[side] = checks
        result = decide(json.loads((RUN / 'scores.json').read_text())['summary'], writing)
        save('automatic-decision.json', result)
        save('experiment-complete.json', dict(training_steps=50, new_responses=49,
                                             reused_reference_responses=98))
        print(json.dumps(result, indent=2))
    except BaseException as error:
        save('experiment-failed.json', dict(error=repr(error)))
        raise


if __name__ == '__main__':
    main()
