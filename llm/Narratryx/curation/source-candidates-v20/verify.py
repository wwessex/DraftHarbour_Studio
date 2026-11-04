"""Read-only source, scope, split and proposal audit; no training or inference."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl,validate_dataset,load_ledger,digest
from foundation.source_candidates import scoped_raw_span,continuation
from foundation.mixed_curriculum import require_distinct_source_spans
OUT=ROOT/'artifacts/source-candidates-v20'
LEDGER=ROOT/'rights/grounding-balanced-v1.scoped.jsonl'


def verify(require_tokens=True):
    p=json.loads((OUT/'verification.json').read_text())
    for group in ['protected_hashes','input_hashes']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    for n,h in p['output_hashes'].items():assert file_hash(OUT/n)==h,n
    ledger=load_ledger(LEDGER)
    candidates=read_jsonl(OUT/'candidates.jsonl');proposal=read_jsonl(OUT/'records.proposed.jsonl')
    bindings={b['id']:b for b in read_jsonl(OUT/'derivations.jsonl')}
    parents={r['id']:r for r in read_jsonl(ROOT/'artifacts/balanced-fiction-v9/records.jsonl')}
    approved={r['id']:r for r in read_jsonl(ROOT/'artifacts/clean-source-approved-v1/prose.approved.jsonl')}
    dogs=next(r for r in read_jsonl(ROOT/'artifacts/independent-scenes-v1/draft.records.jsonl') if r['id']=='james-dogs-1908')
    assert len(candidates)==len(bindings)==9
    for r in candidates:
        b=bindings[r['id']];assert r['teacher'] is None and r['origin']=='derived' and r['split']=='train'
        assert r['review']['reviewer'].startswith('Codex AI:') and r['content_hash']==digest(r['messages'])
        assert b['source_spans']==r['source_spans']
        if b['method']=='contiguous-paragraph-continuation':
            parent=parents[b['parent_id']];span=parent['source_spans'][0];d=b['derivation']
            # Match exact context/answer and complete source paragraph boundaries.
            from foundation.paragraph_lessons import verify_derivation
            verify_derivation(span['text'],d)
            assert r['source_spans']==parent['source_spans']
            assert r['messages'][-1]['content']==d['answer']
            assert r['messages'][0]['content'].split('\n\nPRECEDING PARAGRAPHS:\n')[1]==d['context']
            assert d['answer_paragraphs'] in [1,2]
        elif b['method']=='approved-raw-span-with-newline-normalisation-only':
            a=approved[b['approved_parent_id']]
            source=ledger[a['source_id']]['source']
            with (LEDGER.parent/source['raw_path']).open(newline='') as f:raw=f.read()
            assert a['rights_status']==a['review_status']=='approved'
            assert a['source_id']=='opie-father-daughter-pg49621'
            span=scoped_raw_span(raw,a,source['sha256'])
            assert r['source_spans']==[span] and r['messages'][-1]['content']==span['text']
        else:
            assert b['method']=='documented-author-edition-revision'
            assert r['messages']==dogs['messages'] and r['source_spans']==dogs['source_spans']
            assert r['messages'][-1]['content']==r['source_spans'][1]['text']
    validate_dataset(OUT/'candidates.jsonl',LEDGER,['GB','US'])
    checked=validate_dataset(OUT/'records.proposed.jsonl',LEDGER,['GB','US'])
    train=[r for r in proposal if r['split']=='train'];monitor=[r for r in proposal if r['split']=='validation']
    assert len(train)==28 and len(monitor)==16
    require_distinct_source_spans(train,ledger)
    require_distinct_source_spans(candidates,ledger)
    old=read_jsonl(ROOT/'artifacts/mixed-curriculum-v15b/records.proposed.jsonl')
    expected_monitor=[dict(r,dataset_version=proposal[0]['dataset_version']) for r in old if r['split']=='validation']
    assert monitor==expected_monitor
    assert {r['id'] for r in train if r['id'].startswith('sr14-')}=={r['id'] for r in old if r['id'].startswith('sr14-')}
    assert {r['id'] for r in train if r['id'].startswith('gb-ge-')}=={r['id'] for r in old if r['id'].startswith('gb-ge-')}
    assert 'sc20-invitation-departure' not in {r['id'] for r in train} and 'sr14-event-times' in {r['id'] for r in train}
    old_by_id={r['id']:r for r in old};candidate_by_id={r['id']:r for r in candidates}
    for r in proposal:
        expected=dict(candidate_by_id[r['id']] if r['id'] in candidate_by_id else old_by_id[r['id']],dataset_version=r['dataset_version'])
        assert r==expected
    assert {r['id'] for r in train}==({r['id'] for r in old if r['split']=='train'}-set(p['replaced_full_scene_parents']))|({r['id'] for r in candidates}-{'sc20-invitation-departure'})
    train_authors={a for r in checked if r['split']=='train' for a in r['_author_ids']}
    monitor_authors={a for r in checked if r['split']=='validation' for a in r['_author_ids']}
    assert not train_authors & monitor_authors
    old_train_ids={r['id'] for r in old if r['split']=='train'}
    additional=[r for r in candidates if r['id'] not in set(p['replaced_full_scene_parents'].values())|{'sc20-invitation-departure'}]
    assert len(additional)==6 and sum(len(r['source_spans']) for r in additional)==7
    # Earlier metadata calls these six source groups/spans: the James group contains two edition spans.
    for r in additional:
        require_distinct_source_spans([r]+[o for o in old if o['split']=='train'],ledger)
    evaluation=read_jsonl(ROOT/'artifacts/mixed-training-v16/cases.frozen.jsonl')
    seen=[c for c in evaluation if c.get('evaluation_role')=='seen-training-fit-not-generalisation']
    assert len(seen)==5 and all(c.get('training_prompt_overlap_intentional') is True for c in seen)
    primary=[c for c in evaluation if c not in seen]
    assert len(primary)==44
    assert not {c['prompt'] for c in primary} & {r['messages'][0]['content'] for r in train}
    if require_tokens:
        tokens=json.loads((OUT/'tokenizer-preflight.json').read_text())
        for n,h in tokens['input_hashes'].items():assert file_hash(ROOT/n)==h,n
        assert tokens['passed'] and tokens['records']==44 and tokens['train_records']==28 and tokens['maximum_tokens']<=2048
        assert not tokens['weights_loaded'] and not tokens['training']
    return dict(passed=True,candidates=9,selected_candidates=8,reserved_candidates=1,train_records=28,exposed_validation_monitors=16,additional_lesson_records_relative_v16=6,additional_exact_edition_spans_relative_v16=7,train_authors=sorted(train_authors),validation_authors=sorted(monitor_authors),new_authors=0,source_disjoint_proposal=True,source_answers_verified=True,all_prior_evidence_and_models_unchanged=True,training_executed=False,inference_requests=0,human_quality_ratings=0,model_promoted=False)


if __name__=='__main__':
    result=verify()
    with (OUT/'final-verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
