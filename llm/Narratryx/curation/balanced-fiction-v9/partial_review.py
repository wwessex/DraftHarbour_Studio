"""Report an aborted evaluation without inventing missing responses or completed gates."""
import hashlib,json,os,random,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
from foundation.literary_diagnostics import quoted_dialogue_blocks
from scoring import clock_match,claim_match
RUN=ROOT/'artifacts/balanced-training-v9';DATA=ROOT/'artifacts/balanced-fiction-v9'
def save(name,value,private=False):
 fd=os.open(RUN/name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600 if private else 0o644)
 with os.fdopen(fd,'w') as f:json.dump(value,f,indent=2);f.write('\n')
def main():
 p=json.loads((RUN/'protocol.frozen.json').read_text())
 for group in ['input_hashes','protected_artifacts']:
  for n,h in p[group].items():assert file_hash(ROOT/n)==h,n
 cases=read_jsonl(DATA/'primary.cases.frozen.jsonl');allrows={s:read_jsonl(RUN/f'{s}.responses.jsonl') for s in ['base','current-craft','candidate']};candidate=allrows['candidate']
 assert len(candidate)==45 and candidate[-1]['finish_reason']=='length'
 assert [r['case_id'] for r in candidate]==[c['id'] for c in cases[:45]]
 for side in ['base','current-craft']:
  marker=json.loads((RUN/f'{side}.complete.json').read_text());assert marker['completed'] and marker['cases']==72 and marker['response_sha256']==file_hash(RUN/f'{side}.responses.jsonl')
  assert [r['case_id'] for r in allrows[side]]==[c['id'] for c in cases]
 details=[];summary={}
 for side,entries in allrows.items():
  for c,r in zip(cases,entries):
   assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest() and r['protocol_sha256']==file_hash(RUN/'protocol.frozen.json')
   assert r['messages_count']==1 and r['prior_assistant_messages']==0 and r['usage']['prompt_tokens_details']['cached_tokens']==0
   assert r['usage']['prompt_tokens']+r['usage']['completion_tokens']<=2048 and r['error'] is None
   failed=r['finish_reason']=='length';words=len(r['text'].split());lo=c.get('word_count_min');hi=c.get('word_count_max')
   details.append(dict(condition=side,case_id=c['id'],role=c['evaluation_role'],kind=c['kind'],request_failed=failed,words=words,word_limit_passed=None if lo is None and hi is None else not failed and (lo is None or words>=lo) and (hi is None or words<=hi),clock_exact=not failed and clock_match(r['text'],c['expected_json']) if c['kind']=='clock-state' else None,claim_exact=not failed and claim_match(r['text'],c['expected_json']) if c['kind']=='arrival-claim' else None,exact_repair=not failed and r['text'].strip()==c['exact_reference'] if c.get('exact_reference') else None,dialogue_turn_proxy=not failed and 4<=quoted_dialogue_blocks(r['text'])<=6 if c['kind']=='dialogue' else None))
  # Fair paired summaries cover attempted prefix including the failed request.
  own=[d for d in details if d['condition']==side and d['case_id'] in {c['id'] for c in cases[:45]}];summary[side]={}
  def count(ds,k):return dict(passed=sum(d[k] is True for d in ds),total=sum(d[k] is not None for d in ds))
  for role in sorted({d['role'] for d in own}):
   ds=[d for d in own if d['role']==role];summary[side][role]=dict(matched_attempted_cases=len(ds),request_failures=sum(d['request_failed'] for d in ds),clock_exact=count(ds,'clock_exact'),claim_exact=count(ds,'claim_exact'),exact_repair=count(ds,'exact_repair'),dialogue_turn_proxy=count(ds,'dialogue_turn_proxy'),word_limits={kind:count([d for d in ds if d['kind']==kind],'word_limit_passed') for kind in sorted({d['kind'] for d in ds})})
 save('partial-scores.json',dict(evaluation_complete=False,matched_attempted_prefix=45,candidate_complete_responses=44,candidate_truncated_responses=1,candidate_unattempted_primary=27,candidate_unattempted_extra=36,summary=summary,details=details,interpretation='Candidate hit output cap and looped. Do not treat missing cases as passes or summarise as a completed252-response benchmark. Paired summaries include failed request as failure; full base data retained separately.'))
 prose=[c for c in cases[:44] if c['kind'] not in ['clock-state','arrival-claim']];assert len(prose)==20
 responses={s:{r['case_id']:r for r in entries} for s,entries in allrows.items()};intro=['# Partial blinded comparison — evaluation stopped','','Only20 completed candidate prose cases are included. The next dialogue case repeated text and was truncated;27 remaining primary cases and36 exposed grounding checks were not attempted. This is incomplete evidence, not a release benchmark. A/B/C are independently randomised per case; no human ratings exist. Editing has no minimum length. Mechanical/length passes are not literary quality.','']
 packet=intro.copy();sections={};rng=random.SystemRandom();key=[];ballots=[]
 for c in prose:
  sides=['base','current-craft','candidate'];rng.shuffle(sides);key.append(dict(case_id=c['id'],**dict(zip('ABC',sides))))
  section=['## '+c['id'],'',c['prompt'],'','Known facts: '+'; '.join(c.get('established_facts',[])),'','Unknowns: '+'; '.join(c.get('unknowns',[])),'']
  for label,side in zip('ABC',sides):section+=['### Response '+label,'',responses[side][c['id']]['text'],'']
  packet+=section;sections[c['id']]=section
  for reviewer in ['reviewer-1','reviewer-2']:ballots.append(dict(case_id=c['id'],reviewer=reviewer,ratings=dict(A=None,B=None,C=None),preference=None,evidence=None))
 with (RUN/'PARTIAL-REVIEW.md').open('x') as f:f.write('\n'.join(packet)+'\n')
 save('partial-key.private.json',key,True)
 with (RUN/'partial-human-ballots.blank.jsonl').open('x') as f:
  for r in ballots:f.write(json.dumps(r)+'\n')
 picks=['bf-conservatory-analysis','bf-rope-workshop-rewrite','bf-aquarium-records-analysis','bf-print-shop-analysis','bf-craft-reel-dialogue','bf-craft-reel-pacing','bf-craft-reel-continue','bf-craft-reel-write'];quick=intro.copy()
 for ident in picks:quick+=sections[ident]
 with (RUN/'QUICK-PARTIAL-REVIEW.md').open('x') as f:f.write('\n'.join(quick)+'\n')
 c=cases[44];r=candidate[-1]
 with (RUN/'TRUNCATED-CASE.md').open('x') as f:f.write('# Candidate failure — not a blind comparison\n\n'+c['prompt']+'\n\n## Truncated candidate output\n\n'+r['text']+'\n\nStopped at384 completion tokens. No repair, completion or higher-budget retry was performed.\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
