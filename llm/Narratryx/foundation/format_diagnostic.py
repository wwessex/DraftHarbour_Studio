"""Balanced evaluation-only entity binding cases and transparent scoring proxies."""
import json
import re
from itertools import product

ENTITIES={'original','duplicate'}


def factor_cases():
    rows=[]
    questions={'legibility':'Which register’s legibility is unknown?', 'inspection':'Which register has not been inspected?'}
    for known,first,question,fmt in product(['original','duplicate'],['original','duplicate'],questions,['token','json-answer','json-unknown']):
        unknown=next(x for x in ENTITIES if x!=known)
        facts={known:f'The {known} register has been inspected and is readable.',unknown:f'The {unknown} register has not been inspected, and its legibility is unknown.'}
        other=next(x for x in ENTITIES if x!=first)
        key='answer' if fmt=='json-answer' else 'unknown_object'
        instruction='Return only one lowercase word: original or duplicate.' if fmt=='token' else f'Return JSON only with exactly one key, "{key}". Its value must be the lowercase string "original" or "duplicate".'
        prompt=facts[first]+' '+facts[other]+'\n\n'+questions[question]+'\n'+instruction
        rows.append(dict(id=f'fd17-{known}-{first}-{question}-{fmt}',cohort='balanced-factorial',known_object=known,unknown_object=unknown,first_fact_object=first,question=question,format=fmt,
                         expected_key=None if fmt=='token' else key,expected_entity=unknown,prompt=prompt,training_eligible=False,
                         provenance='Constructed evaluation-only state; no literary teaching target or human benchmark approval.'))
    return rows


def parse_json(text):
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('duplicate key')
            result[k]=v
        return result
    return json.loads(text,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))


def score(text,case):
    """Entity is a response-selection proxy, never evidence of literary reasoning."""
    stripped=text.strip();value=None;json_ok=False
    try:value=parse_json(stripped);json_ok=True
    except (ValueError,TypeError):pass
    anchor=case['cohort']=='exposed-original-control'
    fmt=case['format'];key=case.get('expected_key');entity=None;mode='unassessable'
    if json_ok and isinstance(value,dict):
        if key in value and type(value[key]) is str and value[key] in ENTITIES:
            entity=value[key];mode='requested-field'
        else:
            candidates={v for v in value.values() if type(v) is str and v in ENTITIES}
            if len(candidates)==1:entity=candidates.pop();mode='lone-json-entity-proxy'
    elif not json_ok:
        # Wrong-format plain answers can still identify an entity. Both names
        # in explanatory text are ambiguous and are never guessed into a pass.
        candidates=set(re.findall(r'\b(original|duplicate)\b',stripped.casefold()))
        if len(candidates)==1:entity=candidates.pop();mode='unique-lexical-entity-proxy'
    if anchor:
        format_ok=json_ok and isinstance(value,dict) and set(value)=={'unknown_object','original_readable'} and type(value.get('unknown_object')) is str and value['unknown_object'] in ENTITIES and type(value.get('original_readable')) is bool
        exact=format_ok and value==case['expected_json']
    elif fmt=='token':
        format_ok=stripped in ENTITIES;exact=format_ok and stripped==case['expected_entity']
    else:
        format_ok=json_ok and isinstance(value,dict) and set(value)=={key} and type(value[key]) is str and value[key] in ENTITIES
        exact=format_ok and value[key]==case['expected_entity']
    return dict(format_compliant=bool(format_ok),entity=entity,entity_extraction_mode=mode,
                entity_correct=entity==case['expected_entity'] if entity is not None else None,exact_task_correct=bool(exact))
