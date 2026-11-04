# Build new scoped candidate material from retained original sources; never train.
import copy,json,hashlib,sys
from pathlib import Path
r=Path(__file__).resolve().parents[2];sys.path.insert(0,str(r))
from foundation.validation import file_hash,digest,read_jsonl,validate_dataset,load_ledger
from foundation.scoped_excerpt import excerpt,split_continuation
out=r/'artifacts/source-expansion-v23';out.mkdir()
raw=r/'rights/raw/source-expansion-2026-11-02';ev=r/'rights/evidence/source-expansion-2026-11-02'
old_ledger=r/'rights/grounding-balanced-v1.scoped.jsonl';ledger=read_jsonl(old_ledger);byid={x['id']:x for x in ledger}
pg=(raw/'pg688.txt').read_text()
specs=[
 ('violin-refusal','dialogue','"Ma foi, but monsieur must know', '"Martel," said the first speaker',None,
  'Write three spoken turns with brief narration in a historical New Orleans story. M’sieu Fortier protests that he is too old for love songs; a young man says he wants Fortier’s violin; Fortier refuses and grips the case. Keep the historical register and dialect. The violin is not sold and no agreement is granted. Narration and speech tags are allowed. Return only the exchange.'),
 ('search-departure','fiction','Under the beds, in closets and corners,','Search as they did, there were no signs of Titee.','With lanterns and sticks',
  'Continue after the supplied complete paragraph with one new paragraph of historical story prose. Have the party actually set out along the track with lanterns, sticks and the dog. Describe the wind and strange light as atmosphere, with any luminous comparison kept figurative. Titee is still missing; do not announce a discovery or guaranteed safety. Return only the new paragraph.'),
 ('wade-return','fiction','"But I am barefoot," wailed Annette,','"Ah, Mees Annette," whispered Natalie,','"True," assented the fisherman;',
  'Continue after these complete paragraphs with exactly two new paragraphs. Let the fisherman accept Annette’s objection to walking on the crab-covered sands and agree to wade back; then show their return to the fish-fry and his departure. Preserve the period narration and allow this practical change of route and completed return. Return only new story prose.')]
spans=[];bindings=[]
for name,task,start,stop,answer_start,brief in specs:
 s=excerpt(pg,start,stop);s['rights_record_id']='dunbar-st-rocque-pg688-v23';spans.append(dict(id='v23-'+name,**s))
 bindings.append(dict(id='v23-'+name,task=task,brief=brief,source_spans=[s],derivation=split_continuation(s,answer_start) if answer_start else None))
for n in ['1881','1908']:
 text=(raw/f'james-{n}-reaction.verified.txt').read_text();spans.append(dict(id=f'james-{n}-reaction-v23',rights_record_id=f'james-{n}-reaction-v23',start=0,end=len(text),text=text))
with (out/'scope.json').open('x') as f:json.dump(spans,f,indent=2,ensure_ascii=False);f.write('\n')
review=lambda:dict(status='approved',reviewer='Codex AI: exact source/task preparation and scoped evidence assessment',reviewed_on='2026-11-02',notes='AI assessment under standing permission-free-source scope; not human literary approval or legal certification. Preparation only; no model training or publication.')
new=[]
for n in ['1881','1908']:
 old=byid[f'james-{n}-proposal-revision-v1'];q=copy.deepcopy(old);path=raw/f'james-{n}-reaction.verified.txt';text=path.read_text()
 q['id']=f'james-{n}-reaction-v23';q['title']='The Portrait of a Lady — selected post-proposal reaction, '+n;q['review']=review()
 q['source'].update(raw_path=str(path.relative_to(r/'rights')),sha256=file_hash(path),revision='sha256:'+file_hash(path),retrieved_on='2026-11-02',included_material=f'Only canonical span0:{len(text)}, '+('printed pp141–142, scan leaves155–156.' if n=='1881' else 'printed pp155–157, scan leaves181–183.')+' Scope: artifacts/source-expansion-v23/scope.json, SHA256 '+file_hash(out/'scope.json')+'. No old scope is extended implicitly.',terms_decision='AI assessment supports private local GB/US original-prose preparation/training under the same expired-author basis and digital-artifact provenance as existing James dossiers. No scan/digital-object redistribution or new grant is asserted. Full IA site terms could not be re-read (JS-only response); that limitation is retained, not represented as a complete terms review.')
 q['source']['terms_evidence']=list(dict.fromkeys(q['source']['terms_evidence']+['https://archive.org/about/terms']))
 q['source']['excluded_material']+=' All other new page text, running heads, page layout and italic emphasis excluded.'
 q['clearances']=[dict(c,uses=['training']) for c in q['clearances']]
 new.append(q)
q=copy.deepcopy(byid['doyle-adventures-pg48320']);q.update(id='dunbar-st-rocque-pg688-v23',work_id='goodness-st-rocque-collection',title='The Goodness of St. Rocque and Other Stories — three selected scenes',author_ids=['alice-moore-dunbar-nelson'],contributors=[dict(name='Alice Moore Dunbar-Nelson',role='author of included original narrative prose only',life_dates='1875–1935')],publication=dict(original_year=1899,edition='Pinned PG688 plain-text digital artifact, last-update header1January2021. Original collection corroborated as Dodd, Mead1899 by NYPL bibliographic transcription. Exact physical copy behind PG is unidentified; no1899 facsimile claim.',publisher='Project Gutenberg digital transcription; historical publication Dodd, Mead and Company, New York',evidence=['https://www.gutenberg.org/ebooks/688','https://s3.amazonaws.com/nypl-aaww/SCAAWW_book_11_The_goodness_of_St_Rocque_and_other_stories.pdf']),source=dict(url='https://www.gutenberg.org/cache/epub/688/pg688.txt',retrieved_on='2026-11-02',revision='sha256:'+file_hash(raw/'pg688.txt'),raw_path=str((raw/'pg688.txt').relative_to(r/'rights')),sha256=file_hash(raw/'pg688.txt'),included_material='Only three exact LF-normalized spans bound in artifacts/source-expansion-v23/scope.json, SHA256 '+file_hash(out/'scope.json')+'. Narrated violin refusal, Titee search departure, and return from the shore. No whole-collection clearance.',excluded_material='All provider notices, branding, catalogue summaries, headings, dedication, all other stories/passages, poems, songs, prayers, quoted third-party verse, modern introductions and apparatus. Credits to Judith Boss/Al Haines are retained in raw bytes, not taught as literary prose. NYPL material is bibliographic evidence only, never a teaching target.',terms_evidence=['https://www.gutenberg.org/ebooks/688','https://www.gutenberg.org/policy/permission.html','https://www.gutenberg.org/policy/terms_of_use.html','https://www.gutenberg.org/policy/license.html'],terms_decision='Item catalogue identifies US public domain. PG permissions distinguish unbranded expired original prose from trademark trading; original header/notices retained. AI evidence assessment supports private local GB/US preparation/training on these unbranded expired original-prose spans without a new rights-holder grant. No branded ebook redistribution, provider endorsement, publication or upload authorised. Physical-copy uncertainty is disclosed.',notices='Complete original PG header/footer and embedded licence retained byte-for-byte. No special copyright-holder permission notice applies to the selected original-prose spans.'),clearances=[dict(jurisdiction='GB',uses=['training'],basis='Identified original author died1935; ordinary life-plus-70 literary term expired by end2005. Collection was published1899; no unpublished manuscript, modern literary additions or printed layout included.',evidence=['https://www.gov.uk/copyright/how-long-copyright-lasts','https://www.gutenberg.org/ebooks/688']),dict(jurisdiction='US',uses=['training'],basis='PG item-specific public-domain statement plus1899 historical publication, beyond the maximum historical95-year term. Included text is original published author prose, not later independent contributions.',evidence=['https://www.gutenberg.org/ebooks/688','https://www.copyright.gov/circs/circ15a.pdf'])],unresolved_issues=[],review=review())
new.append(q);ledger+=new
ledgerpath=r/'rights/source-expansion-v23.scoped.jsonl'
with ledgerpath.open('x') as f:
 for q in ledger:f.write(json.dumps(q,ensure_ascii=False)+'\n')
records=[]
for b in bindings:
 s=b['source_spans'][0];d=b['derivation'];prompt=b['brief']+('\n\nPRECEDING PARAGRAPHS:\n'+d['context'] if d else '')
 records.append(dict(schema_version='1.0',id=b['id'],dataset_version='source-expansion-v23-candidates',task=b['task'],split='train',split_group='dunbar-st-rocque-pg688',origin='derived',messages=[dict(role='user',content=prompt),dict(role='assistant',content=d['answer'] if d else s['text'])],source_work_ids=['goodness-st-rocque-collection'],rights_record_ids=['dunbar-st-rocque-pg688-v23'],source_spans=[s],teacher=None,review=review(),rubric=['source fidelity','instruction alignment','scene progression']))
a=next(s for s in spans if s['id']=='james-1881-reaction-v23');b=next(s for s in spans if s['id']=='james-1908-reaction-v23')
a={k:v for k,v in a.items() if k!='id'};b={k:v for k,v in b.items() if k!='id'}
brief='Make a substantive stylistic revision of this period psychological narration. Preserve Isabel’s decision not to marry Lord Warburton, her promise to write, and her uneasy return from the bench to the house. Develop the pressure of the splendid opportunity, the narrowing security it offers, and her doubt about pride versus sympathy. Interpretive emphasis and imagery may change. This is an authentic author-edition alternative, not minimal copyediting or a request for a shorter passage. Return only the revised paragraph.'
records.append(dict(schema_version='1.0',id='v23-james-reaction-revision',dataset_version='source-expansion-v23-candidates',task='editing',split='train',split_group='portrait-of-a-lady',origin='derived',messages=[dict(role='user',content=brief+'\n\nPASSAGE:\n'+a['text']),dict(role='assistant',content=b['text'])],source_work_ids=['portrait-of-a-lady'],rights_record_ids=[a['rights_record_id'],b['rights_record_id']],source_spans=[a,b],teacher=None,review=review(),rubric=['source fidelity','instruction alignment','psychological development']))
bindings.append(dict(id='v23-james-reaction-revision',task='editing',source_spans=[a,b],method='AI scan transcription from1881 pp141–142 and1908 pp155–157; normalize line-wrap hyphenation, spacing, quotation/apostrophe glyphs and split contractions, omit italics, preserve lexical content. Not human verification.'))
for q in records:q['content_hash']=digest(q['messages'])
def rows(name,data):
 with (out/name).open('x') as f:
  for q in data:f.write(json.dumps(q,ensure_ascii=False)+'\n')
rows('candidates.jsonl',records);rows('derivations.jsonl',bindings)
validated=validate_dataset(out/'candidates.jsonl',ledgerpath,['GB','US'],benchmark=read_jsonl(r/'evaluation/tasks.draft.jsonl'))
monitor=[dict(q,dataset_version=records[0]['dataset_version']) for q in read_jsonl(r/'artifacts/source-candidates-v20/records.proposed.jsonl') if q['split']=='validation']
rows('split-check-only.jsonl',records+monitor);validate_dataset(out/'split-check-only.jsonl',ledgerpath,['GB','US'])
prior=read_jsonl(r/'artifacts/source-candidates-v20/records.proposed.jsonl')
assert not {q['messages'][-1]['content'] for q in records}&{q['messages'][-1]['content'] for q in prior}
packet=['# Four source-backed candidates','','Preparation only; no training, human approval or new model quality claim. AI briefs are constructed after reading the original source. Answers are exact published substrings or declared scan transcriptions, never generated literary teaching prose. Standalone candidates, not merged into a training recipe.','']
for q in records:packet+=['## '+q['id'],'',q['messages'][0]['content'],'','### Published source answer','',q['messages'][-1]['content'],'']
(out/'REVIEW.md').write_text('\n'.join(packet))
print('Prepared4 exact-source candidates; new scoped ledger18records (15unchanged+3new). Validation and held-out Wray split checks pass.')
