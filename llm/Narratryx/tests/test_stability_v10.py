import importlib.util
from pathlib import Path
import unittest
HERE=Path(__file__).resolve().parents[1]/'curation/stability-v10'
def load(name):
 s=importlib.util.spec_from_file_location('stability_v10_'+name,HERE/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class StabilityAblationTests(unittest.TestCase):
 def fixture(self):
  old=dict(learning_rate='2e-4',max_steps=128,gradient_accumulation_steps=1,num_epochs=1)
  new=dict(old,learning_rate='5e-5');p=dict(training_steps=128,training=dict(max_steps=128,records=92,presentations=128,learning_rate='5e-5'))
  return old,new,p
 def test_only_rate_change_accepted(self):self.assertTrue(load('plan_checks').validate_ablation(*self.fixture()))
 def test_accumulation_change_rejected(self):
  a,b,p=self.fixture();b['gradient_accumulation_steps']=4
  with self.assertRaises(ValueError):load('plan_checks').validate_ablation(a,b,p)
 def test_identical_long_utterance_across_speakers_detected(self):
  text='Jules: I need that reel because it is the only recording.\nAnika: I need that reel because it is the only recording.'
  self.assertEqual(load('stability_checks').repeated_dialogue(text),2)
 def test_short_acknowledgements_and_distinct_aims_not_flagged(self):
  f=load('stability_checks').repeated_dialogue
  self.assertEqual(f('Cora: No.\nDevin: No.'),0)
  self.assertEqual(f('Cora: I want to preserve the inherited coat.\nDevin: I need to make it wearable for the play.'),1)
 def test_update_and_resource_guards(self):
  f=load('guards').resource_violation
  self.assertIsNone(f(dict(step=128,peak_memory_gb=10,loss=1.)))
  for r in [dict(step=129),dict(peak_memory_gb=10.1),dict(loss=float('nan')),dict(warnings=['bad'])]:self.assertIsNotNone(f(r))
