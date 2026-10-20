"""Traceability/scope regressions use invented temporary source and approvals."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from foundation.austen_review import (build_pack, make_excerpt, normalize_excerpt,
                                     text_hash, verify_excerpt)
from foundation.validation import Invalid, ROOT, file_hash, load_ledger, read_jsonl


class AustenReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = 'EXCLUDED PREFACE\n\nCHAPTER I.\n\nAlpha _emphasis_ opens\nthis paragraph.\n\nIt ends here.\n\nCHAPTER II.\n\nA second chapter.\n'
        self.outer = (self.source.index('Alpha'), len(self.source))
        self.selection = {'id': 'test-excerpt', 'chapter': 1, 'start': 'Alpha _emphasis_',
                          'end': 'It ends here.', 'focus': 'Invented test passage.'}

    def excerpt(self, selection=None):
        return make_excerpt(self.source, selection or self.selection, outer=self.outer,
                            source_sha256='a' * 64, source_path='test.txt',
                            rights_id='fixture-rights', work_id='fixture-work')

    def test_soft_wrap_cleanup_preserves_paragraphs_and_emphasis(self):
        excerpt = self.excerpt()
        self.assertEqual(excerpt['text'], 'Alpha _emphasis_ opens this paragraph.\n\nIt ends here.')
        self.assertEqual(excerpt['span']['text'], self.source[excerpt['span']['start']:excerpt['span']['end']])
        self.assertEqual(excerpt['transformation']['joined_line_breaks'], 1)
        self.assertFalse(excerpt['transformation']['removed_content'])

    def test_captioned_and_bare_illustration_spans_are_rejected(self):
        for marker in ('[Illustration]', '[Illustration: caption]', 'Copyright 1894', 'Project Gutenberg'):
            self.source = 'Alpha ' + marker + ' It ends here.'
            self.outer = (0, len(self.source))
            with self.assertRaisesRegex(Invalid, 'excluded'):
                self.excerpt({**self.selection, 'start': 'Alpha'})

    def test_preface_and_ambiguous_anchor_cannot_be_selected(self):
        with self.assertRaisesRegex(Invalid, 'unique'):
            self.excerpt({**self.selection, 'start': 'EXCLUDED PREFACE'})
        self.source += '\nAlpha _emphasis_ duplicated.'
        self.outer = (self.outer[0], len(self.source))
        with self.assertRaisesRegex(Invalid, 'unique'):
            self.excerpt()

    def test_wrong_chapter_and_cross_chapter_spans_rejected(self):
        with self.assertRaisesRegex(Invalid, 'chapter'):
            self.excerpt({**self.selection, 'chapter': 2})
        with self.assertRaisesRegex(Invalid, 'chapter'):
            self.excerpt({**self.selection, 'end': 'A second chapter.'})

    def test_unrecorded_rewrite_and_bad_source_offset_rejected(self):
        excerpt = self.excerpt()
        excerpt['text'] = excerpt['text'].replace('opens', 'closes')
        with self.assertRaisesRegex(Invalid, 'unrecorded'):
            verify_excerpt(excerpt, self.source, self.outer, 'a' * 64)
        excerpt = self.excerpt()
        excerpt['span']['start'] -= 1
        with self.assertRaisesRegex(Invalid, 'outside'):
            verify_excerpt(excerpt, self.source, self.outer, 'a' * 64)

    def test_hash_line_and_transformation_tampering_rejected(self):
        for mutate, message in (
            (lambda e: e.update(text_sha256='b' * 64), 'hash'),
            (lambda e: e['source_lines'].update(start=1), 'line'),
            (lambda e: e['transformation'].update(joined_line_breaks=100), 'count'),
            (lambda e: e.update(chapter=2), 'chapter'),
        ):
            excerpt = self.excerpt()
            mutate(excerpt)
            with self.assertRaisesRegex(Invalid, message):
                verify_excerpt(excerpt, self.source, self.outer, 'a' * 64)

    def fixture_pack(self):
        """Create fictional evidence, not a grant for any real literary source."""
        spec = json.loads((ROOT / 'curation/austen-pilot-review-v1.json').read_text())
        parts = []
        for index, selection in enumerate(spec['selections'], 1):
            start = f'Fixture passage number {index} starts'
            end = f'and passage number {index} ends.'
            parts.append(f'CHAPTER { {1:"I",3:"III",6:"VI",34:"XXXIV",36:"XXXVI",61:"LXI"}[selection["chapter"]]}.\n\n'
                         f'{start} with _emphasis_\nand felicity; {end}\n\n')
            selection.update(start=start, end=end)
        source = ''.join(parts)
        raw = self.root / 'test-source.txt'
        raw.write_bytes(source.replace('\n', '\r\n').encode())
        source_hash = file_hash(raw)
        spec.update(expected_source_sha256=source_hash, expected_outer_range=[0, len(source)])
        spec_path = self.root / 'spec.json'
        spec_path.write_text(json.dumps(spec))
        rights = copy.deepcopy(load_ledger(ROOT / 'rights/ledger.jsonl')['austen-pride-candidate'])
        rights['title'] = 'INVENTED TEMPORARY TEST SOURCE'
        rights['source'].update(raw_path='test-source.txt', sha256=source_hash)
        rights['review'] = {'status': 'approved', 'reviewer': 'INVENTED TEST REVIEWER',
                            'reviewed_on': '2026-10-17', 'notes': 'Test fixture only.'}
        ledger_path = self.root / 'ledger.jsonl'
        ledger_path.write_text(json.dumps(rights) + '\n')
        snapshot = self.root / 'test-snapshot.txt'
        snapshot.write_text('Invented source-scope review fixture.')
        approval = {'record_id': 'TEST-ONLY-APPROVAL', 'rights_record_id': rights['id'],
                    'decision': 'approved-with-scope-conditions', 'jurisdictions': ['GB', 'US'],
                    'source_sha256': source_hash, 'reviewed_documents': {
                        'test': {'snapshot_path': 'test-snapshot.txt', 'sha256_at_approval': file_hash(snapshot)}}}
        approval_path = self.root / 'approval.json'
        approval_path.write_text(json.dumps(approval))
        manifest = {'sha256': source_hash, 'selection_plan': {'outer_start': 0,
                    'outer_end_exclusive': len(source), 'outer_range_sha256_utf8': text_hash(source)}}
        manifest_path = self.root / 'source-manifest.json'
        manifest_path.write_text(json.dumps(manifest))
        return spec_path, ledger_path, manifest_path, approval_path

    def test_complete_pack_is_traceable_and_never_self_approved(self):
        inputs = self.fixture_pack()
        before = [file_hash(p) for p in inputs]
        output = self.root / 'pack'
        manifest = build_pack(*inputs, output)
        self.assertEqual([file_hash(p) for p in inputs], before)
        self.assertEqual(manifest['excerpt_count'], 6)
        self.assertEqual(manifest['example_count'], 12)
        self.assertEqual(set(manifest['examples_per_skill'].values()), {2})
        self.assertFalse(manifest['training_ready'])
        self.assertEqual(manifest['inference_calls'], 0)
        self.assertEqual(manifest['downloads'], 0)
        excerpts = {e['id']: e for e in read_jsonl(output / 'excerpts.pending.jsonl')}
        examples = read_jsonl(output / 'examples.pending.jsonl')
        source = (self.root / 'test-source.txt').read_text()
        for excerpt in excerpts.values():
            span = excerpt['span']
            self.assertEqual(span['text'], source[span['start']:span['end']])
            self.assertEqual(excerpt['text'], normalize_excerpt(span['text']))
            self.assertEqual(excerpt['review']['status'], 'pending')
        for row in examples:
            self.assertEqual(row['review']['status'], 'pending')
            self.assertEqual(row['teacher']['review']['status'], 'pending')
            self.assertEqual(row['split'], 'train')
            self.assertEqual(row['split_group'], 'author-austen')
        edit = next(e for e in examples if e['id'] == 'austen-editing-01')
        self.assertEqual(edit['messages'][1]['content'], excerpts['austen-charlotte']['text'].replace('felicity', 'happiness'))
        keep = next(e for e in examples if e['id'] == 'austen-editing-02')
        self.assertEqual(keep['messages'][1]['content'], 'No changes needed.\n\n' + excerpts['austen-gratitude']['text'])
        for name, expected in manifest['file_hashes'].items():
            self.assertEqual(file_hash(output / name), expected)

    def test_missing_approval_tampered_source_and_tampered_snapshot_fail_before_writing(self):
        inputs = self.fixture_pack()
        output = self.root / 'pack'
        raw = self.root / 'test-source.txt'
        data = raw.read_bytes()
        raw.write_bytes(data + b'changed')
        with self.assertRaisesRegex(Invalid, 'source hash'):
            build_pack(*inputs, output)
        self.assertFalse(output.exists())
        raw.write_bytes(data)
        (self.root / 'test-snapshot.txt').write_text('Changed snapshot')
        with self.assertRaisesRegex(Invalid, 'snapshot hash'):
            build_pack(*inputs, output)
        self.assertFalse(output.exists())
        ledger = json.loads(inputs[1].read_text())
        ledger['review']['status'] = 'pending'
        inputs[1].write_text(json.dumps(ledger) + '\n')
        with self.assertRaisesRegex(Invalid, 'human source-scope approval'):
            build_pack(*inputs, output)

    def test_existing_review_pack_is_not_overwritten(self):
        inputs = self.fixture_pack()
        output = self.root / 'pack'
        output.mkdir()
        marker = output / 'reviewer-notes.txt'
        marker.write_text('Keep these human notes.')
        with self.assertRaisesRegex(Invalid, 'already exists'):
            build_pack(*inputs, output)
        self.assertEqual(marker.read_text(), 'Keep these human notes.')


if __name__ == '__main__':
    unittest.main()
