import importlib.util
from pathlib import Path
import unittest
from foundation.arrival_claims import overdue_claim
HERE=Path(__file__).resolve().parents[1]/'curation/grounding-training-v7'
def load(name):
 spec=importlib.util.spec_from_file_location('claim_'+name,HERE/(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
class ArrivalClaimTests(unittest.TestCase):
 def test_before_deadline_cannot_be_already_late_even_if_unknown(self):
  for arrived in [False,None,True]:self.assertEqual(overdue_claim('12:40','13:15',arrived)['verdict'],'contradicted')
 def test_due_now_is_not_past_deadline(self):
  for arrived in [False,None,True]:self.assertEqual(overdue_claim('13:15','13:15',arrived)['verdict'],'contradicted')
 def test_past_deadline_requires_known_absence(self):
  self.assertEqual(overdue_claim('13:30','13:15',False),dict(verdict='supported',minutes_to_schedule=-15,arrival_state='overdue'))
 def test_unknown_arrival_after_deadline_is_not_absence(self):
  self.assertEqual(overdue_claim('13:30','13:15',None)['verdict'],'not_established')
 def test_known_arrival_contradicts_still_absent_not_retrospective_lateness(self):
  self.assertEqual(overdue_claim('13:30','13:15',True)['verdict'],'contradicted')
 def test_ambiguous_clock_and_truthy_flags_are_rejected(self):
  for flag in [0,1,'false']:
   with self.assertRaises(ValueError):overdue_claim('13:30','13:15',flag)
  with self.assertRaises(ValueError):overdue_claim('1:30','13:15',False)
 def test_twenty_sixth_update_allowed_twenty_seventh_stops(self):
  guard=load('guards').resource_violation
  self.assertIsNone(guard(dict(step=26,loss=1.0,peak_memory_gb=10)))
  self.assertIsNotNone(guard(dict(step=27)))
 def test_claim_json_rejects_boolean_minutes_and_duplicate_keys(self):
  score=load('scoring').claim_match;e=overdue_claim('13:15','13:15',False)
  self.assertTrue(score('{"arrival_state":"due_now","minutes_to_schedule":0,"verdict":"contradicted"}',e))
  for s in ['{"arrival_state":"due_now","minutes_to_schedule":false,"verdict":"contradicted"}','{"arrival_state":"due_now","minutes_to_schedule":0,"verdict":"supported","verdict":"contradicted"}']:
   self.assertFalse(score(s,e))
