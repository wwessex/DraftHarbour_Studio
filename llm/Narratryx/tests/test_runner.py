"""Offline orchestration tests. All release approvals here are invented fixtures."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import test_foundation as fixtures
from foundation import runner
from foundation.evaluation import freeze
from foundation.validation import Invalid, ROOT, digest, file_hash, read_json, read_jsonl


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.FoundationTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        f = self.fixture
        f.validate()
        for task in f.tasks:
            task['review'] = copy.deepcopy(fixtures.APPROVED_TEST_ONLY)
        f.dump(f.task_path, f.tasks)
        self.lock = f.base / 'benchmark.lock.json'
        freeze(f.task_path, self.lock, f.rubric_path)
        self.config = read_json(ROOT / 'configs/offline-runner.json')
        self.config.update({'ledger': str(f.ledger_path), 'dataset': str(f.dataset_path),
                            'tasks': str(f.task_path), 'lock': str(self.lock),
                            'rubric': str(f.rubric_path), 'prepare_austen': None})
        self.config_path = f.base / 'config.json'
        self.output = f.base / 'run'
        self.save_config()

    def save_config(self):
        self.config_path.write_text(json.dumps(self.config))

    def run_pipeline(self):
        return runner.run(self.config_path, self.output)

    def add_response_run(self, side):
        f = self.fixture
        response_path, run_path = f.base / f'{side}.jsonl', f.base / f'{side}.run.json'
        f.dump(response_path, [f.response(t) for t in f.tasks])
        metadata = f.run_meta()
        metadata.update({'run_id': side, 'artifact_sha256': ('a' if side == 'baseline' else 'b') * 64})
        run_path.write_text(json.dumps(metadata))
        self.config[side] = {'responses': str(response_path), 'run': str(run_path)}
        self.save_config()
        return response_path, run_path

    def test_released_fixture_exports_messages_only_without_training(self):
        report = self.run_pipeline()
        self.assertEqual(report['status'], 'offline-stages-complete')
        self.assertFalse(report['training_started'])
        self.assertEqual(report['jobs_submitted'], 0)
        train = read_jsonl(self.output / 'bundle/train.jsonl')
        self.assertEqual(train, [{'messages': self.fixture.record['messages']}])
        prompts = read_jsonl(self.output / 'bundle/prompts.jsonl')
        self.assertEqual(set(prompts[0]), {'task_id', 'messages'})
        self.assertEqual(read_json(self.output / 'bundle/job-plan.json')['model'], None)

    def test_resume_preserves_completed_artifacts(self):
        self.run_pipeline()
        path = self.output / 'bundle/train.jsonl'
        before = (file_hash(path), path.stat().st_mtime_ns)
        self.run_pipeline()
        self.assertEqual(before, (file_hash(path), path.stat().st_mtime_ns))

    def test_validation_split_is_not_exported_for_training(self):
        f = self.fixture
        rights = copy.deepcopy(f.rights)
        rights.update({'id': 'validation-rights', 'work_id': 'validation-work',
                       'author_ids': ['validation-author']})
        row = copy.deepcopy(f.record)
        row.update({'id': 'held-out', 'split': 'validation', 'split_group': 'held-out-group',
                    'rights_record_ids': ['validation-rights'], 'source_work_ids': ['validation-work'],
                    'messages': [{'role': 'user', 'content': 'Invent a different image.'},
                                 {'role': 'assistant', 'content': 'Snow hid the last footprint.'}]})
        row['content_hash'] = digest(row['messages'])
        f.dump(f.ledger_path, [f.rights, rights])
        f.dump(f.dataset_path, [f.record, row])
        self.assertEqual(self.run_pipeline()['status'], 'offline-stages-complete')
        exported = read_jsonl(self.output / 'bundle/train.jsonl')
        self.assertEqual(exported, [{'messages': f.record['messages']}])

    def test_different_inputs_require_new_run(self):
        self.run_pipeline()
        self.config['training']['max_steps'] += 1
        self.save_config()
        with self.assertRaisesRegex(Invalid, 'inputs changed'):
            self.run_pipeline()

    def test_raw_source_changes_invalidate_resume(self):
        self.run_pipeline()
        (self.fixture.base / 'source.txt').write_text('changed')
        with self.assertRaisesRegex(Invalid, 'inputs changed'):
            self.run_pipeline()

    def test_completed_output_tampering_is_rejected(self):
        self.run_pipeline()
        (self.output / 'bundle/train.jsonl').write_text('changed')
        with self.assertRaisesRegex(Invalid, 'output changed'):
            self.run_pipeline()

    def test_collects_independent_gates_without_approving(self):
        f = self.fixture
        f.rights['unresolved_issues'] = ['INVENTED pending evidence']
        f.record['review']['status'] = 'pending'
        f.tasks[0]['review']['status'] = 'pending'
        f.dump(f.ledger_path, [f.rights])
        f.dump(f.dataset_path, [f.record])
        f.dump(f.task_path, f.tasks)
        before = {p: file_hash(p) for p in (f.ledger_path, f.dataset_path, f.task_path)}
        report = self.run_pipeline()
        self.assertEqual(report['status'], 'blocked')
        self.assertEqual({b['gate'] for b in report['blockers']},
                         {'source:test-rights', 'frozen-benchmark', 'dataset-release'})
        self.assertFalse((self.output / 'bundle').exists())
        self.assertEqual(before, {p: file_hash(p) for p in before})

    def test_paid_flag_cannot_enable_execution(self):
        self.config['paid_execution_enabled'] = True
        self.save_config()
        with self.assertRaises(Invalid):
            self.run_pipeline()
        self.assertFalse(self.output.exists())

    def test_lock_prevents_concurrent_run(self):
        with runner.run_lock(self.output):
            with self.assertRaisesRegex(Invalid, 'another runner'):
                self.run_pipeline()

    def test_recovery_from_interruption_before_state_commit(self):
        save = runner.atomic_json
        calls = 0

        def interrupt_stage_commit(path, value):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError('simulated interruption')
            save(path, value)

        with patch.object(runner, 'atomic_json', side_effect=interrupt_stage_commit):
            with self.assertRaises(OSError):
                self.run_pipeline()
        self.assertTrue((self.output / 'bundle/train.jsonl').exists())
        self.assertEqual(read_json(self.output / 'state.json')['stages'], {})
        self.assertEqual(self.run_pipeline()['status'], 'offline-stages-complete')

    def test_unowned_output_directory_is_preserved(self):
        self.output.mkdir()
        bundle = self.output / 'bundle'
        bundle.mkdir()
        important = bundle / 'existing.txt'
        important.write_text('keep this')
        with self.assertRaisesRegex(Invalid, 'nonempty run directory'):
            self.run_pipeline()
        self.assertEqual(important.read_text(), 'keep this')

    def test_output_cannot_contain_inputs(self):
        with self.assertRaisesRegex(Invalid, 'separate from all inputs'):
            runner.run(self.config_path, self.fixture.base)

    def test_scores_and_prepares_blind_comparison(self):
        self.add_response_run('baseline')
        self.add_response_run('candidate')
        report = self.run_pipeline()
        self.assertTrue(report['evaluation']['comparison_ready'])
        self.assertEqual(report['promotion'], 'disabled')
        key = read_json(self.output / 'evaluation/private-key.json')
        self.assertEqual(key['runs']['left']['run_id'], 'baseline')
        self.assertEqual(len(read_jsonl(self.output / 'evaluation/review.jsonl')), 2)

    def test_unfair_comparison_blocks_without_partial_publication(self):
        self.add_response_run('baseline')
        _, path = self.add_response_run('candidate')
        metadata = read_json(path)
        metadata['generation']['temperature'] = 0.9
        path.write_text(json.dumps(metadata))
        report = self.run_pipeline()
        self.assertEqual(report['blockers'][0]['gate'], 'imported-evaluation')
        self.assertFalse((self.output / 'evaluation').exists())

    def test_missing_responses_are_counted_as_failures(self):
        path, _ = self.add_response_run('baseline')
        self.fixture.dump(path, [self.fixture.response(self.fixture.tasks[0])])
        self.run_pipeline()
        report = read_json(self.output / 'evaluation/baseline.score.json')
        self.assertEqual(report['missing_responses'], 1)

    def test_recipe_refuses_execution_before_ml_imports(self):
        process = subprocess.run([sys.executable, str(ROOT / 'training/unsloth_sft.py'),
                                  '--plan', 'missing.json', '--output', 'missing'], capture_output=True, text=True)
        self.assertEqual(process.returncode, 2)
        self.assertIn('requires --execute', process.stderr)
        self.assertNotIn('ModuleNotFoundError', process.stderr)

    def test_recipe_checks_source_hash_and_model_review(self):
        self.run_pipeline()
        spec = importlib.util.spec_from_file_location('recipe', ROOT / 'training/unsloth_sft.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        bundle = self.output / 'bundle'
        plan = read_json(bundle / 'job-plan.json')
        with self.assertRaisesRegex(ValueError, 'reviewed base model'):
            module.check_plan(plan, bundle / 'train.jsonl', bundle / 'unsloth_sft.py')
        (bundle / 'train.jsonl').write_text('changed')
        with self.assertRaisesRegex(ValueError, 'file hash mismatch'):
            module.check_plan(plan, bundle / 'train.jsonl', bundle / 'unsloth_sft.py')
