"""Phase 1 tests use invented temporary evidence; no fixture grants real rights."""

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from foundation.evaluation import (benchmark, blind, freeze, objective, responses,
                                    score, summarize_reviews, write_new)
from foundation.validation import (Invalid, ROOT, check_leakage, clear_source, digest,
                                  file_hash, load_ledger, read_jsonl, validate_dataset,
                                  validate_schema)


APPROVED_TEST_ONLY = {'status': 'approved', 'reviewer': 'INVENTED TEST FIXTURE REVIEWER',
                      'reviewed_on': '2026-10-17', 'notes': 'Temporary test data only; not legal clearance.'}


class FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.ledger_path = self.base / 'ledger.jsonl'
        self.dataset_path = self.base / 'dataset.jsonl'
        self.raw = 'Mara quietly closed the door.'
        (self.base / 'source.txt').write_text(self.raw)
        self.rights = copy.deepcopy(load_ledger(ROOT / 'rights' / 'ledger.jsonl')['original-seed-pending'])
        self.rights.update({'id': 'test-rights', 'work_id': 'test-work', 'author_ids': ['test-author'],
                            'review': copy.deepcopy(APPROVED_TEST_ONLY), 'unresolved_issues': []})
        self.rights['source'].update({'retrieved_on': '2026-10-17', 'revision': 'test-1',
                                     'raw_path': 'source.txt', 'sha256': file_hash(self.base / 'source.txt'),
                                     'included_material': 'entire invented sentence',
                                     'terms_evidence': ['https://example.invalid/test-only'],
                                     'terms_decision': 'Invented fixture; never use as real evidence.'})
        self.rights['clearances'] = [{'jurisdiction': j, 'basis': 'Invented test-only approval',
                                     'uses': ['training', 'evaluation'],
                                     'evidence': ['https://example.invalid/test-only']} for j in ('GB', 'US')]
        self.record = {'schema_version': '1.0', 'id': 'test-record', 'dataset_version': 'test-1',
                       'task': 'editing', 'split': 'train', 'split_group': 'test-group',
                       'origin': 'human', 'messages': [{'role': 'user', 'content': self.raw},
                                                     {'role': 'assistant', 'content': 'Mara closed the door.'}],
                       'source_work_ids': ['test-work'], 'rights_record_ids': ['test-rights'],
                       'source_spans': [], 'teacher': None, 'review': copy.deepcopy(APPROVED_TEST_ONLY),
                       'rubric': ['Preserve meaning.']}
        self.record['content_hash'] = digest(self.record['messages'])
        self.tasks = copy.deepcopy(benchmark(ROOT / 'evaluation/tasks.draft.jsonl', allow_draft=True)[:2])
        self.task_path = self.base / 'tasks.jsonl'
        self.dump(self.task_path, self.tasks)
        rubric = json.loads((ROOT / 'evaluation/rubric.json').read_text())
        rubric['review'] = APPROVED_TEST_ONLY
        self.rubric_path = self.base / 'rubric.json'
        self.rubric_path.write_text(json.dumps(rubric))

    def dump(self, path, rows):
        path.write_text(''.join(json.dumps(row) + '\n' for row in rows))

    def validate(self, rows=None):
        self.dump(self.ledger_path, [self.rights])
        self.dump(self.dataset_path, [self.record] if rows is None else rows)
        return validate_dataset(self.dataset_path, self.ledger_path, ['GB', 'US'])

    def response(self, task, text='answer', error=None):
        return {'schema_version': '1.0', 'task_id': task['id'], 'text': text, 'error': error,
                'latency_ms': 100, 'completion_tokens': 1}

    def run_meta(self):
        return {'schema_version': '1.0', 'run_id': 'fixture-run', 'model': 'fixture',
                'model_revision': 'fixture-revision', 'tokenizer_revision': 'fixture-tokenizer',
                'prompt_version': 'v1', 'runtime': 'offline-test',
                'generation': {'temperature': 0, 'max_tokens': 200, 'seed': 42},
                'artifact_sha256': 'a' * 64, 'benchmark_sha256': file_hash(self.task_path)}

    def test_all_schemas_are_valid(self):
        from jsonschema import Draft202012Validator
        for path in (ROOT / 'schemas').glob('*.json'):
            Draft202012Validator.check_schema(json.loads(path.read_text()))

    def test_pending_status_blocks_release_even_with_complete_evidence(self):
        # Decisions in the real ledger legitimately change after human review.
        # Exercise the gate using invented evidence, not a frozen approval count.
        row = copy.deepcopy(self.rights)
        row['review'] = {'status': 'pending', 'reviewer': None,
                         'reviewed_on': None, 'notes': 'Pending test-only review.'}
        with self.assertRaisesRegex(Invalid, 'not approved'):
            clear_source(row, self.ledger_path, ['GB', 'US'], 'training')

    def test_pending_example_is_structurally_valid_but_not_approved(self):
        row = read_jsonl(ROOT / 'data/phase1-example.pending.jsonl')[0]
        validate_schema(row, 'dataset-record')
        self.assertEqual(row['content_hash'], digest(row['messages']))
        with self.assertRaisesRegex(Invalid, 'not approved'):
            validate_dataset(ROOT / 'data/phase1-example.pending.jsonl', ROOT / 'rights/ledger.jsonl', ['GB', 'US'])

    def test_valid_invented_provenance(self):
        self.assertEqual(len(self.validate()), 1)

    def test_approval_requires_named_reviewer_and_date(self):
        for field in ('reviewer', 'reviewed_on'):
            rights = copy.deepcopy(self.rights)
            rights['review'][field] = None
            with self.assertRaises(Invalid):
                validate_schema(rights, 'rights-record')

    def test_unknown_fields_and_bad_dates_rejected(self):
        for mutation in ({'unknown': True}, {'review': {**APPROVED_TEST_ONLY, 'reviewed_on': '2026-99-99'}}):
            with self.assertRaises(Invalid):
                validate_schema({**self.rights, **mutation}, 'rights-record')

    def test_pending_rights_cannot_be_bypassed_by_approved_sample(self):
        self.rights['review']['status'] = 'pending'
        with self.assertRaisesRegex(Invalid, 'not approved'):
            self.validate()

    def test_missing_jurisdiction_and_use_rejected(self):
        self.rights['clearances'].pop()
        with self.assertRaisesRegex(Invalid, 'US'):
            self.validate()
        self.rights['clearances'][0]['uses'] = ['evaluation']
        with self.assertRaisesRegex(Invalid, 'training'):
            self.validate()

    def test_unresolved_issues_rejected(self):
        self.rights['unresolved_issues'] = ['Unknown translator']
        with self.assertRaisesRegex(Invalid, 'unresolved'):
            self.validate()

    def test_source_hash_tamper_and_missing_file_rejected(self):
        (self.base / 'source.txt').write_text('Changed source')
        with self.assertRaisesRegex(Invalid, 'hash mismatch'):
            self.validate()
        (self.base / 'source.txt').unlink()
        with self.assertRaises(OSError):
            self.validate()

    def test_raw_path_cannot_escape_ledger_directory(self):
        self.rights['source']['raw_path'] = '../outside.txt'
        with self.assertRaisesRegex(Invalid, 'inside'):
            self.validate()

    def test_public_domain_needs_edition_evidence(self):
        self.rights['source_kind'] = 'public_domain_candidate'
        with self.assertRaisesRegex(Invalid, 'edition'):
            self.validate()

    def test_unknown_rights_and_work_mismatch_rejected(self):
        self.record['rights_record_ids'] = ['unknown']
        with self.assertRaisesRegex(Invalid, 'unknown rights'):
            self.validate()
        self.record['rights_record_ids'] = ['test-rights']
        self.record['source_work_ids'] = ['wrong-work']
        with self.assertRaisesRegex(Invalid, 'work IDs'):
            self.validate()

    def test_source_span_uses_actual_unicode_offsets(self):
        self.record['source_spans'] = [{'rights_record_id': 'test-rights', 'start': 0,
                                      'end': len(self.raw), 'text': self.raw}]
        self.validate()
        self.record['source_spans'][0]['start'] = 1
        with self.assertRaisesRegex(Invalid, 'span mismatch'):
            self.validate()

    def test_message_hash_and_turn_order_rejected(self):
        self.record['messages'][0]['content'] += ' tampered'
        with self.assertRaisesRegex(Invalid, 'content hash'):
            self.validate()
        self.record['messages'][0]['role'] = 'assistant'
        self.record['content_hash'] = digest(self.record['messages'])
        with self.assertRaisesRegex(Invalid, 'alternating'):
            self.validate()

    def test_synthetic_examples_need_teacher_terms(self):
        self.record['origin'] = 'synthetic'
        with self.assertRaisesRegex(Invalid, 'teacher'):
            self.validate()

    def test_synthetic_teacher_terms_need_separate_approval(self):
        seed = read_jsonl(ROOT / 'data/phase1-example.pending.jsonl')[0]
        self.record['origin'] = 'synthetic'
        self.record['teacher'] = seed['teacher']
        with self.assertRaisesRegex(Invalid, 'teacher terms.*not approved'):
            self.validate()

    def test_public_domain_requires_exact_source_span(self):
        self.rights['source_kind'] = 'public_domain_candidate'
        self.rights['publication'] = {'original_year': 1800, 'edition': 'invented fixture',
                                      'publisher': 'invented fixture',
                                      'evidence': ['https://example.invalid/test-only']}
        self.rights['source']['url'] = 'https://example.invalid/test-only'
        for contributor in self.rights['contributors']:
            contributor['life_dates'] = 'Invented fixture dates; no legal assertion'
        with self.assertRaisesRegex(Invalid, 'exact raw-text span'):
            self.validate()
        self.record['source_spans'] = [{'rights_record_id': 'test-rights', 'start': 0,
                                      'end': len(self.raw), 'text': self.raw}]
        self.validate()

    def test_duplicate_ids_and_json_keys_fail_closed(self):
        with self.assertRaisesRegex(Invalid, 'duplicate'):
            self.validate([self.record, self.record])
        path = self.base / 'bad.jsonl'
        path.write_text('{"id":"first","id":"second"}\n')
        with self.assertRaisesRegex(Invalid, 'duplicate JSON key'):
            read_jsonl(path)

    def test_blank_empty_and_nan_jsonl_rejected(self):
        path = self.base / 'bad.jsonl'
        for text in ('', '\n', '{"latency_ms":NaN}\n'):
            path.write_text(text)
            with self.assertRaises(Invalid):
                read_jsonl(path)

    def test_group_work_and_author_leakage_rejected(self):
        for shared in ('split_group', 'source_work_ids', '_author_ids'):
            left = {**self.record, '_author_ids': ['author-a']}
            right = copy.deepcopy(left)
            right.update({'id': 'other', 'split': 'test', 'split_group': 'other-group',
                          'source_work_ids': ['other-work'], '_author_ids': ['author-b']})
            right[shared] = left[shared]
            with self.assertRaisesRegex(Invalid, 'cross-split'):
                check_leakage([left, right])

    def test_near_duplicate_and_benchmark_leakage_rejected(self):
        text = ' '.join(f'word{i}' for i in range(60))
        left = {**self.record, 'messages': [{'role': 'user', 'content': text}]}
        right = {**left, 'id': 'other', 'split': 'test', 'split_group': 'other',
                 'source_work_ids': ['other-work'],
                 'messages': [{'role': 'user', 'content': text + ' additional ending'}]}
        with self.assertRaisesRegex(Invalid, 'near-duplicate'):
            check_leakage([left, right])
        task = {**self.tasks[0], 'context': text}
        with self.assertRaisesRegex(Invalid, 'near-duplicate'):
            check_leakage([left], [task])

    def test_draft_pack_is_balanced_and_not_frozen(self):
        tasks = benchmark(ROOT / 'evaluation/tasks.draft.jsonl', allow_draft=True)
        self.assertEqual(len(tasks), 120)
        self.assertEqual(len({t['scenario_id'] for t in tasks}), 20)
        self.assertEqual({k: sum(t['task'] == k for t in tasks) for k in
                          ('fiction', 'editing', 'analysis', 'dialogue', 'pacing', 'storytelling')},
                         dict.fromkeys(('fiction', 'editing', 'analysis', 'dialogue', 'pacing', 'storytelling'), 20))
        with self.assertRaisesRegex(Invalid, 'not approved'):
            freeze(ROOT / 'evaluation/tasks.draft.jsonl', self.base / 'lock.json')
        self.assertFalse((self.base / 'lock.json').exists())

    def test_frozen_benchmark_detects_changes_and_refuses_overwrite(self):
        for task in self.tasks:
            task['review'] = APPROVED_TEST_ONLY
        self.dump(self.task_path, self.tasks)
        lock = self.base / 'lock.json'
        freeze(self.task_path, lock, self.rubric_path)
        benchmark(self.task_path, lock, rubric=self.rubric_path)
        with self.assertRaises(FileExistsError):
            freeze(self.task_path, lock, self.rubric_path)
        self.tasks[0]['prompt'] += ' changed'
        self.dump(self.task_path, self.tasks)
        with self.assertRaisesRegex(Invalid, 'lock mismatch'):
            benchmark(self.task_path, lock, rubric=self.rubric_path)

    def test_freeze_requires_approved_editorial_rubric(self):
        for task in self.tasks:
            task['review'] = APPROVED_TEST_ONLY
        self.dump(self.task_path, self.tasks)
        with self.assertRaisesRegex(Invalid, 'editorial rubric.*not approved'):
            freeze(self.task_path, self.base / 'lock.json')

    def test_exact_quotes_and_line_checks(self):
        self.assertTrue(objective({'type': 'exact', 'value': 'Mara.'}, 'Mara.', ''))
        self.assertFalse(objective({'type': 'exact', 'value': 'Mara.'}, 'Mara.\n', ''))
        self.assertTrue(objective({'type': 'quotes_from_context', 'min_quotes': 2},
                                  '“quietly” and "door"', self.raw))
        self.assertFalse(objective({'type': 'quotes_from_context', 'min_quotes': 2},
                                   '"quietly" and "quietly"', self.raw))
        self.assertFalse(objective({'type': 'quotes_from_context', 'min_quotes': 1},
                                   '"invented quote"', self.raw))
        self.assertTrue(objective({'type': 'line_count', 'min': 2, 'max': 2}, 'one\n\ntwo', ''))
        self.assertFalse(objective({'type': 'json'}, 'NaN', ''))

    def test_missing_empty_and_error_responses_are_failures(self):
        for rows in ({}, {self.tasks[0]['id']: self.response(self.tasks[0], '')},
                     {self.tasks[0]['id']: self.response(self.tasks[0], 'text', 'timeout')}):
            report = score(self.tasks, rows, self.run_meta(), self.task_path, True)
            self.assertEqual(report['objective_pass_rate'], 0)
            self.assertEqual(report['promotion'], 'not assessed')

    def test_metadata_must_match_benchmark(self):
        run = self.run_meta()
        run['benchmark_sha256'] = 'b' * 64
        with self.assertRaisesRegex(Invalid, 'different benchmark'):
            score(self.tasks, {}, run, self.task_path)

    def test_valid_objective_pass_remains_distinct_from_literary_quality(self):
        self.tasks[0]['checks'] = [{'type': 'exact', 'value': 'expected'}]
        self.dump(self.task_path, self.tasks)
        rows = {t['id']: self.response(t, 'expected') for t in self.tasks}
        report = score(self.tasks, rows, self.run_meta(), self.task_path, True)
        self.assertTrue(report['results'][0]['passed'])
        self.assertEqual(report['promotion'], 'not assessed')
        self.assertIn('human review', report['literary_quality'])

    def test_response_ids_must_be_unique_and_known(self):
        path = self.base / 'responses.jsonl'
        row = self.response(self.tasks[0])
        self.dump(path, [row, row])
        with self.assertRaisesRegex(Invalid, 'duplicate'):
            responses(path, self.tasks)
        self.dump(path, [{**row, 'task_id': 'unknown'}])
        with self.assertRaisesRegex(Invalid, 'unknown'):
            responses(path, self.tasks)

    def test_blind_review_is_reproducible_and_does_not_expose_models(self):
        left = {t['id']: self.response(t, 'left answer') for t in self.tasks}
        right = {t['id']: self.response(t, 'right answer') for t in self.tasks}
        packet, key = blind(self.tasks, left, right, 42)
        self.assertEqual((packet, key), blind(self.tasks, left, right, 42))
        self.assertNotIn('assignments', json.dumps(packet))
        self.assertTrue(all(set(p['answers']) == {'A', 'B'} for p in packet))
        with self.assertRaisesRegex(Invalid, 'exactly one'):
            blind(self.tasks, {}, right, 42)

    def test_review_report_rejects_duplicate_ballots_and_tampered_packet(self):
        rows = {t['id']: self.response(t) for t in self.tasks}
        packet, key = blind(self.tasks, rows, rows, 42)
        ballot = {'task_id': self.tasks[0]['id'], 'reviewer': 'reviewer', 'choice': 'tie',
                  'rationale': 'Equivalent on this task.', 'ratings': {'A': 3, 'B': 3}}
        report = summarize_reviews(self.tasks, packet, key, [ballot])
        self.assertEqual(report['right_win_rate_ties_half'], .5)
        self.assertEqual(report['reviewed_tasks'], 1)
        self.assertEqual(len(report['missing_task_ids']), 1)
        self.assertIsNone(report['scenario_bootstrap_95_ci'])
        with self.assertRaisesRegex(Invalid, 'duplicate'):
            summarize_reviews(self.tasks, packet, key, [ballot, {**ballot, 'reviewer': ' REVIEWER '}])
        packet[0]['prompt'] += ' changed'
        with self.assertRaisesRegex(Invalid, 'hash mismatch'):
            summarize_reviews(self.tasks, packet, key, [ballot])

    def test_review_interval_uses_scenarios_and_reports_review_coverage(self):
        self.tasks[1]['scenario_id'] = 'second-scenario'
        rows = {t['id']: self.response(t) for t in self.tasks}
        packet, key = blind(self.tasks, rows, rows, 10)
        ballots = []
        for task in self.tasks:
            label = next(k for k, v in key['assignments'][task['id']].items() if v == 'right')
            for reviewer in ('one', 'two'):
                ballots.append({'task_id': task['id'], 'reviewer': reviewer, 'choice': label,
                                'rationale': 'Invented evaluation fixture.', 'ratings': {'A': 3, 'B': 3}})
        report = summarize_reviews(self.tasks, packet, key, ballots)
        self.assertEqual(report['reviewed_scenarios'], 2)
        self.assertEqual(report['tasks_with_two_reviewers'], 2)
        self.assertEqual(report['right_win_rate_ties_half'], 1)
        self.assertEqual(report['scenario_bootstrap_95_ci'], [1, 1])

    def test_full_cli_import_score_blind_and_review_flow(self):
        for task in self.tasks:
            task['review'] = APPROVED_TEST_ONLY
        self.dump(self.task_path, self.tasks)
        lock = self.base / 'frozen.json'
        freeze(self.task_path, lock, self.rubric_path)
        cmd = [sys.executable, '-m', 'foundation']
        common = ['--tasks', str(self.task_path), '--lock', str(lock), '--rubric', str(self.rubric_path)]
        for side in ('left', 'right'):
            self.dump(self.base / f'{side}.jsonl', [self.response(t) for t in self.tasks])
            run = {**self.run_meta(), 'run_id': side}
            (self.base / f'{side}.run.json').write_text(json.dumps(run))
        def invoke(arguments):
            result = subprocess.run(cmd + arguments, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.validate()
        validation = invoke(['validate-dataset', str(self.dataset_path), '--ledger', str(self.ledger_path),
                             '--jurisdictions', 'GB', 'US', '--benchmark', str(self.task_path),
                             '--lock', str(lock), '--rubric', str(self.rubric_path),
                             '--output', str(self.base / 'dataset.validation.json')])
        self.assertEqual(validation['records'], 1)
        self.assertFalse(validation['legal_certification'])
        report = invoke(['score', *common, '--responses', str(self.base / 'left.jsonl'),
                         '--run', str(self.base / 'left.run.json'),
                         '--output', str(self.base / 'objective.json')])
        self.assertEqual(report['task_count'], 2)
        directory = self.base / 'comparison'
        invoke(['blind', *common, '--left', str(self.base / 'left.jsonl'),
                '--left-run', str(self.base / 'left.run.json'), '--right', str(self.base / 'right.jsonl'),
                '--right-run', str(self.base / 'right.run.json'), '--output-dir', str(directory)])
        self.dump(self.base / 'ballots.jsonl', [{'task_id': t['id'], 'reviewer': 'test-only',
                  'choice': 'tie', 'rationale': 'Equivalent fixtures.', 'ratings': {'A': 3, 'B': 3}}
                  for t in self.tasks])
        report = invoke(['review-report', *common, '--packet', str(directory / 'review.jsonl'),
                         '--key', str(directory / 'private-key.json'), '--ballots', str(self.base / 'ballots.jsonl'),
                         '--output', str(self.base / 'review-report.json')])
        self.assertEqual(report['right_win_rate_ties_half'], .5)
        self.assertFalse(report['draft_benchmark'])

    def test_cli_is_offline_and_refuses_pending_freeze(self):
        output = self.base / 'prompts.jsonl'
        cmd = [sys.executable, '-m', 'foundation']
        result = subprocess.run(cmd + ['export-prompts', '--tasks', str(self.task_path),
                                      '--allow-draft', '--output', str(output)], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['inference_calls'], 0)
        self.assertNotIn('rubric', output.read_text())
        self.assertNotIn('checks', output.read_text())
        result = subprocess.run(cmd + ['freeze', '--tasks', str(self.task_path),
                                      '--output', str(self.base / 'lock.json')], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertFalse((self.base / 'lock.json').exists())


if __name__ == '__main__':
    unittest.main()
