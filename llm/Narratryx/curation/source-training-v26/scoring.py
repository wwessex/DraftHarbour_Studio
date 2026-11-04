"""Strict closed-task labels, not literary judgement."""
import json


def strict_json_match(text,expected):
    def pairs(items):
        result={}
        for k,v in items:
            if k in result:raise ValueError('duplicate key')
            result[k]=v
        return result
    try:
        actual=json.loads(text,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    except (ValueError,TypeError):return False
    return isinstance(actual,dict) and set(actual)==set(expected) and all(type(actual[k]) is type(v) and actual[k]==v for k,v in expected.items())
