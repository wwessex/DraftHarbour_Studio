"""Retain prior lessons and add source-backed deterministic claim decisions."""
import copy,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.arrival_claims import overdue_claim
from foundation.grounding_lessons import arrival_state
from foundation.validation import digest,file_hash,read_jsonl,validate_dataset
OUT=ROOT/'artifacts/arrival-claims-v1'
LEDGER=ROOT/'rights/grounding-balanced-v1.scoped.jsonl'
HERE=Path(__file__).resolve().parent
INSTRUCTION=('This is a constructed snapshot, not additional original plot. Assess the claim: '
 '"The expected visitor is already late and still absent." Use only TASK STATE, same-day24-hour HH:MM. '
 'arrived:null means unknown, not absent. Already late requires now strictly after scheduled. '
 'A known arrival contradicts still absent, even if its actual arrival time is unspecified. '
 'At/before scheduled, already late is contradicted; after scheduled with unknown arrival the claim is not established. '
 'Return JSON only with verdict (supported/contradicted/not_established), minutes_to_schedule '
 '(scheduled minus now; preserve negative signs), arrival_state '
 '(arrived/not_established/not_yet_due/due_now/overdue). Do not identify a culprit or invent a cause.')
def save(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2,ensure_ascii=False);f.write('\n')
def rows(name,values):
 with (OUT/name).open('x') as f:
  for row in values:f.write(json.dumps(row,ensure_ascii=False)+'\n')
def main():
 if OUT.exists():raise ValueError('Refusing overwrite')
 prior=ROOT/'artifacts/grounding-balanced-v1/records.jsonl'
 validate_dataset(prior,LEDGER,['GB','US']);retained=read_jsonl(prior)
 validate_dataset(ROOT/'artifacts/grounding-editing-v1/records.jsonl',ROOT/'rights/grounding-editing-v1.scoped.jsonl',['GB','US']);core=read_jsonl(ROOT/'artifacts/grounding-editing-v1/records.jsonl')
 clocks=[r for r in core if r['id'].startswith('ge-clock-')]
 assert len(clocks)==24 and all(r['split']=='train' for r in clocks)
 for row in retained:row['dataset_version']='arrival-claims-v1'
 OUT.mkdir();new=[];trace=[]
 for source in clocks:
  old=source['messages'][0]['content'];state=json.loads(old.split('TASK STATE:\n')[1].split('\n\nSOURCE EXCERPT:\n')[0])
  target=overdue_claim(state['now'],state['scheduled'],state['arrived'])
  row=copy.deepcopy(source);row.update(id='claim-'+source['id'],dataset_version='arrival-claims-v1')
  row['messages']=[dict(role='user',content=INSTRUCTION+'\n\nSCHEDULE QUOTATION:\n'+old.split('SCHEDULE QUOTATION:\n',1)[1]),dict(role='assistant',content=json.dumps(target,separators=(',',':')))]
  row['review']=dict(status='approved',reviewer='Codex AI: deterministic truth-table/source-span audit',reviewed_on='2026-10-31',notes='AI audit, not human approval. Composite current-lateness/absence claim with explicit task metadata; unchanged existing source span and source schedule. No generated literary teaching target, new original plot, culprit or arrival time.')
  row['content_hash']=digest(row['messages']);new.append(row);trace.append(dict(id=row['id'],parent_id=source['id'],state=state,target=target))
 rows('records.jsonl',retained+new);rows('trace.jsonl',trace)
 checked=validate_dataset(OUT/'records.jsonl',LEDGER,['GB','US'])
 assert len([r for r in checked if r['split']=='train'])==104
 assert len([r for r in checked if r['split']=='validation'])==16
 assert read_jsonl(OUT/'records.jsonl')[:len(retained)]==retained
 # New evaluation tuples, distinct schedules from training and all previous tests.
 tests=[]
 for schedule in ['09:50','16:35']:
  for offset,arrived in [(-25,False),(0,False),(20,False),(-25,None),(55,None),(20,True)]:
   h,m=map(int,schedule.split(':'));total=h*60+m+offset;now=f'{total//60:02d}:{total%60:02d}'
   state=dict(now=now,scheduled=schedule,arrived=arrived)
   for kind,target in [('clock-state',arrival_state(now,schedule,arrived)),('arrival-claim',overdue_claim(now,schedule,arrived))]:
    instruction=INSTRUCTION if kind=='arrival-claim' else 'Use same-day24-hour HH:MM. arrived:null means unknown, not absent. Return JSON only with state (arrived/not_established/not_yet_due/due_now/overdue) and minutes_to_schedule (scheduled minus now). A future appointment is not overdue.'
    tests.append(dict(id=f'ac-test-{len(tests):02d}',kind=kind,prompt=instruction+'\n\nTASK STATE:\n'+json.dumps(state),expected_json=target,word_count_min=None,word_count_max=None,established_facts=['Only the explicit same-day task snapshot is given.'],unknowns=['Identity, actual arrival time and cause are unspecified.'],evaluation_role='fresh-structured',provenance='Original deterministic evaluation-only diagnostic, not human-approved benchmark or training material.'))
 scenarios=[('map-room','Ruth','Kiran','09:10','09:25','10:05','logged the archive humidity','a small ivory button','a catalogue drawer'),('boat-shed','Tessa','Omar','12:00','12:20','13:10','checked the rudder cable','a folded blue receipt','a wooden stool'),('costume-room','Lena','Pavel','14:15','14:40','15:20','mended a sleeve','a bent silver pin','the cutting table'),('weather-station','Ada','Soren','17:05','17:25','18:00','read the rain gauge','a red fabric tag','the doorway')]
 for name,person,visitor,past,now,due,action,obj,place in scenarios:
  context=f'At {past}, {person} {action}. It is now {now}. {visitor} is expected at {due} and has not arrived. There is {obj} beside {place}. Who left it there is unknown.'
  task_prompts={'selected-edit':f'Remove only the accidental duplicated word inside TARGET. Preserve every other character. Return only corrected target. Do not edit CONTEXT.\n\nCONTEXT:\n{context} The the cupboard is closed.\n\nTARGET:\n{person} left the the recorded result unchanged.', 'analysis':'Separate explicit facts, qualified inferences and unknowns in at most70words. Do not assume lateness, identify a culprit, invent prior presence or infer gender from a name.\n\n'+context,'rewrite':'Rewrite as restrained story prose in at most90words. Preserve all times, completed versus expected events and uncertainty. Do not merely repeat unchanged. Return only prose.\n\n'+context,'continue':'Continue in60–90words, adding only a new paragraph. Preserve names, current time, future expected arrival and uncertainty about the object. Add one concrete action without asserting an unknown culprit or motive as fact.\n\n'+context}
  for kind,prompt in task_prompts.items():
   tests.append(dict(id=f'ac-transfer-{name}-{kind}',kind=kind,prompt=prompt,context=context,word_count_min=60 if kind=='continue' else None,word_count_max={'analysis':70,'rewrite':90,'continue':90}.get(kind),exact_reference=f'{person} left the recorded result unchanged.' if kind=='selected-edit' else None,established_facts=[f'{past} completed action',f'{now} current time',f'{due} expected arrival, not occurred'],unknowns=['Object origin, culprit and motive are not established.'],evaluation_role='fresh-prose-transfer',provenance='Codex AI-authored evaluation-only fictional situation; no training target or human benchmark approval.'))
 assert len(tests)==40
 rows('evaluation.cases.frozen.jsonl',tests)
 inputs=[prior,ROOT/'artifacts/grounding-editing-v1/records.jsonl',ROOT/'rights/grounding-editing-v1.scoped.jsonl',LEDGER,HERE/'build.py',ROOT/'foundation/arrival_claims.py',ROOT/'foundation/grounding_lessons.py']
 save('build-verification.json',dict(passed=True,retained_messages_and_spans_unchanged=96,new_training_records=24,training_records=104,monitor_records=16,prose_retained=56,structured_training=48,training_schedule_families=2,new_clock_cases=12,new_claim_cases=12,new_prose_cases=16,generated_literary_targets=0,human_quality_ratings=0,input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in inputs}))
 print('Validated104 training records +16 exposed monitor records;40 fresh diagnostic cases frozen.')
if __name__=='__main__':main()
