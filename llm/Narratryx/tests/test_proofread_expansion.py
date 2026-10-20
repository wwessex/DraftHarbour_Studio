import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from foundation.proofread_expansion import build, exclude_reasons


class ProofreadExpansionTests(unittest.TestCase):
    def fixture(self, root):
        def token(n):
            return 'word' + chr(97 + n // 26 // 26) + chr(97 + n // 26 % 26) + chr(97 + n % 26)
        sources = []
        for i in range(2):
            text = ' '.join(token(n) for n in range(i * 225, (i + 1) * 225)).capitalize() + '.'
            # Deliberately repeated paragraph tests deduplication. Unknown tokens
            # test that dictionary membership cannot certify or rewrite prose.
            raw = '*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\r\n\r\n' + text + '\r\n\r\n' + text + '\r\n\r\nEND_STORY\r\n1.C. retained license'
            path = root / f'raw{i}.txt'
            path.write_bytes(raw.encode())
            sources.append(dict(id=f'source{i}', author_id=f'author{i}', work_id=f'work{i}',
                                split='train_candidate', raw_path=path.name,
                                raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                body_start=raw.index(text), body_end=raw.index('END_STORY'),
                                start_anchor=text, end_anchor='END_STORY'))
            # The full first paragraph is repeated, but its prefix need not be
            # the anchor: use a unique boundary including the source header.
            sources[-1]['start_anchor'] = raw[:raw.index(text)] + text[:10]
            sources[-1]['body_start'] = 0
        vocab = root / 'vocab.txt'
        vocab.write_text('a i the')
        plan = dict(status='pending_review', training_authorized=False, max_words_per_author=250,
                    vocabulary_path=vocab.name, vocabulary_sha256=hashlib.sha256(vocab.read_bytes()).hexdigest(),
                    reserved_author_ids=['reserved'], reserved_work_ids=['reserved-work'],
                    protected_files=[], sources=sources)
        # Start on the first paragraph with a unique prefix: the first copy has
        # an additional trailing space, unchanged by whitespace normalization.
        for s in sources:
            path = root / s['raw_path']; raw = path.read_bytes().decode()
            first = raw.index('Word'); stop = raw.index('\r\n\r\n', first)
            raw = raw[:stop] + ' ' + raw[stop:]
            path.write_bytes(raw.encode())
            s.update(body_start=first, body_end=raw.index('END_STORY'),
                     start_anchor=raw[first:stop+1], raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        path = root / 'plan.json'; path.write_text(json.dumps(plan))
        return path, plan

    def test_scope_excludes_verse_footnotes_provider_and_scripture_context(self):
        self.assertIn('indented_verse_or_attribution', exclude_reasons('    Quoted verse.', 'opie'))
        self.assertIn('annotation_or_footnote', exclude_reasons('Prose with [1].', 'opie'))
        self.assertIn('provider_or_editorial_matter', exclude_reasons('Project Gutenberg notice.', 'opie'))
        self.assertIn('outside_secular_narrative_scope', exclude_reasons('A hymn from Scripture.', 'wray-nestleton-pg41916'))

    def test_build_preserves_spans_deduplicates_and_never_approves(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); path, plan = self.fixture(root); out = root / 'out'
            self.assertEqual(build(path, out), {'author0': 225, 'author1': 225})
            rows = [json.loads(l) for l in (out / 'train-candidates.pending.jsonl').read_text().splitlines()]
            self.assertEqual(len(rows), 2)
            for row in rows:
                source = next(s for s in plan['sources'] if s['id'] == row['source_id'])
                raw = (root / source['raw_path']).read_bytes().decode()
                self.assertEqual(row['text'], ' '.join(raw[row['raw_start']:row['raw_end']].split()))
                self.assertEqual(row['rights_status'], 'pending')
                self.assertEqual(row['review_status'], 'pending')
                self.assertGreater(row['quality']['dictionary_outlier_rate'], .9)
            self.assertIn('exact_or_near_duplicate', (out / 'rejected.jsonl').read_text())
            with self.assertRaises(FileExistsError):
                build(path, out)

    def test_reserved_author_and_tampered_source_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); path, plan = self.fixture(root)
            plan['reserved_author_ids'] = ['author0']; path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'reserved'):
                build(path, root / 'out')
            plan['reserved_author_ids'] = []; path.write_text(json.dumps(plan))
            (root / 'raw0.txt').write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                build(path, root / 'out')
            self.assertFalse((root / 'out').exists())

    def test_protected_text_is_not_retained_to_meet_word_quota(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); path, plan = self.fixture(root)
            raw = (root / 'raw0.txt').read_bytes().decode()
            protected = root / 'protected.jsonl'
            protected.write_text(json.dumps({'prompt': raw}) + '\n')
            plan['protected_files'] = [{'path': protected.name, 'sha256': hashlib.sha256(protected.read_bytes()).hexdigest()}]
            path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'insufficient'):
                build(path, root / 'out')
            self.assertFalse((root / 'out').exists())

    def test_training_flag_and_missing_full_license_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); path, plan = self.fixture(root)
            plan['training_authorized'] = True; path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'review-only'):
                build(path, root / 'out')
            plan['training_authorized'] = False
            raw = (root / 'raw0.txt').read_bytes().replace(b'1.C.', b'none')
            (root / 'raw0.txt').write_bytes(raw)
            plan['sources'][0]['raw_sha256'] = hashlib.sha256(raw).hexdigest()
            path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, 'license'):
                build(path, root / 'out')


if __name__ == '__main__':
    unittest.main()
