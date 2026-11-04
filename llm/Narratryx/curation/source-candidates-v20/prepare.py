"""Prepare nine source-only candidates and a source-disjoint review proposal; no training."""
import copy
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import digest,file_hash,read_jsonl,validate_dataset,load_ledger
from foundation.mixed_curriculum import require_distinct_source_spans
from foundation.source_candidates import scoped_raw_span,continuation
OUT=ROOT/'artifacts/source-candidates-v20'
LEDGER=ROOT/'rights/grounding-balanced-v1.scoped.jsonl'
VERSION='source-candidates-v20-review-proposal'
CONT=[
 ('resistance','gb-wilson-resistance',2,1,'Continue after these two complete paragraphs with one new paragraph of historical story prose. Show Mrs. B. lowering the stick and Frado returning toward the house, with Mrs. B. carrying the wood. End on Frado’s recognition of the effect of her resistance. Do not add an explanation or repeat the input. This scene permits the actual reaction and outcome, not just a promise.'),
 ('market-departure','gb-harper-market',5,1,'Continue the supplied complete paragraphs with one new paragraph. Let the other servant confirm the coded market exchange, refer to long faces at the post office, and depart at a quicker pace. Retain the historical speech and brief action tag. Return only the new story paragraph; do not explain the code or add independent confirmation of the news.'),
 ('invitation-departure','gb-hopkins-invitation',1,2,'Continue the complete invitation paragraph with exactly two new paragraphs: Sappho courteously accepts; Dora says goodbye until Sunday, says she will be preparing for company, and leaves down the stairs. This scene explicitly permits acceptance and departure. Preserve the historical dialogue and narration; return only new story prose.')]
DIRECT=[
 ('conditional-escort',75334,'fiction','Write one paragraph of period social fiction. Agnes offers money without speaking; the cottager declines it and she replaces the half-guinea. Resolve their disagreement about an escort with an explicit limited agreement: he will accompany her to her friends’ street and wait, and she will return to the cottage if the friends are gone. This scene permits that agreement. Use dialogue with narration; return only the paragraph.'),
 ('unfulfilled-wait',148523,'fiction','Write one paragraph of period social fiction showing an expectation that is not fulfilled. Clifford waits near the inn through the day, secures a coach place and travels at least six miles before abandoning the hope that Agnes will stop the coach. She must not actually appear or speak. Return only the story paragraph.'),
 ('garden-action',179101,'fiction','Write one paragraph of period social fiction about Agnes responding physically to Fitzhenry’s garden request. Connect the work with her former role, show her trembling hand and pleased obedience as she ties up the straggling flowers, and let him follow attentively. Do not announce a cure or a complete recovery of his memory. Return only story prose.'),
 ('contrasting-aims',86909,'dialogue','Write one paragraph of narrated period dialogue in three spoken turns: Agnes refuses undeserved credit and explains her fear of intruding; Fanny rejects that self-exclusion with affection; Agnes explains why she needs a sympathetic friend to endure her duty. Give their concerns distinct emphasis, retaining the historical register. Narration and speech tags are allowed; this is not a dialogue-only task. Return only story prose.'),
 ('reported-money',19080,'fiction','Write one paragraph of period social fiction after Clifford and Agnes have travelled a hundred miles towards Gretna Green. Show him pretending alarm over the wrong pocket-book and claiming limited money for the remaining journey; Agnes is distressed but believes his account. Distinguish his performance from her belief without certifying the claim as an independently checked fact. Return only story prose.')]


def review():
    return dict(status='approved',reviewer='Codex AI: source derivation and task-alignment preparation review',reviewed_on='2026-11-01',notes='AI preparation assessment only, not human literary approval or new legal certification. Exact source-derived literary answer within existing training scope; task brief authored after reading the source. Candidate for sampling review, not training execution or model promotion.')


def main():
    if OUT.exists():raise ValueError('Refuse overwrite')
    prior_lock=ROOT/'curation/fiction-questions-v19/diagnostic.lock.json'
    lock=json.loads(prior_lock.read_text());protected={}
    for group in ['source_hashes','artifact_hashes']:
        protected.update(lock[group])
    prior_protocol=json.loads((ROOT/'artifacts/fiction-questions-v19/protocol.frozen.json').read_text())
    protected.update(prior_protocol['protected_artifacts'])
    for n,h in protected.items():assert file_hash(ROOT/n)==h,n
    ledger=load_ledger(LEDGER)
    parent_path=ROOT/'artifacts/balanced-fiction-v9/records.jsonl'
    parents={r['id']:r for r in read_jsonl(parent_path) if r['split']=='train'}
    approved_path=ROOT/'artifacts/clean-source-approved-v1/prose.approved.jsonl'
    approved=read_jsonl(approved_path)
    pending_path=ROOT/'artifacts/clean-source-expansion-v1/train-candidates.screened.pending.jsonl'
    assert file_hash(pending_path)=='b575358cf5c419545c27326ec6e9e04076aad886c0d0fb38b3e6f9ad6e6d907e'
    pending={r['id']:r for r in read_jsonl(pending_path)}
    candidates=[];bindings=[]
    for name,parent_id,index,count,instruction in CONT:
        parent=parents[parent_id];span=parent['source_spans'][0];d=continuation(span,index,count)
        row=copy.deepcopy(parent);row.update(id='sc20-'+name,dataset_version=VERSION,task='fiction',review=review())
        row['messages']=[dict(role='user',content=instruction+'\n\nPRECEDING PARAGRAPHS:\n'+d['context']),dict(role='assistant',content=d['answer'])]
        row['content_hash']=digest(row['messages']);candidates.append(row)
        bindings.append(dict(id=row['id'],method='contiguous-paragraph-continuation',parent_id=parent_id,derivation=d,source_spans=row['source_spans']))
    opie=ledger['opie-father-daughter-pg49621'];raw_path=LEDGER.parent/opie['source']['raw_path']
    assert file_hash(raw_path)==opie['source']['sha256']
    with raw_path.open(newline='') as f:raw=f.read()
    for name,start,task,instruction in DIRECT:
        a=next(r for r in approved if r['source_id']=='opie-father-daughter-pg49621' and r['raw_start']==start)
        assert a['rights_status']==a['review_status']=='approved' and a['approval_record_id']=='clean-source-expansion-human-approval-2026-10-18'
        assert all(a[k]==v for k,v in pending[a['id']].items() if k not in ['rights_status','review_status'])
        span=scoped_raw_span(raw,a,opie['source']['sha256'])
        row=dict(schema_version='1.0',id='sc20-'+name,dataset_version=VERSION,task=task,split='train',split_group='opie-father-daughter-pg49621',origin='derived',messages=[dict(role='user',content=instruction),dict(role='assistant',content=span['text'])],source_work_ids=[opie['work_id']],rights_record_ids=[opie['id']],source_spans=[span],teacher=None,review=review(),rubric=['source fidelity','instruction alignment','concrete scene progression'])
        row['content_hash']=digest(row['messages']);candidates.append(row)
        bindings.append(dict(id=row['id'],method='approved-raw-span-with-newline-normalisation-only',approved_parent_id=a['id'],original_raw_start=a['raw_start'],original_raw_end=a['raw_end'],original_raw_span_sha256=a['raw_span_sha256'],approval_record_id=a['approval_record_id'],source_spans=[span]))
    dogs_path=ROOT/'artifacts/independent-scenes-v1/draft.records.jsonl'
    dogs=copy.deepcopy(next(r for r in read_jsonl(dogs_path) if r['id']=='james-dogs-1908'))
    dogs.update(id='sc20-dogs-lexical-revision',dataset_version=VERSION,review=review())
    dogs['content_hash']=digest(dogs['messages']);candidates.append(dogs)
    bindings.append(dict(id=dogs['id'],method='documented-author-edition-revision',parent_id='james-dogs-1908',source_spans=dogs['source_spans'],limitation='Existing lexical edition alternative, not a newly discovered substantive revision or shorter paragraph. No universal preference for later edition.'))
    assert len(candidates)==9
    require_distinct_source_spans(candidates,ledger)
    previous_path=ROOT/'artifacts/mixed-curriculum-v15b/records.proposed.jsonl'
    previous=read_jsonl(previous_path);by_id={r['id']:r for r in candidates}
    replacements={'gb-wilson-resistance':'sc20-resistance','gb-harper-market':'sc20-market-departure'}
    selected=[]
    for row in previous:
        q=copy.deepcopy(by_id[replacements[row['id']]] if row['id'] in replacements else row)
        q['dataset_version']=VERSION;selected.append(q)
    additions=[r for r in candidates if r['id'] not in set(replacements.values())|{'sc20-invitation-departure'}]
    for row in additions:selected.append(copy.deepcopy(row))
    train=[r for r in selected if r['split']=='train'];assert len(train)==28
    require_distinct_source_spans(train,ledger)
    OUT.mkdir()
    def rows(name,items):
        with (OUT/name).open('x') as f:
            for item in items:f.write(json.dumps(item,ensure_ascii=False)+'\n')
    rows('candidates.jsonl',candidates);rows('derivations.jsonl',bindings);rows('records.proposed.jsonl',selected)
    validate_dataset(OUT/'candidates.jsonl',LEDGER,['GB','US']);validate_dataset(OUT/'records.proposed.jsonl',LEDGER,['GB','US'])
    packet=['# Source-only teaching candidates','','Preparation only. Nine candidates, eight selected in a28-example review proposal. All source prose already appeared in earlier preparation or raw/task training. No new authors or whole-book rights. Instructions are AI-authored after reading the source; literary answers are exact published substrings. AI source/task review is not human quality approval. No training recipe or job is launched.','']
    for row in candidates:
        packet+=['## '+row['id'],'',row['messages'][0]['content'],'','### Published answer','',row['messages'][-1]['content'],'']
    with (OUT/'REVIEW.md').open('x') as f:f.write('\n'.join(packet))
    inputs=[Path(__file__),ROOT/'foundation/source_candidates.py',ROOT/'foundation/paragraph_lessons.py',ROOT/'foundation/mixed_curriculum.py',LEDGER,parent_path,approved_path,pending_path,raw_path,dogs_path,previous_path,prior_lock,ROOT/'rights/approvals/clean-source-expansion-human-approval-2026-10-18.json']
    proof=dict(status='candidate-preparation-only',candidate_records=9,selected_candidates=8,reserved_candidates=['sc20-invitation-departure'],reserve_reason='Overlaps retained sr14-event-times repair; do not sample together.',proposal_train_records=28,broader_prose_records=20,semantic_repairs=5,structural_edits=3,exposed_validation_monitors=16,replaced_full_scene_parents=replacements,additional_train_spans_relative_v16=6,new_source_grants=0,new_authors=0,new_literary_answer_prose=0,training_jobs=0,inference_requests=0,human_quality_ratings=0,model_promoted=False,protected_hashes=protected,input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in inputs},output_hashes={n:file_hash(OUT/n) for n in ['candidates.jsonl','derivations.jsonl','records.proposed.jsonl','REVIEW.md']})
    with (OUT/'verification.json').open('x') as f:json.dump(proof,f,indent=2);f.write('\n')
    print('Prepared9 source-only candidates;8 selected in28-train/16-monitor review proposal. No training or inference.')


if __name__=='__main__':main()
