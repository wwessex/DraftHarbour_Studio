import unittest
from foundation.scoped_excerpt import excerpt,split_continuation


class ScopedExcerptTests(unittest.TestCase):
    def test_exact_interval_preserves_characters(self):
        source='Header\n\nFirst, odd spelling.\n\nSecond.\n\nFooter'
        s=excerpt(source,'First,','Footer')
        self.assertEqual(source[s['start']:s['end']],s['text'])
        self.assertEqual(s['text'],'First, odd spelling.\n\nSecond.')
        d=split_continuation(s,'Second.')
        self.assertEqual(d['context'],'First, odd spelling.')
        self.assertEqual(source[d['answer_start']:d['answer_end']],d['answer'])

    def test_ambiguous_or_reversed_markers_fail(self):
        for source,a,b in [('a a b','a','b'),('b a','a','b'),('a b','missing','b')]:
            with self.assertRaises(ValueError):excerpt(source,a,b)

    def test_sentence_fragment_not_a_paragraph_boundary(self):
        with self.assertRaises(ValueError):split_continuation(dict(start=0,end=20,text='First sentence. Next.'),'Next.')
