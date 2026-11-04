"""Single training-field ablation, not an undocumented recipe change."""
def validate_ablation(old,new,protocol):
 if set(old)!=set(new) or {k for k in old if old[k]!=new[k]}!={'learning_rate'}:raise ValueError('Only learning rate may change')
 if float(old['learning_rate'])!=2e-4 or float(new['learning_rate'])!=5e-5:raise ValueError('Unexpected rates')
 if protocol['training_steps']!=128 or protocol['training']['max_steps']!=128 or new['max_steps']!=128:raise ValueError('Update cap mismatch')
 if protocol['training']['records']!=92 or protocol['training']['presentations']!=128:raise ValueError('Dataset description mismatch')
 if float(protocol['training']['learning_rate'])!=float(new['learning_rate']):raise ValueError('Rate description mismatch')
 return True
