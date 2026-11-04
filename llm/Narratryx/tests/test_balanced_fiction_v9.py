import importlib.util
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 p=ROOT/'curation/balanced-fiction-v9'/(name+'.py');s=importlib.util.spec_from_file_location('balanced_v9_'+name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class BalancedFictionPlanTests(unittest.TestCase):
 def fixture(self):
  t=dict(records=92,presentations=128,prose_records=56,structural_records=36,focused_unique_records=12,focused_exposures=4,max_steps=128,epochs=1,batch_size=1,gradient_accumulation=1,context_limit=2048,learning_rate='2e-4')
  p=dict(training=t,training_steps=128,resource_stop=dict(max_steps=128));r=dict(max_steps=128,num_epochs=1,batch_size=1,gradient_accumulation_steps=1,max_seq_length=2048,learning_rate='2e-4')
  f=dict(unique_training_records=92,training_presentations=128,supervised_train_tokens=10173,prose_supervised_tokens=8686);s=dict(unique_training_records=92,presentation_order=['id']*128)
  return p,r,f,s
 def test_distinct_lessons_and_repeated_presentations_are_separate(self):
  self.assertTrue(load('plan_checks').validate_plan(*self.fixture()))
 def test_stale_unique_count_or_exposure_count_rejected(self):
  for key,value in [('records',104),('presentations',92)]:
   p,r,f,s=self.fixture();p['training'][key]=value
   with self.assertRaises(ValueError):load('plan_checks').validate_plan(p,r,f,s)
 def test_update_limit(self):
  guard=load('guards').resource_violation
  self.assertIsNone(guard(dict(step=128,loss=1.,peak_memory_gb=10)))
  self.assertIsNotNone(guard(dict(step=129)))
 def test_warning_memory_and_nonfinite_stop(self):
  guard=load('guards').resource_violation
  for p in [dict(warnings=['bad']),dict(error='bad'),dict(peak_memory_gb=10.1),dict(loss=float('nan'))]:self.assertIsNotNone(guard(p))
