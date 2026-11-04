"""Decode fixed AI judgements only after locking them; never fills human ballots."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'artifacts/task-matched-training-v3';OUT=ROOT/'artifacts/task-matched-quality-review-2026-10-26'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 review_path=OUT/'ai-review.labels.v2.frozen.json';review=json.loads(review_path.read_text());lock=json.loads((OUT/'review.v2.lock.json').read_text())
 assert sha(review_path)==lock['review_sha256'] and lock['key_consulted_before_freeze'] is False
 for rel,value in review['input_hashes'].items():assert sha(ROOT/'configs/narratryx-craft-v1.json' if rel=='model-pin' else RUN/rel)==value,rel
 assert len(review['cases'])==8 and review['human_ballots_completed']==0
 # Identities are read only after validating the immutable judgement/packet hashes.
 key_path=RUN/'blind-key.private.json';key={r['case_id']:r for r in json.loads(key_path.read_text())}
 models=['base','current-craft','candidate'];strict_wins={m:0 for m in models};decoded=[];three_way_ties=0;uncertain_ties=0
 responses={m:{r['case_id']:r for r in map(json.loads,(RUN/f'{m}.responses.jsonl').read_text().splitlines())} for m in models}
 for row in review['cases']:
  mapping=key[row['case_id']];assert {mapping[k] for k in 'ABC'}==set(models)
  assert set(row['task_fit'])==set('ABC') and all(1<=score<=5 for score in row['task_fit'].values())
  assert row['preferred'] and set(row['preferred']).issubset(set('ABC'))
  for label in 'ABC':
   text=responses[mapping[label]][row['case_id']]['text'].strip()
   assert hashlib.sha256(text.encode()).hexdigest()==row['response_sha256'][label]
   assert len(text.split())==row['word_counts'][label]
  preferred=[mapping[label] for label in row['preferred']]
  if len(preferred)==1:strict_wins[preferred[0]]+=1
  elif len(preferred)==3:three_way_ties+=1
  else:uncertain_ties+=1
  decoded.append(dict(case_id=row['case_id'],model_ratings={mapping[label]:value for label,value in row['task_fit'].items()},preferred_models=preferred,decision=row['decision']))
 summary=dict(review_type=review['review_type'],cases=8,responses=24,strict_ai_preferences=strict_wins,three_way_ties=three_way_ties,uncertain_two_way_ties=uncertain_ties,population_quality_score=None,human_ratings=0,promotion=False,interpretation='Descriptive preferences from one informed AI reviewer on a purposive subset. Some preferred answers still require major revision. Not independent human quality evidence, statistical superiority, or Muse equivalence.')
 with (OUT/'decoded.private.json').open('x') as f:json.dump(dict(summary=summary,cases=decoded,key_sha256=sha(key_path),judgements_sha256=sha(review_path)),f,indent=2);f.write('\n')
 with (OUT/'verification.json').open('x') as f:json.dump(dict(passed=True,judgements_verified_before_decoding=True,original_packet_and_model_responses_unchanged=True,human_ballots_unchanged=True,model_pin_unchanged=True,judgements_sha256=sha(review_path),key_sha256=sha(key_path),decoder_sha256=sha(Path(__file__)),human_ratings=0,promoted=False),f,indent=2);f.write('\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
