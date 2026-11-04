import importlib.util
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'curation/source-training-v22'


def load(name):
    spec=importlib.util.spec_from_file_location('source22_'+name,HERE/(name+'.py'))
    module=importlib.util.module_from_spec(spec)
    sys.path.insert(0,str(HERE))
    try:spec.loader.exec_module(module)
    finally:sys.path.pop(0)
    return module


class SourceTrainingV22Tests(unittest.TestCase):
    def test_resource_guards_stop_overshoot_and_nonfinite_values(self):
        guard=load('guards').resource_violation
        self.assertIsNone(guard(dict(step=28,loss=1.,peak_memory_gb=10)))
        for p in [dict(step=29),dict(loss=float('nan')),dict(eval_loss=float('inf')),dict(warnings=['bad']),dict(error='bad'),dict(peak_memory_gb=10.01)]:
            self.assertIsNotNone(guard(p))

    def test_exposed_cases_not_called_new_and_seen_kept_separate(self):
        score=load('report').score_case
        row=dict(text='{"answer":true}',error=None,finish_reason='stop')
        case=dict(id='sr14-example',kind='closed',expected_json={'answer':True})
        d=score('candidate',case,row)
        self.assertEqual(d['cohort'],'focused-exposed');self.assertTrue(d['structured_exact'])
        self.assertFalse(score('candidate',case,dict(row,finish_reason='length'))['structured_exact'])
        seen=dict(id='seen-example',kind='seen-source-repair',corruption=dict(source_answer='The gull.',start=4,source_end=8,original='gull',wrong='tern'))
        fit=score('candidate',seen,dict(text='The gull.',error=None,finish_reason='stop'))
        self.assertEqual(fit['cohort'],'seen-training-fit');self.assertTrue(fit['exact_full_answer'])

    def test_repeat_flag_separate_from_word_limit(self):
        score=load('report').score_case
        text='Mina: We can inspect this separate copy first.\nEwan: We can inspect this separate copy first.'
        d=score('candidate',dict(id='legacy',kind='dialogue',word_count_min=None,word_count_max=100),dict(text=text,error=None,finish_reason='stop'))
        self.assertTrue(d['word_limit_passed']);self.assertTrue(d['dialogue_repeat_flag'])
