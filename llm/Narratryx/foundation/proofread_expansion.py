"""Offline extraction of pinned proofread sources into a pending review pool.

No training exports, model calls, network access or rights-approval mutations.
"""
import argparse
from collections import Counter
import json
from pathlib import Path
import re

from .english_pd import paragraphs, quality, sha, shingles, overlap, words, write_json, write_jsonl


def exclude_reasons(span, source_id):
    reasons = []
    if '[' in span or ']' in span:
        reasons.append('annotation_or_footnote')
    if re.search(r'(?m)^[ \t]{4,}\S', span):
        reasons.append('indented_verse_or_attribution')
    # Conservative project scope, not a claim that religious prose is protected.
    # Avoid selecting scripture/hymn quotations embedded in this religious novel.
    if source_id == 'wray-nestleton-pg41916' and re.search(
            r'\b(God|Lord|Christ|Jesus|Saviour|Savior|Scripture|Bible|Gospel|'
            r'heaven|heavenly|holy|hymn|psalm|verse|prayer|pray|faith|religion|'
            r'sermon|church|chapel|preach\w*|Methodis\w*)\b', span, re.I):
        reasons.append('outside_secular_narrative_scope')
    if re.search(r'Gutenberg|www\.|https?://|transcriber|copyright', span, re.I):
        reasons.append('provider_or_editorial_matter')
    return reasons


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from strings(child)


def build(plan_path, output):
    plan_path, output = Path(plan_path).resolve(), Path(output).resolve()
    plan = json.loads(plan_path.read_text())
    root = plan_path.parent
    if plan['status'] != 'pending_review' or plan['training_authorized'] is not False:
        raise ValueError('review-only plan required')
    if len({s['author_id'] for s in plan['sources']}) != len(plan['sources']):
        raise ValueError('one source per distinct author required for this expansion')
    limit = plan['max_words_per_author']
    if type(limit) is not int or limit < 250:
        raise ValueError('invalid author word budget')
    vocab_path = (root / plan['vocabulary_path']).resolve()
    vocabulary_data = vocab_path.read_bytes()
    if sha(vocabulary_data) != plan['vocabulary_sha256']:
        raise ValueError('vocabulary checksum mismatch')
    vocabulary = set(vocabulary_data.decode().lower().split()) | {'a', 'i', 'the', 'and', 'of', 'to', 'in', 'he', 'she', 'it'}
    protected, protected_inputs = set(), []
    for item in plan['protected_files']:
        path = (root / item['path']).resolve()
        data = path.read_bytes()
        if sha(data) != item['sha256']:
            raise ValueError('protected input changed')
        protected_inputs.append(item)
        for line in data.decode().splitlines():
            for text in strings(json.loads(line)):
                protected.update(shingles(text, 12))
    candidates, rejected, per_source = [], [], []
    source_ids = set()
    for source in plan['sources']:
        if source['id'] in source_ids or source['split'] != 'train_candidate':
            raise ValueError('duplicate or non-training source')
        source_ids.add(source['id'])
        if source['author_id'] in plan['reserved_author_ids'] or source['work_id'] in plan['reserved_work_ids']:
            raise ValueError('reserved author/work cannot enter training')
        raw_path = (root / source['raw_path']).resolve()
        if not raw_path.is_relative_to(root):
            raise ValueError('source outside plan directory')
        data = raw_path.read_bytes()
        if sha(data) != source['raw_sha256']:
            raise ValueError('source checksum mismatch')
        raw = data.decode('utf-8')
        start, end = source['body_start'], source['body_end']
        if raw.count(source['start_anchor']) != 1 or raw.count(source['end_anchor']) != 1:
            raise ValueError('ambiguous body anchor')
        if not raw[start:].startswith(source['start_anchor']) or not raw[end:].startswith(source['end_anchor']):
            raise ValueError('body anchor mismatch')
        if '*** START OF THE PROJECT GUTENBERG EBOOK ' not in raw[:start] or '1.C.' not in raw[end:]:
            raise ValueError('full source and license required')
        stats = Counter()
        for a, b, span in paragraphs(raw, start, end):
            text, reasons, metrics = quality(span, vocabulary)
            # A generic word list mislabels Agnes, Fitzhenry and Yorkshire
            # dialect as OCR damage. Keep this metric for review, not rejection
            # of a proofread transcription; never rewrite those tokens.
            reasons = [reason for reason in reasons if reason != 'dictionary_outliers']
            reasons += exclude_reasons(span, source['id'])
            if not reasons and shingles(text, 12) & protected:
                reasons.append('protected_test_overlap_12_words')
            rid = source['id'] + ':' + str(a) + ':' + str(b)
            if reasons:
                stats.update(set(reasons))
                rejected.append({'id': rid, 'reasons': sorted(set(reasons))})
                continue
            stats['machine_pass'] += 1
            candidates.append({'id': rid, 'source_id': source['id'], 'author_id': source['author_id'],
                               'work_id': source['work_id'], 'split': 'train_candidate',
                               'text': text, 'raw_start': a, 'raw_end': b,
                               'raw_file_sha256': source['raw_sha256'], 'raw_span_sha256': sha(span.encode()),
                               'text_sha256': sha(text.encode()), 'transform': 'collapse_whitespace_only',
                               'quality': metrics, 'rights_status': 'pending', 'review_status': 'pending'})
        per_source.append({'source_id': source['id'], 'counts': dict(stats)})
    kept, seen, grams, counts = [], set(), [], Counter()
    for row in sorted(candidates, key=lambda x: x['text_sha256']):
        key, gram = ' '.join(words(row['text'])), shingles(row['text'])
        reason = None
        if key in seen or any(overlap(gram, other) >= .8 for other in grams):
            reason = 'exact_or_near_duplicate'
        elif counts[row['author_id']] + row['quality']['word_count'] > limit:
            reason = 'author_word_budget'
        if reason:
            rejected.append({'id': row['id'], 'reasons': [reason]})
            continue
        kept.append(row); seen.add(key); grams.append(gram)
        counts[row['author_id']] += row['quality']['word_count']
    if any(counts[s['author_id']] < limit * .9 for s in plan['sources']):
        raise ValueError('insufficient eligible text for balanced expansion')
    output.mkdir(parents=True, exist_ok=False)
    write_jsonl(output / 'train-candidates.pending.jsonl', kept)
    write_jsonl(output / 'rejected.jsonl', rejected)
    write_json(output / 'audit.json', {'status': 'pending_rights_scope_and_editorial_approval',
                                     'training_started': False, 'release_ready': False,
                                     'plan_sha256': sha(plan_path.read_bytes()), 'protected_inputs': protected_inputs,
                                     'per_source': per_source, 'retained_passages': len(kept),
                                     'words_per_author': dict(counts),
                                     'reserved_authors': plan['reserved_author_ids'],
                                     'transform': 'collapse_whitespace_only',
                                     'limits': ['Text filtering is not facsimile proofreading.',
                                                'Word-5-gram Jaccard >= 0.8 deduplication; protected 12-word matches screened.',
                                                'No inference about base-model pretraining contamination.']})
    write_json(output / 'manifest.json', {'files': {p.name: sha(p.read_bytes()) for p in sorted(output.iterdir())},
                                        'builder_sha256': sha(Path(__file__).read_bytes())})
    return dict(counts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.plan, args.output), indent=2))
