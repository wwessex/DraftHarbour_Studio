import importlib.util
import unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'curation/mixed-training-v16/scoring.py'
S=importlib.util.spec_from_file_location('mixed16_scoring',P)
M=importlib.util.module_from_spec(S);S.loader.exec_module(M)


class MixedClosedScoringTests(unittest.TestCase):
    def test_correct_object_and_boolean_state(self):
        self.assertTrue(M.strict_json_match('{"unknown_object":"duplicate","original_readable":true}',dict(unknown_object='duplicate',original_readable=True)))

    def test_integer_one_is_not_a_boolean(self):
        self.assertFalse(M.strict_json_match('{"allowed":1}',dict(allowed=True)))

    def test_duplicate_and_unknown_keys_rejected(self):
        for text in ['{"state":"overdue","state":"not_yet_due"}','{"state":"not_yet_due","extra":0}']:
            self.assertFalse(M.strict_json_match(text,dict(state='not_yet_due')))

    def test_nonfinite_float_and_explanation_rejected(self):
        for text in ['{"minutes":NaN}','{"minutes":35.0}','Here is JSON: {"minutes":35}']:
            self.assertFalse(M.strict_json_match(text,dict(minutes=35)))
