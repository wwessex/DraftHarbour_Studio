import unittest
from collections import Counter
from foundation.question_ablation import cases, QUESTION, diagnose
from foundation.binding_ablation import cases as backgrounds


class QuestionAblationTests(unittest.TestCase):
    def test_balanced_pairs(self):
        rows = cases()
        self.assertEqual(len(rows), 32)
        self.assertEqual(len({c['id'] for c in rows}), 32)
        for q in [False, True]:
            subset = [c for c in rows if c['direct_question'] == q]
            self.assertEqual(Counter(c['expected_entity'] for c in subset), {'original': 8, 'duplicate': 8})
            self.assertEqual(len({(c['known_object'], c['first_fact_object'], c['unknown_cue_explicit'], c['field_count']) for c in subset}), 16)

    def test_only_question_changes(self):
        rows = cases()
        for background in backgrounds():
            pair = {c['direct_question']: c for c in rows if c['pair_id'] == background['id']}
            self.assertEqual(pair[False]['prompt'], background['prompt'])
            self.assertEqual(pair[True]['prompt'].replace(QUESTION, '', 1), background['prompt'])
            self.assertEqual(pair[True]['expected_json'], pair[False]['expected_json'])

    def test_labels_and_scorer(self):
        import json
        for c in cases():
            self.assertFalse(c['training_eligible'])
            self.assertTrue(diagnose(json.dumps(c['expected_json']), c)['exact_task_correct'])
            wrong = dict(c['expected_json'], unknown_object=c['known_object'])
            score = diagnose(json.dumps(wrong), c)
            self.assertTrue(score['format_compliant'])
            self.assertFalse(score['entity_correct'])
