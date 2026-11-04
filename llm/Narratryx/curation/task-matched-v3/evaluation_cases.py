"""New evaluation-only fiction: eight scenarios, six skills; never training answers."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'artifacts/task-matched-v3'
SCENARIOS=[
 ('seed-bank','Mina and Joel','Mina kept the borrowed key flat beneath her palm. Across the seed-bank counter, Joel counted the empty return envelopes twice. The cold-room alarm had stopped, but its red lamp remained lit. Mina had promised to return the key before the inspection. She had not promised to explain why she needed it. Joel reached for the inspection clipboard, then waited.', ['The key is borrowed and still under Mina’s palm.','The alarm is silent but its red lamp remains lit.','Mina has promised to return the key before inspection.','The reason she needed it is not established.']),
 ('observatory','Iris and Dev','Iris watched Dev fold the telescope cover along its old creases. Tonight’s public viewing had been cancelled because of cloud, not equipment failure. Three children still waited beside the locked gate. Dev had the cancellation notice in his pocket; Iris had been asked to speak to the parents. Neither had yet approached the gate.', ['Cloud caused the cancellation, not equipment failure.','Three children wait by a locked gate.','Dev has the notice; Iris must speak to the parents.','Neither has approached the gate.']),
 ('bakery','Celia and Tom','I set the empty cake box on the flour-dusted bench. Tom read the collection time on the order slip without looking at me. The cake was still in the refrigerator; the missing part was the name in chocolate. Outside, a bicycle bell rang twice. I knew whose order it was. Tom knew only that the customer was early.', ['The first-person narrator is Celia.','The cake is refrigerated, not missing.','The chocolate name has not been added.','Celia recognises the customer; Tom knows only that they are early.']),
 ('tram-depot','Anik and Bea','Anik held the damaged route map against the depot window. Bea had brought a replacement, but it showed last winter’s timetable. The first tram would not leave for another ten minutes. Rain ticked against the glass. Bea pointed to the torn corner, where someone had written a stop name in blue ink. Anik did not recognise the handwriting.', ['The replacement has last winter’s timetable.','The first tram departs in ten minutes, not immediately.','A stop name is written in blue ink on the damaged map.','Anik does not recognise the handwriting.']),
 ('costume-room','Ada and Leon','Ada eased the borrowed jacket off the dressmaker’s dummy. One sleeve had been shortened, and the loose thread caught on her ring. Leon stood by the return ledger with his pen uncapped. The performance had ended an hour ago. Ada had permission to borrow the jacket, but nobody had authorised the alteration. She freed the thread and turned the sleeve inside out.', ['Borrowing was permitted; alteration was not authorised.','One sleeve has been shortened.','The performance has already ended.','The sleeve is turned inside out at the ending.']),
 ('map-room','Rosa and Em','I kept the tracing paper between my hand and the map. Em slid a clean weight towards me without speaking. The donor would arrive at noon, and the pencilled correction still lacked a date. We knew who had drawn the map. We did not know who had changed the river’s course. The clock struck eleven while I compared the two lines.', ['The first-person narrator is Rosa.','The donor arrives at noon; the clock now strikes eleven.','The map’s creator is known, but the person who made the correction is not.','The correction’s date is unknown.']),
 ('laundry','Nell and Arun','Nell lifted the blue coat from the dry-cleaning rail. Inside its lining was an unopened envelope bearing the shop’s old address. Arun had found the coat in an unclaimed order from March. No customer had called about it. Nell knew the handwriting on the envelope, but she had not said whose it was. Arun moved the return receipt closer to the lamp.', ['The envelope is unopened.','The coat came from an unclaimed March order.','No customer has called about it.','Nell recognises the handwriting; Arun has not been told whose it is.']),
 ('aquarium','Faye and Otis','Faye lowered the inspection lamp behind the empty display tank. Otis held the repair order, still unsigned. The fish had been moved safely to another tank that morning; the public notice simply said the display was closed. A fine line of moisture shone along the lower seal. Faye switched off the lamp before Otis could read her expression.', ['The display tank is empty, but the fish are safe elsewhere.','The repair order is unsigned.','Moisture is visible along the lower seal.','Otis cannot infer Faye’s private thoughts as fact.']),
]
KINDS=['write','editing','analysis','continue','dialogue','pacing']
def build():
 cases=[]
 for i,(ident,speakers,context,facts) in enumerate(SCENARIOS):
  for kind in KINDS[:3] if i%2==0 else KINDS[3:]:
   text=context;reference=None;minimum=0;maximum=None
   if kind=='editing':
    words=list(__import__('re').finditer(r'\b[A-Za-z]{5,}\b',context));word=words[1];text=context[:word.start()]+word.group()+' '+context[word.start():];reference=context
    instruction='Remove only the accidentally duplicated consecutive word. Preserve every other character, punctuation mark, viewpoint and fact. Return only the corrected passage.'
   elif kind=='write':
    instruction='Write a new short scene from the situation below in 60–90 words. Use its narrator, tense, setting and established facts. Give the central character an immediate practical choice without resolving the main uncertainty. Return only story prose.';minimum=60;maximum=90
   elif kind=='analysis':
    instruction='In at most 70 words, analyse viewpoint, immediate conflict and pacing. Ground your account in two concrete details from the passage. Distinguish inference from established fact. Do not invent relationships or unseen outcomes.';maximum=70
   elif kind=='continue':
    instruction='Continue immediately after this ending in 60–90 words. Preserve narrator, tense, known facts and limits on knowledge. Show a small next development without recapping or presenting unknown history as fact. Return only new story prose.';minimum=60;maximum=90
   elif kind=='dialogue':
    instruction=f'Write the next brief exchange between {speakers} in at most 100 words, with 4–6 spoken turns. Let competing immediate wants show through subtext. Retain viewpoint, tense and established facts; new actions and spoken revelations are allowed. Return only the scene.';maximum=100
   else:
    instruction='Rewrite this passage with shorter sentences and a faster rhythm, in at most 85 words. Preserve the narrator, tense, important facts, negative statements, unresolved questions and order of events. Do not complete an action that has not happened. Return only revised prose.';maximum=85
   cases.append(dict(id=ident+'-'+kind,scenario_id='v3-'+ident,kind=kind,task='editing' if kind in ['editing','pacing'] else 'fiction' if kind in ['write','continue'] else kind,context=text,prompt=instruction+'\n\nPASSAGE:\n'+text,word_count_min=minimum,word_count_max=maximum,exact_reference=reference,established_facts=facts,provenance='Original Codex AI-authored evaluation-only fiction, not literary training targets. AI structural review; no human approval or literary ratings.',context_sha256=hashlib.sha256(context.encode()).hexdigest()))
 assert len(cases)==24 and len({c['scenario_id'] for c in cases})==8
 assert all(c['word_count_min']==0 for c in cases if c['task']=='editing')
 with (OUT/'test.cases.jsonl').open('x') as f:
  for case in cases:f.write(json.dumps(case,ensure_ascii=False)+'\n')
 print('Frozen input candidate: 24 evaluation-only cases across eight new scenarios; no training targets generated.')
if __name__=='__main__':build()
