"""Reject contradictory descriptive/executable experiment plans."""
def validate_plan(protocol,request,preflight):
 expected={'records':preflight['records'],'max_steps':request['max_steps'],'epochs':request['num_epochs'],'batch_size':request['batch_size'],'gradient_accumulation':request['gradient_accumulation_steps'],'context_limit':request['max_seq_length']}
 for key,value in expected.items():
  if protocol['training'].get(key)!=value:raise ValueError('Plan mismatch: '+key)
 if float(protocol['training']['learning_rate'])!=float(request['learning_rate']):raise ValueError('Plan mismatch: learning_rate')
 if protocol['training_steps']!=request['max_steps'] or protocol['resource_stop']['max_steps']!=request['max_steps']:raise ValueError('Plan mismatch: update caps')
 if preflight['passes']!=request['num_epochs']:raise ValueError('Plan mismatch: passes')
 return True
