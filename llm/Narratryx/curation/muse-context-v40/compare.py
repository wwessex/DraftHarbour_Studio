"""Run the current craft adapter on the frozen development screen."""
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RUN = ROOT / 'artifacts/muse-context-v40/comparison'
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
    captured = RUN.parent / 'shared-context.json'
    fixture = HERE / 'project.json'
    cases = []
    for item in json.loads(captured.read_text()):
        for condition in ('oracle', 'references'):
            cases.append(dict(id=f"{item['id']}-{condition}", skill=item['action'],
                              prompt=item['brief'] + '\n\nCURRENT PASSAGE:\n' + item['chapter']
                              + '\n\nSTORY CONTEXT:\n' + item[condition]))
    assert len(cases) == 6
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
    paths = (fixture, captured, Path(__file__), path,
             PREVIOUS / 'evaluate.py', ROOT / 'runtime/local/engine.py')
    plan['input_hashes'].update({str(p.relative_to(ROOT)): file_hash(p) for p in paths})
    plan.update(test_cases_path=str(path.relative_to(ROOT)), context_limit=2048,
                status='oracle-versus-shared-reference-comparison')
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
