"""Prepare source-exact semantic repair candidates; no generated literary answers."""
import copy
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import digest,file_hash,read_jsonl,validate_dataset
from foundation.source_restoration import corrupt_input,verify_corruption
OUT=ROOT/'artifacts/semantic-restoration-v14'
LEDGER=ROOT/'rights/grounding-balanced-v1.scoped.jsonl'
SPECS=[
    ('materials','gb-hopkins-room',0,None,'dark-blue denim','plain white muslin',
     'The bedstead and washing utensils are hidden by dark-blue denim embroidered in white floss. The window draperies are plain white muslin. Restore the mistaken material assignment, preserving every other character.'),
    ('lever','gb-v2-new-003-write',0,None,'gliding into the future','gliding into the past',
     'In this fictional demonstration, the first described lever sends the machine into the future; the other reverses the motion. Restore the first lever’s direction, preserving every other character. This is a character’s account of a fictional device, not a real physics claim.'),
    ('announced-visit','gb-v2-new-010-continue',0,None,'There will call upon you to-night','There called upon you last night',
     'This note announces a future visit tonight at a quarter to eight. It does not report a visit already completed. Restore only the opening verb/time phrase, preserving every other character.'),
    ('event-times','gb-hopkins-invitation',0,0,'Refreshments at nine sharp','Refreshments at half after seven',
     'The invitation is for Sunday evening: reception at half past seven; refreshments at nine. It has not happened yet in this invitation. Restore the refreshment time without changing the reception time or any other character.'),
    ('deferred-answer','gb-james-proposal-revision',1,None,'say no more about this to-day','announce our engagement to-day',
     'Isabel admires the opportunity but defers answering Lord Warburton. She asks him to stop discussing the proposal today; she does not accept an engagement. Restore only that mistaken final request, preserving every other character.'),
    ('explicit-condition','gb-v2-directed-opie-0262',0,None,'To this condition he consented','To this condition he refused',
     'Fanny makes the marriage conditional on Agnes and her child being welcome to a home with her. Her suitor explicitly consents, and the marriage follows. Restore only his response to the condition, preserving every other character. Do not turn an actual agreement into unresolved permission.'),
    ('unanswered-question','gb-hopkins-embroidery',0,4,'did not tell her where she had learned','did tell her where she had learned',
     'Sappho offers to teach Dora embroidery but does not disclose where she learned it. Dora notices that omission. Restore only the mistaken assertion of disclosure, preserving every other character. This is an unanswered factual question, not a refusal to teach.'),
    ('promise','gb-wilson-help',0,2,'I’ll help you, if nobody else will.','I’ve already helped you, when nobody else would.',
     'Jim promises future support through his work. The passage does not establish a completed payment or completed help. Restore only the promise, preserving every other character and the historical speech.'),
    ('concrete-action','gb-hopkins-work',0,1,'pushing a chair toward Dora','wondering whether to ask permission',
     'Sappho answers Dora’s question about her work and ends by offering her a chair with a physical action. No additional permission requirement for offering that chair is established. Restore only the final action, preserving every other character.'),
]


def evaluation_cases():
    # New evaluation-only microtasks; no literary reference answer is supplied.
    cases=[
        dict(id='sr14-binding',kind='object-state',prompt='The original register is readable. A duplicate has not been inspected. Return JSON only with unknown_object (original/duplicate) and original_readable (boolean). Do not invent an inspection.',expected_json=dict(unknown_object='duplicate',original_readable=True)),
        dict(id='sr14-future',kind='clock-state',prompt='Same-day24-hour snapshot: now11:35, scheduled12:10, arrived:false. Return JSON only with state (arrived/not_established/not_yet_due/due_now/overdue) and minutes_to_schedule (scheduled minus now).',expected_json=dict(state='not_yet_due',minutes_to_schedule=35)),
        dict(id='sr14-permission',kind='permission-state',prompt='Only cutting or marking the original chart requires Leda’s approval. Visual inspection of the separate spare is expressly allowed and needs no approval. Leda has not approved original alteration. Return JSON only with may_alter_original and may_inspect_spare, both booleans.',expected_json=dict(may_alter_original=False,may_inspect_spare=True)),
        dict(id='sr14-evidence',kind='evidence-state',prompt='A patch was checked for size against a sleeve. No heat or durability test took place. Return JSON only with size_checked, heat_tested and durability_tested, all booleans.',expected_json=dict(size_checked=True,heat_tested=False,durability_tested=False)),
        dict(id='sr14-inventory-rewrite',kind='rewrite',prompt='Rewrite the paragraph in at most90words to reduce repetition. Preserve object/property assignments and uncertainty. Add no knowledge, permission, people or equipment. Return only revised prose.\n\nPARAGRAPH:\nThe original register was readable. Tomas stood by the duplicate. The duplicate had not been inspected. Tomas looked from the readable register to the duplicate. Leda had not agreed to mark the original.',word_count_max=90),
        dict(id='sr14-spare-continue',kind='continue',prompt='Add exactly one new paragraph of60–100words with a concrete practical next action. A workshop has an original chart, a separate untested spare, a pencil and a ruler; this is the complete resource list. Leda alone must approve cutting or marking the original and has not done so. Visual inspection and measuring the spare are expressly allowed without approval. Ordinary actions with these listed resources are permitted; add no equipment, people or new permission. Preserve uncertainty about heat resistance.\n\nPRECEDING PARAGRAPH:\nTomas put the ruler beside the spare. Leda kept the original chart flat on the table. Neither had checked the spare’s size or heat resistance.',word_count_min=60,word_count_max=100),
        dict(id='sr14-arrival-dialogue',kind='dialogue',prompt='Write four to six dialogue turns in at most110words. It is13:20; the courier is expected at14:05 and has not arrived. The courier is not late; if an interval is mentioned, compute it correctly. Mina wants the original letter undamaged. Ewan needs a readable copy for a display. A separate copy is present but its legibility is unknown. They may inspect the copy without approval; altering the original requires Mina’s approval, which has not been given. No new people, equipment or copies may be introduced. Move forward through inspection rather than inventing original-alteration consent. Return only dialogue.',word_count_max=110),
        dict(id='sr14-size-continue',kind='continue',prompt='Continue with one new paragraph of60–100words. A tailor has checked a scrap against a sleeve for size only. It fits. Its durability and heat resistance remain unknown. The available items are the sleeve, scrap, needle and thread; this list is closed. No permission is needed to inspect or handle the separate scrap; attaching it to the sleeve requires the owner’s approval and no approval has been given. Add a feasible next action without claiming an unperformed test, guaranteed durability or permission to attach it. Return only the new prose.\n\nPRECEDING PARAGRAPH:\nNessa laid the fitted scrap beside the sleeve. Cal touched the loose thread and waited.',word_count_min=60,word_count_max=100),
    ]
    for c in cases:
        c.setdefault('word_count_min',None);c.setdefault('word_count_max',None)
        c.update(evaluation_role='new-unrun-semantic-transfer',training_eligible=False,
                 provenance='AI-authored evaluation-only task; deterministic JSON references are task labels, not literary teaching answers. No human benchmark approval.')
    return cases


def main():
    if OUT.exists():raise ValueError('Refuse overwrite')
    lock_path=ROOT/'curation/task-matched-v13-ai-review/review.lock.json'
    lock=json.loads(lock_path.read_text())
    protected=dict(lock['source_hashes']) | dict(lock['artifact_hashes'])
    prior=json.loads((ROOT/'artifacts/task-matched-v13-ai-review/verification.json').read_text())
    protected.update(prior['protected_hashes'])
    for n,h in protected.items():assert file_hash(ROOT/n)==h,n
    source_path=ROOT/'artifacts/balanced-fiction-v9/records.jsonl'
    original={r['id']:r for r in read_jsonl(source_path)}
    candidates=[];bindings=[]
    for name,parent_id,span_index,paragraph_index,good,bad,facts in SPECS:
        parent=original[parent_id];assert parent['split']=='train' and parent['teacher'] is None
        span=parent['source_spans'][span_index];text=span['text'];start=0
        if paragraph_index is not None:
            chunks=text.split('\n\n');text=chunks[paragraph_index]
            start=sum(len(x)+2 for x in chunks[:paragraph_index])
        assert span['text'][start:start+len(text)]==text
        binding=corrupt_input(text,good,bad);verify_corruption(text,binding)
        r=copy.deepcopy(parent);r['id']='sr14-'+name;r['dataset_version']='semantic-restoration-v14-candidates';r['task']='editing'
        r['messages']=[dict(role='user',content='Repair this deliberately corrupted source-derived passage using FACTS. Change only the stated semantic error; preserve all other characters, historical voice and line breaks. Return only the corrected passage. No minimum output length.\n\nFACTS:\n'+facts+'\n\nPASSAGE:\n'+binding['damaged_input']),dict(role='assistant',content=text)]
        r['content_hash']=digest(r['messages'])
        r['review']=dict(status='approved',reviewer='Codex AI: exact source restoration and instruction alignment review',reviewed_on='2026-11-01',notes='AI preparation review only, not human approval or legal certification. Input is deterministically corrupted; answer is an exact contiguous published source span. New editing candidate, no generated literary answer, no training job authorised by this metadata.')
        candidates.append(r);bindings.append(dict(id=r['id'],parent_id=parent_id,source_span_index=span_index,source_relative_start=start,source_relative_end=start+len(text),absolute_start=span['start']+start,absolute_end=span['start']+start+len(text),corruption=binding))
    assert len(candidates)==len({b['parent_id'] for b in bindings})==9
    cases=evaluation_cases();old_prompts={c['prompt'] for c in read_jsonl(ROOT/'artifacts/task-matched-v13-plan/cases.frozen.jsonl')}
    assert len(cases)==8 and all(c['prompt'] not in old_prompts for c in cases)
    OUT.mkdir()
    def rows(n,values):
        with (OUT/n).open('x') as f:
            for r in values:f.write(json.dumps(r,ensure_ascii=False)+'\n')
    rows('candidates.jsonl',candidates);rows('derivations.jsonl',bindings);rows('cases.frozen.jsonl',cases)
    validate_dataset(OUT/'candidates.jsonl',LEDGER,['GB','US'])
    packet=['# Source-exact semantic restoration candidates','','Preparation only. These are narrow semantic-editing tasks. All answers are exact published source substrings; only inputs are deterministically corrupted. No human approval, training, added author diversity or demonstrated storytelling gain. Do not replace the broader prose curriculum with these nine repair tasks.','']
    for r in candidates:packet+=['## '+r['id'],'',r['messages'][0]['content'],'','### Exact published answer','',r['messages'][-1]['content'],'']
    with (OUT/'REVIEW.md').open('x') as f:f.write('\n'.join(packet))
    inputs=[source_path,LEDGER,lock_path,Path(__file__),ROOT/'foundation/source_restoration.py',ROOT/'artifacts/task-matched-v13-plan/cases.frozen.jsonl']
    proof=dict(status='preparation-only-not-a-training-recipe',candidates=9,unique_parent_lessons=9,new_sources=0,new_source_spans=0,new_literary_answers_authored=0,new_unrun_evaluation_cases=8,
               dataset_validation_passed=True,human_quality_ratings=0,model_promoted=False,
               protected_hashes=protected,input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in inputs},output_hashes={n:file_hash(OUT/n) for n in ['candidates.jsonl','derivations.jsonl','cases.frozen.jsonl','REVIEW.md']})
    with (OUT/'verification.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
    print('Prepared nine source-exact semantic repairs and eight new unrun evaluation cases; no training.')


if __name__=='__main__':main()
