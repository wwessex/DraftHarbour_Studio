"""Evaluation-only prompt pairs; no generated literary training targets."""
import re

QUESTIONS = {
    'sr14-inventory-rewrite': "Which register is readable, which has not been inspected, and whose agreement to mark the original is still missing?",
    'ta11-archive-card-rewrite': "Which card is untested, what permission is missing, and which arrival is still expected in the future?",
    'sr14-spare-continue': "What concrete next action uses the permitted spare inspection or measurement without cutting or marking the original or claiming heat resistance?",
    'bf-conservatory-continue': "Which event has already happened, which arrival is still in the future, and what concrete action can advance the scene without establishing who left the ring?",
    'sr14-arrival-dialogue': "How much time remains until the courier is expected, which copy needs inspection, and how can the speakers advance that inspection without altering the original?",
    'bf-craft-reel-dialogue': "What practical next step addresses Anika's test while preserving the choir recording and uncertainty about the unchecked spare?",
}


def cases(source):
    lookup = {c['id']: c for c in source}
    rows = []
    for index, (ident, question) in enumerate(QUESTIONS.items()):
        parent = lookup[ident]
        suffix = "\n\nGUIDING QUESTIONS:\n" + question + "\nUse these questions to guide the requested fiction. Return only the requested prose or dialogue, without answers or planning notes."
        for variant in (['original', 'clarified'] if index % 2 == 0 else ['clarified', 'original']):
            row = dict(parent)
            row.update(id='fq19-' + ident + '-' + variant, parent_case_id=ident, variant=variant,
                       prompt=parent['prompt'] + (suffix if variant == 'clarified' else ''),
                       added_suffix=suffix if variant == 'clarified' else '',
                       evaluation_role='exposed-development-prompt-comparison', training_eligible=False,
                       provenance='AI-authored evaluation-only scenario and guiding questions. Original scenario exposed; no human gold or teaching answer.')
            rows.append(row)
    return rows


def mechanics(text, case):
    words = len(text.split())
    minimum, maximum = case.get('word_count_min'), case.get('word_count_max')
    paragraphs = len([p for p in re.split(r'\n\s*\n', text.strip()) if p.strip()])
    return dict(words=words, word_limit_passed=(minimum is None or words >= minimum) and (maximum is None or words <= maximum),
                paragraphs=paragraphs, one_paragraph_passed=paragraphs == 1 if case['kind'] in ['rewrite', 'continue'] else None)
