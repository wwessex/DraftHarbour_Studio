import importlib.util
from pathlib import Path
import unittest
p=Path(__file__).resolve().parents[1]/'curation/tiny-fit-v8b/guards.py'
s=importlib.util.spec_from_file_location('tiny_fit_guards',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class TinyFitGuardsTests(unittest.TestCase):
 def test_update_bound(self):
  self.assertIsNone(m.resource_violation(dict(step=48,loss=1.,peak_memory_gb=10)))
  self.assertIsNotNone(m.resource_violation(dict(step=49)))
 def test_resource_and_metric_failures_stop(self):
  for x in [dict(warnings=['bad']),dict(error='bad'),dict(loss=float('nan')),dict(peak_memory_gb=10.1)]:self.assertIsNotNone(m.resource_violation(x))

class TinyFitPlanTests(unittest.TestCase):
 def load(self):
  import json
  root=Path(__file__).resolve().parents[1]
  path=root/'curation/tiny-fit-v8b/plan_checks.py'
  spec=importlib.util.spec_from_file_location('tiny_plan',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  request=dict(max_steps=48,num_epochs=4,batch_size=1,gradient_accumulation_steps=1,max_seq_length=2048,learning_rate='2e-4')
  protocol=dict(training=dict(records=12,max_steps=48,epochs=4,batch_size=1,gradient_accumulation=1,context_limit=2048,learning_rate='2e-4'),training_steps=48,resource_stop=dict(max_steps=48))
  return module,protocol,request,dict(records=12,passes=4)
 def test_matching_plan_is_accepted(self):
  m,p,r,f=self.load();self.assertTrue(m.validate_plan(p,r,f))
 def test_stale_descriptive_dataset_and_update_counts_rejected(self):
  m,p,r,f=self.load();p['training']['records']=104;p['training']['max_steps']=26
  with self.assertRaises(ValueError):m.validate_plan(p,r,f)
