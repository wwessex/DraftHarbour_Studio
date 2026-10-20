"""Bounded, source-only craft pilot. Does not train, download or change approvals."""
from pathlib import Path
import hashlib, json, re, sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import digest, validate_dataset, validate_schema

OUT = ROOT / 'artifacts/craft-expansion-v1'
RAW = ROOT / 'rights/raw/craft-expansion-2026-10-20'
DATE = '2026-10-20'

def write(name, value):
    with (OUT / name).open('x') as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write('\n')

def rows(name, data):
    with (OUT / name).open('x') as f:
        for row in data:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

def norm(s):
    return ' '.join(s.split())

SELECTION = {
    'wharton': {
        17: 'How does choosing a reflecting consciousness constrain a story’s observations and metaphors?',
        25: 'Explain Wharton’s proposal for placing dialogue at narrative climaxes and its effect on the passage of time.',
        26: 'What problems does Wharton identify when dialogue is made to carry too much narrative exposition?',
        27: 'How does Wharton distinguish the typical short story’s scale from the novel’s?',
        30: 'What test does Wharton propose before adding another character to a story?',
        31: 'When does Wharton consider a change of reflecting consciousness necessary?',
    },
    'hamilton': {
        26: 'Explain Hamilton’s account of the relationship between character, action and setting in a narrative event.',
        29: 'How does Hamilton distinguish a representative fictional character from an individualized one?',
        31: 'When does Hamilton consider direct psychological analysis useful, and when can it become intrusive?',
        45: 'Why might an author choose a subsidiary actor to narrate an extraordinary protagonist’s story?',
        47: 'What advantages and structural problems does Hamilton identify in an exchange-of-letters narrative?',
        48: 'What changes when an epistolary story has a single letter writer rather than several?',
        50: 'Describe what an omniscient narrator can know about the characters and action.',
        51: 'What practical freedoms does omniscience give a narrator?',
        53: 'How can a third-person narrator deliberately limit omniscience?',
        54: 'How can limited third-person viewpoint change between scenes?',
        55: 'Use Hamilton’s example of two people in locked adjacent rooms to distinguish omniscient and limited narration.',
        64: 'How can disproportionate attention to subsidiary matters create ironic emphasis?',
        75: 'What intellectual and emotional jobs does Hamilton assign to the opening of a short story?',
        85: 'Why does Hamilton treat the arrangement of words as essential to style?',
    },
}

def build():
    candidates = json.loads((OUT/'paragraph-candidates.json').read_text())
    records, scope = [], []
    for group, selection in SELECTION.items():
        source = {'wharton':'wharton-writing', 'hamilton':'hamilton-manual'}[group]
        raw = (RAW/(source+'.txt')).read_text()
        for i, question in selection.items():
            p = candidates[group][i]
            original = raw[p['start']:p['end']]
            assert norm(original) == p['text']
            # Strip a historical topical heading, never rewrite the author's prose.
            target = re.sub(r'^=[^=]+=[—-]*\s*', '', p['text'])
            ident = f'{source}-craft-{i:03d}'
            messages = [dict(role='user', content=question), dict(role='assistant', content=target)]
            span = dict(rights_record_id=source, start=p['start'], end=p['end'], text=original)
            record = dict(schema_version='1.0', id=ident, dataset_version='craft-expansion-v1',
                          task='analysis', split='train', split_group=source, origin='derived',
                          messages=messages, source_work_ids=[source], rights_record_ids=[source],
                          source_spans=[span], teacher=None,
                          review=dict(status='approved', reviewer='Codex AI: source and prompt alignment review',
                                      reviewed_on=DATE, notes='AI review, not a human ballot. Answer is historical source prose; whitespace collapsed and leading topical heading removed. No generated literary answer. Historical opinions are attributed, not universal rules.'),
                          rubric=['usefulness', 'coherence'], content_hash=digest(messages))
            validate_schema(record, 'dataset-record')
            records.append(record)
            scope.append(dict(id=ident, source_id=source, use='training', start=p['start'], end=p['end'],
                              transformation='collapse whitespace; remove leading =topical heading.=-- only',
                              target_sha256=hashlib.sha256(target.encode()).hexdigest()))

    # Complete paragraphs, selected explicitly rather than generated literary context.
    selections = [
        ('garden-marquee', 'mansfield-garden', 'And after all the weather was ideal.', 'Four men in their shirt-sleeves',
         ['Weather is warm and windless; the sky has no cloud.', 'Breakfast has not finished when the marquee workers arrive.', 'Mother delegates arrangements to her children.', 'Meg has wet hair; Laura goes outside holding bread-and-butter.'],
         ['The marquee location has not been decided in this passage.', 'The workers’ private thoughts are unknown.'], 'Laura and her mother'),
        ('brill-bench', 'mansfield-garden', 'Only two people shared her “special” seat:', 'The old people sat on the bench, still as statues.',
         ['Miss Brill shares a seat with an old man and an old woman.', 'The man wears a velvet coat and holds a carved walking-stick.', 'The woman has knitting on her embroidered apron.', 'The couple are silent; the spectacles conversation is a memory of last Sunday.'],
         ['The current couple’s thoughts and relationship are not established.', 'The remembered English couple must not be confused with the current couple.'], 'the old man and old woman on the current bench'),
        ('sandy-kitchen', 'chesnutt-conjure', 'On the northeast corner of my vineyard', 'To save expense, I decided to tear down',
         ['The vineyard is in central North Carolina beside the Lumberton plank-road.', 'The old building has one room, one window and one door.', 'The shutter has fallen; the chimney is cracked.', 'The wife requests a separate kitchen although the house already has a convenient one.'],
         ['The wife’s reason is unknown to the first-person narrator.', 'The request has not yet been fulfilled in this passage.'], 'the narrator and his wife'),
        ('julius-chair', 'chesnutt-conjure', 'One Sunday afternoon in early spring,', '“Julius,” I remarked,',
         ['It is Sunday afternoon in early spring in North Carolina.', 'The narrator and his wife are on the front piazza.', 'The wife has a missionary report; the narrator puts aside a novel.', 'Julius arrives in Sunday clothes, offers to sit on the top step, then takes a chair after Annie insists.'],
         ['The narrator cannot know Julius’s unspoken thoughts.', 'Do not move Julius back to the step as if he had refused the chair.'], 'Annie and Julius'),
    ]
    contexts, cases = [], []
    for ident, source, begin, end, facts, unknowns, speakers in selections:
        raw = (RAW/(source+'.txt')).read_text()
        start = raw.index(begin, 70000 if ident=='garden-marquee' else 200000 if ident=='brill-bench' else 30000 if ident=='sandy-kitchen' else 87000)
        # Source uses straight quotes in Chesnutt, curly quotes in Mansfield.
        end = end.replace('“', '"').replace('”', '"') if source.startswith('chesnutt') else end
        stop = raw.index(end, start)
        original = raw[start:stop].rstrip()
        stop = start + len(original)
        context = norm(original)
        contexts.append(dict(id=ident, source_id=source, start=start, end=stop, raw_text=original,
                             text=context, facts=facts, unknowns=unknowns))
        scope.append(dict(id=ident, source_id=source, use='evaluation', start=start, end=stop,
                          transformation='collapse whitespace; editing case duplicates one existing word'))
        variants = [
            ('continuity', 'fiction', 'Write a plausible NEW continuation of 80–140 words. Preserve the narrator, tense, established facts and limits on knowledge. Do not reproduce or try to recall the published continuation. Return only story prose.', context, None, 80, 140),
            ('editing', 'editing', 'Copyedit this passage with the smallest necessary change. Preserve its voice, spelling, dialect, punctuation and facts. Correct accidental duplication; do not modernize, embellish or explain. Return only the corrected passage.', None, context, 0, None),
            ('dialogue', 'dialogue', f'Write a NEW scene immediately after this passage with 6–10 spoken turns between {speakers}. Let differing wants emerge through subtext, without recapping facts they already know. Brief action beats are allowed. Preserve established events and viewpoint; invent no access to unspoken thoughts outside it. Return only the scene.', context, None, 0, 200),
            ('pacing', 'pacing', 'Compress this passage to 80–120 words. Retain its key facts, viewpoint, temporal relationships and emotional direction while moving briskly. Do not invent an event or resolve uncertainty. Return only the revised prose.', context, None, 80, 120),
        ]
        for kind, task, instruction, supplied, reference, minimum, maximum in variants:
            if kind=='editing':
                tokens=context.split(' '); j=next(i for i,w in enumerate(tokens) if i>=20 and w.isalpha() and len(w)>4)
                tokens.insert(j,tokens[j]);supplied=' '.join(tokens)
            cases.append(dict(id=f'{ident}-{kind}', scenario_id=ident, source_id=source, kind=kind, task=task,
                              context=supplied, prompt=instruction+'\n\nPASSAGE:\n'+supplied,
                              source_facts=facts, source_unknowns=unknowns,
                              word_count_min=minimum, word_count_max=maximum,
                              exact_reference=reference,
                              quality_review='human required; no canonical-continuation exact match',
                              provenance=dict(context='public-domain source', instructions='Codex task design; never a training target')))
    rows('train.records.jsonl', records)
    rows('test.contexts.jsonl', contexts)
    rows('test.cases.jsonl', cases)
    write('scope.json', scope)
    write('curation-summary.json',dict(training_examples=len(records), training_words=sum(len(r['messages'][1]['content'].split()) for r in records),
          test_cases=len(cases), train_authors=['Edith Wharton','Clayton Meeker Hamilton'],
          test_authors=['Katherine Mansfield','Charles W. Chesnutt'], revision_pairs=0,
          revision_reason='Conservative matching found no verified substantive pair; typography, transcription corrections and added headings are not author revision targets.',
          benchmark_status='Experiment-specific sourced-context diagnostic; not the formal original_synthetic foundation benchmark. No schema weakened or false synthetic provenance assigned.',
          literary_targets='Historical author prose only. No generated creative answer or teacher output.',
          limitations=['Twenty historical craft answers cannot establish broad writing competence.', 'Authors held out from project fine-tuning may occur in base pretraining.', 'Craft explanations are not supervised demonstrations of editing or new fiction.']))
    print('Created',len(records),'source-only craft answers and',len(cases),'fresh-author diagnostic cases.')

if __name__ == '__main__':
    build()
