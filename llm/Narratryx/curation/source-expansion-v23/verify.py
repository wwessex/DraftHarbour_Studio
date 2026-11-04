"""Read-only exact-source, rights-scope and split audit. No model calls."""
import json
import re
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl,validate_dataset,load_ledger
from foundation.scoped_excerpt import split_continuation
OUT=ROOT/'artifacts/source-expansion-v23'
LEDGER=ROOT/'rights/source-expansion-v23.scoped.jsonl'


def verify():
    p=json.loads((OUT/'verification.json').read_text())
    for group in ['input_hashes','protected_hashes']:
        for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
    for n,h in p['output_hashes'].items():assert file_hash(OUT/n)==h,n
    lock=json.loads((ROOT/'curation/source-expansion-v23/source-lock.json').read_text())
    for n,h in lock['file_hashes'].items():assert file_hash(ROOT/n)==h,n
    for n,h in json.loads((OUT/'additional-inputs.json').read_text()).items():assert file_hash(ROOT/n)==h,n
    ledger=load_ledger(LEDGER);old=load_ledger(ROOT/'rights/grounding-balanced-v1.scoped.jsonl')
    assert len(ledger)==18 and all(ledger[k]==v for k,v in old.items())
    new=set(ledger)-set(old)
    assert new=={'dunbar-st-rocque-pg688-v23','james-1881-reaction-v23','james-1908-reaction-v23'}
    assert all(ledger[k]['review']['reviewer'].startswith('Codex AI:') for k in new)
    assert all(c['uses']==['training'] for k in new for c in ledger[k]['clearances'])
    checked=validate_dataset(OUT/'candidates.jsonl',LEDGER,['GB','US'],benchmark=read_jsonl(ROOT/'evaluation/tasks.draft.jsonl'))
    rows=read_jsonl(OUT/'candidates.jsonl');bindings={b['id']:b for b in read_jsonl(OUT/'derivations.jsonl')}
    scopes=json.loads((OUT/'scope.json').read_text())
    assert len(rows)==4 and len(scopes)==5
    for r in rows:
        b=bindings[r['id']];assert r['source_spans']==b['source_spans']
        assert r['teacher'] is None and r['origin']=='derived' and r['split']=='train'
        for s in r['source_spans']:
            raw=ROOT/'rights'/ledger[s['rights_record_id']]['source']['raw_path']
            assert raw.read_text()[s['start']:s['end']]==s['text']
            assert any(all(scope.get(k)==v for k,v in s.items()) for scope in scopes)
        if b.get('derivation'):
            d=b['derivation'];span=b['source_spans'][0]
            answer_start=d['answer_start']-span['start'];actual=split_continuation(span,span['text'][answer_start:])
            assert d==actual
            assert r['messages'][-1]['content']==d['answer']
            assert r['messages'][0]['content'].split('\n\nPRECEDING PARAGRAPHS:\n')[1]==d['context']
        else:
            assert r['messages'][-1]['content']==r['source_spans'][-1]['text']
    revision=next(r for r in rows if r['task']=='editing')
    assert revision['source_spans'][0]['text'] in revision['messages'][0]['content']
    assert len(revision['source_spans'][0]['text'].split())==439 and len(revision['messages'][-1]['content'].split())==483
    split=validate_dataset(OUT/'split-check-only.jsonl',LEDGER,['GB','US'])
    assert len(split)==20 and sum(r['split']=='validation' for r in split)==16
    assert not {a for r in split if r['split']=='train' for a in r['_author_ids']} & {a for r in split if r['split']=='validation' for a in r['_author_ids']}
    for n in ['evaluation','configs']:
        assert not any(re.search(r'dunbar|st.?rocque',f.read_text(errors='replace'),re.I) for f in (ROOT/n).rglob('*') if f.is_file())
    tokens=json.loads((OUT/'tokenizer-preflight.json').read_text())
    for n,h in tokens['input_hashes'].items():assert file_hash(ROOT/n)==h,n
    assert tokens['passed'] and tokens['records']==4 and tokens['supervised_train_tokens']==924 and tokens['maximum_tokens']==1205
    assert not tokens['weights_loaded'] and not tokens['training']
    excluded=json.loads((OUT/'exclusions.json').read_text());assert len(excluded)==3 and all(e['status']=='discovery-only-training-ineligible' for e in excluded)
    assert all('speaker' not in ledger[s['rights_record_id']]['source']['raw_path'] for r in rows for s in r['source_spans'])
    return dict(passed=True,candidates=4,new_scoped_records=3,unchanged_prior_ledger_records=15,new_author_ids=['alice-moore-dunbar-nelson'],scan_backed_revision_pairs=1,narrated_dialogue_examples=1,complete_paragraph_continuations=2,excluded_source_options=3,maximum_tokens=1205,supervised_tokens=924,author_split_verified=True,prior_artifacts_and_models_unchanged=True,training_executed=False,inference_requests=0,human_quality_ratings=0,model_promoted=False)


if __name__=='__main__':
    result=verify()
    with (OUT/'final-verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
