"""Fail-closed structural, provenance and split checks. Never grants legal clearance."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
TASKS = ('fiction', 'editing', 'analysis', 'dialogue', 'pacing', 'storytelling')


class Invalid(ValueError):
    """A supplied artifact is incomplete, inconsistent, or unapproved."""


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Invalid(f'duplicate JSON key: {key}')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_keys,
                      parse_constant=lambda x: (_ for _ in ()).throw(Invalid(f'invalid number: {x}')))


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line_number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip():
            raise Invalid(f'{path}:{line_number}: blank JSONL record')
        # Use the same strict decoder as JSON files without touching the filesystem.
        try:
            row = json.loads(line, object_pairs_hook=_unique_pairs,
                             parse_constant=lambda x: (_ for _ in ()).throw(Invalid(x)))
        except (ValueError, TypeError) as exc:
            raise Invalid(f'{path}:{line_number}: {exc}') from exc
        rows.append(row)
    if not rows:
        raise Invalid(f'{path}: empty artifact')
    return rows


def _unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise Invalid(f'duplicate JSON key: {key}')
        result[key] = value
    return result


def validate_schema(value: object, name: str) -> None:
    schema = read_json(ROOT / 'schemas' / f'{name}.schema.json')
    Draft202012Validator.check_schema(schema)
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value))
    if errors:
        error = errors[0]
        raise Invalid(f'{name} at {list(error.absolute_path)}: {error.message}')


def approved(review: dict, label: str) -> None:
    if review['status'] != 'approved':
        raise Invalid(f'{label}: review status is {review["status"]}, not approved')


def index_rows(rows: list[dict], schema: str, key: str = 'id') -> dict:
    result = {}
    for row in rows:
        validate_schema(row, schema)
        if row[key] in result:
            raise Invalid(f'duplicate {schema} {key}: {row[key]}')
        result[row[key]] = row
    return result


def load_ledger(path: Path) -> dict:
    return index_rows(read_jsonl(path), 'rights-record')


def clear_source(record: dict, ledger_path: Path, jurisdictions: list[str], use: str) -> str:
    """Check recorded decisions and local evidence; cannot determine copyright status."""
    approved(record['review'], record['id'])
    if record['unresolved_issues']:
        raise Invalid(f'{record["id"]}: unresolved rights issues')
    if not jurisdictions or any(not re.fullmatch('[A-Z]{2}', j) for j in jurisdictions):
        raise Invalid('explicit two-letter jurisdictions are required')
    for jurisdiction in jurisdictions:
        matching = [c for c in record['clearances'] if c['jurisdiction'] == jurisdiction]
        if len(matching) != 1 or use not in matching[0]['uses']:
            raise Invalid(f'{record["id"]}: missing/ambiguous {jurisdiction} clearance for {use}')
    source = record['source']
    for field in ('retrieved_on', 'revision', 'raw_path', 'sha256', 'included_material',
                  'terms_decision'):
        if not source[field]:
            raise Invalid(f'{record["id"]}: missing source {field}')
    if not source['terms_evidence']:
        raise Invalid(f'{record["id"]}: source terms evidence required')
    if record['source_kind'] == 'public_domain_candidate':
        publication = record['publication']
        if not all(publication[k] for k in ('original_year', 'edition', 'publisher', 'evidence')):
            raise Invalid(f'{record["id"]}: exact edition/publication evidence required')
        if not source['url']:
            raise Invalid(f'{record["id"]}: source URL required')
        if any(not c['life_dates'] for c in record['contributors']):
            raise Invalid(f'{record["id"]}: contributor dates/status evidence required')
    base = ledger_path.resolve().parent
    raw = (base / source['raw_path']).resolve()
    if not raw.is_relative_to(base):
        raise Invalid('raw_path must stay inside the ledger directory')
    if file_hash(raw) != source['sha256']:
        raise Invalid(f'{record["id"]}: raw-file hash mismatch')
    return raw.read_text(encoding='utf-8')


def shingles(text: str) -> set[tuple[str, ...]]:
    words = re.findall(r'\w+', text.casefold())
    return {tuple(words[i:i + 5]) for i in range(len(words) - 4)} if len(words) >= 20 else set()


def check_leakage(records: list[dict], benchmark: list[dict] | None = None) -> None:
    """Pilot-scale pairwise lexical screen, plus hard group/work/author boundaries."""
    seen = {}
    texts = []
    for row in records:
        split = row['split']
        for namespace, values in (('group', [row['split_group']]),
                                  ('work', row['source_work_ids']),
                                  ('author', row.get('_author_ids', []))):
            for value in values:
                key = namespace, value
                if key in seen and seen[key] != split:
                    raise Invalid(f'cross-split {namespace}: {value}')
                seen[key] = split
        text = '\n'.join(m['content'] for m in row['messages'])
        texts.append((row['id'], split, text, shingles(text)))
    for task in benchmark or []:
        key = 'group', task['split_group']
        if key in seen and seen[key] != 'test':
            raise Invalid(f'benchmark split-group leak: {task["split_group"]}')
        text = task['context']
        texts.append((task['id'], 'test', text, shingles(text)))
    for i, (ident, split, text, tokens) in enumerate(texts):
        for other_id, other_split, other_text, other_tokens in texts[:i]:
            if split == other_split:
                continue
            exact = ' '.join(text.casefold().split()) == ' '.join(other_text.casefold().split())
            overlap = len(tokens & other_tokens) / min(len(tokens), len(other_tokens)) if tokens and other_tokens else 0
            if exact or overlap >= .8:
                raise Invalid(f'exact/near-duplicate across splits: {ident}, {other_id}')


def validate_dataset(path: Path, ledger_path: Path, jurisdictions: list[str],
                     benchmark: list[dict] | None = None) -> list[dict]:
    ledger = load_ledger(ledger_path)
    records = list(index_rows(read_jsonl(path), 'dataset-record').values())
    cleared = {}
    versions = {r['dataset_version'] for r in records}
    if len(versions) != 1:
        raise Invalid('dataset versions must match')
    for row in records:
        approved(row['review'], row['id'])
        if row['content_hash'] != digest(row['messages']):
            raise Invalid(f'{row["id"]}: message content hash mismatch')
        roles = [m['role'] for m in row['messages']]
        if roles[0] == 'system':
            roles = roles[1:]
        if len(roles) < 2 or roles != ['user', 'assistant'] * (len(roles) // 2):
            raise Invalid(f'{row["id"]}: expected alternating user/assistant turns ending in assistant')
        if row['origin'] == 'synthetic' and row['teacher'] is None:
            raise Invalid(f'{row["id"]}: synthetic example requires teacher/terms provenance')
        if row['teacher'] is not None:
            approved(row['teacher']['review'], f'{row["id"]} teacher terms')
        works, authors = set(), set()
        for ident in row['rights_record_ids']:
            if ident not in ledger:
                raise Invalid(f'{row["id"]}: unknown rights record {ident}')
            rights = ledger[ident]
            use = 'training' if row['split'] == 'train' else 'evaluation'
            if (ident, use) not in cleared:
                cleared[ident, use] = clear_source(rights, ledger_path, jurisdictions, use)
            works.add(rights['work_id'])
            authors.update(rights['author_ids'])
            if rights['source_kind'] == 'public_domain_candidate' and not any(
                s['rights_record_id'] == ident for s in row['source_spans']
            ):
                raise Invalid(f'{row["id"]}: public-domain source requires an exact raw-text span')
        if set(row['source_work_ids']) != works:
            raise Invalid(f'{row["id"]}: source work IDs do not match rights records')
        for span in row['source_spans']:
            if span['rights_record_id'] not in row['rights_record_ids']:
                raise Invalid('span references an undeclared rights record')
            use = 'training' if row['split'] == 'train' else 'evaluation'
            raw = cleared[span['rights_record_id'], use]
            if span['start'] >= span['end'] or raw[span['start']:span['end']] != span['text']:
                raise Invalid(f'{row["id"]}: source span mismatch (Unicode code-point offsets)')
        row['_author_ids'] = sorted(authors)
    check_leakage(records, benchmark)
    return records
