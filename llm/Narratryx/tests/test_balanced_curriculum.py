"""Retained prose must stay distinct and semantic clarification must preserve source."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

from foundation.balanced_curriculum import balanced_take
from foundation.validation import Invalid

PATH=Path(__file__).resolve().parents[1]/'curation/grounding-balanced-v1/build.py'
SPEC=importlib.util.spec_from_file_location('grounding_balanced_build',PATH)
BUILD=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class BalancedCurriculumTests(unittest.TestCase):
    def test_selection_balances_works_without_mutating_candidates(self):
        rows=[dict(id='a1',source_work_ids=['a'],source_spans=[dict(text='First source')]),
              dict(id='a2',source_work_ids=['a'],source_spans=[dict(text='Second source')]),
              dict(id='b1',source_work_ids=['b'],source_spans=[dict(text='Third source')])]
        before=copy.deepcopy(rows)
        selected,_=balanced_take(rows,2)
        self.assertEqual([r['id'] for r in selected],['a1','b1'])
        self.assertEqual(rows,before)

    def test_whitespace_or_case_variants_do_not_inflate_source_count(self):
        rows=[dict(id='a',source_work_ids=['a'],source_spans=[dict(text='Same source.')]),
              dict(id='b',source_work_ids=['b'],source_spans=[dict(text=' SAME\nSOURCE. ')])]
        with self.assertRaises(Invalid):balanced_take(rows,2)

    def test_insufficient_distinct_material_is_not_padded(self):
        row=dict(id='a',source_work_ids=['a'],source_spans=[dict(text='Only source')])
        with self.assertRaises(Invalid):balanced_take([row],2)

    def fixtures(self):
        source='You will eat. I’ll help you, if nobody else will.'
        row=dict(id='ge-evidence-21',messages=[dict(role='user',content='Directions.\nCLASSIFY THIS QUOTATION:\nYou will eat.\n\nSOURCE EXCERPT:\n'+source),
                 dict(role='assistant',content=json.dumps(dict(status='plan',evidence=['You will eat.'])))])
        decisions=dict(accept_unchanged=[],clarify=dict(id='ge-evidence-21'),reviewer='Codex AI',status_reasons=dict(plan='Promise, not completion.'))
        return row,decisions,source

    def test_clarification_changes_only_the_query_and_evidence(self):
        row,decisions,source=self.fixtures();before=copy.deepcopy(row)
        revised=BUILD.review_semantics([row],decisions)[0]
        self.assertEqual(row,before)
        self.assertEqual(revised['messages'][0]['content'].split('SOURCE EXCERPT:\n',1)[1],source)
        target=json.loads(revised['messages'][1]['content'])
        self.assertEqual(target,dict(status='plan',evidence=['I’ll help you, if nobody else will.']))

    def test_missing_semantic_decision_is_rejected(self):
        row,decisions,_=self.fixtures();decisions['clarify']['id']='missing'
        with self.assertRaises(Invalid):BUILD.review_semantics([row],decisions)

    def test_duplicate_semantic_decision_is_rejected(self):
        row,decisions,_=self.fixtures();decisions['accept_unchanged']=[row['id']]
        with self.assertRaises(Invalid):BUILD.review_semantics([row],decisions)
