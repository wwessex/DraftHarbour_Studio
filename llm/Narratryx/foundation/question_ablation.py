"""Matched direct-question addition; evaluation only, never training material."""
from foundation.binding_ablation import cases as background_cases, diagnose

QUESTION = "Which register's legibility is unknown? "


def cases():
    rows = []
    for background in background_cases():
        for direct in [False, True]:
            row = dict(background)
            row.update(id=background['id'].replace('ba17-', 'qa18-') + f'-{int(direct)}',
                       pair_id=background['id'], direct_question=direct,
                       cohort='matched-direct-question-ablation',
                       provenance='Exploratory evaluation after v17b; no training eligibility or independent confirmation.')
            if direct:
                facts, instruction = background['prompt'].split('Return JSON only', 1)
                row['prompt'] = facts + QUESTION + 'Return JSON only' + instruction
            rows.append(row)
    return rows
