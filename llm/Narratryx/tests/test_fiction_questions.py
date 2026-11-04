import unittest
from foundation.fiction_questions import QUESTIONS, cases, mechanics


class FictionQuestionsTests(unittest.TestCase):
    def source(self):
        return [dict(id=k, kind=('rewrite' if 'rewrite' in k else 'continue' if 'continue' in k else 'dialogue'), prompt='Original facts: ' + k, word_count_min=None, word_count_max=100) for k in QUESTIONS]

    def test_six_pairs_and_task_balance(self):
        from collections import Counter
        rows=cases(self.source())
        self.assertEqual(len(rows),12)
        self.assertEqual(Counter(c['kind'] for c in rows),{'rewrite':4,'continue':4,'dialogue':4})
        self.assertEqual(sum(c['variant']=='original' for c in rows),6)
        self.assertTrue(all(c['training_eligible'] is False for c in rows))

    def test_original_unchanged_and_clarification_only_appended(self):
        rows=cases(self.source())
        for parent in self.source():
            pair={c['variant']:c for c in rows if c['parent_case_id']==parent['id']}
            self.assertEqual(pair['original']['prompt'],parent['prompt'])
            self.assertEqual(pair['clarified']['prompt'],parent['prompt']+pair['clarified']['added_suffix'])
            self.assertIn(QUESTIONS[parent['id']],pair['clarified']['prompt'])
            self.assertEqual(pair['original']['word_count_min'],pair['clarified']['word_count_min'])

    def test_mechanics_are_not_quality_or_a_minimum_edit_length(self):
        c=dict(kind='rewrite',word_count_min=None,word_count_max=3)
        self.assertTrue(mechanics('Fixed.',c)['word_limit_passed'])
        self.assertFalse(mechanics('one two three four',c)['word_limit_passed'])
        self.assertFalse(mechanics('one\n\ntwo',c)['one_paragraph_passed'])
        self.assertNotIn('quality',mechanics('Fixed.',c))
