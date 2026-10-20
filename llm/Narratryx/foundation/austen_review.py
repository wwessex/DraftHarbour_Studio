"""Build a small, local, traceable review pack; never approve, upload or train."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys

from .evaluation import benchmark, write_new
from .validation import (Invalid, ROOT, TASKS, check_leakage, digest, file_hash,
                         load_ledger, read_json, validate_schema)


def text_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def pending(note: str) -> dict:
    return {'status': 'pending', 'reviewer': None, 'reviewed_on': None, 'notes': note}


def normalize_excerpt(raw: str) -> str:
    """Join single print line breaks only. Do not change punctuation/emphasis."""
    return re.sub(r'(?<!\n)\n(?!\n)', ' ', raw)


def roman_number(value: str) -> int:
    numbers = {'I': 1, 'V': 5, 'X': 10, 'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    total, previous = 0, 0
    for letter in reversed(value.upper()):
        number = numbers[letter]
        total += -number if number < previous else number
        previous = max(previous, number)
    return total


def chapter_at(source: str, position: int, outer: tuple[int, int]) -> int:
    chapter = 1
    for match in re.finditer(r'(?im)^\s*chapter\s+([ivxlcdm]+)\.?\s*$', source[outer[0]:position]):
        chapter = roman_number(match.group(1))
    return chapter


def check_allowed_text(raw: str) -> None:
    if re.search(r'\[Illustration\b|Copyright\s+1894|Project Gutenberg|CHISWICK PRESS|\{\d+\}', raw, re.I):
        raise Invalid('selected excerpt contains excluded illustration, notice or page/printer material')


def make_excerpt(source: str, selection: dict, *, outer: tuple[int, int],
                 source_sha256: str, source_path: str, rights_id: str, work_id: str) -> dict:
    if not 0 <= outer[0] < outer[1] <= len(source):
        raise Invalid('invalid outer narrative range')
    body = source[outer[0]:outer[1]]
    start_anchor, end_anchor = selection['start'], selection['end']
    if not start_anchor.strip() or not end_anchor.strip():
        raise Invalid('empty selection anchor')
    if body.count(start_anchor) != 1 or body.count(end_anchor) != 1:
        raise Invalid(f'{selection["id"]}: selection anchors must be unique within narrative range')
    start = outer[0] + body.index(start_anchor)
    end = outer[0] + body.index(end_anchor) + len(end_anchor)
    if end <= start:
        raise Invalid('selection end precedes start')
    raw = source[start:end]
    check_allowed_text(raw)
    chapter = chapter_at(source, start, outer)
    if chapter != selection['chapter'] or chapter_at(source, end, outer) != chapter:
        raise Invalid(f'{selection["id"]}: incorrect chapter label or cross-chapter selection')
    excerpt = {'schema_version': '1.0', 'id': selection['id'], 'rights_record_id': rights_id,
               'source_work_id': work_id, 'source_sha256': source_sha256, 'source_path': source_path,
               'chapter': chapter, 'focus': selection['focus'],
               'span': {'rights_record_id': rights_id, 'start': start, 'end': end, 'text': raw},
               'source_lines': {'start': source.count('\n', 0, start) + 1,
                                'end': source.count('\n', 0, end) + 1},
               'text': normalize_excerpt(raw), 'text_sha256': text_hash(normalize_excerpt(raw)),
               'raw_span_sha256': text_hash(raw),
               'transformation': {'id': 'join-soft-wraps-v1',
                                  'description': 'Replace isolated LF print-wrap characters with spaces; retain paragraph breaks, Unicode punctuation and underscore emphasis exactly. Offsets refer to the LF-normalized source view, not original bytes.',
                                  'joined_line_breaks': len(re.findall(r'(?<!\n)\n(?!\n)', raw)),
                                  'preserves_paragraphs': True, 'preserves_emphasis_markup': True,
                                  'removed_content': False},
               'review': pending('AI-selected source passage. Human scope approval exists; this exact selection and transformation still require review.')}
    verify_excerpt(excerpt, source, outer, source_sha256)
    return excerpt


def verify_excerpt(excerpt: dict, source: str, outer: tuple[int, int], expected_hash: str) -> None:
    validate_schema(excerpt, 'excerpt-record')
    span = excerpt['span']
    if not outer[0] <= span['start'] < span['end'] <= outer[1]:
        raise Invalid('excerpt outside approved narrative inspection range')
    if excerpt['source_sha256'] != expected_hash or source[span['start']:span['end']] != span['text']:
        raise Invalid('excerpt source identity or span mismatch')
    if span['rights_record_id'] != excerpt['rights_record_id']:
        raise Invalid('inconsistent excerpt rights record')
    check_allowed_text(span['text'])
    if excerpt['text'] != normalize_excerpt(span['text']):
        raise Invalid('clean excerpt contains unrecorded text changes')
    if excerpt['text_sha256'] != text_hash(excerpt['text']) or excerpt['raw_span_sha256'] != text_hash(span['text']):
        raise Invalid('excerpt hash mismatch')
    if (chapter_at(source, span['start'], outer) != excerpt['chapter']
            or chapter_at(source, span['end'], outer) != excerpt['chapter']):
        raise Invalid('excerpt chapter mapping mismatch')
    if excerpt['transformation']['joined_line_breaks'] != len(re.findall(r'(?<!\n)\n(?!\n)', span['text'])):
        raise Invalid('transformation count mismatch')
    if excerpt['source_lines'] != {'start': source.count('\n', 0, span['start']) + 1,
                                   'end': source.count('\n', 0, span['end']) + 1}:
        raise Invalid('source line mapping mismatch')


def make_example(definition: dict, excerpt: dict, spec: dict) -> dict:
    mode = definition.get('target_mode', 'authored')
    if mode == 'replace_once':
        if excerpt['text'].count(definition['old']) != 1:
            raise Invalid('exact editing replacement must identify one occurrence')
        target = excerpt['text'].replace(definition['old'], definition['new'], 1)
    elif mode == 'no_change':
        target = 'No changes needed.\n\n' + excerpt['text']
    elif mode == 'authored':
        target = definition['target']
    else:
        raise Invalid(f'unsupported target construction: {mode}')
    messages = [{'role': 'user', 'content': definition['instruction'] + '\n\nPassage:\n' + excerpt['text']},
                {'role': 'assistant', 'content': target}]
    record = {'schema_version': '1.0', 'id': definition['id'], 'dataset_version': spec['pack_id'],
              'task': definition['task'], 'split': 'train', 'split_group': spec['split_group'],
              'origin': 'synthetic', 'messages': messages,
              'source_work_ids': [spec['source_work_id']], 'rights_record_ids': [spec['rights_record_id']],
              'source_spans': [excerpt['span']],
              'teacher': {'model': 'Codex', 'revision': 'conversation-01a14bea-d041-7363-b30b-66b4af6a77bf-curation-v1',
                          'terms_url': 'https://openai.com/policies/terms-of-use/',
                          'training_permission': 'PENDING: review the actual terms applicable to this account and intended training use. This is conversation-authored draft material; no provider checkpoint revision is claimed.',
                          'review': pending('Source-scope approval does not automatically approve synthetic-output terms.')},
              'review': pending('Draft synthetic target; review usefulness, grounding, source selection, output terms and voice preservation before any training.'),
              'rubric': definition['rubric'], 'content_hash': digest(messages)}
    validate_schema(record, 'dataset-record')
    return record


def render_review(excerpts: list[dict], examples: list[dict], definitions: list[dict], raw_path: Path) -> str:
    mapping = {d['id']: d for d in definitions}
    lines = ['# Austen pilot: excerpts and draft training examples', '',
             '**For review only — not a released or training-ready dataset.**', '',
             'Six short excerpts from the pinned 1894-edition transcription; twelve draft examples, two per skill. '
             'All Austen-derived records are assigned to the same author group and proposed training split. '
             'The independent benchmark is unchanged. All exact excerpts, targets and teacher terms remain pending review.', '',
             'Targets are new synthetic drafts, except for explicitly requested copied/edited source wording. '
             'Invented scenes are alternatives or technique exercises, never claims about Austen’s canonical continuation. '
             'Only isolated print-wrap line breaks were joined; paragraph breaks, punctuation and `_emphasis_` markup remain intact. '
             'Offsets count Unicode code points in the LF-normalized source view. The original byte snapshot is unchanged.', '',
             'Review each item for source fidelity, scope exclusions, useful instructions, target quality and grounded claims. '
             'Keep, revise or reject individual examples; do not approve the full raw book by approving a passage.', '']
    for excerpt in excerpts:
        span = excerpt['span']; number = excerpt['chapter']
        lines += [f'## {excerpt["id"]}', '',
                  f'Chapter {number}; source characters [{span["start"]}, {span["end"]}); '
                  f'lines {excerpt["source_lines"]["start"]}–{excerpt["source_lines"]["end"]}. '
                  f'[Unchanged source]({raw_path}:{excerpt["source_lines"]["start"]}).', '', excerpt['focus'], '',
                  '\n'.join('> ' + line if line else '>' for line in excerpt['text'].split('\n')), '']
        for example in examples:
            if mapping[example['id']]['excerpt_id'] != excerpt['id']:
                continue
            lines += [f'### {example["id"]} — {example["task"]}', '',
                      '**Instruction:** ' + mapping[example['id']]['instruction'], '',
                      '**Draft target:**', '', '```text', example['messages'][-1]['content'], '```', '',
                      '**Review criteria:**', ''] + ['- ' + r for r in example['rubric']] + ['']
    return '\n'.join(lines) + '\n'


def build_pack(spec_path: Path, ledger_path: Path, source_manifest_path: Path,
               approval_path: Path, output: Path) -> dict:
    if output.exists():
        raise Invalid('output directory already exists; choose a new review version')
    spec, source_manifest, approval = map(read_json, (spec_path, source_manifest_path, approval_path))
    ledger = load_ledger(ledger_path)
    rights = ledger[spec['rights_record_id']]
    if rights['review']['status'] != 'approved' or approval['decision'] != 'approved-with-scope-conditions':
        raise Invalid('explicit human source-scope approval is required')
    if approval['rights_record_id'] != rights['id'] or rights['work_id'] != spec['source_work_id']:
        raise Invalid('approval/source work mismatch')
    if not {'GB', 'US'} <= set(approval['jurisdictions']):
        raise Invalid('review scope must include recorded GB/US approval')
    for entry in approval['reviewed_documents'].values():
        snapshot = (ledger_path.parent / entry['snapshot_path']).resolve()
        if not snapshot.is_relative_to(ledger_path.parent.resolve()) or file_hash(snapshot) != entry['sha256_at_approval']:
            raise Invalid('approved review-document snapshot hash mismatch')
    raw_path = (ledger_path.parent / rights['source']['raw_path']).resolve()
    if not raw_path.is_relative_to(ledger_path.parent.resolve()):
        raise Invalid('raw source escapes the ledger directory')
    source_hash = file_hash(raw_path)
    if len({source_hash, rights['source']['sha256'], approval['source_sha256'],
            source_manifest['sha256'], spec['expected_source_sha256']}) != 1:
        raise Invalid('source hash does not match approved evidence/specification')
    source = raw_path.read_text(encoding='utf-8')
    outer = tuple(spec['expected_outer_range'])
    selection = source_manifest['selection_plan']
    if list(outer) != [selection['outer_start'], selection['outer_end_exclusive']]:
        raise Invalid('outer narrative range changed since selection specification')
    if text_hash(source[outer[0]:outer[1]]) != selection['outer_range_sha256_utf8']:
        raise Invalid('outer narrative range hash mismatch')
    excerpts = [make_excerpt(source, s, outer=outer, source_sha256=source_hash,
                             source_path=rights['source']['raw_path'], rights_id=rights['id'],
                             work_id=rights['work_id']) for s in spec['selections']]
    by_id = {e['id']: e for e in excerpts}
    if len(by_id) != len(excerpts) or len({e['id'] for e in spec['examples']}) != len(spec['examples']):
        raise Invalid('duplicate excerpt or example IDs')
    if spec['split'] != 'train' or spec['split_group'] != 'author-austen':
        raise Invalid('Austen pilot must remain in one author training group')
    examples = [make_example(d, by_id[d['excerpt_id']], spec) for d in spec['examples']]
    counts = {task: sum(e['task'] == task for e in examples) for task in TASKS}
    if len(excerpts) != 6 or set(counts.values()) != {2}:
        raise Invalid('pilot specification must contain six excerpts and two examples per skill')
    tasks = benchmark(ROOT / 'evaluation/tasks.draft.jsonl', allow_draft=True)
    check_leakage(examples, tasks)
    # All inputs are checked before creating a new output directory. No source,
    # ledger, approval or benchmark file is changed by this builder.
    output.mkdir(parents=True, exist_ok=False)
    write_new(output / 'excerpts.pending.jsonl', excerpts, jsonl=True)
    write_new(output / 'examples.pending.jsonl', examples, jsonl=True)
    review = render_review(excerpts, examples, spec['examples'], raw_path)
    with (output / 'REVIEW.md').open('x', encoding='utf-8') as handle:
        handle.write(review)
    manifest = {'schema_version': '1.0', 'pack_id': spec['pack_id'],
                'created_at_utc': datetime.now(timezone.utc).isoformat(),
                'status': 'pending-human-excerpt-example-and-teacher-terms-review',
                'training_ready': False, 'inference_calls': 0, 'downloads': 0,
                'excerpt_count': len(excerpts), 'example_count': len(examples), 'examples_per_skill': counts,
                'source_sha256': source_hash, 'rights_record_id': rights['id'],
                'source_scope_approval': approval['record_id'],
                'coordinate_basis': 'Unicode code points in UTF-8 source read with universal-newline normalization; end exclusive',
                'input_hashes': {name: file_hash(path) for name, path in
                                 [('spec', spec_path), ('ledger', ledger_path), ('approval', approval_path),
                                  ('source_manifest', source_manifest_path),
                                  ('draft_benchmark', ROOT / 'evaluation/tasks.draft.jsonl')]},
                'file_hashes': {name: file_hash(output / name) for name in
                                ['excerpts.pending.jsonl', 'examples.pending.jsonl', 'REVIEW.md']},
                'checks': ['exact source/approval/snapshot hashes match', 'source spans reproduce original text view',
                           'all excerpts inside narrative range and chapter-checked', 'no excluded marker/notice content in selected spans',
                           'only recorded whitespace transformation applied', 'strict excerpt/SFT schemas pass',
                           'one Austen author group/train split', 'lexical screen against independent draft benchmark passed'],
                'limitations': ['Synthetic targets and their applicable terms are not human-approved.',
                                'Lexical screening cannot rule out semantic or pretrained-model contamination.',
                                'No source-release or dataset-release approval; the existing source-selection gate remains open.',
                                'No training, upload, new source acquisition or application change.']}
    write_new(output / 'manifest.json', manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--spec', type=Path, default=ROOT / 'curation/austen-pilot-review-v1.json')
    parser.add_argument('--ledger', type=Path, default=ROOT / 'rights/ledger.jsonl')
    parser.add_argument('--source-manifest', type=Path, default=ROOT / 'rights/evidence/austen-pride-1894-source.json')
    parser.add_argument('--approval', type=Path, default=ROOT / 'rights/approvals/austen-pride-2026-10-17.json')
    args = parser.parse_args()
    try:
        result = build_pack(args.spec, args.ledger, args.source_manifest, args.approval, args.output_dir)
    except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}), file=sys.stderr)
        return 1
    print(json.dumps({'ok': True, 'output_dir': str(args.output_dir.resolve()), **result}, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
