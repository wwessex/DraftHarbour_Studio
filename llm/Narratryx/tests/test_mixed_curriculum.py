import unittest
from foundation.mixed_curriculum import require_distinct_source_spans,repair_diagnostics
from foundation.source_restoration import corrupt_input


class MixedCurriculumTests(unittest.TestCase):
    def test_alias_rights_records_cannot_hide_source_overlap(self):
        ledger={k:dict(source=dict(sha256='same')) for k in ['a','alias']}
        rows=[dict(id='one',source_spans=[dict(rights_record_id='a',start=0,end=10)]),dict(id='two',source_spans=[dict(rights_record_id='alias',start=5,end=12)])]
        with self.assertRaises(ValueError):require_distinct_source_spans(rows,ledger)

    def test_adjacent_spans_and_different_sources_are_allowed(self):
        ledger={'a':dict(source=dict(sha256='same')),'b':dict(source=dict(sha256='different'))}
        rows=[dict(id='one',source_spans=[dict(rights_record_id='a',start=0,end=10)]),dict(id='two',source_spans=[dict(rights_record_id='a',start=10,end=20)]),dict(id='three',source_spans=[dict(rights_record_id='b',start=0,end=10)])]
        require_distinct_source_spans(rows,ledger)

    def test_correct_anchor_does_not_excuse_added_commentary(self):
        b=corrupt_input('The spare is unknown.','spare','original')
        d=repair_diagnostics('Here is the correction: The spare is unknown.',b)
        self.assertTrue(d['correct_anchor_present_once'])
        self.assertFalse(d['outside_correction_preserved'])
        self.assertIsNone(d['correction_at_expected_slot'])

    def test_outside_preservation_is_separate_from_correcting_the_error(self):
        b=corrupt_input('The spare is unknown.','spare','original')
        wrong=repair_diagnostics(b['damaged_input'],b)
        self.assertTrue(wrong['outside_correction_preserved'])
        self.assertFalse(wrong['correction_at_expected_slot'])
        self.assertTrue(repair_diagnostics(b['source_answer'],b)['exact_full_answer'])

    def test_corruption_phrase_may_legitimately_appear_elsewhere(self):
        b=corrupt_input('The bed is denim. The window is muslin.','denim','muslin')
        self.assertTrue(repair_diagnostics(b['source_answer'],b)['correct_anchor_present_once'])
        self.assertFalse(repair_diagnostics(b['damaged_input'],b)['correct_anchor_present_once'])
