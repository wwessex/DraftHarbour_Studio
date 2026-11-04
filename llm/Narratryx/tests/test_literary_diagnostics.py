import unittest
from foundation.literary_diagnostics import quoted_dialogue_blocks

class LiteraryDiagnosticTests(unittest.TestCase):
    def test_typographic_and_straight_quotes_with_action_beats(self):
        self.assertEqual(quoted_dialogue_blocks('“Wait.” She shut the door.\n\n"Why?"\n\nHe looked away.'),2)
    def test_unpaired_quote_is_not_a_complete_block(self):
        self.assertEqual(quoted_dialogue_blocks('An unfinished "remark\nNo dialogue.'),0)
    def test_multiple_fragments_same_line_count_once(self):
        self.assertEqual(quoted_dialogue_blocks('"No," she said, "I will wait."'),1)
