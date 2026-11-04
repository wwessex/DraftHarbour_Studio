"""Prepare a bounded diagnostic, using unchanged existing structural examples only."""
import copy,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import read_jsonl,file_hash,validate_dataset,load_ledger,clear_source
from foundation.arrival_claims import overdue_claim
DATA=ROOT/'artifacts/tiny-fit-v8';OLD=ROOT/'artifacts/arrival-claims-v1';PREV=ROOT/'artifacts/grounding-training-v7'
def save(name,value):
 with (DATA/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
def rows(name,values):
 with (DATA/name).open('x') as f:
  for r in values:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def main():
 if DATA.exists():raise ValueError('Refuse overwrite')
 parent=json.loads((PREV/'protocol.frozen.json').read_text())
 for group in ['input_hashes','protected_artifacts']:
  for p,h in parent[group].items():assert file_hash(ROOT/p)==h,p
 selected={r['record_id'] for r in read_jsonl(PREV/'fit-probe.responses.jsonl')};assert len(selected)==12
 oldrows=read_jsonl(OLD/'records.jsonl');picked=[copy.deepcopy(r) for r in oldrows if r['id'] in selected];assert len(picked)==12
 ledger_path=ROOT/'rights/grounding-balanced-v1.scoped.jsonl';ledger=load_ledger(ledger_path)
 for rid in {rid for r in picked for rid in r['rights_record_ids']}:clear_source(ledger[rid],ledger_path,['GB','US'],'evaluation')
 for r in picked:r['dataset_version']='tiny-fit-v8'
 preflight=json.loads((OLD/'tokenizer-preflight.json').read_text());token_map=dict(zip(preflight['training_record_order'],read_jsonl(OLD/'train.tokens.jsonl')))
 tokens=[token_map[r['id']] for r in picked]
 DATA.mkdir();rows('records.jsonl',picked);rows('train.tokens.jsonl',tokens);rows('seen-monitor.tokens.jsonl',tokens)
 assert len(validate_dataset(DATA/'records.jsonl',ledger_path,['GB','US']))==12
 order=[r['id'] for r in picked];cases=[];trained_tuples=set()
 for r in picked:
  prompt=r['messages'][0]['content'];state=json.loads(prompt.split('TASK STATE:\n')[1].split('\n\nSOURCE EXCERPT:\n')[0]);trained_tuples.add((state['now'],state['scheduled'],state['arrived']))
  cases.append(dict(id=r['id'],kind='arrival-claim',cohort='seen-training',prompt=prompt,expected_json=json.loads(r['messages'][-1]['content'])))
 # Two source families; six new tuples each, each presented in two formats.
 families={}
 for r in picked:
  state=json.loads(r['messages'][0]['content'].split('TASK STATE:\n')[1].split('\n\nSOURCE EXCERPT:\n')[0]);families.setdefault(state['scheduled'],(r,state))
 from importlib.util import spec_from_file_location,module_from_spec
 spec=spec_from_file_location('claim_builder',ROOT/'curation/arrival-claims-v1/build.py');module=module_from_spec(spec);spec.loader.exec_module(module)
 for scheduled,(r,oldstate) in families.items():
  for offset,arrived in [(-25,False),(-25,None),(15,False),(15,None),(15,True),(-25,True)]:
   h,m=map(int,scheduled.split(':'));total=h*60+m+offset;state=dict(oldstate,now=f'{total//60:02d}:{total%60:02d}',arrived=arrived)
   assert (state['now'],scheduled,arrived) not in trained_tuples
   target=overdue_claim(state['now'],scheduled,arrived)
   prefix,rest=r['messages'][0]['content'].split('TASK STATE:\n',1);_,suffix=rest.split('\n\nSOURCE EXCERPT:\n',1)
   prompts={'heldout-matched-source':prefix+'TASK STATE:\n'+json.dumps(state)+'\n\nSOURCE EXCERPT:\n'+suffix,'heldout-standalone':module.INSTRUCTION+'\n\nTASK STATE:\n'+json.dumps(state)}
   for cohort,prompt in prompts.items():cases.append(dict(id=f'tiny-transfer-{len(cases):02d}',kind='arrival-claim',cohort=cohort,prompt=prompt,expected_json=target))
 assert len(cases)==36;rows('cases.frozen.jsonl',cases)
 cfg=json.loads((PREV/'request.json').read_text());cfg.update(project_name='Narratryx-tiny-fit-v8',local_datasets=[str(DATA/'train.tokens.jsonl')],local_eval_datasets=[str(DATA/'seen-monitor.tokens.jsonl')],learning_rate='2e-4',batch_size=1,gradient_accumulation_steps=1,num_epochs=4,max_steps=48,warmup_steps=2,save_steps=48,eval_steps=12)
 save('request.proposed.json',cfg)
 total=sum(sum(t!=-100 for t in r['labels'][1:]) for r in tokens)
 save('preflight.json',dict(records=12,unique_supervised_tokens=total,maximum_tokens=max(len(r['input_ids']) for r in tokens),passes=4,expected_supervised_token_exposures=total*4,source_targets_unchanged=True,monitor_is_training_set=True,no_literary_quality_assessment=True,training_record_order=order))
 for name in ['adapter/adapters.safetensors','adapter/adapter_config.json','completion.json','protocol.frozen.json']:
  p=PREV/name;parent['protected_artifacts'][str(p.relative_to(ROOT))]=file_hash(p)
 paths=[DATA/n for n in ['records.jsonl','train.tokens.jsonl','seen-monitor.tokens.jsonl','cases.frozen.jsonl','request.proposed.json','preflight.json']]+[Path(__file__)]
 parent['input_hashes'].update({str(p.relative_to(ROOT)):file_hash(p) for p in paths})
 parent.update(training_steps=48,created_on='2026-10-31',scope='Tiny supervised-fit diagnostic only; no app changes, model promotion, literary targets, paid jobs or publication.',fit_gate=dict(required_seen_correct=10,total=12,transfer_only_after_fit_gate=True),resource_stop=dict(peak_mlx_gb=10,timeout_seconds=1200,max_steps=48))
 save('protocol.proposed.frozen.json',parent)
 print('Prepared12 unchanged teaching rows;48-update cap;12seen plus24 gated transfer requests.')
if __name__=='__main__':main()
