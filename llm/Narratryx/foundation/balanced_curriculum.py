"""Stable source-aware retention selection; no model imports or literary generation."""
from collections import Counter, defaultdict
import re

from foundation.validation import Invalid


def source_unit(row):
    return ' '.join(row['source_spans'][-1]['text'].casefold().split())


def balanced_take(candidates, count, used=(), existing=()):
    seen = set(used)
    groups = defaultdict(list)
    for row in candidates:
        groups[row['source_work_ids'][0]].append(row)
    picked = []
    while len(picked) < count:
        counts = Counter(r['source_work_ids'][0] for r in list(existing)+picked)
        changed = False
        for work in sorted(groups, key=lambda w:(counts[w], w)):
            while groups[work]:
                row = groups[work].pop(0)
                unit = source_unit(row)
                if unit in seen:
                    continue
                picked.append(row)
                seen.add(unit)
                changed = True
                break
            if len(picked) == count:
                break
        if not changed:
            raise Invalid('insufficient distinct source units for retention quota')
    return picked, seen


def retain_prose(candidates):
    rows = [r for r in candidates if r['split']=='train'
            and not r['messages'][-1]['content'].lstrip().startswith('{')]
    selected, used, membership = [], set(), {}
    def take(pool, count, kind):
        nonlocal used
        chosen, used = balanced_take(pool, count, used, selected)
        selected.extend(chosen)
        membership.update({r['id']:kind for r in chosen})
    for task, count in [('storytelling',2),('editing',2),('pacing',3),('dialogue',8),('analysis',8)]:
        take([r for r in rows if r['task']==task and
              (task!='editing' or r['id'].startswith('james-'))], count, 'prose-'+task)
    is_continue = lambda r:bool(re.search(r'\bContinue\b',r['messages'][0]['content'][:180]))
    take([r for r in rows if r['task']=='fiction' and is_continue(r)
          and len(r['messages'][-1]['content'].split())>=20],8,'prose-continue')
    take([r for r in rows if r['task']=='fiction' and not is_continue(r)],25,'prose-write')
    if len(selected)!=56 or len(used)!=56:
        raise Invalid('retention plan must contain56 distinct supporting passages')
    return selected, membership
