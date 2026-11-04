import copy
import unittest
from foundation.paragraph_lessons import paragraph_lesson, verify_derivation


class ParagraphLessonTests(unittest.TestCase):
    def test_next_whole_paragraph_keeps_exact_unicode(self):
        source = '“Where?” she asked.\n\n“I won’t say,” he said.\n\nShe waited.'
        d = paragraph_lesson(source, 1)
        self.assertEqual(d['context'], '“Where?” she asked.')
        self.assertEqual(d['answer'], '“I won’t say,” he said.')
        verify_derivation(source, d)

    def test_three_turn_dialogue_stays_contiguous(self):
        source = 'A question.\n\n“No.”\n\n“Really?”\n\n“Yes.”'
        d = paragraph_lesson(source, 1, 3)
        self.assertEqual(d['answer'], '“No.”\n\n“Really?”\n\n“Yes.”')
        verify_derivation(source, d)

    def test_no_context_missing_answer_and_bad_count_are_rejected(self):
        for index, count in [(0,1),(2,1),(1,0),(1,2)]:
            with self.assertRaises(ValueError):
                paragraph_lesson('First.\n\nSecond.', index, count)

    def test_invented_answer_or_skipped_paragraph_is_rejected(self):
        source = 'First.\n\nSecond.\n\nThird.'
        d = paragraph_lesson(source, 1)
        bad = copy.deepcopy(d)
        bad['answer'] = 'He agreed.'
        with self.assertRaises(ValueError):
            verify_derivation(source, bad)
        skipped = paragraph_lesson(source, 2)
        skipped['context'] = 'First.'
        skipped['context_end'] = len('First.')
        with self.assertRaises(ValueError):
            verify_derivation(source, skipped)
