"""Build pending synthetic remediation drafts; never train or grant approvals."""
from pathlib import Path
import json,sys,copy,re
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import digest,file_hash,validate_schema,validate_dataset,Invalid,read_jsonl,check_leakage
from foundation.evaluation import objective
OUT=ROOT/'artifacts/remediation-v1'
CONTEXTS={
'clock':'At closing time, Selma found the brass key beneath the clock she had repaired. The collection label named her estranged aunt, who had died that spring. The customer was waiting outside the locked shop.',
'print':'Jonah had promised to deliver forty programmes before the concert began. The printer stopped after the thirty-ninth copy. Beside it, his younger sister held the last sheet of blue paper.'}
DRAFTS=[]
def add(scene,task,instruction,target,checks,rubric,why):
 DRAFTS.append(dict(id=f'remediation-{scene}-{task}-01',scene=scene,task=task,instruction=instruction,target=target,checks=checks,rubric=rubric,why=why))
def words(lo,hi):return {'type':'word_count','min':lo,'max':hi}
add('clock','editing','Check for a clear grammatical error. If none exists, write "No changes needed." followed by the passage exactly unchanged. Do not modernise or polish the prose. No explanation is required.',
'No changes needed.\n\n'+CONTEXTS['clock'],[{'type':'exact','value':'No changes needed.\n\n'+CONTEXTS['clock']}],['Recognises that no grammatical correction is necessary.','Preserves every character in the reproduced passage.'], 'Resists unnecessary edits and explanations; no minimum word count.')
add('print','editing','Remove only the duplicated word in the passage. Reproduce the corrected passage, then give one brief change-list item identifying the exact deletion. Preserve every other character.',
CONTEXTS['print']+'\n\n- Deleted the second "the" from "the the thirty-ninth copy".',
[{'type':'exact','value':CONTEXTS['print']+'\n\n- Deleted the second "the" from "the the thirty-ninth copy".'}],['Makes only the requested deletion.','Change list accurately describes the deletion.'], 'Teaches a verifiable edit with an honest change list; no minimum word count.')
add('clock','analysis','Analyse the immediate conflict in 80–140 words. Include two short exact quotations in double quotes. Separate established facts, interpretation and one possible next action; do not assume the customer\'s identity or explain the aunt\'s death.',
'''Established: Selma has repaired a clock, found a "brass key" beneath it, and read a label naming her estranged aunt. Her aunt died that spring. A customer is "waiting outside the locked shop". The passage does not identify that customer or explain why the aunt's name appears on the label.

Interpretation: the label may complicate an ordinary collection, but Selma's feelings and the key's purpose remain unstated. A possible next action is to ask the customer about the label before handing over the clock. This is a proposed choice, not an event the passage already establishes.''',
[words(80,140),{'type':'quotes_from_context','min_quotes':2}],['Quotes exactly from the passage.','Does not identify the customer or invent the key\'s purpose.','Labels interpretation and proposed action.'], 'Prevents inferred motives and relationships from becoming asserted facts.')
add('print','analysis','Analyse the practical goal and obstacle in 80–140 words. Include two short exact quotations in double quotes. Distinguish what is known from possible solutions. Do not invent a reason for the printer failure or a motive for the sister.',
'''Established: Jonah promised to deliver "forty programmes" before the concert began. The printer stopped after producing thirty-nine. His sister holds "the last sheet of blue paper". He is therefore one programme short, but the passage does not say why the printer stopped or how much time remains.

Interpretation: the final sheet makes another attempt consequential, although we do not know whether the paper caused the fault. A possible next action is to check the printer before using that sheet. Sharing a copy could be another proposal, but would not itself fulfil the promise to deliver forty. Neither solution has happened in the supplied scene.''',
[words(80,140),{'type':'quotes_from_context','min_quotes':2}],['Preserves quantities and the delivery promise.','Does not diagnose an unspecified printer fault.','Distinguishes a workaround from fulfilling the promise.'], 'Teaches bounded analysis with exact evidence and explicit uncertainty.')
add('clock','dialogue','Write exactly eight lines of dialogue between Selma and the customer, 70–120 words total. Use only quoted speech: no speaker labels, action, narration or explanation. Give the speakers conflicting aims and leave a motive unstated. Preserve the supplied facts.',
'''"The shop is closed. Tell me the name on your collection slip."
"You have the label already. Could you bring the clock to the door?"
"It names my aunt. She died this spring."
"Then you know which clock I mean. I can wait while you fetch it."
"I repaired it. That doesn't tell me who sent you."
"Would opening the door make that conversation any easier?"
"Not until you tell me what belongs beneath the clock."
"Bring the label as well. We should read it together."''',
[words(70,120),{'type':'line_count','min':8,'max':8}],['Every line consists only of speech.','Selma seeks identification while the customer presses for access.','Does not explain the unstated motive or establish the customer\'s identity.'], 'Targets dialogue-only output and subtext without an explanatory tag.')
add('print','dialogue','Write exactly eight lines of dialogue between Jonah and his sister, 70–120 words total. Use only quoted speech: no speaker labels, action, narration or explanation. Let their immediate aims differ and leave a motive unstated. Preserve all numbers and the original promise.',
'''"Thirty-nine. I promised forty before the concert, and the printer has stopped."
"I still have the last blue sheet. Tell me when you want it."
"Not yet. I won't feed it into a machine I haven't checked."
"Then let me take these copies over while you look."
"You could stay and help me count them again."
"You've counted twice. I can carry thirty-nine without losing one."
"Will you wait at the entrance until I bring the last?"
"I'll leave them there for you. Someone will have to collect them."''',
[words(70,120),{'type':'line_count','min':8,'max':8}],['Every line consists only of speech.','The shortfall remains one programme; the held sheet is not silently consumed.','Different aims emerge without explaining the sister\'s private motive.'], 'Teaches constrained speech without narration or invented canon.')
add('clock','pacing','Rewrite the supplied beat twice, labelled Fast: and Slow:, using 90–150 words total. Change rhythm and emphasis while preserving every event, fact and their sequence. Add no dialogue, action, identities, motives or explanation of the key.',
'''Fast: Closing time. Selma found a brass key beneath the clock. She had repaired that clock. Then the collection label: her estranged aunt's name. Her aunt had died that spring. Outside, a customer waited. The shop was locked.

Slow: At closing time, Selma found a brass key beneath the clock she had repaired. The collection label bore the name of her estranged aunt. It was her aunt's name on a label for collection, though her aunt had died that spring. A customer was waiting outside. Between the customer and the inside of the shop was a locked door.''',
[words(90,150),{'type':'contains','value':'Fast:'},{'type':'contains','value':'Slow:'}],['Both versions preserve discovery, label, death timing and the waiting customer.','Neither version unlocks the door or explains the key.','Pace differs through rhythm and attention rather than additional events.'], 'Separates pacing changes from plot invention.')
add('print','pacing','Rewrite the supplied beat twice, labelled Fast: and Slow:, using 90–150 words total. Preserve all facts and their sequence. Change rhythm and emphasis without fixing the printer, using the sheet, starting the concert or adding dialogue.',
'''Fast: Forty programmes. Jonah had promised them before the concert began. The printer stopped at thirty-nine. One short. Beside it stood his younger sister, holding the last sheet of blue paper.

Slow: Jonah had promised to deliver forty programmes before the concert began. The printer had produced thirty-nine copies when it stopped. Thirty-nine against the forty he had promised: one copy still missing from the delivery. Beside the printer, his younger sister held a sheet of blue paper. It was the last sheet, still in her hands beside the machine that had stopped.''',
[words(90,150),{'type':'contains','value':'Fast:'},{'type':'contains','value':'Slow:'}],['Preserves forty promised, thirty-nine printed and the held last sheet.','Does not resolve the malfunction or move beyond the supplied moment.','Controls pace through sentence length and emphasis.'], 'Teaches an event-preserving pacing contrast.')
add('clock','storytelling','Propose two alternative next-scene plans in 120–180 words total. Begin with established facts. For each proposal, identify a choice, an immediate cost or consequence, and a later payoff caused by that choice. Label every added event or motive as a proposal; keep the plans separate.',
'''Established: Selma found a key under a repaired clock. Its label names her estranged aunt, who died that spring. A customer waits outside the locked shop.

Proposal A — Verification. Choice: Selma speaks through the door and asks for a collection receipt before opening. Proposed consequence: the customer leaves to fetch it, delaying the handover and risking the sale. Proposed later payoff: the receipt names a storage address; because Selma insisted on documentation, she now has a lead she would otherwise have missed.

Proposal B — Disclosure. Choice: Selma opens the door but tells the customer about the key before handing over the clock. Proposed consequence: the customer asks to postpone collection until its ownership is clarified. Proposed later payoff: that joint delay lets them compare records and discover conflicting instructions. Her disclosure creates the opportunity; the key's purpose remains unresolved.''',
[words(120,180)],['Clearly separates established facts and two alternative inventions.','Each later development depends on the specified choice.','Does not solve the mystery by assertion.'], 'Targets explicit causal links and consistent positions.')
add('print','storytelling','Propose two alternative next-scene plans in 120–180 words total. Begin with established facts. Give each proposal a choice, a consequence and a later payoff caused by that choice. Label inventions as proposals. Do not claim that delivering thirty-nine fulfils a promise of forty.',
'''Established: Jonah promised forty programmes before the concert. The printer stopped at thirty-nine; his younger sister holds the last blue sheet.

Proposal A — Ask for help. Choice: Jonah sends his sister to ask the organiser about another printer while he checks this one. Proposed consequence: he must admit the shortfall before the deadline. Proposed later payoff: the organiser finds a working machine, and his sister brings back directions. Asking early makes a fortieth copy possible; it does not guarantee one.

Proposal B — Deliver with disclosure. Choice: Jonah takes thirty-nine programmes and tells the organiser that one is missing. Proposed consequence: the organiser must arrange sharing, and Jonah has not fulfilled his promise. Proposed later payoff: after the concert, that recorded shortfall leads them to agree a spare-copy allowance for the next event. Honest reporting enables a better plan rather than magically producing the missing copy.''',
[words(120,180)],['Maintains the numerical shortfall and acknowledges incomplete delivery.','Proposed inventions stay distinct from source facts.','Payoffs arise from communication and its consequences.'], 'Teaches useful consequences without declaring an impossible success.')
add('clock','fiction','Continue in 100–150 words, third-person past tense. Advance one immediate decision without resolving the mystery. Preserve the repaired clock, the key, the aunt\'s death and estrangement, and the customer outside a locked shop. Output prose only.',
'''Selma laid the key beside the clock, where she could see both. She had intended to switch off the bench light; instead she turned its shade towards the collection label. The name did not change.

Beyond the glass, the customer lifted a hand. Selma had no reason yet to connect that person with her aunt beyond the label, and the label was enough to make her pause.

She left the door locked and went to it without the clock.

"Have you brought the collection receipt?"

The customer lowered the raised hand and reached into a coat pocket. Selma watched the movement. She would ask for the paper first; whatever she did with the key could wait.''',
[words(100,150)],['Preserves supplied facts, viewpoint and tense.','Advances a choice to seek documentation without identifying the customer.','Ends with a local turn rather than solving the whole mystery.'], 'Practises a restrained continuation with one consequential decision.')
add('print','fiction','Continue in 100–150 words, third-person past tense. Advance one immediate decision without resolving the whole difficulty. Preserve the promise of forty, thirty-nine printed copies, the stopped printer and his sister holding the last blue sheet. Output prose only.',
'''Jonah reached for the blue sheet, then stopped before his fingers touched it. His sister held it out a little farther.

"I need to see what's wrong first."

He set the thirty-nine programmes in a square pile. Counting them once more would not make another copy, and the neatness of the stack was beginning to feel like a way of postponing the telephone call.

He took out his phone and found the organiser's number. His sister lowered the sheet but kept it clear of the printer.

Jonah pressed Call. He would say thirty-nine at the beginning, before asking whether anyone had access to another machine. When the line connected, he kept his eyes on the pile.''',
[words(100,150)],['Keeps quantities, the stopped printer and the unused sheet consistent.','The new immediate choice is an honest request for help.','Does not fulfil the promise without an actual fortieth copy.'], 'Practises cause and effect without silently repairing the obstacle.')

def write_new(path,value,jsonl=False):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x') as f:
  if jsonl:
   for r in value:f.write(json.dumps(r,ensure_ascii=False)+'\n')
  else:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')

def main():
 # Refuse to overwrite prior review material.
 assert not OUT.exists(), 'Review pack already exists; preserve reviewed bytes'
 OUT.mkdir(parents=True)
 review=dict(status='pending',reviewer=None,reviewed_on=None,notes='AI-authored draft. No human approval, contractual clearance or training authorization.')
 ledger=next(r for r in read_jsonl(ROOT/'rights/ledger.jsonl') if r['id']=='original-seed-pending')
 ledger=copy.deepcopy(ledger)
 ledger.update(id='original-remediation-v1-pending',work_id='original-remediation-v1',title='Original synthetic clock-shop and concert-printing remediation scenes',author_ids=['codex-remediation-v1'],review=review)
 ledger['unresolved_issues']=['Applicable account/output-use terms and permission for the intended training use remain unreviewed.','Contexts and targets are AI-generated, not public-domain literature or human-authored examples.','Editorial acceptance and training release remain pending.']
 validate_schema(ledger,'rights-record')
 rows=[];results=[]
 for d in DRAFTS:
  context=CONTEXTS[d['scene']]
  if d['id']=='remediation-print-editing-01':context=context.replace('the thirty-ninth','the the thirty-ninth')
  messages=[dict(role='user',content='Context:\n'+context+'\n\nTask:\n'+d['instruction']),dict(role='assistant',content=d['target'])]
  row=dict(schema_version='1.0',id=d['id'],dataset_version='remediation-v1-pending',task=d['task'],split='train',split_group='original-remediation-'+d['scene'],origin='synthetic',messages=messages,source_work_ids=[ledger['work_id']],rights_record_ids=[ledger['id']],source_spans=[],teacher=dict(model='Codex',revision='conversation-authored-drafts-2026-10-19; exact serving revision unavailable',terms_url='https://openai.com/policies/terms-of-use/',training_permission='UNREVIEWED: establish the agreement applicable to this account and intended use before training.',review=review),review=review,rubric=d['rubric'],content_hash=digest(messages))
  validate_schema(row,'dataset-record')
  checks=[dict(check=c,passed=objective(c,d['target'],context)) for c in d['checks']]
  if d['task']=='dialogue':checks.append(dict(check='only quoted speech on each of exactly eight lines',passed=all(l.startswith('"') and l.endswith('"') and l.count('"')==2 for l in d['target'].splitlines())))
  results.append(dict(id=d['id'],words=len(re.findall(r"\b[\w]+(?:['’-][\w]+)*\b",d['target'])),checks=checks))
  rows.append(row)
 assert len(rows)==12 and all(c['passed'] for r in results for c in r['checks']),results
 # Check against every existing benchmark scenario, not just ferry/orchard.
 benchmark=read_jsonl(ROOT/'evaluation/tasks.draft.jsonl')
 check_leakage(rows,benchmark)
 assert not any(c==t['context'] for c in CONTEXTS.values() for t in benchmark)
 protected=[ROOT/'evaluation/tasks.draft.jsonl',ROOT/'evaluation/rubric.json',ROOT/'artifacts/clean-source-training-v1/fresh-context-v1/responses.jsonl',ROOT/'artifacts/clean-source-approved-v1/train.text.jsonl',ROOT/'artifacts/clean-source-training-v1/adapter/adapters.safetensors']
 pins={str(p.relative_to(ROOT)):file_hash(p) for p in protected}
 dataset=ROOT/'data/remediation-v1.pending.jsonl';lp=ROOT/'rights/remediation-v1.pending.jsonl'
 write_new(dataset,rows,True);write_new(lp,[ledger],True)
 try:validate_dataset(dataset,lp,['GB','US'],benchmark)
 except Invalid as exc:blocked=str(exc)
 else:raise AssertionError('Pending drafts must not pass training release')
 write_new(OUT/'validation.json',dict(schema_valid=True,records=12,task_counts={t:sum(r['task']==t for r in rows) for t in sorted({r['task'] for r in rows})},objective_checks=results,existing_leakage_checks_passed=True,benchmark_contexts_reused=False,source_and_teacher_reviews='pending',training_release_blocked=True,release_failure=blocked,dataset_sha256=file_hash(dataset),ledger_sha256=file_hash(lp),protected_inputs=pins,limitations=['Objective checks do not establish literary quality.','Two invented scenarios; not a balanced or training-ready dataset.','No web-wide originality search or contractual clearance performed.','No evaluation target has been copied into this training draft.']))
 with (OUT/'REVIEW.md').open('x') as f:
  f.write('# Remediation drafts — review before any training\n\n12 synthetic candidates, two per skill. New contexts; no benchmark targets or book excerpts reused. All human quality, source/output-use terms reviews and training release remain pending. No human votes have been recorded.\n\n')
  for d,row,result in zip(DRAFTS,rows,results):
   f.write(f"## {d['id']}\n\nPurpose: {d['why']}\n\n{row['messages'][0]['content']}\n\n### Draft target\n\n{d['target']}\n\nCriteria:\n\n")
   for criterion in d['rubric']:f.write('- '+criterion+'\n')
   f.write(f"\nMechanical check: passed; {result['words']} words. This is not editorial approval.\n\nHuman decision: keep / revise / reject: ____\nReason or replacement: ____\n\n")
 assert all(file_hash(ROOT/n)==h for n,h in pins.items())
 print(json.dumps(dict(records=12,mechanical_checks='passed',release='blocked as intended',dataset=str(dataset),review=str(OUT/'REVIEW.md')),indent=2))
if __name__=='__main__':main()
