"""Source-only literary mixture; no download, teacher outputs or new rights decisions."""
from pathlib import Path
import copy
import hashlib
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import digest, validate_dataset, check_leakage
OUT = ROOT / 'artifacts/literary-mix-v1'
LEDGER = ROOT / 'rights/literary-mix-v1.scoped.jsonl'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def rows(path, values):
    with path.open('x') as stream:
        for value in values:
            stream.write(json.dumps(value, ensure_ascii=False) + '\n')


def derived_tasks(text):
    """Every target is an unchanged source substring. No purported authored revision."""
    words = list(re.finditer(r'\S+', text))
    cut = words[len(words) // 2].start()
    boundaries = [m.end() for m in re.finditer(r'[.!?][\"”]?\s+', text)
                  if len(text[:m.end()].split()) >= 12 and len(text[m.end():].split()) >= 20]
    if boundaries:
        cut = min(boundaries, key=lambda value: abs(value - cut))
    yield ('continuation', 'fiction', 'Continue the following fiction fragment in its existing voice, viewpoint and tense. Return only the next prose passage, without repeating the fragment or adding explanation.\n\nFRAGMENT:\n' + text[:cut].rstrip(), cut, len(text))
    # Only complete quoted utterances, with enough preceding context; no invented lines.
    for match in re.finditer(r'"[^"\n]+"', text):
        if len(text[:match.start()].split()) >= 10 and 8 <= len(match.group().split()) <= 80:
            yield ('dialogue', 'dialogue', 'Write the next spoken line after this context. Preserve the speaker’s period voice and situation. Return only the quoted dialogue line, with no explanation.\n\nCONTEXT:\n' + text[:match.start()].rstrip(), match.start(), match.end())
            break


def build():
    OUT.mkdir(parents=True, exist_ok=False)
    inputs = [ROOT/'artifacts/source-tasks-v1/records.jsonl', ROOT/'artifacts/source-tasks-v1/excerpts.jsonl', ROOT/'artifacts/craft-expansion-v1/train.records.jsonl', ROOT/'rights/source-tasks-v1.scoped.jsonl', ROOT/'rights/craft-expansion-v1.scoped.jsonl']
    old = validate_dataset(inputs[0], inputs[3], ['GB', 'US'])
    craft = validate_dataset(inputs[2], inputs[4], ['GB', 'US'])
    ledgers = read(inputs[3]) + read(inputs[4])
    assert len({r['id'] for r in ledgers}) == len(ledgers)
    # Byte-equivalent decisions copied into a combined ledger; no scope expansion.
    rows(LEDGER, ledgers)
    records, trace = [], []
    for excerpt in read(inputs[1]):
        if excerpt['split'] != 'train':
            continue  # Austen remains evaluation-only, never a candidate training input.
        source = excerpt['span']
        original = next(r for r in old if r['id'].endswith('-restore') and r['source_spans'] == [source])
        split = 'validation' if excerpt['author'] == 'james-jackson-wray' else 'train'
        variants = [('repair', 'editing', original['messages'][0]['content'], 0, len(excerpt['text']))] + list(derived_tasks(excerpt['text']))
        for kind, task, prompt, start, end in variants:
            target = excerpt['text'][start:end]
            assert target and target in excerpt['text']
            record = copy.deepcopy(original)
            record.pop('_author_ids', None)
            record.update(id=f'mix-{len(records):04d}-{kind}', dataset_version='literary-mix-v1', task=task, split=split,
                          messages=[dict(role='user', content=prompt), dict(role='assistant', content=target)], teacher=None, origin='derived')
            record['review'] = dict(status='approved', reviewer='Codex AI: deterministic source derivation and alignment audit', reviewed_on='2026-10-25', notes='AI audit, not human literary judgement or legal certification. Target is an unchanged substring within an already scoped source. Repair removes only a mechanical duplicate, not a genuine author revision. Dialogue is a source-derived next-line demonstration, not original teacher generation.')
            record['content_hash'] = digest(record['messages'])
            records.append(record)
            trace.append(dict(record_id=record['id'], source_id=excerpt['sid'], source_span=source, transformed_excerpt_sha256=digest(excerpt['text']), target_start=start, target_end=end, target_sha256=hashlib.sha256(target.encode()).hexdigest(), prior_approval=excerpt['approval'], kind=kind))
    for source_record in craft:
        record = copy.deepcopy(source_record)
        record.pop('_author_ids', None)
        record.update(id='mix-' + record['id'], dataset_version='literary-mix-v1')
        records.append(record)
        trace.append(dict(record_id=record['id'], kind='attributed-craft', prior_record_id=source_record['id'], prior_file_sha256=sha(inputs[2]), target_sha256=hashlib.sha256(record['messages'][-1]['content'].encode()).hexdigest()))
    rows(OUT/'records.jsonl', records)
    rows(OUT/'trace.jsonl', trace)
    validated = validate_dataset(OUT/'records.jsonl', LEDGER, ['GB', 'US'])
    assert all(r['teacher'] is None and r['origin'] == 'derived' for r in validated)
    contexts = read(ROOT/'artifacts/craft-expansion-v1/test.contexts.jsonl')
    check_leakage(validated, [dict(id=c['id'], split_group=c['source_id'], context=c['text']) for c in contexts])
    cases = read(ROOT/'artifacts/craft-training-v2/test.cases.jsonl')
    for context in contexts:
        for kind, instruction, cap in [
            ('voice', 'Rewrite this passage more concisely in at most 140 words while preserving the original narrator, tense, dialect and emotional distance. Keep all established relationships and limits on knowledge. Return only revised story prose.', 140),
            ('analysis', 'In at most 120 words, analyse the passage’s viewpoint, source of tension and pacing. Support the observations with details present in the supplied passage. Distinguish inference from fact; do not invent later events.', 120),
        ]:
            cases.append(dict(id=context['id']+'-'+kind, scenario_id=context['id'], source_id=context['source_id'], kind=kind, task='analysis' if kind=='analysis' else 'editing', context=context['text'], prompt=instruction+'\n\nPASSAGE:\n'+context['text'], exact_reference=None, word_count_min=0, word_count_max=cap, source_facts=context['facts'], source_unknowns=context['unknowns']))
    assert len(cases) == 24
    rows(OUT/'test.cases.jsonl', cases)
    from collections import Counter
    report = dict(records=len(records), by_split=dict(Counter(r['split'] for r in records)), training_by_task=dict(Counter(r['task'] for r in records if r['split']=='train')), input_hashes={str(p.relative_to(ROOT)):sha(p) for p in inputs}, ledger_sha256=sha(LEDGER), current_candidate_author_work_disjoint=True,
        limitations=['Wray validation work appeared in earlier exploratory adapters, but is excluded from this fresh candidate training. It is not a pristine project-wide holdout.', 'Mansfield/Chesnutt remain excluded from all project fine-tuning. Their four contexts were used in earlier diagnostics; no base-pretraining absence is claimed.', 'No genuine author revision, modern creative teacher target, full-scene demonstration or fictional compression target admitted. Pacing/storytelling teaching is limited to attributed craft explanations.', 'Twenty craft explanations and a narrow historical fiction sample do not establish Muse parity. Human quality review remains required.'])
    with (OUT/'validation.json').open('x') as f: json.dump(report, f, indent=2)
    with (OUT/'TRAINING-REVIEW.md').open('x') as f:
        f.write('# Source-only literary mix — AI audit, not human quality approval\n\n')
        for record in records:
            if record['split'] == 'train':
                f.write(f'## {record["id"]} ({record["task"]})\n\n{record["messages"][0]["content"]}\n\n**SOURCE TARGET**\n\n{record["messages"][-1]["content"]}\n\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    build()
