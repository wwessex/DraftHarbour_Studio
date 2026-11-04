import copy
import unittest
from foundation.task_alignment import lesson_form, observable_checks, verify_unchanged_target


def record(prompt='Write a scene.', answer='A scene.'):
    return dict(task='fiction', messages=[dict(role='user', content=prompt), dict(role='assistant', content=answer)],
                source_spans=[dict(text=answer)], rights_record_ids=['source'], source_work_ids=['work'],
                split='train', split_group='work', teacher=None, origin='derived')


class TaskAlignmentTests(unittest.TestCase):
    def test_boundary_reconstruction_is_not_a_directed_scene(self):
        self.assertEqual(lesson_form(record('Write.\nOPENING:\nA\nCLOSING:\nend.')), 'boundary-reconstruction')

    def test_fragment_and_paragraph_continuations_are_distinguished(self):
        self.assertEqual(lesson_form(record('Continue.\nFRAGMENT:\nHe was')), 'sentence-fragment-continuation')
        self.assertEqual(lesson_form(record('Continue directly after this passage.')), 'paragraph-continuation')

    def test_observables_do_not_impose_editing_minimum(self):
        checks = observable_checks(record('Edit. Return only the repair.', 'A.'))
        self.assertIsNone(checks['word_maximum'])
        self.assertFalse(checks['exceeds_word_maximum'])
        self.assertTrue(checks['answer_is_exact_source_span'])

    def test_repeated_sentences_and_word_overflow_are_reported(self):
        checks = observable_checks(record('Use at most 3 words.', 'He left. He left.'))
        self.assertTrue(checks['exceeds_word_maximum'])
        self.assertEqual(checks['repeated_exact_sentences'], ['He left.'])

    def test_instruction_repair_cannot_change_answer_or_source_or_split(self):
        old = record()
        new = copy.deepcopy(old)
        new['messages'][0]['content'] = 'A more precise brief.'
        verify_unchanged_target(old, new)
        for field, value in [('split', 'test'), ('source_spans', []), ('teacher', {'name': 'teacher'})]:
            bad = copy.deepcopy(new)
            bad[field] = value
            with self.assertRaises(ValueError):
                verify_unchanged_target(old, bad)
        new['messages'][-1]['content'] = 'An invented teaching answer.'
        with self.assertRaises(ValueError):
            verify_unchanged_target(old, new)
