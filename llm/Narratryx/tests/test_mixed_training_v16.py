import copy
import importlib.util
import json
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def load(name):
    p=ROOT/'curation/mixed-training-v16'/(name+'.py');s=importlib.util.spec_from_file_location('mixed16_'+name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m


class MixedTrainingPlanTests(unittest.TestCase):
    def fixture(self):
        p=dict(training=dict(records=22,presentations=22,broader_prose=14,semantic_repairs=5,structural_edits=3,monitor_records=16,epochs=1,batch_size=1,gradient_accumulation=1,learning_rate='5e-5',lora_rank=8,lora_alpha=16,lora_dropout=0,seed=42),training_steps=22,context_limit=2048,
               evaluation=dict(primary_cases=44,new_unrun_primary=8,exposed_primary=36,seen_training_fit_cases=5,conditions=['base','current-craft','candidate'],primary_requests=132,seen_fit_requests=15,total_requests=147,max_new_tokens=384,temperature=0,seed=42,repetition_penalty=1.0,fresh_context=True),resource_stop=dict(max_steps=22))
        r=dict(max_steps=22,num_epochs=1,batch_size=1,gradient_accumulation_steps=1,learning_rate='5e-5',save_steps=22,eval_steps=22,max_seq_length=2048,warmup_steps=2,resume_from_checkpoint=None)
        t=dict(training_records=22,presentations=22,monitor_records=16,supervised_training_tokens=2449,collated_multiset_matches=True)
        return p,r,t

    def test_frozen_plan_is_consistent(self):self.assertTrue(load('plan_checks').validate_plan(*self.fixture()))

    def test_seen_fit_cannot_be_relabelled_as_primary(self):
        p,r,t=self.fixture();p['evaluation']['primary_cases']=49
        with self.assertRaises(ValueError):load('plan_checks').validate_plan(p,r,t)

    def test_more_updates_or_resume_rejected(self):
        for key,value in [('max_steps',25),('resume_from_checkpoint','old')]:
            p,r,t=self.fixture();r[key]=value
            with self.assertRaises(ValueError):load('plan_checks').validate_plan(p,r,t)

    def test_resource_caps_and_nonfinite_progress(self):
        f=load('guards').resource_violation
        self.assertIsNone(f(dict(step=22,loss=1.,peak_memory_gb=10)))
        for p in [dict(step=23),dict(loss=float('nan')),dict(warnings=['bad']),dict(error='bad'),dict(peak_memory_gb=10.1)]:self.assertIsNotNone(f(p))
