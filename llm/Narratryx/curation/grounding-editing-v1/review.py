from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=R/'artifacts/grounding-editing-v1'
rows=list(map(json.loads,(O/'records.jsonl').read_text().splitlines()));tr=list(map(json.loads,(O/'trace.jsonl').read_text().splitlines()));by={t['id']:t for t in tr}
lines=['# Grounding and selection-editing curriculum review','', '178 structured lessons; no generated literary teaching prose, model training or human quality approval. Paired records are not independent passages.','', '## Selected-text repair and unchanged cases','']
for row in rows[:4]:
 lines += ['### '+row['id'],'',row['messages'][0]['content'],'','Expected structural answer:','```json',row['messages'][1]['content'],'```','']
lines += ['## Evidence classifications','', 'Labels are informed AI annotations for the supplied fiction, not claims about real-world history. Review each category and exact quotation.','']
units={}
for r in rows:
 if by[r['id']]['kind']=='evidence-status':units.setdefault(by[r['id']]['unit'],[]).append(r)
for unit, items in units.items():
 source=items[0]['messages'][0]['content'].split('SOURCE EXCERPT:\n',1)[1]
 lines += ['### '+unit,'',source,'']
 for r in items:
  p=r['messages'][0]['content'];query=p.split('CLASSIFY THIS QUOTATION:\n',1)[1].split('\n\nSOURCE EXCERPT:',1)[0] if 'CLASSIFY THIS QUOTATION:' in p else p.split('QUESTION:\n',1)[1].split('\n\nSOURCE EXCERPT:',1)[0]
  lines += ['- '+r['id']+': '+query,'  '+r['messages'][1]['content']]
 lines += ['']
lines += ['## Constructed schedule snapshots','', 'These task states are hypothetical, not added original plot. The literary source supplies only an announced schedule. Null arrival means unknown, never automatically absent. No cause, identity or new prose is generated.','']
for r in [r for r in rows if by[r['id']]['kind']=='clock-state'][:6]:
 state=r['messages'][0]['content'].split('TASK STATE:\n',1)[1].split('\n\nSOURCE EXCERPT:',1)[0]
 lines += ['- '+r['id']+': '+state+' → '+r['messages'][1]['content']]
lines += ['', '## Review limits','', 'No final training mixture is approved. Preserve prose-generation tasks and old exact-edit tests; do not train only on these JSON examples. Validate transfer to ordinary story prose and independently review semantic annotations before a further experiment.','']
with (O/'REVIEW.md').open('x') as f:f.write('\n'.join(lines))
# Original synthetic fiction below is evaluation only, never an answer-generation teacher.
worlds=[('canal-lock','Petra','Ivo','10:10','10:35','11:20','logged the lock pressure','a loose brass washer lay in an open box'),('planetarium','Mei','Anton','15:05','15:20','16:00','tested the projector','a black lens cap lay on the console'),('puppet-workshop','Salma','Ewan','08:00','08:25','09:00','repaired the red puppet hinge','a knotted cord lay on the table'),('bookbinding-room','Felix','Nora','11:05','11:40','12:10','wrapped the repaired volume','a torn cotton ribbon lay beside the press')]
cases=[]
for world,actor,visitor,past,now,future,action,clue in worlds:
 context=f'At {past}, {actor} {action}. It is now {now}. {visitor} is expected at {future} and has not arrived. {clue[0].upper()+clue[1:]}. Who put it there is unknown.'
 for task in ['selected-edit','analysis','rewrite','continue']:
  c=dict(id='ge-transfer-'+world+'-'+task,scenario_id=world,kind=task,context=context,provenance='Original Codex AI-authored evaluation-only diagnostic; no human approval, not training material.',word_count_min=None,word_count_max=None,exact_reference=None,established_facts=[past+' completed action',now+' current time',future+' expected arrival, not occurred'],unknowns=['Who left the object, intent and motive are not established.'])
  if task=='selected-edit':
   target=f'{actor} left the the recorded result unchanged.';c['prompt']='Remove only the accidental duplicated word inside TARGET. Preserve every other character. Return only the corrected target. Do not edit CONTEXT.\n\nCONTEXT:\n'+context+' The the cupboard stayed closed.\n\nTARGET:\n'+target;c['exact_reference']=target.replace('the the','the')
  elif task=='analysis':c['prompt']='In at most70words, distinguish explicit facts, qualified inference and unknowns. Do not assume lateness before the expected time, identify a culprit, invent prior presence or infer gender from a name.\n\n'+context;c['word_count_max']=70
  elif task=='rewrite':c['prompt']='Rewrite this as restrained story prose in at most90words, preserving times, completed versus expected events and uncertainty about the object. Do not merely repeat it unchanged. Return only prose.\n\n'+context;c['word_count_max']=90
  else:c['prompt']='Continue in60–90words. Keep the exact character names and all established times. You may add an action, but leave the visitor’s arrival and the object’s authorship unresolved. Do not invent proof of who left it. Return only new prose.\n\n'+context;c['word_count_min']=60;c['word_count_max']=90
  cases.append(c)
with (O/'prose-transfer.evaluation-only.jsonl').open('x') as f:
 for c in cases:f.write(json.dumps(c,ensure_ascii=False)+'\n')
lock={str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [O/'REVIEW.md',O/'prose-transfer.evaluation-only.jsonl']}
with (R/'curation/grounding-editing-v1/review-lock.json').open('x') as f:json.dump(dict(files=lock,created_on='2026-10-29',training=False),f,indent=2);f.write('\n')
print('Prepared review packet and16 evaluation-only prose-transfer cases across four new situations.')
