"""Deterministic structural supervision; never generates literary answer prose."""
from __future__ import annotations

import re

from foundation.anchored_edits import AnchorEdit, apply_anchor_edits

STATUSES = ('explicit_fact', 'character_statement', 'plan', 'request', 'hypothetical',
            'uncertain_or_inferred', 'reported_information', 'not_established')


def minutes(clock: str) -> int:
    if not isinstance(clock, str) or not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', clock):
        raise ValueError('explicit same-day HH:MM clock required')
    hour, minute = map(int, clock.split(':'))
    return hour*60 + minute


def arrival_state(now: str, scheduled: str, arrived: bool | None) -> dict:
    if arrived is not None and type(arrived) is not bool:
        raise ValueError('arrival must be true, false or null; absence is not inferred')
    remaining = minutes(scheduled) - minutes(now)
    if arrived is True:
        state = 'arrived'
    elif arrived is None:
        state = 'not_established'
    elif remaining > 0:
        state = 'not_yet_due'
    elif remaining == 0:
        state = 'due_now'
    else:
        state = 'overdue'
    return dict(state=state, minutes_to_schedule=remaining)


def evidence_target(source: str, status: str, quote: str | None) -> dict:
    if status not in STATUSES:
        raise ValueError('unknown evidence status')
    if status == 'not_established':
        if quote is not None:
            raise ValueError('unknown answer must not invent positive evidence')
        return dict(status=status, evidence=[])
    if not quote or source.count(quote) != 1:
        raise ValueError('evidence must be an exact unique source quote')
    return dict(status=status, evidence=[quote])


def selection_pair(source: str) -> dict:
    """Two matched cases: repair inside selection; ignore a duplicate outside it."""
    words = source.split()
    if not 25 <= len(words) <= 180:
        raise ValueError('source outside reviewed length bounds')
    text = ' '.join(words)
    if re.search(r'\b(\w+)\s+\1\b', text, re.I):
        raise ValueError('source already contains a repeated word')
    cut = max(6, len(words)//5)
    before = ' '.join(words[:cut])
    target = ' '.join(words[cut:])
    anchors = [m for m in re.finditer(r'\b[A-Za-z]{5,}\b', target)
               if len(re.findall(r'\b'+re.escape(m.group())+r'\b', target)) == 1]
    if not anchors:
        raise ValueError('no exact unique repair anchor')
    word = anchors[0].group()
    start = anchors[0].start()
    broken = target[:start] + word + ' ' + target[start:]
    edits = [dict(before=word+' '+word, after=word)]
    if apply_anchor_edits(broken, broken, [AnchorEdit(**edit) for edit in edits]) != target:
        raise ValueError('repair fails to recover the exact selected text')
    # This is an explicitly constructed UI context, not a new historical scene.
    # The same duplicate occurs outside the selection to expose global repairs.
    outside = before + ' ' + word + ' ' + word
    return dict(before=before, clean=target, broken=broken, edits=edits,
                outside_with_duplicate=outside, source_normalized=text)
