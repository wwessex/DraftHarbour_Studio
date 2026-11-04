"""Task-matched source-only pilot. Fresh instructions, never generated literary answers."""
from pathlib import Path
import copy, hashlib, json, re, sys
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import validate_dataset, digest
OUT = ROOT/'artifacts/task-matched-v3'
LEDGER = ROOT/'rights/literary-mix-v2.scoped.jsonl'
BRIEFS = [
 'Write a first-person retrospective opening for a period science-fiction scene. An animated inventor explains a paradox to relaxed dinner guests. Establish the luxurious room through firelight, glasses and his patented chairs, ending on the listeners watching his earnest gestures.',
 'Write a single spoken explanation by an inventor who has studied four-dimensional geometry. Use portraits of the same man at eight, fifteen, seventeen and twenty-three to explain how three-dimensional appearances are sections of a four-dimensional being.',
 'Write a period science-fiction demonstration: the Time Traveller introduces his model machine, explains its strange appearance, points to a twinkling bar and identifies two small levers. Include speech and brief physical actions.',
 'Write the Time Traveller defending his model after two years of work. Explain its two directions and saddle, announce the impending demonstration and invite witnesses to inspect the table to rule out a trick. Keep the defensive edge in his speech.',
 'Write a first-person eyewitness account of a model time machine disappearing. Delay the action briefly, have the inventor borrow the Psychologist’s finger to move the lever, then describe wind, disturbed flames and the model fading until the table is bare.',
 'Write a first-person period scene after an unsettling demonstration. While the Time Traveller lights his pipe and announces a larger machine and his intended journey, the Psychologist betrays his nerves by trying to light an uncut cigar.',
 'Write a period science-fiction explanation by the Psychologist: a machine moving rapidly through time could be hard to perceive, like a spinning spoke or flying bullet. Use ratios of time and finish with his hand passing through the empty space.',
 'Write a first-person period scene as dinner guests follow the Time Traveller through a draughty corridor to his laboratory. Use flickering lamplight and puzzled disbelief, then describe the larger machine and unfinished crystalline bars.',
 'Write Watson’s surprised reply to Holmes after a deduction. Confirm a muddy Thursday country walk despite changed clothes, and explain that Watson’s wife has given Mary Jane notice. Show his astonishment through speech rather than an explanation of Holmes’s method.',
 'Write Watson’s first-person response after Holmes explains a deduction. He laughs, admits that each solution seems simple after explanation, yet confesses he is baffled beforehand and thinks his eyesight is just as good.',
 'Write the text of a formal mysterious appointment note in a period detective story. Promise a visitor at quarter to eight tonight, invoke discretion and service to European royalty, include an unusual construction about reports received, and warn that the visitor may wear a mask.',
 'Write dialogue in a historical detective scene in which Holmes claims the note’s syntax and Bohemian paper point to a German writer. Present this as the fictional character’s confident deduction, ending with the presumed visitor arriving; do not add explanatory commentary.',
 'Write a brief period detective scene: a broad-shouldered count requires both listeners to keep absolute secrecy for two years, explaining that the matter could influence European history. Leave the substance undisclosed.',
 'Write Watson’s first-person narration as Holmes, eyes closed, asks him to consult an index about a woman. Explain Holmes’s habit of cataloguing people and subjects, and place her entry between a rabbi and a writer on deep-sea fishes.',
 'Write Holmes reading a woman’s biographical index entry in clipped speech: New Jersey, 1858, contralto, La Scala, Warsaw, retirement and London. Then have him put the compromising-letter problem directly to His Majesty.',
 'Write an anxious royal client’s speech in a period detective story. He fears a determined woman will send a photograph if he marries another woman. Contrast her beauty with her resolve and finish on his insistence that she will stop at nothing.',
]
DIALOGUE = {
 82596:'Write a brief, emotional exchange between Agnes and Fanny in period social fiction. Agnes fears she has lost an old friend; Fanny insists on her own affection and practical help, growing distressed at the thought of Agnes in want. Mix short interruptions with Fanny’s longer reassurance.',
 83641:'Write a brief period scene as Agnes uncovers the child concealed in her lap. Fanny hesitantly begins a question, Agnes answers that he is her child, and Fanny’s restrained affection for the mother finds expression in her caresses of the boy. Include only two spoken turns.',
 114302:'Write a short period scene during Agnes’s breakfast. Wedding bells prompt her question to Fanny, who hesitates, identifies Caroline Seymour’s wedding, and vents her irritation about the fuss. Keep the speech embedded in narration.',
 73966:'Write a short scene of period social fiction in which Agnes silently offers a cottager money, he refuses it, and they negotiate whether he should escort her to town. Use one direct refusal followed by narrated disagreement and a practical compromise.',
 41435:'Write a period theatre-lobby encounter: Agnes urgently questions a tradesman about her father. Let her interruptions outrun his answers and her anguish override shame. End when she interprets his unfinished reply as hope of forgiveness and blesses him.',
 85355:'Write a three-turn exchange between Agnes and Fanny in period social fiction. Agnes believes her disgrace makes accepting hospitality a presumption; Fanny protests warmly; Agnes explains that friendship may help her endure duty and sorrow. Preserve the era’s moral vocabulary as character speech.',
}
ANALYSIS = {
 'wharton-writing-craft-017':'Explain Edith Wharton’s account of a viewpoint character as a reflector: what limits must the narrator respect, and how should the writer inhabit the chosen consciousness?',
 'wharton-writing-craft-025':'Explain Edith Wharton’s argument for reserving dialogue for culminating moments, including her wave-and-spray comparison and its effect on the passage of narrative time.',
 'wharton-writing-craft-026':'Explain Edith Wharton’s criticism of using conversation to carry too much exposition, including why characters telling one another known information produces improbable and diluted dialogue.',
 'wharton-writing-craft-027':'Explain Edith Wharton’s distinction between a typical short story and a novel, addressing temporal development, supporting characters and her sailing analogy.',
 'wharton-writing-craft-031':'Explain when Edith Wharton considers a shift to another reflecting consciousness necessary, with attention to what a viewpoint character can know or react to.',
 'hamilton-manual-craft-026':'Explain Clayton Hamilton’s view that narrative represents events through the union of character, action and setting rather than any one element alone.',
 'hamilton-manual-craft-045':'Explain Clayton Hamilton’s reasons for choosing an admiring minor character as narrator of an extraordinary protagonist, using his examples of Dupin and Sherlock Holmes.',
 'hamilton-manual-craft-055':'Explain Clayton Hamilton’s locked-door example contrasting absolute and limited omniscience, including how an established viewpoint constrains which room can be represented.',
 'hamilton-manual-craft-064':'Explain Clayton Hamilton’s exceptional use of inverse proportion for ironic emphasis: extended subsidiary detail followed by a sudden important sentence.',
 'hamilton-manual-craft-075':'Explain Clayton Hamilton’s account of a short story’s opening: its intellectual signal about action, character or setting and its emotional signal about tone, with his reference to Poe.',
}

def write_rows(path, rows):
 with path.open('x') as f:
  for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
def main():
 OUT.mkdir(exist_ok=False)
 prior=validate_dataset(ROOT/'artifacts/literary-mix-v2/records.jsonl', LEDGER, ['GB','US'])
 byid={r['id']:r for r in prior};records=[];trace=[];used=set()
 def add(original, kind, task, prompt, answer, derivation):
  source=original['source_spans'][0];key=(source['rights_record_id'],source['start'],source['end']);assert key not in used;used.add(key)
  row=copy.deepcopy(original);row.pop('_author_ids',None);row.update(id=f'v3-{len(records):03d}-{kind}',dataset_version='task-matched-v3',task=task,split='train',teacher=None,origin='derived')
  row['messages']=[dict(role='user',content=prompt),dict(role='assistant',content=answer)]
  row['review']=dict(status='approved',reviewer='Codex AI: source and instruction alignment audit',reviewed_on='2026-10-25',notes='AI audit, not human quality approval. Literary text is unchanged cleared source prose/subspan. Instructions are constructed after reading the source, not historically commissioned briefs. JSON copyedit wrappers are structural labels with source-derived replacement text; no generated literary teaching answer.')
  row['content_hash']=digest(row['messages']);records.append(row)
  trace.append(dict(id=row['id'],kind=kind,prior_record_id=original['id'],source_key=list(key),source_answer_reused_from_v2=True,derivation=derivation))
 for i,brief in enumerate(BRIEFS):
  old=byid[f'v2-new-{i:03d}-write'];target=old['messages'][1]['content']
  add(old,'directed-write','fiction',brief+' Return only the passage, without a heading or explanation.',target,dict(type='unchanged source paragraph',text_sha256=hashlib.sha256(target.encode()).hexdigest()))
 opie=[r for r in prior if r['split']=='train' and r['rights_record_ids']==['opie-father-daughter-pg49621'] and r['task']=='fiction' and 'directed-opie' in r['id']]
 for start,prompt in DIALOGUE.items():
  old=next(r for r in opie if r['source_spans'][0]['start']==start);target=old['messages'][1]['content'];add(old,'dialogue-scene','dialogue',prompt+' Return only story prose, without commentary.',target,dict(type='unchanged source paragraph including dialogue and narration'))
 selected=[r for r in opie if (r['source_spans'][0]['rights_record_id'],r['source_spans'][0]['start'],r['source_spans'][0]['end']) not in used]
 # Four already cleared scenes: brief pacing instructions tied to the actual source event.
 pacing=[(51232,'Slow the moment as Agnes crosses a desolate wintry landscape with her child. Let her longing for a human voice turn to fear and guilty recollection, then end with her hurrying onward.'),(47214,'Move a period scene from relief to practical urgency: Agnes reaches Green Park, hears the late hour, remembers a midnight coach and secures a place just as it leaves.'),(187330,'End a period scene with sudden acceleration: a boy attracts Lady Mountcarrol’s attention, runs to inspect a fine carriage, is lifted inside by the lord and driven away before the mourners can react.'),(139314,'Write a reflective period paragraph about Agnes helping the sick despite her poverty. Slow the narrative to focus on sympathy, medicine, cleanliness and the consolations she can still offer.')]
 for start,brief in pacing:
  old=next(r for r in opie if r['source_spans'][0]['start']==start);target=old['messages'][1]['content'];add(old,'paced-scene','pacing',brief+' Use period social-fiction narration. Return only the passage.',target,dict(type='unchanged source paragraph; pacing-directed generation, not an author revision'))
 selected=[r for r in selected if (r['source_spans'][0]['rights_record_id'],r['source_spans'][0]['start'],r['source_spans'][0]['end']) not in used]
 # Complete first sentence is supplied; the remaining source text is the answer.
 continuing=[]
 for old in selected:
  text=old['messages'][1]['content'];m=re.search(r'[.!?](?:[\"”])?\s+',text)
  if m and 25<=len(text[m.end():].split())<=130 and len(text[:m.end()].split())>=8:continuing.append((old,m.end()))
 assert len(continuing)>=6
 for old,cut in continuing[:6]:
  text=old['messages'][1]['content'];answer=text[cut:];add(old,'continue','fiction','Continue directly after this period social-fiction passage, preserving narrator and tense. Return only the new prose; do not repeat the supplied text or explain.\n\nPASSAGE:\n'+text[:cut].rstrip(),answer,dict(type='exact source suffix',start_in_prior_answer=cut,end_in_prior_answer=len(text)))
 selected=[r for r in selected if (r['source_spans'][0]['rights_record_id'],r['source_spans'][0]['start'],r['source_spans'][0]['end']) not in used]
 for i,old in enumerate(selected[:8]):
  text=old['messages'][1]['content'];word=next(m for m in re.finditer(r'\b[a-zA-Z]{5,}\b',text) if text.count(m.group())==1);token=word.group()
  if i<6:broken=text[:word.start()]+token+' '+text[word.start():];edits=[dict(before=token+' '+token,after=token)]
  else:broken=text;edits=[]
  answer=json.dumps(dict(edits=edits),ensure_ascii=False,separators=(',',':'))
  add(old,'anchored-copyedit','editing','Copyedit only TARGET PASSAGE. Remove accidental consecutive duplicated words and preserve all other characters. Return JSON only: {"edits":[{"before":"exact unique original span","after":"corrected span"}]}. Each before must occur exactly once in the original target; edits must not overlap. Return {"edits":[]} when unchanged. No markdown or commentary.\n\nTARGET PASSAGE:\n'+broken,answer,dict(type='mechanical corruption and structural JSON labels',original_paragraph_sha256=hashlib.sha256(text.encode()).hexdigest(),corrected_paragraph=text,source_replacement=token if edits else None))
 for suffix,question in ANALYSIS.items():
  old=byid['v2-mix-'+suffix];target=old['messages'][1]['content'];add(old,'attributed-craft','analysis',question+' Give the historical author’s explanation only; no heading or invented quotation.',target,dict(type='unchanged attributed historical craft explanation; not a new analysis of unseen fiction'))
 assert len(records)==50 and len(used)==50
 validation=[copy.deepcopy(r) for r in prior if r['split']=='validation']
 for row in validation:
  row.pop('_author_ids',None);row['dataset_version']='task-matched-v3';row['id']='v3-val-'+row['id']
 write_rows(OUT/'records.jsonl',records+validation);write_rows(OUT/'trace.jsonl',trace)
 valid=validate_dataset(OUT/'records.jsonl',LEDGER,['GB','US'])
 from collections import Counter
 report=dict(passed=True,train_records=50,unique_training_source_spans=50,validation_records=len(validation),categories=dict(Counter(r['kind'] for r in trace)),generated_literary_targets=0,new_independent_source_spans=0,human_quality_ratings=0,limitations=['All 50 source spans occurred in the prior v2 training corpus; new task framing is not new independent literary data.','Six dialogue records include brief exchanges and narrated negotiation, not six uniformly long multi-turn scenes.','Craft answers are historical explanation, not grounded analysis of newly supplied fiction.','Pacing examples are source-authored scenes matched to briefs, not before/after author revisions.','No modern-register corpus, broad genre coverage or Muse-equivalence evidence.','Dickens structural revision remains separate and is not added to this bounded pilot.'])
 (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
 with (OUT/'REVIEW.md').open('x') as f:
  f.write('# Task-matched v3 — source-only AI alignment review\n\n'+json.dumps(report,indent=2)+'\n\n')
  for row in records:f.write('## '+row['id']+'\n\n'+row['messages'][0]['content']+'\n\n**SOURCE-DERIVED ANSWER**\n\n'+row['messages'][1]['content']+'\n\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
