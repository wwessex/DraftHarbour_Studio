"""Deterministically corrupt inputs while retaining exact published answer targets."""


def corrupt_input(source: str, original: str, wrong: str) -> dict:
    if not original or not wrong or original == wrong or source.count(original) != 1:
        raise ValueError('need one exact unique source anchor and a distinct nonempty corruption')
    start = source.index(original)
    damaged = source[:start] + wrong + source[start + len(original):]
    return dict(source_answer=source, damaged_input=damaged, start=start,
                original=original, wrong=wrong, source_end=start + len(original), damaged_end=start + len(wrong))


def verify_corruption(source: str, binding: dict) -> None:
    if binding != corrupt_input(source, binding['original'], binding['wrong']):
        raise ValueError('changed source target, offsets or input outside the declared corruption')
