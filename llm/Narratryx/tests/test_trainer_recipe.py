import copy
import unittest
from foundation.trainer_recipe import validate_token_row, token_multiset, validate_plan


class TrainerRecipeTests(unittest.TestCase):
    def fixture(self):
        p=dict(training=dict(records=28,presentations=28,broader_prose=20,semantic_repairs=5,structural_edits=3,monitor_records=16,epochs=1,batch_size=1,gradient_accumulation=1,learning_rate='5e-5',lora_rank=8,lora_alpha=16,lora_dropout=0,seed=42),training_steps=28,context_limit=2048,evaluation=dict(primary_cases=44,exposed_primary=44,new_unrun_primary=0,seen_training_fit_cases=5,conditions=['base','current-craft','candidate'],primary_requests=132,seen_fit_requests=15,total_requests=147,max_new_tokens=384,temperature=0,seed=42,repetition_penalty=1.0,fresh_context=True),resource_stop=dict(max_steps=28,peak_mlx_gb=10,process_tree_rss_bytes=10000000000,phase_deadline_seconds=1200,stop_on_warning_error_nonfinite_or_truncation=True))
        q=dict(max_steps=28,num_epochs=1,batch_size=1,gradient_accumulation_steps=1,learning_rate='5e-5',save_steps=28,eval_steps=28,max_seq_length=2048,warmup_steps=2,resume_from_checkpoint=None,packing=False,train_on_completions=True,random_seed=42,model_random_state=42,lora_random_state=42,lora_r=8,lora_alpha=16,lora_dropout=0,trust_remote_code=False,hf_dataset=None)
        a=dict(training_records=28,monitor_records=16,supervised_training_tokens=3033,all_preprocessing_unchanged=True,collated_multiset_matches=True,worker_configuration_checked=True)
        return p,q,a

    def test_consistent_plan(self):
        self.assertTrue(validate_plan(*self.fixture()))

    def test_caps_resume_and_seen_fit_cannot_drift(self):
        for key,value in [('max_steps',56),('resume_from_checkpoint','prior'),('packing',True)]:
            p,q,a=self.fixture();q[key]=value
            with self.assertRaises(ValueError):validate_plan(p,q,a)
        p,q,a=self.fixture();p['evaluation']['new_unrun_primary']=8
        with self.assertRaises(ValueError):validate_plan(p,q,a)
        p,q,a=self.fixture();p['resource_stop']['peak_mlx_gb']=11
        with self.assertRaises(ValueError):validate_plan(p,q,a)

    def test_missing_masks_and_truncated_targets_rejected(self):
        row=dict(input_ids=[1,2,3,9],labels=[-100,-100,3,9],attention_mask=[1]*4)
        self.assertEqual(validate_token_row(row,9),2)
        for key,value in [('labels',[1,2,3,9]),('labels',[-100,-100,-100,-100]),('input_ids',[1,2,3])]:
            bad=copy.deepcopy(row);bad[key]=value
            with self.assertRaises(ValueError):validate_token_row(bad,9)

    def test_batch_multiset_detects_duplicate_replacing_missing_record(self):
        a=dict(input_ids=[1,2],labels=[-100,2]);b=dict(input_ids=[3,4],labels=[-100,4])
        self.assertNotEqual(token_multiset([a,b]),token_multiset([a,a]))
