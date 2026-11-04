import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def load(name):
    p=ROOT/'curation/task-matched-v13'/(name+'.py')
    spec=importlib.util.spec_from_file_location('task13_'+name,p)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


class TaskMatchedPilotTests(unittest.TestCase):
    def fixture(self):
        p=dict(training=dict(records=25,presentations=25,monitor_records=16,max_steps=25,epochs=1,batch_size=1,gradient_accumulation=1,learning_rate='5e-5',context_limit=2048),training_steps=25,
               evaluation=dict(cases=36,new_unrun_cases=12,exposed_cases=24,conditions=3,planned_requests=108,max_new_tokens=384,temperature=0,seed=42,repetition_penalty=1.0))
        r=dict(max_steps=25,num_epochs=1,batch_size=1,gradient_accumulation_steps=1,learning_rate='5e-5',max_seq_length=2048,save_steps=25,eval_steps=25,warmup_steps=2,resume_from_checkpoint=None)
        t=dict(train_records=25,monitor_records=16,supervised_train_tokens=2298,collated_multiset_matches=True)
        return p,r,t

    def test_consistent_bounded_plan(self):
        self.assertTrue(load('plan_checks').validate_plan(*self.fixture()))

    def test_stale_exposure_and_update_counts_rejected(self):
        for group,key,value in [('training','presentations',128),('evaluation','planned_requests',24)]:
            p,r,t=self.fixture();p[group][key]=value
            with self.assertRaises(ValueError):load('plan_checks').validate_plan(p,r,t)

    def test_resume_or_unverified_collation_rejected(self):
        p,r,t=self.fixture();r['resume_from_checkpoint']='prior'
        with self.assertRaises(ValueError):load('plan_checks').validate_plan(p,r,t)
        p,r,t=self.fixture();t['collated_multiset_matches']=False
        with self.assertRaises(ValueError):load('plan_checks').validate_plan(p,r,t)

    def test_caps_warning_and_nonfinite_guards(self):
        check=load('guards').resource_violation
        self.assertIsNone(check(dict(step=25,loss=1.,peak_memory_gb=10)))
        for value in [dict(step=26),dict(warnings=['warning']),dict(error='error'),dict(loss=float('nan')),dict(peak_memory_gb=10.1)]:
            self.assertIsNotNone(check(value))
