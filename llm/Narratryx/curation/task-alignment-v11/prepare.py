"""Audit all v9 lessons; prepare a smaller source-only proposal without training."""
import copy
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import digest, file_hash, read_jsonl, validate_dataset
from foundation.task_alignment import lesson_form, observable_checks, verify_unchanged_target

OUT = ROOT / 'artifacts/task-alignment-v11'
PARENT = ROOT / 'artifacts/balanced-fiction-v9/records.jsonl'
LEDGER = ROOT / 'rights/grounding-balanced-v1.scoped.jsonl'
REPAIRS = {
    'gb-v2-directed-opie-0256': 'Write a brief period social-fiction paragraph about Agnes consulting Fanny on how to earn a living. Fanny keeps a day-school and takes in shawl-work in a manufacturing town. Move from Agnes asking about her livelihood to an agreed plan for the same work and a small back room in Fanny’s dwelling. Include the agreement explicitly; this scene permits a resolved arrangement. Return only the paragraph.',
    'gb-v2-directed-opie-0262': 'Write a period social-fiction paragraph in which Fanny makes a condition before accepting a marriage proposal: Agnes and her child must be welcome to make a home with her whenever they choose. Have her suitor explicitly consent, then close with Agnes witnessing the marriage. This scene permits agreement and a later outcome; it is not a request to preserve unresolved consent. Return only the paragraph.',
}
DIRECT = {'gb-hopkins-host', 'gb-hopkins-room', 'gb-james-face-1908', 'gb-james-proposal-revision',
          'gb-wilson-resistance', 'gb-v3-022-paced-scene', 'gb-v3-023-paced-scene',
          'gb-harper-market', 'gb-hopkins-embroidery', 'gb-wilson-help', 'gb-v3-016-dialogue-scene',
          'gb-harper-newspaper', 'gb-hopkins-work', 'gb-v3-017-dialogue-scene', 'gb-hopkins-invitation'}


def decision(row):
    ident = row['id']
    form = lesson_form(row)
    if ident in DIRECT:
        return 'retain-prose', 'The directed brief describes the supplied scene or author revision. Historical prose, narrated dialogue and actual permissions remain explicit; this is not evidence of modern dialogue-only or unknown-fact handling.'
    if ident in REPAIRS:
        return 'repair-brief', 'Replace opening/closing reconstruction with source-derived agents, practical terms and explicit agreement. Keep the published answer byte-identical. Agreement is allowed in this scene, not a demonstration of preserving missing consent.'
    if row['task'] == 'editing' and form == 'structural-json':
        return 'retain-edit', 'Anchored duplicate repair or justified no-change control. Structured labels are not literary prose and do not teach general stylistic rewriting.'
    if form == 'boundary-reconstruction':
        return 'quarantine-from-proposal', 'Boundary completion is a legitimate task but poorly matched to writing scenes from facts. Retain historically; do not label it a corrupt answer or a proven cause of degeneration.'
    if form == 'sentence-fragment-continuation':
        return 'reference-only', 'Finishes a sentence from the source without repeating the input. Does not demonstrate adding a whole new paragraph after a completed user paragraph.'
    if form == 'paragraph-continuation':
        return 'reference-only', 'Adds source prose, but the sparse prompt omits surrounding story state. It does not demonstrate the factual/resource constraints required by the failed transfer tasks.'
    if form == 'quoted-craft-exposition':
        return 'reference-only', 'Relevant historical craft explanation. Quoted advice is not a worked example of applying that technique to a new scene.'
    if ident == 'gb-dickens-structural-ending':
        return 'reference-only', 'Legitimate author alternative ending but 1,035 answer words with unintroduced referents at the opening. Different task/scale from restrained rewriting; defer from this short-scene proposal.'
    if form == 'structural-json':
        return 'separate-grounding-arm', 'Keep deterministic evidence/clock/claim labels intact for a separate diagnostic. No oversampling in the proposed writing mixture; no finding that these labels are wrong.'
    raise ValueError(f'unreviewed lesson: {ident}')


def new_cases():
    cases = []
    settings = [
        ('archive-card', 'Maren', 'Osei', 'the only handwritten index card', 'a catalogue demonstration', 'an untested blank card', '10:20', '11:00'),
        ('music-score', 'Tess', 'Imani', 'the only annotated music score', 'a rehearsal display', 'an unchecked photocopy', '15:05', '15:50'),
        ('seed-label', 'Rafi', 'June', 'the only surviving seed label', 'a greenhouse workshop', 'an untested tracing sheet', '09:10', '09:55'),
    ]
    for name, a, b, obj, need, spare, now, due in settings:
        context = f'{a} wants to preserve {obj} without alteration. {b} needs it for {need}. They have {spare}; its suitability is unknown. Neither has agreed to mark, cut or damage the original. It is {now}; the supervisor is expected at {due} and has not arrived.'
        paragraph = f'{a} laid the original on the table. {b} stood beside the spare. They looked at the original again. They had not tested the spare. The supervisor had not arrived. They still had to decide what to do.'
        for kind, instruction, lo, hi in [
            ('dialogue', 'Write four to six dialogue turns, at most 110 words. Give the speakers distinct aims and subtext. Advance one practical next step while preserving missing permission and uncertainty about the spare. Return only dialogue.', None, 110),
            ('continue', 'Add one new paragraph of 60–100 words after the supplied paragraph. Do not repeat it. Add a concrete next action while preserving uncertainty, missing permission and the future arrival. Return only the new paragraph.', 60, 100),
            ('rewrite', 'Rewrite the supplied paragraph in at most 100 words. Improve its movement and reduce repetition without adding permission, resources or knowledge. Return only the revised paragraph.', None, 100),
            ('selected-edit', 'Remove only the accidentally repeated consecutive word inside TARGET. Preserve every other character. Return only the corrected TARGET. Errors outside TARGET must remain untouched.', None, None),
        ]:
            prompt = instruction + '\n\nESTABLISHED STATE:\n' + context
            if kind in ['continue', 'rewrite']:
                prompt += '\n\nPARAGRAPH:\n' + paragraph
            if kind == 'selected-edit':
                prompt += f'\n\nCONTEXT:\nThe the tray stayed closed.\n\nTARGET:\n{a} checked the the spare.'
            cases.append(dict(id=f'ta11-{name}-{kind}', kind=kind, prompt=prompt,
                              word_count_min=lo, word_count_max=hi,
                              exact_reference=f'{a} checked the spare.' if kind == 'selected-edit' else None,
                              established_facts=[context], unknowns=['Spare suitability; consent to alter original; actual supervisor arrival.'],
                              evaluation_role='new-unrun-writing-transfer',
                              provenance='AI-authored evaluation-only scenario. No literary answer, human gold or training target. Author knows the task; models have not been run on these cases.'))
    return cases


def main():
    if OUT.exists():
        raise ValueError('Refuse to overwrite an audit or proposal')
    parent = json.loads((ROOT / 'artifacts/stability-v10/protocol.frozen.json').read_text())
    protected = dict(parent['input_hashes']) | dict(parent['protected_artifacts'])
    for name in ['protocol.frozen.json', 'completion.json', 'candidate.complete.json', 'candidate.responses.jsonl', 'verification.json', 'adapter/adapters.safetensors', 'adapter/adapter_config.json']:
        path = ROOT / 'artifacts/stability-v10' / name
        protected[str(path.relative_to(ROOT))] = file_hash(path)
    for name, expected in protected.items():
        if file_hash(ROOT / name) != expected:
            raise ValueError(f'protected input changed: {name}')
    validate_dataset(PARENT, LEDGER, ['GB', 'US'])
    raw = read_jsonl(PARENT)
    train = [r for r in raw if r['split'] == 'train']
    assert len(train) == 92
    audit, proposed = [], []
    for r in train:
        status, reason = decision(r)
        audit.append(dict(id=r['id'], task=r['task'], form=lesson_form(r), decision=status,
                          evidence=reason, checks=observable_checks(r), source_work_ids=r['source_work_ids'],
                          original_content_hash=r['content_hash'], answer_sha256=digest(r['messages'][-1]['content']),
                          reviewer='Codex AI: informed task-alignment audit, not human approval or causal diagnosis'))
        if status not in ['retain-prose', 'repair-brief', 'retain-edit']:
            continue
        q = copy.deepcopy(r)
        q['dataset_version'] = 'task-alignment-v11-proposal'
        if status == 'repair-brief':
            q['messages'][0]['content'] = REPAIRS[r['id']]
        q['content_hash'] = digest(q['messages'])
        q['review'] = dict(status='approved', reviewer='Codex AI: source-answer and brief alignment review',
                           reviewed_on='2026-11-01', notes='AI preparation review only, not human quality approval or legal certification. ' + reason)
        verify_unchanged_target(r, q)
        proposed.append(q)
    assert len(proposed) == 25 and Counter(a['decision'] for a in audit)['repair-brief'] == 2
    monitor = copy.deepcopy([r for r in raw if r['split'] == 'validation'])
    for r in monitor:
        r['dataset_version'] = 'task-alignment-v11-proposal'
    cases = new_cases()
    old_case_paths = [ROOT / 'artifacts/balanced-fiction-v9/primary.cases.frozen.jsonl', ROOT / 'artifacts/stability-v10-plan/cases.frozen.jsonl']
    old_prompts = {r['prompt'] for p in old_case_paths for r in read_jsonl(p)}
    assert len(cases) == 12 and all(c['prompt'] not in old_prompts for c in cases)
    OUT.mkdir()
    def rows(name, values):
        with (OUT / name).open('x') as f:
            for r in values:
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
    rows('audit.jsonl', audit)
    rows('records.proposed.jsonl', proposed + monitor)
    rows('cases.frozen.jsonl', cases)
    validate_dataset(OUT / 'records.proposed.jsonl', LEDGER, ['GB', 'US'])
    summary = dict(status='preparation-only-no-training', audited_train_records=92,
                   decisions=dict(Counter(a['decision'] for a in audit)),
                   forms=dict(Counter(a['form'] for a in audit)), proposed_training_records=25,
                   prose_records=17, structural_edit_records=8, previously_exposed_monitor_records=16,
                   new_unrun_evaluation_cases=12, literary_answers_changed=0, instruction_repairs=2,
                   new_sources=0, human_approvals=0, model_promoted=False, protected_hashes=protected,
                   input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in [PARENT, LEDGER, Path(__file__), ROOT / 'foundation/task_alignment.py'] + old_case_paths},
                   output_hashes={name:file_hash(OUT / name) for name in ['audit.jsonl', 'records.proposed.jsonl', 'cases.frozen.jsonl']},
                   limits=['No training request or runner supplied; token preflight and recipe/evaluation review required.',
                           'No training demonstration of grounded paragraph continuation or strict modern dialogue-only negotiation with missing consent.',
                           'New scenarios are correlated development tasks, not an independent human benchmark.',
                           'Alignment defects do not establish the cause of v9/v10 degeneration.'])
    (OUT / 'verification.json').write_text(json.dumps(summary, indent=2) + '\n')
    packet = ['# Source-only task-alignment proposal', '', 'Preparation only. AI review, no human approval. Published answers are unchanged; only two source-derived briefs are repaired. Historical dialect and narrator judgements remain attributed to the source scenes. All records are previously exposed training material; the Wray monitor is also exposed.', '']
    for r in proposed:
        packet += ['## ' + r['id'], '', r['messages'][0]['content'], '', '### Unchanged answer', '', r['messages'][-1]['content'], '']
    (OUT / 'REVIEW.md').write_text('\n'.join(packet))
    print(json.dumps({k:v for k,v in summary.items() if not k.endswith('hashes')}, indent=2))


if __name__ == '__main__':
    main()
