"""Mechanical checks and a blinded prose packet, never automated literary ratings."""
import hashlib,json,os,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from foundation.literary_diagnostics import quoted_dialogue_blocks
from scoring import clock_match,claim_match
RUN=ROOT/'artifacts/balanced-training-v9'
def save(name,value,private=False):
 fd=os.open(RUN/name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600 if private else 0o644)
 with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 p=json.loads((RUN/'protocol.frozen.json').read_text())
 for n,h in p['input_hashes'].items():assert file_hash(ROOT/n)==h,n
 primary=read_jsonl(ROOT/p['test_cases_path']);extra=read_jsonl(ROOT/p['extra_cases_path']);responses={};details=[];summary={}
 for side in p['model_conditions']:
  cases=primary+extra if side=='candidate' else primary;entries=read_jsonl(RUN/f'{side}.responses.jsonl');complete=json.loads((RUN/f'{side}.complete.json').read_text())
  assert complete['completed'] and complete['cases']==len(cases) and complete['response_sha256']==file_hash(RUN/f'{side}.responses.jsonl')
  assert [r['case_id'] for r in entries]==[c['id'] for c in cases]
  responses[side]={r['case_id']:r for r in entries}
  for c,r in zip(cases,entries):
   assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest() and r['protocol_sha256']==file_hash(RUN/'protocol.frozen.json')
   assert r['messages_count']==1 and r['prior_assistant_messages']==0 and r['usage']['prompt_tokens_details']['cached_tokens']==0
   assert r['usage']['prompt_tokens']+r['usage']['completion_tokens']<=2048 and not r['error'] and r['finish_reason']!='length'
   text=r['text'];words=len(text.split());lo=c.get('word_count_min');hi=c.get('word_count_max')
   details.append(dict(condition=side,case_id=c['id'],role=c['evaluation_role'],kind=c['kind'],words=words,word_limit_passed=None if lo is None and hi is None else (lo is None or words>=lo) and (hi is None or words<=hi),exact_repair=text.strip()==c['exact_reference'] if c.get('exact_reference') is not None else None,clock_exact=clock_match(text,c['expected_json']) if c['kind']=='clock-state' else None,claim_exact=claim_match(text,c['expected_json']) if c['kind']=='arrival-claim' else None,dialogue_turn_proxy=4<=quoted_dialogue_blocks(text)<=6 if c['kind']=='dialogue' else None,unchanged_requested_rewrite=text.strip()==c['context'].strip() if c['kind']=='rewrite' and c.get('context') else None))
  own=[d for d in details if d['condition']==side];summary[side]={}
  def count(ds,key):return dict(passed=sum(d[key] is True for d in ds),total=sum(d[key] is not None for d in ds))
  for role in sorted({d['role'] for d in own}):
   ds=[d for d in own if d['role']==role];summary[side][role]=dict(requests=len(ds),clock_exact=count(ds,'clock_exact'),claim_exact=count(ds,'claim_exact'),exact_repair=count(ds,'exact_repair'),dialogue_turn_proxy=count(ds,'dialogue_turn_proxy'),unchanged_rewrite_count=sum(d['unchanged_requested_rewrite'] is True for d in ds),word_limits={kind:count([d for d in ds if d['kind']==kind],'word_limit_passed') for kind in sorted({d['kind'] for d in ds})})
 save('scores.json',dict(summary=summary,details=details,human_literary_ratings=0,interpretation='Mechanical closed-task/format checks only. Extra tiny checks and writing retention are exposed diagnostics, not fresh literary approval. Unchanged rewrites are an exploratory instruction-adherence diagnostic.'))
 prose=[c for c in primary if c['kind'] not in ['clock-state','arrival-claim']];assert len(prose)==48
 intro=['# Blinded balanced-model prose comparison','','A/B/C are randomised independently per case. There are 48 prose cases: 24 fresh cases and 24 exposed retention regressions. No human ratings exist. The new situations are AI-authored evaluation-only inputs, not human-approved benchmark gold.','','Rate usefulness, voice, coherent viewpoint/tense, grounding and the requested craft skill from 1–5. Record concrete evidence, invented facts and contradicted constraints. Do not reward length or extra explanation. Editing has no minimum word count. Keep the private condition key separate until ballots are submitted. Closed JSON, word limits and quotation counts are not literary quality.','']
 packet=intro.copy();sections={};key=[];ballots=[];rng=random.SystemRandom()
 for c in prose:
  sides=p['model_conditions'].copy();rng.shuffle(sides);key.append(dict(case_id=c['id'],**dict(zip('ABC',sides))))
  section=['## '+c['id'],'','Role: '+c['evaluation_role'],'',c['prompt'],'','Known facts: '+'; '.join(c.get('established_facts',[])),'','Unknowns: '+'; '.join(c.get('unknowns',[])),'']
  for label,side in zip('ABC',sides):section+=['### Response '+label,'',responses[side][c['id']]['text'],'']
  packet+=section;sections[c['id']]=section
  for reviewer in ['reviewer-1','reviewer-2']:ballots.append(dict(case_id=c['id'],reviewer=reviewer,ratings=dict(A=None,B=None,C=None),preference=None,evidence=None))
 with (RUN/'BLIND-REVIEW.md').open('x') as f:f.write('\n'.join(packet)+'\n')
 save('blind-key.private.json',key,True)
 with (RUN/'human-ballots.blank.jsonl').open('x') as f:
  for r in ballots:f.write(json.dumps(r)+'\n')
 picks=['bf-conservatory-analysis','bf-rope-workshop-rewrite','bf-craft-reel-dialogue','bf-craft-coat-pacing','bf-craft-reel-write','bf-craft-coat-continue','seed-library-dialogue','mountain-shelter-continue']
 quick=intro+['Eight suggested starting cases follow. Full coverage is in BLIND-REVIEW.md.','']
 for ident in picks:quick+=sections[ident]
 with (RUN/'QUICK-REVIEW.md').open('x') as f:f.write('\n'.join(quick)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
