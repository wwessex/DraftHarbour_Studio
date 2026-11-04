"""New original diagnostic fiction, evaluation only; never literary teaching targets."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'artifacts/revision-preflight-v1/test.cases.jsonl'
TIMED = [
    ('silk-conservation', 'Esme', 'Hugo', '08:10', '08:45', '09:20',
     'sealed a silk panel in a storage box', 'a loose blue thread lay beside the box',
     'Esme set the the sealed box on the padded table.'),
    ('saffron-cooperative', 'Farah', 'Lin', '12:05', '12:40', '13:15',
     'counted the labelled saffron jars', 'a torn label lay on the packing bench',
     'Farah placed the counted counted jars in a wooden crate.'),
    ('glass-kiln', 'Niko', 'Maren', '17:10', '17:45', '18:30',
     'switched off the glass kiln', 'a cracked test tile lay beside the controls',
     'Niko left the kiln door firmly firmly closed.'),
    ('ferry-parcel-office', 'June', 'Tomas', '06:20', '06:55', '07:30',
     'logged a parcel in the ferry-office register', 'a piece of red twine lay on the desk',
     'June checked the register before before locking the drawer.'),
]
SCENES = [
    ('seed-library', 'Vera wants to lend the final packet of beans to a school garden. Alden must keep a viable sample for next season. The packet contains twelve seeds, and the school bus leaves in ten minutes. Neither has counted how many seeds are viable.'),
    ('rehearsal-room', 'Imani wants the quartet to try her new ending tonight. Pavel has promised the hall caretaker they will leave at nine. It is eight fifty, and the violist has a broken string. No replacement string has been found.'),
    ('mountain-shelter', 'Orla wants to descend before fog hides the trail markers. Ben wants to wait for their overdue companion. They have one working torch and enough tea for three people. They have received no message from the companion.'),
    ('community-kitchen', 'Sana needs the only large pot for the evening soup. Ellis has filled it with pears promised to the neighbours. The soup guests arrive in twenty minutes. There is a clean small saucepan, but nobody has checked whether it will hold all the pears.'),
]


def cases():
    result = []
    for world, actor, visitor, past, now, future, action, clue, broken in TIMED:
        context = (f'At {past}, {actor} {action}. It is now {now}. {visitor} is expected at {future} and has not arrived. '
                   f'At the present moment, {clue}. Who left it there is unknown.')
        prefix = dict(scenario_id=world, context=context,
                      provenance='Original Codex AI-authored diagnostic fiction; evaluation only, not training data or human-approved formal benchmark.',
                      established_facts=[f'{actor} completed the stated action at {past}.',
                                         f'Present time is {now}.', f'{visitor} has not arrived; expected at {future}.'],
                      unknowns=['Who left the discovered object; intention or guilt is not established.'])
        result.append({**prefix, 'id': world + '-copyedit', 'kind': 'minimal-copyedit', 'task': 'editing',
                       'prompt': 'Remove only the accidentally repeated consecutive word. Preserve all other characters. Return only the corrected sentence.\n\n' + broken,
                       'exact_reference': broken.replace('the the', 'the').replace('counted counted', 'counted').replace('firmly firmly', 'firmly').replace('before before', 'before'),
                       'word_count_min': None, 'word_count_max': None})
        result.append({**prefix, 'id': world + '-chronology', 'kind': 'chronology-rewrite', 'task': 'editing',
                       'prompt': 'Rewrite the passage as clear, restrained story prose in at most90words. Preserve all times, what has already happened, what is still expected and what remains unknown. Do not add an arrival or an explanation for the discovered object. Return only the prose.\n\n' + context,
                       'exact_reference': None, 'word_count_min': None, 'word_count_max': 90})
        result.append({**prefix, 'id': world + '-analysis', 'kind': 'grounded-analysis', 'task': 'analysis',
                       'prompt': 'In at most70words, identify one explicit fact, one cautious inference and one unresolved question. Label each. An inference must be supported and marked uncertain; do not invent who left the object.\n\n' + context,
                       'exact_reference': None, 'word_count_min': None, 'word_count_max': 70})
    for world, context in SCENES:
        prefix = dict(scenario_id=world, context=context,
                      provenance='Original Codex AI-authored diagnostic fiction; evaluation only, not training data or human-approved formal benchmark.',
                      established_facts=[context], unknowns=['Unresolved information in the context must not silently become established fact.'])
        for kind, task, instruction, low, high in [
            ('dialogue', 'dialogue', 'Write four to six spoken turns, each as a separate quoted paragraph, with optional brief action beats. Let the two established characters respond to each other and negotiate their conflicting goals. Keep within100words. No heading or explanation.', None, 100),
            ('pacing', 'pacing', 'Write a tense scene of at most85words. Start with the practical obstacle, accelerate through an attempted action, then end with a consequence or new decision. Preserve the given resources and unresolved facts. No heading or commentary.', None, 85),
            ('continue', 'fiction', 'Continue the scene in60–90words. Add only the new paragraph, preserving characters, resources and uncertainty. Let one concrete action move their problem forward without simply announcing everything is solved. No heading or commentary.', 60, 90),
        ]:
            result.append({**prefix, 'id': world + '-' + kind, 'kind': kind, 'task': task,
                           'prompt': instruction + '\n\nCONTEXT:\n' + context,
                           'exact_reference': None, 'word_count_min': low, 'word_count_max': high})
    return result


if __name__ == '__main__':
    with OUT.open('x', encoding='utf-8') as f:
        for row in cases():
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    print('Prepared24 evaluation-only cases across eight new scenarios; no training targets.')
