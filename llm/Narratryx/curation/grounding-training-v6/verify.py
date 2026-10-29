"""Read-only verification of completed experiment evidence; no quality approval."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl, validate_dataset

RUN = ROOT / 'artifacts/grounding-training-v6'
DATA = ROOT / 'artifacts/grounding-balanced-v1'


def verify():
    protocol = json.loads((RUN / 'protocol.frozen.json').read_text())
    for group in ['input_hashes', 'protected_artifacts']:
        for relative, expected in protocol[group].items():
            assert file_hash(ROOT / relative) == expected, relative
    assert file_hash(Path(protocol['base_path'])/'model.safetensors') == protocol['base_weights_sha256']
    records = validate_dataset(DATA/'records.jsonl', ROOT/'rights/grounding-balanced-v1.scoped.jsonl', ['GB', 'US'])
    assert len([r for r in records if r['split']=='train']) == 80
    assert len([r for r in records if r['split']=='validation']) == 16
    cases = read_jsonl(RUN/'cases.frozen.jsonl')
    total = 0
    for side in protocol['model_conditions']:
        rows = read_jsonl(RUN/f'{side}.responses.jsonl')
        complete = json.loads((RUN/f'{side}.complete.json').read_text())
        assert complete['completed'] and complete['cases'] == 64
        assert file_hash(RUN/f'{side}.responses.jsonl') == complete['response_sha256']
        assert [r['case_id'] for r in rows] == [c['id'] for c in cases]
        adapter = RUN/'adapter/adapters.safetensors' if side == 'candidate' else ROOT/'artifacts/craft-training-v2/adapter/adapters.safetensors'
        for row, case in zip(rows, cases):
            assert not row['error'] and row['finish_reason'] != 'length'
            assert row['prompt_sha256'] == hashlib.sha256(case['prompt'].encode()).hexdigest()
            assert row['protocol_sha256'] == file_hash(RUN/'protocol.frozen.json')
            assert row['messages_count'] == 1 and row['prior_assistant_messages'] == 0
            assert row['usage']['prompt_tokens_details']['cached_tokens'] == 0
            assert row['adapter_enabled'] == (side != 'base')
            assert row['adapter_sha256'] == file_hash(adapter)
            assert row['usage']['prompt_tokens'] + row['usage']['completion_tokens'] <= 2048
        total += len(rows)
    completion = json.loads((RUN/'completion.json').read_text())
    assert completion['completed'] and completion['steps'] == 20 and not completion['model_promoted']
    assert file_hash(RUN/'adapter/adapters.safetensors') == completion['adapter_sha256']
    progress = json.loads((RUN/'final-progress.json').read_text())
    assert not progress['error'] and not progress['warnings'] and progress['is_completed']
    assert progress['step'] == 20 and progress['num_tokens'] == 9085
    assert progress['peak_memory_gb'] is not None and progress['peak_memory_gb'] <= 10
    phase = json.loads((RUN/'training.phase.json').read_text())
    assert phase['completed'] and phase['elapsed_seconds'] <= 1200
    initial = json.loads((RUN/'service-initial.json').read_text())
    final = json.loads((RUN/'service-final.json').read_text())
    assert not final['experiment_error']
    if initial['running']:
        assert final['restored'] and final['http_ready']
    else:
        assert not final['started_by_experiment'] and final['port_free']
    assert json.loads((RUN/'experiment-complete.json').read_text())['completed']
    ballots = read_jsonl(RUN/'human-ballots.blank.jsonl')
    assert len(ballots) == 80 and all(b['preference'] is None and b['evidence'] is None and
                                    all(v is None for v in b['ratings'].values()) for b in ballots)
    previous = ROOT/'artifacts/grounding-training-v5'
    before = json.loads((previous/'request.json').read_text())
    after = json.loads((RUN/'request.json').read_text())
    assert {k for k in after if after[k] != before[k]} == {'learning_rate'}
    assert float(after['learning_rate']) == 5e-5
    assert total == 192
    assert (RUN/'blind-key.private.json').stat().st_mode & 0o777 == 0o600
    return dict(passed=True, matched_responses=total, training_steps=20,
                training_elapsed_seconds=phase['elapsed_seconds'], peak_mlx_gb=progress['peak_memory_gb'],
                frozen_inputs_unchanged=True, protected_artifacts_unchanged=True,
                base_weights_unchanged=True, initial_service_state_preserved=True,
                selected_model_unchanged=True, human_quality_ratings=0, model_promoted=False)


if __name__ == '__main__':
    report = verify()
    with (RUN/'final-verification.json').open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print(json.dumps(report, indent=2))
