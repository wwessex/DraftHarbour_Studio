"""Post-run audit; never promotes a model or fabricates human ratings."""
from pathlib import Path
import hashlib,json,math,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import validate_dataset,load_ledger,clear_source
RUN=ROOT/'artifacts/literary-mix-training-v2'

def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def read(path):return [json.loads(line) for line in path.read_text().splitlines()]
def main():
    protocol=json.loads((RUN/'protocol.frozen.json').read_text())
    for name,want in protocol['input_hashes'].items():assert sha(ROOT/name)==want,name
    for name,want in protocol['protected_artifacts'].items():assert sha(ROOT/name)==want,name
    assert sha(Path(protocol['base_path'])/'model.safetensors')==protocol['base_weights_sha256']
    ledger_path=ROOT/'rights/literary-mix-v2.scoped.jsonl'
    records=validate_dataset(ROOT/'artifacts/literary-mix-v2/records.jsonl',ledger_path,['GB','US'])
    ledger=load_ledger(ledger_path)
    assert len(records)==352 and sum(r['split']=='train' for r in records)==244
    assert all(r['teacher'] is None and r['origin']=='derived' for r in records)
    cases=read(ROOT/protocol['test_cases_path']);assert len(cases)==20
    assert all(not case['word_count_min'] for case in cases if case['task']=='editing')
    train_authors={a for r in records if r['split']=='train' for a in r['_author_ids']}
    valid_authors={a for r in records if r['split']=='validation' for a in r['_author_ids']}
    test_authors={'codex-ai-diagnostic-author'}
    assert not train_authors & (valid_authors|test_authors)
    assert all('evaluation only' in case['provenance']['context'] for case in cases)
    tokens=read(ROOT/'artifacts/literary-mix-v2/train.tokens.jsonl')
    for row in tokens:
        first=next(i for i,label in enumerate(row['labels']) if label!=-100)
        assert row['labels'][:first]==[-100]*first and row['labels'][first:]==row['input_ids'][first:]
    completion=json.loads((RUN/'completion.json').read_text())
    assert completion['completed'] and completion['steps']==61
    assert sha(RUN/'adapter/adapters.safetensors')==completion['adapter_sha256']
    final=json.loads((RUN/'final-progress.json').read_text())
    assert final['is_completed'] and not final['error'] and not final['warnings'] and final['peak_memory_gb']<=10
    progress=read(RUN/'progress.jsonl')
    assert all(math.isfinite(row['loss']) for row in progress if row.get('loss') is not None)
    evals={row['step']:row['eval_loss'] for row in progress if row.get('eval_loss') is not None}
    assert evals, 'Do not claim monitored validation without actual loss observations'
    comparisons={}
    for side in protocol['model_conditions']:
        result=json.loads((RUN/f'{side}.complete.json').read_text())
        responses=read(RUN/f'{side}.responses.jsonl')
        assert result['completed'] and result['models_unloaded']
        assert len(responses)==20 and result['response_sha256']==sha(RUN/f'{side}.responses.jsonl')
        assert all(not row['error'] and row['messages_count']==1 and row['prior_assistant_messages']==0 for row in responses)
        assert all(row['protocol_sha256']==sha(RUN/'protocol.frozen.json') for row in responses)
        comparisons[side]=dict(responses=len(responses),truncated=sum(row['finish_reason']=='length' for row in responses))
    ballots=read(RUN/'human-ballots.blank.jsonl')
    assert len(ballots)==40 and all(all(value is None for value in row['ratings'].values()) and row['preference'] is None for row in ballots)
    cpu=Path('/Users/williamwessex/Library/Caches/DraftHarbour/literary-v2-foundation.log').read_text()
    assert re.search(r'Ran 110 tests',cpu) and cpu.rstrip().endswith('OK')
    audit=dict(passed=True,audit_script_sha256=sha(Path(__file__)),training_records=244,validation_records=108,supervised_train_tokens=sum(sum(label!=-100 for label in row['labels']) for row in tokens),steps=61,validation_observations=evals,comparisons=comparisons,prior_models_and_base_unchanged=True,exact_source_provenance_checked=True,prompt_labels_ignored=True,training_validation_test_authors_disjoint_for_this_candidate=True,validation_previously_seen_in_other_adapters=True,human_quality_ratings=0,model_promoted=False,application_versions_changed_by_this_model_task=[],protocol_sha256=sha(RUN/'protocol.frozen.json'),adapter_sha256=completion['adapter_sha256'])
    with (RUN/'final-verification.json').open('x') as f:json.dump(audit,f,indent=2)
    print(json.dumps(audit,indent=2))
if __name__=='__main__':main()
