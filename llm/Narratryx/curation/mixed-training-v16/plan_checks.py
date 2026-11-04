"""Reject stale counts or changed caps before the authorised local pilot starts."""
def validate_plan(p,r,t):
    expected=dict(records=22,presentations=22,broader_prose=14,semantic_repairs=5,structural_edits=3,monitor_records=16,epochs=1,batch_size=1,gradient_accumulation=1,learning_rate='5e-5',lora_rank=8,lora_alpha=16,lora_dropout=0,seed=42)
    if p['training']!=expected or p['training_steps']!=22 or p['context_limit']!=2048:
        raise ValueError('mixed training description mismatch')
    for key,value in dict(max_steps=22,num_epochs=1,batch_size=1,gradient_accumulation_steps=1,learning_rate='5e-5',save_steps=22,eval_steps=22,max_seq_length=2048,warmup_steps=2,resume_from_checkpoint=None).items():
        if r[key]!=value:raise ValueError('executable recipe mismatch: '+key)
    e=p['evaluation']
    for key,value in dict(primary_cases=44,new_unrun_primary=8,exposed_primary=36,seen_training_fit_cases=5,conditions=['base','current-craft','candidate'],primary_requests=132,seen_fit_requests=15,total_requests=147,max_new_tokens=384,temperature=0,seed=42,repetition_penalty=1.0,fresh_context=True).items():
        if e[key]!=value:raise ValueError('evaluation cohort mismatch: '+key)
    if t['training_records']!=22 or t['presentations']!=22 or t['monitor_records']!=16 or t['supervised_training_tokens']!=2449 or not t['collated_multiset_matches']:
        raise ValueError('token dataset mismatch')
    if p['resource_stop']['max_steps']!=22:raise ValueError('resource update cap mismatch')
    return True
