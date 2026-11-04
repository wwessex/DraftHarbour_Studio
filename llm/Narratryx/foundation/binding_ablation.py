"""Exploratory follow-up, separately frozen after the v17 format diagnostic."""
from itertools import product
from foundation.format_diagnostic import score,parse_json


def cases():
    rows=[]
    for known,first,explicit,fields in product(['original','duplicate'],['original','duplicate'],[False,True],[1,2]):
        unknown='duplicate' if known=='original' else 'original'
        unknown_sentence=('A duplicate' if unknown=='duplicate' else 'An original')+' has not been inspected.'
        if explicit:unknown_sentence+=' Its legibility is unknown.'
        facts={known:f'The {known} register is readable.',unknown:unknown_sentence}
        second='duplicate' if first=='original' else 'original'
        instruction='Return JSON only with unknown_object (original/duplicate)'
        if fields==2:instruction+=f' and {known}_readable (boolean)'
        prompt=facts[first]+' '+facts[second]+' '+instruction+'. Do not invent an inspection.'
        expected={'unknown_object':unknown}
        if fields==2:expected[known+'_readable']=True
        rows.append(dict(id=f'ba17-{known}-{first}-{int(explicit)}-{fields}',cohort='exploratory-cue-field-ablation',format='json-unknown',expected_key='unknown_object',
                         known_object=known,first_fact_object=first,unknown_cue_explicit=explicit,field_count=fields,expected_entity=unknown,expected_json=expected,
                         prompt=prompt,training_eligible=False,provenance='Evaluation-only follow-up designed after v17 results; not independent confirmation or a literary teaching target.'))
    return rows


def diagnose(text,case):
    result=score(text,case)
    try:value=parse_json(text.strip())
    except (ValueError,TypeError):value=None
    expected=case['expected_json']
    compliant=isinstance(value,dict) and set(value)==set(expected) and all(type(value[k]) is type(v) for k,v in expected.items())
    if compliant:compliant=value['unknown_object'] in ['original','duplicate']
    result.update(format_compliant=bool(compliant),exact_task_correct=bool(compliant and value==expected))
    return result
