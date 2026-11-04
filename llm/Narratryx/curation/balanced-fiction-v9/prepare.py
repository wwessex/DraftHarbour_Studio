"""Freeze source-only prose retention plus explicitly repeated existing claim lessons."""
import copy,json,random,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl,validate_dataset,load_ledger,clear_source
from foundation.arrival_claims import overdue_claim
from foundation.grounding_lessons import arrival_state
DATA=ROOT/'artifacts/balanced-fiction-v9';HERE=Path(__file__).resolve().parent
LEDGER=ROOT/'rights/grounding-balanced-v1.scoped.jsonl'
def save(name,value):
 with (DATA/name).open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')
def rows(name,values):
 with (DATA/name).open('x') as f:
  for r in values:f.write(json.dumps(r,ensure_ascii=False)+'\n')
def main():
 if DATA.exists():raise ValueError('Refuse overwrite')
 old=ROOT/'artifacts/grounding-balanced-v1';tiny=ROOT/'artifacts/tiny-fit-v8';proof=ROOT/'artifacts/tiny-fit-training-v8b'
 parent=json.loads((proof/'protocol.frozen.json').read_text())
 for group in ['input_hashes','protected_artifacts']:
  for n,h in parent[group].items():assert file_hash(ROOT/n)==h,n
 assert json.loads((proof/'candidate.complete.json').read_text())['scores']['seen-training']['passed']==12
 original=read_jsonl(old/'records.jsonl');retained=[copy.deepcopy(r) for r in original if r['split']=='train'];monitor=[copy.deepcopy(r) for r in original if r['split']=='validation'];focus=read_jsonl(tiny/'records.jsonl')
 assert len(retained)==80 and len(monitor)==16 and len(focus)==12
 raw=retained+focus+monitor
 assert len({r['id'] for r in raw})==108
 for r in raw:r['dataset_version']='balanced-fiction-v9'
 DATA.mkdir();rows('records.jsonl',raw);validated=validate_dataset(DATA/'records.jsonl',LEDGER,['GB','US'])
 assert sum(r['split']=='train' for r in validated)==92
 prose=[r for r in retained if not r['messages'][-1]['content'].lstrip().startswith('{')];struct=[r for r in retained if r not in prose]
 assert len(prose)==56 and len(struct)==24
 random.Random(42).shuffle(prose);random.Random(43).shuffle(struct)
 presentations=[]
 for block in range(4):
  group=prose[block*14:(block+1)*14]+struct[block*6:(block+1)*6]+focus
  random.Random(42+block).shuffle(group);presentations+=group
 counts=Counter(r['id'] for r in presentations)
 assert len(presentations)==128 and all(counts[r['id']]==1 for r in retained) and all(counts[r['id']]==4 for r in focus)
 save('selection.json',dict(unique_training_records=92,training_presentations=128,retained_original_records=80,retained_prose_lessons=56,focused_unique_records=12,focus_exposures=4,presentation_order=[r['id'] for r in presentations],exposures=dict(counts),note='Token-file order is not a guarantee of optimiser order. Installed worker uses its own seeded sampler; repeated presentations are not new independent source material.'))
 # Fresh structured diagnostics use schedule families not used by earlier structured tests.
 import importlib.util
 spec=importlib.util.spec_from_file_location('claim_builder',ROOT/'curation/arrival-claims-v1/build.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 tests=[]
 for schedule in ['12:05','21:10']:
  for offset,arrived in [(-20,False),(0,False),(35,False),(-20,None),(50,None),(35,True)]:
   h,m=map(int,schedule.split(':'));minutes=h*60+m+offset;state=dict(now=f'{minutes//60:02d}:{minutes%60:02d}',scheduled=schedule,arrived=arrived)
   for kind,target in [('clock-state',arrival_state(state['now'],schedule,arrived)),('arrival-claim',overdue_claim(state['now'],schedule,arrived))]:
    instruction=module.INSTRUCTION if kind=='arrival-claim' else 'Use same-day24-hour HH:MM. arrived:null means unknown, not absent. Return JSON only with state (arrived/not_established/not_yet_due/due_now/overdue) and minutes_to_schedule (scheduled minus now). A future appointment is not overdue.'
    tests.append(dict(id=f'bf-structured-{len(tests):02d}',kind=kind,prompt=instruction+'\n\nTASK STATE:\n'+json.dumps(state),expected_json=target,word_count_min=None,word_count_max=None,established_facts=['Only this same-day snapshot is established.'],unknowns=['Actual arrival time, motive and identity are unspecified.'],evaluation_role='fresh-structured',provenance='Deterministic evaluation-only task; no human benchmark approval.'))
 settings=[('conservatory','Iris','Nabil','08:10','08:35','09:15','sealed the seed tray','a brass ring','the bench'),('rope-workshop','Bryn','Sita','11:25','11:50','12:30','checked the rope gauge','a folded paper pattern','the window'),('aquarium-records','Noor','Emil','14:05','14:25','15:10','logged the tank temperature','a grey glove','the cabinet'),('print-shop','Elena','Hassan','17:20','17:40','18:25','cleaned the ink roller','a white chalk fragment','the ink case')]
 for name,actor,visitor,past,now,due,action,obj,place in settings:
  context=f'At {past}, {actor} {action}. It is now {now}. {visitor} is expected at {due} and has not arrived. There is {obj} beside {place}. Who left it there is unknown.'
  prompts={'selected-edit':f'Remove only the accidental duplicated word inside TARGET. Preserve every other character. Return only corrected target. Do not edit CONTEXT.\n\nCONTEXT:\n{context} The the cupboard is closed.\n\nTARGET:\n{actor} left the the recorded result unchanged.','analysis':'Separate explicit facts, qualified inferences and unknowns in at most70words. Do not assume lateness, identify a culprit, invent prior presence or infer gender from a name.\n\n'+context,'rewrite':'Rewrite as restrained story prose in at most90words. Preserve all times, completed versus expected events and uncertainty. Do not merely repeat unchanged. Return only prose.\n\n'+context,'continue':'Continue in60–90words, adding only a new paragraph. Preserve names, current time, future expected arrival and uncertainty about the object. Add one concrete action without asserting an unknown culprit or motive as fact.\n\n'+context}
  for kind,prompt in prompts.items():tests.append(dict(id=f'bf-{name}-{kind}',kind=kind,prompt=prompt,context=context,word_count_min=60 if kind=='continue' else None,word_count_max={'analysis':70,'rewrite':90,'continue':90}.get(kind),exact_reference=f'{actor} left the recorded result unchanged.' if kind=='selected-edit' else None,established_facts=[f'{past} completed action',f'{now} current time',f'{due} expected arrival, not occurred'],unknowns=['Object origin, culprit and motive are not established.'],evaluation_role='fresh-prose-transfer',provenance='Codex AI-authored evaluation-only fiction, never a teaching target or human gold.'))
 scenes=[('reel','Jules wants to preserve the only recording of a vanished neighbourhood choir. Anika needs the same reusable reel to test a repaired recorder. The only spare reel has not been checked. Neither has authority to erase the choir recording.','Jules turned the reel over in both hands. The label was worn. Anika laid the recorder cable on the table. The machine had been repaired. It needed a test. The spare reel sat in a box. Nobody had checked it. Jules held the choir recording closer.'),('coat','Cora wants to preserve an inherited coat exactly as it is. Devin needs a wearable coat for a community play. They have one matching button and an untested scrap of lining. Cora has not agreed to cut the original fabric.','Cora spread the coat on the table. The cuff was frayed. Devin set down the matching button. The rehearsal clothes were waiting. Cora touched the old seam. The lining scrap was still folded. Nobody knew whether it was strong enough. Devin reached toward the scissors.')]
 for name,context,paragraph in scenes:
  prompts={'dialogue':'Write4–6 dialogue turns in at most100words. Give both characters distinct aims and subtext. Move the practical negotiation forward without inventing consent or resolving everything by luck. Return only dialogue.\n\n'+context,'pacing':'Compress the paragraph to at most85words, making the immediate decision sharper while preserving facts, unresolved resource questions and character agency. Return only prose.\n\nFACTS:\n'+context+'\n\nPARAGRAPH:\n'+paragraph,'continue':'Continue the scene in60–90words. Add only one new paragraph and one concrete action that moves the practical problem forward. Preserve resources and missing consent; do not invent a miraculous spare or simply solve everything.\n\n'+context,'write':'Write90–130words of scene prose from these facts. Keep viewpoint consistent, reveal conflicting aims through action, and end with an unresolved practical choice. Preserve resource limits and missing consent. No heading or commentary.\n\n'+context}
  for kind,prompt in prompts.items():tests.append(dict(id=f'bf-craft-{name}-{kind}',kind=kind,prompt=prompt,word_count_min={'continue':60,'write':90}.get(kind),word_count_max={'dialogue':100,'pacing':85,'continue':90,'write':130}[kind],established_facts=[context],unknowns=['Spare material suitability and consent are unresolved.'],evaluation_role='fresh-craft',provenance='Codex AI-authored evaluation-only fiction; no literary training answer.'))
 assert len(tests)==48;rows('fresh.cases.frozen.jsonl',tests)
 retention=read_jsonl(ROOT/'artifacts/revision-preflight-v1/test.cases.jsonl')
 for r in retention:r['evaluation_role']='exposed-retention'
 assert len(retention)==24;rows('primary.cases.frozen.jsonl',tests+retention)
 extras=read_jsonl(tiny/'cases.frozen.jsonl')
 for r in extras:
  r['evaluation_role']='exposed-tiny-'+r.pop('cohort');r['word_count_min']=None;r['word_count_max']=None
  r['established_facts']=['Original tiny-fit task snapshot only.'];r['unknowns']=['Origin, identity and motives are unspecified.']
 assert len(extras)==36;rows('candidate-extra.cases.frozen.jsonl',extras)
 inputs=[old/'records.jsonl',tiny/'records.jsonl',tiny/'cases.frozen.jsonl',proof/'candidate.complete.json',LEDGER,Path(__file__),ROOT/'curation/arrival-claims-v1/build.py',ROOT/'foundation/arrival_claims.py']
 save('build-verification.json',dict(passed=True,unique_training_records=92,training_presentations=128,monitor_records=16,new_source_works=0,new_literary_teaching_targets=0,new_human_approvals=0,fresh_cases=48,exposed_retention=24,candidate_extra_cases=36,input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in inputs}))
 print('Built92 unique training lessons;128 presentations;72 primary cases plus36 exposed candidate checks.')
if __name__=='__main__':main()
