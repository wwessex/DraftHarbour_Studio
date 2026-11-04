import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from foundation.experiment_evidence import verify
from foundation.validation import Invalid, file_hash


class ExperimentEvidenceTests(unittest.TestCase):
    def setUp(self):
        directory = TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.run = Path(directory.name)
        protocol = self.run / 'protocol.frozen.json'
        self.cases = self.run / 'cases.frozen.jsonl'
        self.cases.write_text(json.dumps(
            dict(id='one', prompt='Prompt', kind='continue', training_eligible=False)) + '\n')
        case_name = f'artifacts/{self.run.name}/{self.cases.name}'
        protocol.write_text(json.dumps(dict(test_cases_path=case_name,
                                            input_hashes={case_name: file_hash(self.cases),
                                                          'artifacts/craft-training-v2/adapter/adapters.safetensors': 'craft-pin'})))
        self.row = dict(case_id='one', condition='base', kind='continue', finish_reason='stop',
                        error=None, text='Complete draft.', prior_assistant_messages=0,
                        messages_count=1, usage={}, adapter_enabled=False, adapter_sha256='craft-pin',
                        protocol_sha256=file_hash(protocol),
                        prompt_sha256=hashlib.sha256(b'Prompt').hexdigest())

    def stamp(self):
        responses = self.run / 'base.responses.jsonl'
        responses.write_text(json.dumps(self.row) + '\n')
        (self.run / 'base.complete.json').write_text(json.dumps(dict(
            completed=True, cases=1, response_sha256=file_hash(responses),
            models_unloaded=True, adapter_unchanged=True)))

    def test_valid_evidence(self):
        self.stamp()
        self.assertEqual(verify(self.run, ['base'])['conditions']['base']['cases'], 1)

    def test_tampering_after_completion_is_rejected(self):
        self.stamp()
        (self.run / 'base.responses.jsonl').write_text('{}')
        with self.assertRaises(Invalid):
            verify(self.run, ['base'])

    def test_bad_metadata_is_rejected_even_with_a_matching_stamp(self):
        original = self.row.copy()
        for change in (dict(finish_reason='length'), dict(prompt_sha256='changed'),
                       dict(prior_assistant_messages=1), dict(adapter_enabled=True),
                       dict(adapter_sha256='wrong-adapter'),
                       dict(usage={'prompt_tokens_details': {'cached_tokens': 3}})):
            with self.subTest(change=change):
                self.row = dict(original, **change)
                self.stamp()
                with self.assertRaises(Invalid):
                    verify(self.run, ['base'])


    def test_changed_frozen_cases_are_rejected(self):
        self.stamp()
        self.cases.write_text(self.cases.read_text().replace('Prompt', 'Changed prompt'))
        with self.assertRaises(Invalid):
            verify(self.run, ['base'])
