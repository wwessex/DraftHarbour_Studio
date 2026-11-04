"""Original edit fixtures, never training examples."""
import unittest
from foundation.anchored_edits import AnchorEdit, apply_anchor_edits

class AnchoredEditTests(unittest.TestCase):
    def test_unicode_typography_and_untouched_text_remain_exact(self):
        text='“Wait,” Ada said. Ravi’s coat was wet wet. 🧭'
        self.assertEqual(apply_anchor_edits(text,text,[AnchorEdit('wet wet','wet')]),'“Wait,” Ada said. Ravi’s coat was wet. 🧭')
    def test_rejects_ambiguous_anchors(self):
        with self.assertRaisesRegex(ValueError,'ambiguous'):apply_anchor_edits('red red red','red red red',[AnchorEdit('red red','red')])
    def test_rejects_missing_anchor(self):
        with self.assertRaisesRegex(ValueError,'not found'):apply_anchor_edits('Stay here.','Stay here.',[AnchorEdit('Elsewhere','Here')])
    def test_rejects_overlapping_edits(self):
        with self.assertRaisesRegex(ValueError,'overlapping'):apply_anchor_edits('one two three','one two three',[AnchorEdit('one two','one'),AnchorEdit('two three','three')])
    def test_rejects_stale_target(self):
        with self.assertRaisesRegex(ValueError,'changed'):apply_anchor_edits('Changed.','Original.',[AnchorEdit('Original','Updated')])
    def test_multiple_changes_use_original_coordinates(self):
        text='“slow slow” and very very quiet.'
        self.assertEqual(apply_anchor_edits(text,text,[AnchorEdit('slow slow','slow'),AnchorEdit('very very','very')]),'“slow” and very quiet.')
