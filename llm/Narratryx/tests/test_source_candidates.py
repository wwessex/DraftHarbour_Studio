import hashlib
import unittest
from foundation.source_candidates import scoped_raw_span, continuation


class SourceCandidatesTests(unittest.TestCase):
    def approved(self):
        raw='Header\r\nOne line\r\nnext.\r\nEnd'
        selected='One line\r\nnext.'
        return raw,dict(raw_file_sha256='pinned',raw_start=8,raw_end=23,raw_span_sha256=hashlib.sha256(selected.encode()).hexdigest(),text='One line next.',source_id='scope')

    def test_crlf_offsets_remain_traceable(self):
        raw,a=self.approved();span=scoped_raw_span(raw,a,'pinned')
        self.assertEqual(span['start'],7)
        self.assertEqual(raw.replace('\r\n','\n')[span['start']:span['end']],span['text'])

    def test_scope_or_source_mismatch_rejected(self):
        raw,a=self.approved()
        with self.assertRaises(ValueError):scoped_raw_span(raw,a,'other')
        a['raw_end']+=1
        with self.assertRaises(ValueError):scoped_raw_span(raw,a,'pinned')

    def test_continuation_keeps_complete_paragraph_and_exact_answer(self):
        span=dict(text='First complete paragraph.\n\nSecond paragraph.\n\nThird paragraph.')
        d=continuation(span,1,2)
        self.assertEqual(d['context'],'First complete paragraph.')
        self.assertEqual(d['answer'],'Second paragraph.\n\nThird paragraph.')
        with self.assertRaises(ValueError):continuation(span,0)
