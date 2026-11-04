"""Score the exposed stability suite, preserving missing and truncated references."""
import hashlib,json,os,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from scoring import clock_match,claim_match
from stability_checks import repeated_dialogue
RUN=ROOT/'artifacts/stability-v10';PLAN=ROOT/'artifacts/stability-v10-plan'
def save(name,value,private=False):
 fd=os.open(RUN/name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600 if private else 0o644)
 with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 p=json.loads((RUN/'protocol.frozen.json').read_text())
 for group in ['input_hashes','protected_artifacts']:
  for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
 cases=read_jsonl(PLAN/'cases.frozen.jsonl');new=read_jsonl(RUN/'candidate.responses.jsonl') if (RUN/'candidate.responses.jsonl').exists() else []
 assert [r['case_id'] for r in new]==[c['id'] for c in cases[:len(new)]]
 answers={s:{r['case_id']:r for r in read_jsonl(PLAN/(s+'.reference.jsonl'))} for s in ['base','current-craft','high-lr']};answers['lower-rate']={r['case_id']:r for r in new}
 details=[];summary={}
 for side,rows in answers.items():
  ds=[]
  for c in cases:
   r=rows.get(c['id'])
   if r is None:
    d=dict(condition=side,case_id=c['id'],role=c['evaluation_role'],kind=c['kind'],available=False);details.append(d);continue
   assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest()
   failed=bool(r.get('error')) or r['finish_reason']=='length';text=r['text'];words=len(text.split());lo=c.get('word_count_min');hi=c.get('word_count_max');repeat=repeated_dialogue(text) if c['kind']=='dialogue' else None
   d=dict(condition=side,case_id=c['id'],role=c['evaluation_role'],kind=c['kind'],available=True,request_failed=failed,truncated=r['finish_reason']=='length',words=words,word_limit_passed=None if lo is None and hi is None else not failed and (lo is None or words>=lo) and (hi is None or words<=hi),repeat_count=repeat,dialogue_repeat_flag=repeat>=2 if repeat is not None else None,clock_exact=not failed and clock_match(text,c['expected_json']) if c['kind']=='clock-state' else None,claim_exact=not failed and claim_match(text,c['expected_json']) if c['kind']=='arrival-claim' else None,exact_edit=not failed and text.strip()==c['exact_reference'] if c.get('exact_reference') else None)
   ds.append(d);details.append(d)
  def count(items,key):return dict(passed=sum(d.get(key) is True for d in items),total=sum(d.get(key) is not None for d in items))
  summary[side]=dict(available=len(ds),missing=24-len(ds),request_failures=sum(d['request_failed'] for d in ds),truncations=sum(d['truncated'] for d in ds),dialogue_repeat_flags=sum(d['dialogue_repeat_flag'] is True for d in ds),clock_exact=count(ds,'clock_exact'),claim_exact=count(ds,'claim_exact'),exact_edit=count(ds,'exact_edit'),word_limits={kind:count([d for d in ds if d['kind']==kind],'word_limit_passed') for kind in sorted({c['kind'] for c in cases})})
 complete=(RUN/'candidate.complete.json').exists() and len(new)==24
 save('scores.json',dict(candidate_evaluation_complete=complete,summary=summary,details=details,exposed_failure_enriched_suite=True,reused_references=True,human_quality_ratings=0,interpretation='Missing high-rate rows are unattempted, not successes. Mechanical stability/format/closed-task scores are not literary quality.'))
 writing=[c for c in cases if c['evaluation_role']=='exposed-writing-stability' and c['id'] in answers['lower-rate'] and answers['lower-rate'][c['id']]['finish_reason']!='length']
 intro=['# Small stability review: current craft versus lower-rate candidate','','All cases are exposed, failure-enriched development checks. These are reused current-model references and newly generated candidate outputs. Labels are randomised separately per completed writing case. No human ratings exist. Record evidence of distinct aims, coherence, practical action, instruction adherence and invented consent/resources; word counts and exact-repetition flags do not prove literary quality.','']
 packet=intro.copy();key=[];ballots=[];rng=random.SystemRandom()
 for c in writing:
  sides=['current-craft','lower-rate'];rng.shuffle(sides);key.append(dict(case_id=c['id'],**dict(zip('AB',sides))));packet+=['## '+c['id'],'',c['prompt'],'']
  for label,side in zip('AB',sides):packet+=['### Response '+label,'',answers[side][c['id']]['text'],'']
  for reviewer in ['reviewer-1','reviewer-2']:ballots.append(dict(case_id=c['id'],reviewer=reviewer,ratings=dict(A=None,B=None),preference=None,evidence=None))
 if not writing:packet+=['No complete candidate writing cases are available; no prose-quality comparison can be made.','']
 with (RUN/'REVIEW.md').open('x') as f:f.write('\n'.join(packet)+'\n')
 save('blind-key.private.json',key,True)
 with (RUN/'human-ballots.blank.jsonl').open('x') as f:
  for r in ballots:f.write(json.dumps(r)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
