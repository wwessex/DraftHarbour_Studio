"""Offline, review-only prose extraction. This module never exports training jobs.

Inputs are individually selected local OCR files, not a Hub dataset loader.
Offsets are Python Unicode code points in UTF-8 files read with newline=''.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def sha(data):
    return hashlib.sha256(data).hexdigest()


def normalized(text):
    return ' '.join(text.split())


def words(text):
    return re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?", text.lower())


def shingles(text, n=5):
    tokens = words(text)
    return {tuple(tokens[i:i+n]) for i in range(len(tokens)-n+1)}


def overlap(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def quality(raw, vocabulary):
    """Conservative heuristics; passing is not OCR proofreading or approval."""
    text = normalized(raw)
    tokens = words(text)
    reasons = []
    if not 40 <= len(tokens) <= 250:
        reasons.append('word_count')
    if re.search(r'[-‐]\s*\n\s*[A-Za-z]', raw):
        reasons.append('split_word')
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    if any(re.fullmatch(r'[\d\W_]+', line) or
           (len(re.sub('[^A-Za-z]', '', line)) >= 4 and line.isupper())
           for line in lines):
        reasons.append('page_number_or_heading')
    if re.search(r'https?://|www\.|digitized|microfiche|copyright|library|printed by', text, re.I):
        reasons.append('wrapper_or_paratext')
    if re.search(r'[^A-Za-z0-9\s.,;:!?\-—–\'’‘"“”()£$&]', text):
        reasons.append('ocr_symbol')
    if re.search(r'[A-Za-z]\d|\d[A-Za-z]|[A-Za-z][*^<>_]', text):
        reasons.append('damaged_token')
    if not re.match(r'''^["“'‘(—–\s]*[A-Z]''', text) or not re.search(r'''[.!?]["”'’)]*$''', text):
        reasons.append('incomplete_boundary')
    unknown = [w for w in tokens if w not in vocabulary and w.replace("'", '') not in vocabulary]
    rate = len(unknown) / max(1, len(tokens))
    if rate > .06:
        reasons.append('dictionary_outliers')
    return text, reasons, {'word_count': len(tokens), 'dictionary_outlier_rate': rate}


def paragraphs(raw, start, end):
    if not 0 <= start < end <= len(raw):
        raise ValueError('invalid body range')
    # Keep one contiguous raw span per record; never stitch across rejected text.
    pos = start
    for boundary in re.finditer(r'\r?\n[ \t]*\r?\n(?:[ \t]*\r?\n)*', raw[start:end]):
        stop = start + boundary.start()
        if raw[pos:stop].strip():
            yield pos, stop, raw[pos:stop]
        pos = start + boundary.end()
    if raw[pos:end].strip():
        yield pos, end, raw[pos:end]


def check_assignments(sources):
    authors, works = {}, {}
    for source in sources:
        if source['split'] not in {'train_candidate', 'heldout_candidate', 'quarantine'}:
            raise ValueError('unknown split')
        if source['split'] == 'quarantine':
            continue
        for table, key in [(authors, source['author_id']), (works, source['work_id'])]:
            if key in table and table[key] != source['split']:
                raise ValueError('author/work crosses splits')
            table[key] = source['split']


def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')


def write_jsonl(path, rows):
    with path.open('x', encoding='utf-8') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')


def build(plan_path, output):
    plan_path, output = Path(plan_path).resolve(), Path(output).resolve()
    plan = json.loads(plan_path.read_text())
    root = plan_path.parent
    if plan['status'] != 'pending_review' or plan['training_authorized'] is not False:
        raise ValueError('review-only plan required')
    check_assignments(plan['sources'])
    vocabulary_path = Path(plan['vocabulary_path'])
    vocabulary_data = vocabulary_path.read_bytes()
    if sha(vocabulary_data) != plan['vocabulary_sha256']:
        raise ValueError('vocabulary checksum mismatch')
    vocabulary = set(vocabulary_data.decode().lower().split())
    vocabulary.update({'a', 'i', 'the', 'and', 'of', 'to', 'in', 'he', 'she', 'it'})
    protected = set()
    protected_inputs = []
    for name in plan['protected_files']:
        path = (root / name).resolve()
        data = path.read_bytes()
        protected_inputs.append({'path': str(path), 'sha256': sha(data)})
        for line in data.decode().splitlines():
            record = json.loads(line)
            def strings(value):
                if isinstance(value, str):
                    yield value
                elif isinstance(value, dict):
                    for child in value.values():
                        yield from strings(child)
                elif isinstance(value, list):
                    for child in value:
                        yield from strings(child)
            for text in strings(record):
                protected.update(shingles(text, 12))
    candidates, rejections, per_source = [], [], []
    for source in plan['sources']:
        path = (root / source['raw_path']).resolve()
        if not path.is_relative_to(root):
            raise ValueError('source outside plan directory')
        data = path.read_bytes()
        if sha(data) != source['raw_sha256']:
            raise ValueError('raw checksum mismatch')
        raw = data.decode('utf-8')
        if source['split'] == 'quarantine':
            per_source.append({'identifier': source['identifier'], 'quarantined': True})
            continue
        # Bounds include exact anchors, to fail on a misselected edition/body.
        start, end = source['body_start'], source['body_end']
        if not raw[start:].startswith(source['start_anchor']) or not raw[end:].startswith(source['end_anchor']):
            raise ValueError('body anchor mismatch')
        stats = Counter()
        for a, b, span in paragraphs(raw, start, end):
            text, reasons, metrics = quality(span, vocabulary)
            key = source['identifier'] + ':' + str(a) + ':' + str(b)
            if not reasons and shingles(text, 12) & protected:
                reasons.append('protected_test_overlap_12_words')
            if reasons:
                stats.update(reasons)
                rejections.append({'id': key, 'reasons': reasons, 'start': a, 'end': b})
                continue
            candidates.append({'id': key, 'identifier': source['identifier'],
                               'author_id': source['author_id'], 'work_id': source['work_id'],
                               'split': source['split'], 'text': text, 'raw_start': a, 'raw_end': b,
                               'raw_span_sha256': sha(span.encode()), 'text_sha256': sha(text.encode()),
                               'quality': metrics, 'review_status': 'pending',
                               'rights_status': 'pending', 'transform': 'collapse_whitespace_only'})
            stats['quality_pass'] += 1
        per_source.append({'identifier': source['identifier'], 'counts': dict(stats)})
    # Prefer the reserved author when duplicates cross splits. Sort by content hash
    # for reproducible sampling across the whole body, rather than openings only.
    kept, seen, duplicate_audit, cap_counts = [], set(), [], Counter()
    kept_shingles = []
    for record in sorted(candidates, key=lambda r: (r['split'] != 'heldout_candidate', r['text_sha256'])):
        fingerprint = ' '.join(words(record['text']))
        grams = shingles(record['text'])
        duplicate = fingerprint in seen or any(overlap(grams, other) >= .8 for other in kept_shingles)
        if duplicate:
            duplicate_audit.append({'id': record['id'], 'reason': 'exact_or_jaccard_5gram_ge_0.8'})
            continue
        if cap_counts[record['identifier']] >= plan['max_passages_per_work']:
            rejections.append({'id': record['id'], 'reasons': ['deterministic_work_cap']})
            continue
        seen.add(fingerprint); kept_shingles.append(grams); kept.append(record)
        cap_counts[record['identifier']] += 1
    if not any(r['split'] == 'train_candidate' for r in kept) or not any(r['split'] == 'heldout_candidate' for r in kept):
        raise ValueError('empty train or heldout candidate set')
    output.mkdir(parents=True, exist_ok=False)
    for split in ['train_candidate', 'heldout_candidate']:
        write_jsonl(output / (split + '.pending.jsonl'), [r for r in kept if r['split'] == split])
    write_jsonl(output / 'rejected.jsonl', rejections + duplicate_audit)
    totals = {}
    for source in plan['sources']:
        rows = [r for r in kept if r['identifier'] == source['identifier']]
        totals[source['identifier']] = {'split': source['split'], 'passages': len(rows),
                                      'words': sum(r['quality']['word_count'] for r in rows)}
    write_json(output / 'audit.json', {'status': 'pending_rights_and_editorial_review',
                                     'plan_sha256': sha(plan_path.read_bytes()),
                                     'protected_inputs': protected_inputs,
                                     'per_source': per_source, 'totals': totals,
                                     'duplicates_removed': len(duplicate_audit),
                                     'near_duplicate_rule': 'Jaccard >= 0.8 of lowercased word 5-gram sets',
                                     'benchmark_overlap_rule': 'shared contiguous 12-word sequence; not semantic detection',
                                     'training_started': False, 'release_ready': False})
    write_json(output / 'manifest.json', {'files': {p.name: sha(p.read_bytes()) for p in sorted(output.iterdir())},
                                        'builder_sha256': sha(Path(__file__).read_bytes()),
                                        'dataset_revision': plan['dataset_revision']})
    return totals


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.plan, args.output), indent=2))
