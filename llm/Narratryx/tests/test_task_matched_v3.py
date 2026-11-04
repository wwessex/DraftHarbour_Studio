"""Evaluation design regressions; no model, corpus or ignored-artifact dependency."""
from pathlib import Path
import importlib.util,json,re,tempfile,unittest
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('task_matched_v3_cases',ROOT/'curation/task-matched-v3/evaluation_cases.py')
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)

class TaskMatchedEvaluationTests(unittest.TestCase):
 def setUp(self):
  self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
  old=MODULE.OUT;MODULE.OUT=Path(self.directory.name);self.addCleanup(setattr,MODULE,'OUT',old)
  MODULE.build();self.cases=[json.loads(line) for line in (MODULE.OUT/'test.cases.jsonl').read_text().splitlines()]
 def test_balanced_skills_and_distinct_scenarios(self):
  self.assertEqual(len(self.cases),24);self.assertEqual(len({c['scenario_id'] for c in self.cases}),8)
  for kind in MODULE.KINDS:self.assertEqual(sum(c['kind']==kind for c in self.cases),4)
  self.assertEqual(len({c['id'] for c in self.cases}),24)
 def test_repairs_are_minimal_and_have_no_minimum_length(self):
  for case in self.cases:
   if case['task']=='editing':self.assertEqual(case['word_count_min'],0)
   if case['kind']=='editing':
    matches=list(re.finditer(r'\b([A-Za-z]+) \1\b',case['context']));self.assertEqual(len(matches),1)
    match=matches[0];restored=case['context'][:match.start()]+match.group(1)+case['context'][match.end():]
    self.assertEqual(restored,case['exact_reference'])
 def test_creative_answers_are_unfilled_and_contexts_evaluation_only(self):
  for case in self.cases:
   self.assertIn('evaluation-only',case['provenance']);self.assertIn('not literary training targets',case['provenance'])
   self.assertTrue(case['established_facts']);self.assertNotIn('messages',case)
   if case['kind']!='editing':self.assertIsNone(case['exact_reference'])
 def test_design_refuses_overwriting_frozen_cases(self):
  before=(MODULE.OUT/'test.cases.jsonl').read_bytes()
  with self.assertRaises(FileExistsError):MODULE.build()
  self.assertEqual((MODULE.OUT/'test.cases.jsonl').read_bytes(),before)
