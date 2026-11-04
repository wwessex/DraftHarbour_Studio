"""An AI selection must be complete, explicit and leave the historical draft intact."""
import copy
import importlib.util
from pathlib import Path
import unittest

from foundation.validation import Invalid

PATH = Path(__file__).resolve().parents[1] / 'curation/independent-scenes-review-v1/review.py'
SPEC = importlib.util.spec_from_file_location('scene_review', PATH)
REVIEW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(REVIEW)


class IndependentSceneReviewTests(unittest.TestCase):
    def setUp(self):
        self.rows = [dict(id='a', dataset_version='original', review={'status': 'pending'},
                          messages=[{'role': 'assistant', 'content': 'source prose'}]),
                     dict(id='b', dataset_version='original', review={'status': 'pending'},
                          messages=[{'role': 'assistant', 'content': 'other source prose'}])]
        self.decisions = dict(reviewer='Codex AI', reviewed_on='2026-10-26',
                              review_type='AI assessment, not human approval', decisions=[
                                  dict(id='a', decision='accept', reason='source and task aligned'),
                                  dict(id='b', decision='reference-only', reason='low sampling value')])

    def test_selection_preserves_source_answer_and_original_pending_draft(self):
        before = copy.deepcopy(self.rows)
        selected = REVIEW.apply_decisions(self.rows, self.decisions)
        self.assertEqual(self.rows, before)
        self.assertEqual([row['id'] for row in selected], ['a'])
        self.assertEqual(selected[0]['messages'], before[0]['messages'])
        self.assertEqual(selected[0]['review']['reviewer'], 'Codex AI')
        self.assertIn('not human approval', selected[0]['review']['notes'])

    def test_missing_or_extra_decisions_cannot_approve_selection(self):
        for entries in [self.decisions['decisions'][:1],
                        self.decisions['decisions'] + [dict(id='unknown', decision='accept', reason='x')]]:
            with self.subTest(entries=entries), self.assertRaises(Invalid):
                REVIEW.apply_decisions(self.rows, {**self.decisions, 'decisions': entries})

    def test_duplicate_decision_is_rejected(self):
        entries = self.decisions['decisions'] + [self.decisions['decisions'][0]]
        with self.assertRaises(Invalid):
            REVIEW.apply_decisions(self.rows, {**self.decisions, 'decisions': entries})

    def test_unknown_or_unreasoned_approval_is_rejected(self):
        for change in [dict(decision='auto-approved'), dict(reason='')]:
            decisions = copy.deepcopy(self.decisions)
            decisions['decisions'][0].update(change)
            with self.subTest(change=change), self.assertRaises(Invalid):
                REVIEW.apply_decisions(self.rows, decisions)
