"""Original fixture strings are test inputs, never model training records."""
import importlib.util
from pathlib import Path
import unittest
p = Path(__file__).resolve().parents[1] / 'curation/literary-mix-v2/build.py'
s = importlib.util.spec_from_file_location('literary_mix_v2', p)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)


class LiteraryMixV2Tests(unittest.TestCase):
    def test_word_cap_rounds_up_without_a_minimum(self):
        for count in [1, 9, 10, 11, 99, 140]:
            text = ' '.join(['word'] * count)
            self.assertGreaterEqual(m.cap(text), count)
            self.assertLess(m.cap(text), count + 10)

    def test_write_preserves_anchors_and_requests_only_an_upper_cap(self):
        text = ' '.join('word' + str(i) for i in range(45))
        prompt = m.write_prompt(text, 'science-fiction')
        self.assertIn('at most 50 words', prompt)
        self.assertIn(' '.join(text.split()[:8]), prompt)
        self.assertIn(' '.join(text.split()[-8:]), prompt)
        self.assertNotIn('at least', prompt)

    def test_source_target_unchanged_and_ai_review_not_human_approval(self):
        record = m.new_record('fixture', 'fiction', 'Instruction', 'Exact source.', 'source',
                              dict(rights_record_id='source', start=0, end=13, text='Exact source.'), 'work')
        self.assertEqual(record['messages'][-1]['content'], 'Exact source.')
        self.assertIsNone(record['teacher'])
        self.assertEqual(record['origin'], 'derived')
        self.assertIn('Codex AI', record['review']['reviewer'])
        self.assertIn('not human', record['review']['notes'])
