import copy
import unittest
from foundation.source_restoration import corrupt_input,verify_corruption


class SourceRestorationTests(unittest.TestCase):
    def test_only_input_is_corrupted_and_unicode_line_breaks_survive(self):
        text='“Tomorrow,” she said.\nThe spare is untested.'
        b=corrupt_input(text,'Tomorrow','Yesterday')
        self.assertEqual(b['source_answer'],text)
        self.assertEqual(b['damaged_input'],'“Yesterday,” she said.\nThe spare is untested.')
        verify_corruption(text,b)

    def test_ambiguous_missing_and_identity_edits_rejected(self):
        for text,good,bad in [('x x','x','y'),('abc','z','y'),('abc','a','a'),('abc','','y')]:
            with self.assertRaises(ValueError):corrupt_input(text,good,bad)

    def test_changed_target_or_outside_input_rejected(self):
        b=corrupt_input('A future visit.','future','past')
        for field in ['source_answer','damaged_input']:
            bad=copy.deepcopy(b);bad[field]+=' Added prose.'
            with self.assertRaises(ValueError):verify_corruption('A future visit.',bad)

    def test_false_offsets_rejected(self):
        b=corrupt_input('A future visit.','future','past');b['start']=0
        with self.assertRaises(ValueError):verify_corruption('A future visit.',b)
