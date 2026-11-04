import unittest
from collections import Counter
from foundation.format_diagnostic import factor_cases,score


class FormatDiagnosticTests(unittest.TestCase):
    def test_full_factorial_and_balanced_targets(self):
        rows=factor_cases();self.assertEqual(len(rows),24)
        self.assertEqual(len({(c['known_object'],c['first_fact_object'],c['question'],c['format']) for c in rows}),24)
        self.assertEqual(Counter(c['expected_entity'] for c in rows),{'original':12,'duplicate':12})

    def test_facts_and_targets_are_counterbalanced(self):
        for c in factor_cases():
            self.assertNotEqual(c['known_object'],c['expected_entity'])
            self.assertIn('The '+c['expected_entity']+' register has not been inspected',c['prompt'])

    def test_correct_entity_and_wrong_format_are_separate(self):
        c=next(c for c in factor_cases() if c['format']=='json-answer' and c['expected_entity']=='duplicate')
        r=score('The duplicate.',c);self.assertTrue(r['entity_correct']);self.assertFalse(r['format_compliant'])

    def test_schema_valid_does_not_mean_correct(self):
        c=next(c for c in factor_cases() if c['format']=='json-answer' and c['expected_entity']=='duplicate')
        r=score('{"answer":"original"}',c);self.assertTrue(r['format_compliant']);self.assertFalse(r['entity_correct'])

    def test_ambiguous_answer_and_duplicate_json_keys_are_not_guessed(self):
        c=next(c for c in factor_cases() if c['format']=='json-answer')
        self.assertIsNone(score('The original and the duplicate.',c)['entity_correct'])
        self.assertFalse(score('{"answer":"original","answer":"duplicate"}',c)['format_compliant'])
