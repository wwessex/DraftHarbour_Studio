"""Prepare complete-paragraph continuations inside existing exact scoped spans."""
import copy
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import digest, file_hash, read_jsonl, validate_dataset
from foundation.paragraph_lessons import paragraph_lesson, verify_derivation

OUT = ROOT / 'artifacts/paragraph-dialogue-v12'
PRIOR = ROOT / 'artifacts/task-alignment-v11'
LEDGER = ROOT / 'rights/grounding-balanced-v1.scoped.jsonl'
SPECS = [
    ('embroidery', 'gb-hopkins-embroidery', 4, 1,
     'Continue after the complete supplied paragraphs with one new paragraph of period story prose. Sappho may offer to teach Dora embroidery, but leave where she learned it unanswered and let Dora notice that omission. Preserve their names, existing friendship and historical narrative voice. Do not repeat the input or add an explanation.'),
    ('support', 'gb-wilson-help', 3, 1,
     'Continue after the complete supplied paragraphs with one new paragraph. Let Mag soften at Jim’s promise while remaining wounded by how others treat her. Keep the historical speech and brief emotional narration. His offer is a promise, not proof that money or work has already been delivered. Return only new story prose; do not repeat the input.'),
    ('work', 'gb-hopkins-work', 1, 1,
     'Continue after the supplied complete paragraph with one new paragraph of period story prose. Let Sappho answer Dora’s question about the work, distinguish her preference from the frustrations of taking dictation and offer Dora a chair. Preserve names and setting. Return only new prose, without repeating the input or adding an explanation.'),
    ('news', 'gb-harper-newspaper', 1, 1,
     'Continue after the supplied complete paragraph with one new paragraph containing Robert’s cautiously spoken news of the war and his coded comparison with fresh market produce. Preserve his historical speech. This is his report, not independently verified narration. Return only the new paragraph, without repeating the input or explaining the code.'),
    ('rumour-dialogue', 'gb-harper-newspaper', 3, 3,
     'Continue the exchange with exactly three short spoken turns: Robert rejects the rumour, Linda says she heard it and Robert calls that report a falsehood. Preserve these characters’ historical speech. Return only the three quoted turns in separate paragraphs, with no narration, speaker labels or explanation. Do not reproduce the supplied paragraphs or invent evidence for the rumour.'),
]


def main():
    if OUT.exists():
        raise ValueError('Refuse overwrite')
    lock_path = ROOT / 'curation/task-alignment-v11/preparation.lock.json'
    lock = json.loads(lock_path.read_text())
    protected = dict(lock['source_hashes'])
    protected.update({str((PRIOR / n).relative_to(ROOT)):h for n,h in lock['artifact_hashes'].items()})
    proof = json.loads((PRIOR / 'verification.json').read_text())
    protected.update(proof['protected_hashes'])
    for name, h in protected.items():
        assert file_hash(ROOT / name) == h, name
    old = read_jsonl(ROOT / 'artifacts/balanced-fiction-v9/records.jsonl')
    parents = {r['id']:r for r in old if r['split'] == 'train'}
    candidates, bindings = [], []
    for name, parent_id, index, count, instruction in SPECS:
        parent = parents[parent_id]
        assert len(parent['source_spans']) == 1
        span = parent['source_spans'][0]
        d = paragraph_lesson(span['text'], index, count)
        verify_derivation(span['text'], d)
        r = copy.deepcopy(parent)
        r['id'] = 'pd12-' + name
        r['dataset_version'] = 'paragraph-dialogue-v12-proposal'
        r['task'] = 'dialogue' if name == 'rumour-dialogue' else 'fiction'
        r['messages'] = [dict(role='user', content=instruction + '\n\nPRECEDING PARAGRAPHS:\n' + d['context']),
                         dict(role='assistant', content=d['answer'])]
        r['content_hash'] = digest(r['messages'])
        r['review'] = dict(status='approved', reviewer='Codex AI: exact source and instruction alignment review', reviewed_on='2026-11-01',
                           notes='AI preparation review, not human literary approval or legal certification. Exact contiguous context/answer within the existing scoped parent source. No generated literary answer; no newly cleared span. Historical register is not modernised. Training not executed.')
        candidates.append(r)
        bindings.append(dict(id=r['id'], parent_id=parent_id, source_span=span, derivation=d,
                             absolute_context_start=span['start'], absolute_context_end=span['start'] + d['context_end'],
                             absolute_answer_start=span['start'] + d['answer_start'], absolute_answer_end=span['start'] + d['answer_end']))
    # Replace, rather than append, full-scene presentations from these four parents.
    replacement = {'gb-hopkins-embroidery':'pd12-embroidery', 'gb-wilson-help':'pd12-support',
                   'gb-hopkins-work':'pd12-work', 'gb-harper-newspaper':'pd12-rumour-dialogue'}
    by_id = {r['id']:r for r in candidates}
    proposed = []
    for parent in read_jsonl(PRIOR / 'records.proposed.jsonl'):
        r = copy.deepcopy(by_id[replacement[parent['id']]] if parent['id'] in replacement else parent)
        r['dataset_version'] = 'paragraph-dialogue-v12-proposal'
        proposed.append(r)
    assert sum(r['split'] == 'train' for r in proposed) == 25
    assert all(n not in {r['id'] for r in proposed} for n in replacement)
    OUT.mkdir()
    def rows(name, values):
        with (OUT / name).open('x') as f:
            for r in values:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
    rows('candidates.jsonl', candidates)
    rows('derivations.jsonl', bindings)
    rows('records.proposed.jsonl', proposed)
    validate_dataset(OUT / 'candidates.jsonl', LEDGER, ['GB', 'US'])
    validate_dataset(OUT / 'records.proposed.jsonl', LEDGER, ['GB', 'US'])
    packet = ['# Complete-paragraph and dialogue source lessons', '', 'Preparation only. Informed AI review, no human approval. Source spans, context and answers are exact; no modernised or generated literary teaching prose. Four variants replace their full-scene parents in the proposed mixture. The Robert news paragraph is an alternative, excluded from that mixture. All source material has appeared in earlier training.', '']
    for r in candidates:
        packet += ['## ' + r['id'], '', r['messages'][0]['content'], '', '### Exact published continuation', '', r['messages'][-1]['content'], '']
    (OUT / 'REVIEW.md').write_text('\n'.join(packet))
    inputs = [Path(__file__), ROOT / 'foundation/paragraph_lessons.py', LEDGER, lock_path,
              ROOT / 'artifacts/balanced-fiction-v9/records.jsonl', PRIOR / 'cases.frozen.jsonl']
    report = dict(status='preparation-only-no-training', candidates=5, paragraph_candidates=4, dialogue_candidates=1,
                  proposal_training_records=25, replaced_full_scene_parents=4, reserve_candidates=['pd12-news'],
                  exposed_monitor_records=16, new_literary_answers_authored=0, new_source_spans=0,
                  evaluation_cases_path='artifacts/task-alignment-v11/cases.frozen.jsonl', evaluation_cases_run=0,
                  human_quality_ratings=0, model_promoted=False, protected_hashes=protected,
                  input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in inputs},
                  output_hashes={n:file_hash(OUT / n) for n in ['candidates.jsonl','derivations.jsonl','records.proposed.jsonl','REVIEW.md']})
    with (OUT / 'verification.json').open('x') as f:
        json.dump(report, f, indent=2)
    print('Prepared five exact-source lessons; four replace full-scene parents in the 25-example proposal. No training.')


if __name__ == '__main__':
    main()
