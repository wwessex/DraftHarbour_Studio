"""Traceable scoped-source lessons. No generated literary answer text."""
import hashlib
from foundation.paragraph_lessons import paragraph_lesson, verify_derivation


def scoped_raw_span(raw_preserved, approved, expected_source_sha):
    if approved['raw_file_sha256'] != expected_source_sha:
        raise ValueError('source identity mismatch')
    start, end = approved['raw_start'], approved['raw_end']
    selected = raw_preserved[start:end]
    if hashlib.sha256(selected.encode()).hexdigest() != approved['raw_span_sha256']:
        raise ValueError('original raw span mismatch')
    if ' '.join(selected.split()) != approved['text']:
        raise ValueError('approved prose does not match selected raw span')
    prefix = raw_preserved[:start].replace('\r\n', '\n').replace('\r', '\n')
    text = selected.replace('\r\n', '\n').replace('\r', '\n')
    return dict(rights_record_id=approved['source_id'],start=len(prefix),end=len(prefix)+len(text),text=text)


def continuation(span, answer_index, answer_count=1):
    derivation = paragraph_lesson(span['text'], answer_index, answer_count)
    verify_derivation(span['text'], derivation)
    return derivation
