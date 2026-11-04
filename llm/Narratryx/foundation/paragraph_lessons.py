"""Exact contiguous source derivation; never creates new literary answer prose."""
import re


def paragraph_lesson(text: str, answer_index: int, answer_count: int = 1) -> dict:
    paragraphs = list(re.finditer(r'\S(?:.*?\S)?(?=\n\s*\n|\Z)', text, re.S))
    if answer_index < 1 or answer_count < 1 or answer_index + answer_count > len(paragraphs):
        raise ValueError('need preceding complete paragraphs and an available contiguous answer')
    start = paragraphs[answer_index].start()
    end = paragraphs[answer_index + answer_count - 1].end()
    context_end = paragraphs[answer_index - 1].end()
    return dict(context=text[:context_end], answer=text[start:end],
                context_start=0, context_end=context_end, answer_start=start, answer_end=end,
                answer_paragraphs=answer_count)


def verify_derivation(text: str, derivation: dict) -> None:
    if derivation['context_start'] != 0 or not 0 < derivation['context_end'] < derivation['answer_start'] < derivation['answer_end'] <= len(text):
        raise ValueError('source intervals overlap or fall outside the scoped source')
    if text[:derivation['context_end']] != derivation['context'] or text[derivation['answer_start']:derivation['answer_end']] != derivation['answer']:
        raise ValueError('context/answer is not the exact source substring')
    if text[derivation['context_end']:derivation['answer_start']].strip():
        raise ValueError('skipped intervening source prose')
    if derivation['answer'] in derivation['context']:
        raise ValueError('answer already present in context')
