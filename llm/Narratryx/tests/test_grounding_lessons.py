"""Evidence discipline, unknown states and selected-text repairs fail closed."""
import unittest

from foundation.anchored_edits import AnchorEdit, apply_anchor_edits
from foundation.grounding_lessons import arrival_state, evidence_target, minutes, selection_pair


class GroundingLessonTests(unittest.TestCase):
    def test_future_absent_visitor_is_not_late(self):
        self.assertEqual(arrival_state('12:40','13:15',False),
                         dict(state='not_yet_due', minutes_to_schedule=35))

    def test_past_schedule_without_arrival_is_overdue(self):
        self.assertEqual(arrival_state('14:00','13:15',False)['state'], 'overdue')

    def test_exact_due_time_is_not_already_overdue(self):
        self.assertEqual(arrival_state('13:15','13:15',False)['state'], 'due_now')

    def test_unknown_arrival_does_not_become_absence(self):
        for now in ['12:40','13:15','14:00']:
            self.assertEqual(arrival_state(now,'13:15',None)['state'], 'not_established')

    def test_known_arrival_is_not_reversed_by_schedule(self):
        self.assertEqual(arrival_state('12:40','13:15',True)['state'], 'arrived')

    def test_ambiguous_or_invalid_clock_is_rejected(self):
        for value in ['1:15','24:00','12:60','quarter to eight',None]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                minutes(value)

    def test_truthy_values_cannot_substitute_for_explicit_arrival(self):
        for value in ['false',0,1,[]]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                arrival_state('12:40','13:15',value)

    def test_evidence_cannot_be_reworded_or_invented(self):
        with self.assertRaises(ValueError):
            evidence_target('The visitor is expected.', 'plan', 'The visitor arrived.')

    def test_ambiguous_evidence_anchor_is_rejected(self):
        with self.assertRaises(ValueError):
            evidence_target('Here. Here.', 'explicit_fact', 'Here.')

    def test_unknown_answer_has_no_fabricated_evidence(self):
        self.assertEqual(evidence_target('A box lay there.', 'not_established', None),
                         dict(status='not_established',evidence=[]))
        with self.assertRaises(ValueError):
            evidence_target('A box lay there.', 'not_established', 'A box lay there.')

    def test_selected_repair_leaves_matching_outside_error_untouched(self):
        source = ('The visitor carried a battered leather satchel across the silent courtyard while '
                  'several curious children watched from the windows above the closed iron gateway for signs of movement.')
        pair = selection_pair(source)
        outside = pair['outside_with_duplicate']
        fixed = apply_anchor_edits(pair['broken'], pair['broken'], [AnchorEdit(**e) for e in pair['edits']])
        self.assertEqual(fixed,pair['clean'])
        self.assertIn(pair['edits'][0]['before'],outside)
        self.assertEqual(apply_anchor_edits(pair['clean'],pair['clean'],[]),pair['clean'])
        self.assertEqual(outside,pair['outside_with_duplicate'])

    def test_naturally_repeated_word_is_not_false_noop_gold(self):
        text = 'The visitor said that that cupboard was closed and carried the old satchel across the silent courtyard while several curious children watched from the upstairs windows.'
        with self.assertRaises(ValueError):
            selection_pair(text)
