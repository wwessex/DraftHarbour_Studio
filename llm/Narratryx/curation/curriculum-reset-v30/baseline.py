"""Run the current craft adapter on the frozen development screen."""
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/curriculum-reset-v30-baseline'
PREVIOUS = ROOT / 'curation/source-training-v26'
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl


def main():
    assert __debug__
    if sys.argv[1:] == ['--evaluate']:
        evaluate = runpy.run_path(str(PREVIOUS / 'evaluate.py'))['main']
        evaluate.__globals__['RUN'] = RUN
        sys.argv[1:] = ['current-craft']
        evaluate()
        return
    assert not RUN.exists()
    frozen = json.loads((HERE / 'fresh-screen.lock.json').read_text())
    screen = ROOT / frozen['path']
    assert file_hash(screen) == frozen['sha256']
    cases = read_jsonl(screen)
    assert len(cases) == frozen['cases'] == len({c['id'] for c in cases}) == 12
    assert all(c['training_eligible'] is False for c in cases)
    previous = runpy.run_path(str(PREVIOUS / 'run.py'))
    plan = previous['load_plan']()
    previous['verify_inputs'](plan)
    helpers = runpy.run_path(str(previous['HELPERS']))
    helpers['phase'].__globals__.update(RUN=RUN, PYTHON=Path(sys.executable))
    if not helpers['port_free']():
        raise RuntimeError('Port 8890 is occupied')
    RUN.mkdir()
    path = RUN / 'cases.frozen.jsonl'
    with path.open('x') as stream:
        for case in cases:
            stream.write(json.dumps(dict(case, kind=case['skill']), ensure_ascii=False) + '\n')
    paths = (screen, HERE / 'fresh-screen.lock.json', Path(__file__), path,
             PREVIOUS / 'evaluate.py', ROOT / 'runtime/local/engine.py')
    plan['input_hashes'].update({str(p.relative_to(ROOT)): file_hash(p) for p in paths})
    plan.update(test_cases_path=str(path.relative_to(ROOT)), context_limit=2048,
                status='development-screen-baseline')
    helpers['save']('protocol.frozen.json', plan)
    helpers['phase']('current-craft', [str(Path(__file__)), '--evaluate'], 1200)
    output = RUN / 'current-craft.responses.jsonl'
    rows = read_jsonl(output)
    assert [r['case_id'] for r in rows] == [c['id'] for c in cases]
    assert all(r['finish_reason'] == 'stop' and not r['error'] and
               r['prior_assistant_messages'] == 0 and
               r['usage']['prompt_tokens_details']['cached_tokens'] == 0 for r in rows)
    marker = json.loads((RUN / 'current-craft.complete.json').read_text())
    assert file_hash(output) == marker['response_sha256']
    helpers['save']('baseline.json', dict(responses=len(rows), fresh_context=True,
                                        response_sha256=file_hash(output),
                                        training_eligible=False))


if __name__ == '__main__':
    main()
