"""Select exact, unique source intervals without rewriting literary text."""


def excerpt(text, opening, following):
    if not opening or not following or text.count(opening) != 1 or text.count(following) != 1:
        raise ValueError('source markers must be unique and nonempty')
    start, end = text.index(opening), text.index(following)
    while end > start and text[end-1].isspace():
        end -= 1
    if end <= start:
        raise ValueError('source interval reversed or empty')
    return dict(start=start,end=end,text=text[start:end])


def split_continuation(span, answer_opening):
    text=span['text']
    if not answer_opening or text.count(answer_opening) != 1:
        raise ValueError('answer boundary must be unique')
    start=text.index(answer_opening)
    context=text[:start].rstrip()
    if not context or '\n\n' not in text[len(context):start]:
        raise ValueError('continuation must start after a complete source paragraph')
    return dict(context=context,answer=text[start:],context_start=span['start'],context_end=span['start']+len(context),answer_start=span['start']+start,answer_end=span['end'])
