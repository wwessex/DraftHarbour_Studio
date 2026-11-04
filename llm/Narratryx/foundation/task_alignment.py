"""Observable lesson coverage, not an automatic literary-quality or rights review."""
import re


def lesson_form(row: dict) -> str:
    prompt = row['messages'][0]['content']
    answer = row['messages'][-1]['content']
    if answer.lstrip().startswith('{'):
        return 'structural-json'
    if '\nOPENING:\n' in prompt and '\nCLOSING:\n' in prompt:
        return 'boundary-reconstruction'
    if '\nFRAGMENT:\n' in prompt:
        return 'sentence-fragment-continuation'
    if prompt.startswith('Continue directly after'):
        return 'paragraph-continuation'
    if row['task'] == 'analysis':
        return 'quoted-craft-exposition'
    if row['task'] == 'editing':
        return 'author-revision'
    return 'directed-scene'


def observable_checks(row: dict) -> dict:
    prompt = row['messages'][0]['content']
    answer = row['messages'][-1]['content']
    maximum = re.search(r'at most (\d+) words', prompt)
    fragment = prompt.split('\nFRAGMENT:\n', 1)[-1] if '\nFRAGMENT:\n' in prompt else None
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', answer) if s.strip()]
    repeated = sorted({s for s in sentences if sentences.count(s) > 1})
    return dict(answer_words=len(answer.split()),
                word_maximum=int(maximum[1]) if maximum else None,
                exceeds_word_maximum=bool(maximum and len(answer.split()) > int(maximum[1])),
                answer_paragraphs=len(re.split(r'\n\s*\n', answer.strip())),
                repeats_entire_fragment=bool(fragment and fragment in answer),
                repeated_exact_sentences=repeated,
                answer_is_exact_source_span=any(answer == s['text'] for s in row['source_spans']))


def verify_unchanged_target(original: dict, proposal: dict) -> None:
    """Instruction repairs may never silently replace source answers/provenance."""
    for key in ['source_spans', 'rights_record_ids', 'source_work_ids', 'split', 'split_group', 'teacher', 'origin']:
        if proposal[key] != original[key]:
            raise ValueError(f'changed protected field: {key}')
    if proposal['messages'][-1] != original['messages'][-1]:
        raise ValueError('changed teaching answer')
