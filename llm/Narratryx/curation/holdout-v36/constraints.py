"""Mechanical checks for the frozen originality holdout."""
import re

SPEAKER = re.compile(r"^\s*(?:\*\*)?[A-Za-z][A-Za-z .'-]{0,30}(?:\*\*)?:(?:\*\*)?\s*\S")
QUOTATION = re.compile(r'"([^"\n]+)"|“([^”\n]+)”')


def checks(case, output):
    text = output.strip()
    limits = case['constraints']
    result = {'nonempty': bool(text)}
    count = len(text.split())
    if 'min_words' in limits:
        result['minimum_words'] = count >= limits['min_words']
    if 'max_words' in limits:
        result['maximum_words'] = count <= limits['max_words']
    if 'paragraphs' in limits:
        result['paragraphs'] = bool(text) and len(re.split(r'\n[ \t]*\n', text)) == limits['paragraphs']
    if 'min_turns' in limits:
        lines = [line for line in text.splitlines() if line.strip()]
        result['dialogue_turns'] = (limits['min_turns'] <= len(lines) <= limits['max_turns']
                                    and all(SPEAKER.match(line) for line in lines))
    if limits.get('changed'):
        source = case['prompt'].split('PARAGRAPH:', 1)[1]
        result['changed_rewrite'] = bool(text) and source.split() != text.split()
    if 'exact_quotes' in limits:
        source = ' '.join(case['prompt'].split('PASSAGE:', 1)[1].split())
        quotes = {' '.join((a or b).split()) for a, b in QUOTATION.findall(text)}
        result['supported_quotes'] = sum(q in source for q in quotes if q) >= limits['exact_quotes']
    return result
