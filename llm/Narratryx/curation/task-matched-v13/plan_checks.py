"""Fail closed on stale recipe and evaluation descriptions before loading weights."""
def validate_plan(protocol, request, tokens):
    expected = dict(records=25, presentations=25, monitor_records=16, max_steps=25,
                    epochs=1, batch_size=1, gradient_accumulation=1, learning_rate='5e-5', context_limit=2048)
    if protocol['training'] != expected:
        raise ValueError('inconsistent training description')
    for key, value in dict(max_steps=25, num_epochs=1, batch_size=1, gradient_accumulation_steps=1,
                           learning_rate='5e-5', max_seq_length=2048, save_steps=25, eval_steps=25,
                           warmup_steps=2, resume_from_checkpoint=None).items():
        if request[key] != value:
            raise ValueError('inconsistent executable request: ' + key)
    if tokens['train_records'] != 25 or tokens['monitor_records'] != 16 or tokens['supervised_train_tokens'] != 2298:
        raise ValueError('unexpected token dataset')
    if not tokens['collated_multiset_matches'] or protocol['training_steps'] != 25:
        raise ValueError('collation or update cap mismatch')
    if protocol['evaluation'] != dict(cases=36, new_unrun_cases=12, exposed_cases=24, conditions=3,
                                      planned_requests=108, max_new_tokens=384, temperature=0, seed=42, repetition_penalty=1.0):
        raise ValueError('inconsistent evaluation description')
    return True
