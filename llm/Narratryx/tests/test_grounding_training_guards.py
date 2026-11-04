import importlib.util
from pathlib import Path
import unittest

HERE=Path(__file__).resolve().parents[1]/'curation/grounding-training-v5'
def module(name):
    spec=importlib.util.spec_from_file_location('grounding_v5_'+name,HERE/(name+'.py'))
    loaded=importlib.util.module_from_spec(spec);spec.loader.exec_module(loaded);return loaded
GUARDS=module('guards')
SCORE=module('scoring')


class GroundingTrainingGuardsTests(unittest.TestCase):
    def test_twentieth_update_allowed_twentyfirst_stops(self):
        self.assertIsNone(GUARDS.resource_violation(dict(step=20,peak_memory_gb=10,loss=1.0)))
        self.assertIsNotNone(GUARDS.resource_violation(dict(step=21)))

    def test_memory_warning_error_and_nonfinite_stop(self):
        for p in [dict(peak_memory_gb=10.1),dict(loss=float('nan')),dict(warnings=['unsupported']),dict(error='failed')]:
            with self.subTest(p=p):self.assertIsNotNone(GUARDS.resource_violation(p))

    def test_json_order_and_whitespace_do_not_change_clock_correctness(self):
        expected=dict(state='due_now',minutes_to_schedule=0)
        self.assertTrue(SCORE.clock_match(' { "minutes_to_schedule": 0, "state": "due_now" } ',expected))

    def test_false_is_not_a_valid_zero_minute_count(self):
        self.assertFalse(SCORE.clock_match('{"state":"due_now","minutes_to_schedule":false}',dict(state='due_now',minutes_to_schedule=0)))

    def test_duplicate_extra_or_nonjson_output_is_not_repaired(self):
        expected=dict(state='due_now',minutes_to_schedule=0)
        for text in ['{"state":"overdue","state":"due_now","minutes_to_schedule":0}',
                     '{"state":"due_now","minutes_to_schedule":0,"explanation":"x"}',
                     '```json\n{"state":"due_now","minutes_to_schedule":0}\n```']:
            with self.subTest(text=text):self.assertFalse(SCORE.clock_match(text,expected))

    def test_wrong_state_or_number_is_wrong(self):
        expected=dict(state='not_yet_due',minutes_to_schedule=35)
        self.assertFalse(SCORE.clock_match('{"state":"overdue","minutes_to_schedule":35}',expected))
        self.assertFalse(SCORE.clock_match('{"state":"not_yet_due","minutes_to_schedule":-35}',expected))
