"""Cross-check unique lessons, repeated presentations and executable caps."""
def validate_plan(protocol,request,preflight,selection):
 t=protocol['training']
 expected={'records':92,'presentations':128,'prose_records':56,'structural_records':36,'focused_unique_records':12,'focused_exposures':4,'max_steps':128,'epochs':1,'batch_size':1,'gradient_accumulation':1,'context_limit':2048}
 for k,v in expected.items():
  if t.get(k)!=v:raise ValueError('Metadata mismatch: '+k)
 for k,other in [('max_steps','max_steps'),('epochs','num_epochs'),('batch_size','batch_size'),('gradient_accumulation','gradient_accumulation_steps'),('context_limit','max_seq_length')]:
  if t[k]!=request[other]:raise ValueError('Executable mismatch: '+k)
 if float(t['learning_rate'])!=float(request['learning_rate']):raise ValueError('Learning rate mismatch')
 if protocol['training_steps']!=128 or protocol['resource_stop']['max_steps']!=128:raise ValueError('Step cap mismatch')
 if preflight['unique_training_records']!=92 or preflight['training_presentations']!=128 or selection['unique_training_records']!=92 or len(selection['presentation_order'])!=128:raise ValueError('Presentation count mismatch')
 if preflight['supervised_train_tokens']!=10173 or preflight['prose_supervised_tokens']!=8686:raise ValueError('Token exposure mismatch')
 return True
