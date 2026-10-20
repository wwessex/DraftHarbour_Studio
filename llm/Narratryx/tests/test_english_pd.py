import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from foundation.english_pd import build, check_assignments, normalized, paragraphs, quality


class EnglishPDTests(unittest.TestCase):
    def test_offsets_preserve_unicode_and_crlf(self):
        raw = 'wrapper\r\n\r\n“Élan.”\r\n\r\nNext sentence.\r\n\r\nEND'
        spans = list(paragraphs(raw, raw.index('“'), raw.index('END')))
        self.assertEqual([x[2].strip() for x in spans], ['“Élan.”', 'Next sentence.'])
        for start, end, span in spans:
            self.assertEqual(raw[start:end], span)
        self.assertEqual(normalized('word-\n split'), 'word- split')

    def test_rejects_damage_without_repair(self):
        for raw, expected in [('A broken-\nword.', 'split_word'),
                              ('A phrase.\n32\nAnother phrase.', 'page_number_or_heading'),
                              ('Some t3xt.', 'damaged_token'),
                              ('Scanned ■ words.', 'ocr_symbol'),
                              ('A sentence with no ending', 'incomplete_boundary')]:
            self.assertIn(expected, quality(raw, set())[1])

    def test_author_and_work_cannot_cross_splits(self):
        for field in ['author_id', 'work_id']:
            a = dict(author_id='a', work_id='x', split='train_candidate')
            b = dict(author_id='b', work_id='y', split='heldout_candidate')
            b[field] = a[field]
            with self.assertRaisesRegex(ValueError, 'crosses splits'):
                check_assignments([a, b])

    def test_body_bounds_fail_closed(self):
        for start, end in [(-1, 3), (2, 2), (0, 99)]:
            with self.assertRaises(ValueError):
                list(paragraphs('abc', start, end))

    def test_build_blocks_overlap_deduplicates_and_preserves_provenance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sentence = 'A quiet child watched the rain across the garden while the old man waited beside the window and listened for a sound from the road. '
            shared = sentence * 2
            distinct = 'The visitor carried a letter beneath her coat and stopped beside the gate before the light faded across the fields. ' * 3
            protected = 'The sailor stood beside the boat and watched the water move beneath the bridge while a child waited with a lantern near the shore. ' * 2
            vocab = root / 'vocab.txt'
            vocab.write_text(' '.join((shared + distinct + protected).lower().replace('.', '').split()))
            benchmark = root / 'benchmark.jsonl'
            benchmark.write_text(json.dumps({'prompt': protected}) + '\n')
            sources = []
            for ident, split, text in [('a', 'train_candidate', shared + '\n\n' + distinct + '\n\n' + protected),
                                       ('b', 'heldout_candidate', shared)]:
                path = root / (ident + '.txt')
                raw = text.strip() + '\n\nEND'
                path.write_text(raw)
                sources.append(dict(identifier=ident, author_id=ident, work_id=ident, split=split,
                                    raw_path=path.name, raw_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                                    body_start=0, body_end=raw.index('END'), start_anchor=text[:12], end_anchor='END'))
            plan = dict(status='pending_review', training_authorized=False, dataset_revision='test',
                        vocabulary_path=str(vocab), vocabulary_sha256=hashlib.sha256(vocab.read_bytes()).hexdigest(),
                        protected_files=[benchmark.name], sources=sources, max_passages_per_work=5)
            plan_path = root / 'plan.json'
            plan_path.write_text(json.dumps(plan))
            out = root / 'output'
            totals = build(plan_path, out)
            self.assertEqual(totals['a']['passages'], 1)
            self.assertEqual(totals['b']['passages'], 1)
            audit = json.loads((out / 'audit.json').read_text())
            self.assertEqual(audit['duplicates_removed'], 1)
            self.assertFalse(audit['release_ready'])
            row = json.loads((out / 'train_candidate.pending.jsonl').read_text())
            raw = (root / 'a.txt').read_text()
            self.assertEqual(normalized(raw[row['raw_start']:row['raw_end']]), row['text'])
            self.assertIn('protected_test_overlap', (out / 'rejected.jsonl').read_text())
            # Refuse edited sources and destinations, rather than quietly rebuilding.
            (root / 'a.txt').write_text('tampered')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                build(plan_path, root / 'other')

    def test_training_flag_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'plan.json'
            path.write_text(json.dumps({'status': 'pending_review', 'training_authorized': True}))
            with self.assertRaisesRegex(ValueError, 'review-only'):
                build(path, Path(directory) / 'out')


if __name__ == '__main__':
    unittest.main()
