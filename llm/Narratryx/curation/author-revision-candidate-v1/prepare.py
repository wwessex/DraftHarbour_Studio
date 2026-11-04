from pathlib import Path
import urllib.request,hashlib,json,re,argparse
parser=argparse.ArgumentParser(description='Prepare excluded historical revision candidates, never training data');parser.add_argument('--fetch',action='store_true');args=parser.parse_args()
root=Path(__file__).resolve().parents[2];lock=json.loads(Path(__file__).with_name('source-lock.json').read_text());out=root/'artifacts/author-revision-candidate-2026-10-25';out.mkdir(exist_ok=True)
raw=root/'rights/raw/author-revision-candidate-2026-10-25';raw.mkdir(parents=True,exist_ok=True)
manifest=[]
for number in [25851,1400]:
 url=f'https://www.gutenberg.org/cache/epub/{number}/pg{number}.txt'
 p=raw/f'pg{number}.txt'
 if not p.exists() and not args.fetch: raise SystemExit('Raw source missing; pass --fetch to acquire the two pinned files explicitly.')
 data=p.read_bytes() if p.exists() else urllib.request.urlopen(url,timeout=45).read()
 expected=next(item for item in lock['sources'] if item['url']==url)['raw_sha256']
 if hashlib.sha256(data).hexdigest()!=expected: raise SystemExit('Source changed: review it before updating the lock.')
 p.write_bytes(data)
 text=data.decode('utf-8-sig');canonical=out/f'pg{number}.decoded.txt';canonical.write_text(text,encoding='utf-8')
 manifest.append({'url':url,'raw_path':str(p.relative_to(root)),'raw_sha256':hashlib.sha256(data).hexdigest(),'decoded_path':str(canonical.relative_to(root)),'decoded_sha256':hashlib.sha256(text.encode()).hexdigest(),'fetched':'2026-10-25','edition_status':'candidate: exact scan comparison pending'})
 if number==25851:
  # Only the discarded-ending footnote; surrounding Forster commentary remains evidence.
  start=text.rfind('[270]');end=text.find('[271]',start)
  assert start>=0 and end>start
  piece=text[start:end]
  (out/'discarded-ending-footnote.txt').write_text(piece)
  manifest[-1]['excerpt']={'start_codepoint':start,'end_codepoint':end,'sha256':hashlib.sha256(piece.encode()).hexdigest(),'locator':'Vol III, footnote 270; includes attribution wrapper, not training-ready'}
  pos=text.find('Bulwer, who has been');assert pos>0
  (out/'revision-history-evidence.txt').write_text(text[max(0,pos-650):pos+1050])
 else:
  # Last numbered chapter, excluding PG license and end matter.
  matches=list(re.finditer(r'(?m)^Chapter LIX\.?\s*$',text));assert matches
  start=matches[-1].end();end=text.index('*** END OF THE PROJECT GUTENBERG',start)
  piece=text[start:end];(out/'published-ending-chapter.txt').write_text(piece)
  manifest[-1]['excerpt']={'start_codepoint':start,'end_codepoint':end,'sha256':hashlib.sha256(piece.encode()).hexdigest(),'locator':'Chapter LIX; long candidate span, alignment pending'}
(out/'sources.json').write_text(json.dumps({'status':'candidate_only_excluded_from_training','sources':manifest},indent=2)+'\n')
print(json.dumps({'acquired_sources':len(manifest),'status':'candidate_only_excluded_from_training','files':[str(p) for p in out.iterdir() if p.name.endswith('evidence.txt') or p.name=='sources.json']}))

# This draft remains outside the rights ledger and every training builder.
original=(out/'pg25851.decoded.txt').read_bytes().decode('utf-8')
published=(out/'pg1400.decoded.txt').read_bytes().decode('utf-8')
old_start=original.index('It was two\r\nyears more, before I saw herself.', manifest[0]['excerpt']['start_codepoint'])
old_end=original.index('used to be.',old_start)+len('used to be.')
new_start=published.index('Nevertheless, I knew, while I said those words',manifest[1]['excerpt']['start_codepoint'])
new_end=published.index('from her.',new_start)+len('from her.')
def span(text,start,end,number):
 value=text[start:end]
 return {'source':number,'start_codepoint':start,'end_codepoint':end,'sha256':hashlib.sha256(value.encode('utf-8')).hexdigest(),'text':value}
candidate={'id':'dickens-alternative-ending-candidate','status':'excluded_pending_exact_edition_rights_and_alignment_review',
 'task':'structural_alternative_ending_not_minimal_copyedit',
 'instruction':'Replace the discarded final encounter with an alternative ending in which Pip returns to the ruined house and meets Estella there. Keep his first-person retrospective narration; changes to the encounter and ending are expressly allowed. This is one historical author choice, not a universal improvement.',
 'instruction_provenance':'AI-constructed task framing; literary input and target are unchanged source substrings',
 'input':span(original,old_start,old_end,25851),'target':span(published,new_start,new_end,1400),
 'human_approval':None,'training_eligible':False}
(out/'candidate.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n')
print('Prepared one excluded structural-revision candidate; no training files changed.')
