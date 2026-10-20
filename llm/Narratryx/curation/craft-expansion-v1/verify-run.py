"""Final pilot audit. Fails on altered inputs, source drift or evaluation gaps."""
from pathlib import Path
import hashlib,json,math,sys,re
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import load_ledger,validate_dataset,clear_source
RUN=ROOT/'artifacts/craft-training-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def readrows(p):return [json.loads(l) for l in p.read_text().splitlines()]
def main():
    protocol=json.loads((RUN/'protocol.frozen.json').read_text())
    for n,h in protocol['input_hashes'].items():assert sha(ROOT/n)==h,n
    ledger_path=ROOT/'rights/craft-expansion-v1.scoped.jsonl';ledger=load_ledger(ledger_path)
    records=validate_dataset(ROOT/'artifacts/craft-expansion-v1/train.records.jsonl',ledger_path,['GB','US'])
    cases=readrows(ROOT/protocol['test_cases_path'])
    train_sources={r['rights_record_ids'][0] for r in records};test_sources={c['source_id'] for c in cases}
    train_authors={a for s in train_sources for a in ledger[s]['author_ids']}
    test_authors={a for s in test_sources for a in ledger[s]['author_ids']}
    assert not train_authors&test_authors
    for s in test_sources:
        clear_source(ledger[s],ledger_path,['GB','US'],'evaluation')
        assert all('training' not in c['uses'] for c in ledger[s]['clearances'])
    tokens=readrows(ROOT/'artifacts/craft-expansion-v1/train.tokens.jsonl')
    assert sum(sum(x!=-100 for x in r['labels']) for r in tokens)==2850
    for r in tokens:
        first=next(i for i,v in enumerate(r['labels']) if v!=-100)
        assert r['labels'][:first]==[-100]*first and r['labels'][first:]==r['input_ids'][first:]
    outputs={}
    for side in ['base','candidate']:
        completion=json.loads((RUN/f'{side}.complete.json').read_text());assert completion['completed'] and completion['models_unloaded']
        assert completion['response_sha256']==sha(RUN/f'{side}.responses.jsonl')
        rows=readrows(RUN/f'{side}.responses.jsonl');assert len(rows)==16
        assert {r['case_id'] for r in rows}=={c['id'] for c in cases}
        assert all(not r['error'] and r['messages_count']==1 and r['prior_assistant_messages']==0 for r in rows)
        assert all(r['stats']['usage']['prompt_tokens_details']['cached_tokens']==0 for r in rows)
        assert all(r['stats']['usage']['total_tokens']<=2048 for r in rows)
        outputs[side]=dict(responses=16,truncated=sum(r['stats']['finish_reason']=='length' for r in rows))
    progress=json.loads((RUN/'final-progress.json').read_text());assert progress['step']==5 and progress['is_completed'] and not progress['error'] and not progress['warnings']
    assert math.isfinite(progress['loss'])
    cfg=json.loads((RUN/'request.json').read_text());assert sha(Path(cfg['model_snapshot_path'])/'model.safetensors')==protocol['base_weights_sha256']
    completed=json.loads((RUN/'completion.json').read_text());assert sha(RUN/'adapter/adapters.safetensors')==completed['adapter_sha256']
    old_hashes={'clean-source-training-v1':'77bbf1e343b87e880dd53d7c1c2b9ca64df4c1ac4ba7885eefa0bd686ab17f87',
        'clean-source-training-v2':'4fe3e3ab36011b0a48cc2b2419df729432f5f8bb4b0df65d4e6982fe5f4b8eab',
        'source-task-training-v1':'855eb01061b0b51e665ce0f5547bccfb025090b8326a7e4885149f1c53fe7e53'}
    for n,h in old_hashes.items():assert sha(ROOT/'artifacts'/n/'adapter/adapters.safetensors')==h
    test_log=(ROOT/'artifacts/craft-expansion-v1/foundation-tests.log').read_text()
    assert re.search(r'Ran 72 tests',test_log) and test_log.rstrip().endswith('OK')
    audit=dict(passed=True,training_records=20,supervised_tokens=2850,updates=5,outputs=outputs,foundation_tests=72,
        scoped_source_hashes_verified=True,source_answers_and_explicit_loss_labels_verified=True,
        train_test_authors_disjoint=True,heldout_sources_training_prohibited=True,
        base_and_three_old_adapters_unchanged=True,all_models_unloaded=True,human_quality_ratings=0,automatic_promotion=False,
        artifacts={str(p.relative_to(ROOT)):sha(p) for p in [RUN/'protocol.frozen.json',RUN/'completion.json',RUN/'scores.json',RUN/'BLIND-REVIEW.md',ROOT/'rights/dossiers/craft-expansion-2026-10-20.md']})
    with (RUN/'final-verification.json').open('x') as f:json.dump(audit,f,indent=2)
    print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
