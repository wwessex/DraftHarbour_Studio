"""Strict structural checks, kept separate from literary or semantic quality ratings."""
import json


def clock_match(text,expected):
    def pairs(items):
        value={}
        for key,item in items:
            if key in value:raise ValueError('duplicate key')
            value[key]=item
        return value
    try:
        value=json.loads(text,object_pairs_hook=pairs,
                         parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))
    except (TypeError,ValueError):return False
    return (isinstance(value,dict) and set(value)=={'state','minutes_to_schedule'}
            and type(value['state']) is str and type(value['minutes_to_schedule']) is int
            and value==expected)
