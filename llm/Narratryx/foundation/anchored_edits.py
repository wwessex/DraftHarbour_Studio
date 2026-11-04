"""Experimental edit-preview application; no app wiring, inference or file writes."""
from dataclasses import dataclass


@dataclass(frozen=True)
class AnchorEdit:
    before: str
    after: str


def apply_anchor_edits(current_target: str, captured_target: str, edits: list[AnchorEdit]) -> str:
    """Apply exact unique anchors against the captured selection, preserving the rest.

    Offsets are internal Unicode code points; callers pass ONLY the captured target.
    This validates application safety, not the literary correctness of a proposal.
    """
    if current_target != captured_target:
        raise ValueError('target changed since capture')
    if len(edits) > 32:
        raise ValueError('too many edits')
    spans = []
    for edit in edits:
        if not isinstance(edit.before, str) or not isinstance(edit.after, str) or not edit.before:
            raise ValueError('edit anchors must be nonempty strings')
        start = current_target.find(edit.before)
        if start < 0:
            raise ValueError('anchor not found in target')
        if current_target.find(edit.before, start + 1) >= 0:
            raise ValueError('ambiguous anchor')
        spans.append((start, start + len(edit.before), edit.after))
    spans.sort()
    if any(left[1] > right[0] for left, right in zip(spans, spans[1:])):
        raise ValueError('overlapping edits')
    result = current_target
    for start, end, replacement in reversed(spans):
        result = result[:start] + replacement + result[end:]
    return result
