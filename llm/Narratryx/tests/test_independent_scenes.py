"""Source packet guards: corrupt text, unscoped additions and changed evidence fail."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

from foundation.validation import Invalid

PATH = Path(__file__).resolve().parents[1] / 'curation/independent-scenes-v1/prepare.py'
SPEC = importlib.util.spec_from_file_location('independent_scenes_prepare', PATH)
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


class IndependentScenesTests(unittest.TestCase):
    def test_canonical_span_round_trip_and_paragraph_separator(self):
        text = 'First sentence.\n\nSecond sentence.\n'
        segments = [dict(id='first', source='s', start=0, end=15, text='First sentence.'),
                    dict(id='second', source='s', start=17, end=33, text='Second sentence.')]
        PREPARE.verify_segments(segments, {'s': text})

    def test_ocr_or_punctuation_change_is_not_accepted_as_gold(self):
        with self.assertRaises(Invalid):
            PREPARE.verify_segments([dict(id='x', source='s', start=0, end=5, text='hell0')],
                                    {'s': 'hello\n'})

    def test_unscoped_prefix_or_suffix_is_rejected(self):
        for text, start, end in [('added hello\n', 6, 11), ('hello added\n', 0, 5)]:
            with self.subTest(text=text), self.assertRaises(Invalid):
                PREPARE.verify_segments([dict(id='x', source='s', start=start, end=end, text='hello')],
                                        {'s': text})

    def test_duplicate_or_overlapping_spans_are_rejected(self):
        first = dict(id='a', source='s', start=0, end=5, text='hello')
        for second in [first, dict(id='b', source='s', start=3, end=5, text='lo')]:
            with self.subTest(second=second), self.assertRaises(Invalid):
                PREPARE.verify_segments([first, second], {'s': 'hello\n'})

    def test_changed_scan_or_source_bytes_are_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / 'scan'
            source.write_bytes(b'original')
            pinned = {'scan': PREPARE.sha(source)}
            PREPARE.verify_files(root, pinned)
            source.write_bytes(b'replacement')
            with self.assertRaises(Invalid):
                PREPARE.verify_files(root, pinned)

    def test_lock_cannot_reference_files_outside_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root / 'outside'
            outside.write_bytes(b'original')
            inside = root / 'inside'
            inside.mkdir()
            with self.assertRaises(Invalid):
                PREPARE.verify_files(inside, {'../outside': PREPARE.sha(outside)})


if __name__ == '__main__':
    unittest.main()
