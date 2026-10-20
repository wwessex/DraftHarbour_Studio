"""Deterministic public-domain targets; no teacher-model generation or inference."""
from pathlib import Path
import sys,json,copy,re,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import read_json,read_jsonl,file_hash,digest,validate_dataset
from foundation.austen_review import normalize_excerpt
OUT=ROOT/'artifacts/source-tasks-v1'
def sha_text(s):return hashlib.sha256(s.encode()).hexdigest()
def save(path,obj,lines=False):
 with path.open('x') as f:
  if lines:
   for row in obj:f.write(json.dumps(row,ensure_ascii=False)+'\n')
  else:json.dump(obj,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
 assert not OUT.exists(),'Preserve prior experiment; choose a new version'
 records=read_jsonl(ROOT/'artifacts/clean-source-approved-v1/prose.approved.jsonl')
 assert len(records)==108
 ledgers=read_jsonl(ROOT/'rights/clean-sources.approved-v1.jsonl')
 approval=read_json(ROOT/'rights/approvals/austen-six-passage-selection-2026-10-18.json')
 assert approval['decision']=='approved-selection-only' and len(approval['passages'])==6
 austen=next(x for x in read_jsonl(ROOT/'rights/ledger.jsonl') if x['id']=='austen-pride-candidate')
 assert austen['source']['sha256']==approval['source_sha256']
 # Separate scoped ledger records the already-existing exact-selection approval;
 # no prior ledger, approval or synthetic-example status is changed.
 austen=copy.deepcopy(austen)
 austen['source']['included_material']='Only the six exact Austen prose spans already accepted in approvals/austen-six-passage-selection-2026-10-18.json; this experiment permits evaluation only. No generated targets or excluded contributions.'
 austen['unresolved_issues']=[]
 austen['review']['notes']+=' Exact-selection gate discharged for these six spans by approvals/austen-six-passage-selection-2026-10-18.json; scoped copy records that existing human decision, not a fresh human approval.'
 for c in austen['clearances']:c['uses']=['evaluation']
 ledgers.append(austen);byid={r['id']:r for r in ledgers}
 sources={}
 for l in ledgers:
  p=ROOT/'rights'/l['source']['raw_path'];assert file_hash(p)==l['source']['sha256']
  sources[l['id']]=(p.read_bytes().decode('utf-8'),p.read_text())
 excerpts=[]
 for x in records:
  raw,lf=sources[x['source_id']];span=raw[x['raw_start']:x['raw_end']]
  assert sha_text(span)==x['raw_span_sha256'] and ' '.join(span.split())==x['text']
  start=len(raw[:x['raw_start']].replace('\r\n','\n').replace('\r','\n'))
  end=start+len(span.replace('\r\n','\n').replace('\r','\n'))
  assert lf[start:end]==span.replace('\r\n','\n').replace('\r','\n')
  excerpts.append(dict(id=x['id'],sid=x['source_id'],author=x['author_id'],work=x['work_id'],split='train',text=x['text'],span=dict(rights_record_id=x['source_id'],start=start,end=end,text=lf[start:end]),original_raw_coordinates=[x['raw_start'],x['raw_end']],transform='collapse_whitespace_only',approval='clean-source-expansion-human-approval-2026-10-18'))
 for x in approval['passages']:
  raw,lf=sources[austen['id']];span=lf[x['start']:x['end']];text=normalize_excerpt(span)
  assert sha_text(span)==x['raw_span_sha256'] and sha_text(text)==x['text_sha256']
  excerpts.append(dict(id=x['excerpt_id'],sid=austen['id'],author='austen',work='austen-pride',split='test',text=text,span=dict(rights_record_id=austen['id'],start=x['start'],end=x['end'],text=span),transform='join-soft-wraps-v1',approval=approval['record_id']))
 rows=[];trace=[];cases=[]
 for i,x in enumerate(excerpts):
  text=x['text'];words=list(re.finditer(r'\b\w+(?:[’\x27-]\w+)*\b',text));assert len(words)>=20
  candidates=list(re.finditer(r'\b[A-Za-z]{3,}\b',text));hit=candidates[len(candidates)//2]
  corrupt=text[:hit.start()]+hit.group()+' '+text[hit.start():]
  assert len(list(re.finditer(r'\b(\w+)\s+\1\b',corrupt)))==1,'Ambiguous duplicate-word repair'
  qstart=max(0,len(words)//3);qend=min(qstart+8,len(words));start,end=words[qstart].start(),words[qend-1].end()
  cut=words[len(words)//2].start();prefix=text[:cut].rstrip();suffix=text[cut:].lstrip()
  tasks=[('editing','restore','Remove only the consecutive duplicated word. Preserve all other characters and return only the repaired passage.\n\n'+corrupt,text,0,len(text)),('analysis','quote',f'Return exactly words {qstart+1} through {qend} (one-based) from the passage, including punctuation between those words. Add no quotation marks or explanation.\n\n'+text,text[start:end],start,end),('fiction','continue','Continue this excerpt with its original wording from '+byid[x['sid']]['title']+'. Return only the rest of this paragraph, without repeating the excerpt or adding explanation.\n\n'+prefix,suffix,cut,len(text))]
  for task,kind,prompt,target,ts,te in tasks:
   assert target==text[ts:te] and target.strip()==target
   rid=f"source-{x['split']}-{i:03d}-{kind}"
   messages=[dict(role='user',content=prompt),dict(role='assistant',content=target)]
   review=dict(status='approved',reviewer='Codex deterministic derivation audit; source human decisions preserved separately',reviewed_on='2026-10-20',notes='Current user authorised source-derived task construction and experiment. Verbatim source target and mechanical transformation verified; this is not a human literary-quality review.')
   row=dict(schema_version='1.0',id=rid,dataset_version='source-tasks-v1',task=task,split=x['split'],split_group='author-'+x['author'],origin='derived',messages=messages,source_work_ids=[x['work']],rights_record_ids=[x['sid']],source_spans=[x['span']],teacher=None,review=review,rubric=['Output is exactly the source-derived target, without extra text.','Restoration/quote tasks measure constrained fidelity; canonical continuation is not a unique measure of creative quality.'],content_hash=digest(messages))
   rows.append(row);trace.append(dict(id=rid,kind=kind,excerpt_id=x['id'],source_id=x['sid'],source_approval=x['approval'],source_coordinate_basis='Unicode code points after universal-newline normalization',source_span=x['span'],text_transform=x['transform'],target_start_in_transformed_text=ts,target_end_in_transformed_text=te,transformed_text_sha256=sha_text(text),target_sha256=sha_text(target),original_raw_coordinates=x.get('original_raw_coordinates')))
   if x['split']=='test':cases.append(dict(id=rid,kind=kind,task=task,prompt=prompt,target=target,source_id=x['sid'],excerpt_id=x['id']))
 assert len(rows)==342 and len(cases)==18
 assert {r['source_work_ids'][0] for r in rows if r['split']=='train'}.isdisjoint({r['source_work_ids'][0] for r in rows if r['split']=='test'})
 OUT.mkdir(parents=True)
 # Raw files must remain under rights/ for the existing traversal guard.
 ledger=ROOT/'rights/source-tasks-v1.scoped.jsonl';save(ledger,ledgers,True)
 save(OUT/'records.jsonl',rows,True)
 validated=validate_dataset(OUT/'records.jsonl',ledger,['GB','US'])
 assert len(validated)==342
 save(OUT/'train.messages.jsonl',[dict(messages=r['messages']) for r in rows if r['split']=='train'],True)
 save(OUT/'test.cases.jsonl',cases,True);save(OUT/'trace.jsonl',trace,True)
 save(OUT/'excerpts.jsonl',excerpts,True)
 protected=[ROOT/'rights/ledger.jsonl',ROOT/'rights/clean-sources.approved-v1.jsonl',ROOT/'rights/approvals/austen-six-passage-selection-2026-10-18.json',ROOT/'artifacts/clean-source-approved-v1/train.text.jsonl',ROOT/'artifacts/clean-source-training-v2/adapter/adapters.safetensors',ROOT/'evaluation/tasks.draft.jsonl',ROOT/'data/remediation-v1.pending.jsonl']
 save(OUT/'validation.json',dict(ok=True,train_records=324,test_records=18,train_authors=['amelia-opie','james-jackson-wray'],test_authors=['austen'],teacher=None,target_origin='Verbatim slices of approved original prose after recorded whitespace normalization; no generated answers.',foundation_validation='approved scoped sources, spans, message digests and author/work/group/lexical split checks passed',scoped_ledger_sha256=file_hash(ledger),files={p.name:file_hash(p) for p in OUT.iterdir() if p.is_file()},protected_files={str(p.relative_to(ROOT)):file_hash(p) for p in protected},limitations=['Austen is held out from all project fine-tuning, not proven absent from base pretraining.','Canonical continuation admits other valid fictional continuations and may measure memorisation.','These three proxy tasks do not establish dialogue, pacing, causal planning or overall literary quality.','Test tasks are mechanically constructed from existing human-approved prose; no synthetic teacher outputs or old benchmark scenarios are used.']))
 print('Validated 324 source-derived training tasks and 18 Austen author-held-out test tasks.')
if __name__=='__main__':main()
