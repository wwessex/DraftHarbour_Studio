"""Original AI-authored evaluation fixtures ONLY. Never training/teacher targets."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
P=ROOT/'artifacts/literary-mix-v2'

SCENARIOS=[
 ('museum-clock','Ada and Ravi',
  'Ada stood beside the museum clock while Ravi counted the chairs for the morning lecture. The clock had stopped at six, but the staff entrance display showed nine. The visitors were still outside; nobody had unlocked the front doors. Ada held the only door key on a blue cord. Ravi had an empty folder under his arm. “Five more minutes, please,” he said, still arranging the room. He asked about the missing speaker. Ada had received no message from her and did not know why she was late. A caretaker knocked from the corridor. Ada raised one finger to ask for silence, listening for a second knock. Ravi set the folder on a chair.',
  ['The front doors remain locked and visitors are outside.','Ada holds the only door key.','The museum clock is stopped at six; the entrance display reads nine.','The speaker’s reason for being late is unknown.']),
 ('tram-platform','Imani and Leon',
  'Imani watches the empty tracks from the covered tram platform. The tram has not arrived. Leon waits beside her with a dented instrument case, tapping its handle with one finger. It is the first time he has taken this route, and he asks again, “Is this our side?” She points again to the small sign above the shelter. A paper timetable lies between them on the bench; neither of them can read the rain-blurred departure time. Imani has promised to meet a friend at noon, but she has not told Leon about the appointment. He lifts the case when a distant motor starts, then lowers it when a delivery van passes.',
  ['The tram has not arrived; nobody has boarded it.','Leon is carrying an instrument case.','The timetable’s departure time is unreadable.','Leon has not been told about Imani’s noon appointment.']),
 ('orbital-greenhouse','Sera and Noa',
  'Sera checked the orbital greenhouse door for the third time. It was shut. No evacuation order had been given. Inside, Noa stood between two trays of seedlings with her gloves still sealed to her sleeves. She had found a thin crack in one tray and wanted Sera to call the maintenance team before the next watering cycle. “Call maintenance,” Noa said. Sera had brought a roll of repair tape, hoping to avoid another delay. Neither woman knew whether the crack reached the water line. Beyond the glass partition, the station lights shifted to their evening setting. Noa moved the unbroken tray away from the edge of the shelf. Sera set the tape down without opening it.',
  ['The greenhouse door is shut; no evacuation order exists.','Noa’s gloves are sealed to her sleeves.','The depth of the tray crack is unknown.','The tape has not been opened or applied.']),
 ('theatre-letter','Ruth and Ed',
  'Ruth lays the sealed envelope on the theatre desk. Neither she nor Ed has opened it. The evening performance has not begun; the stage lights are on for a rehearsal that is running late. Ed holds the revised cast list but keeps it folded when Ruth turns towards him. “Has my part changed?” she asks. He has been told to wait for the director before discussing the list, and he has not explained that instruction to her. Someone drags a chair across the stage above them. Ruth touches the envelope’s unbroken seal, then pulls her hand away. Ed starts to speak when footsteps sound in the corridor.',
  ['The letter remains sealed and unread by both characters.','The performance has not begun; rehearsal is late.','Ed has the revised cast list, which remains folded.','Ruth does not know Ed’s instruction to wait for the director.']),
]

def build():
    cases=[]
    for ident,speakers,context,facts in SCENARIOS:
        tokens=context.split();index=next(i for i,w in enumerate(tokens) if i>12 and w.isalpha() and len(w)>4)
        broken=tokens[:index]+[tokens[index]]+tokens[index:]
        tasks=[
         ('editing','editing','Remove only the consecutive duplicated word. Preserve every other character, quote, fact and punctuation mark. Return only the corrected passage.', ' '.join(broken),context,0,None),
         ('voice','editing','Rewrite this passage more concisely in at most 85 words. Retain the narrator, tense, voice, important facts, negative statements and order of events. Do not complete an event that has not happened. Return only revised prose.',context,None,0,85),
         ('dialogue','dialogue',f'Write a new scene immediately after this passage with 4–6 spoken turns between {speakers}, in at most 120 words. Preserve the narrator, tense and established facts. Let their different immediate wants emerge through subtext. Do not contradict established facts or present unknown past events as established background. Newly depicted actions and spoken revelations are allowed. Do not claim access to unspoken thoughts outside the viewpoint. Return only the scene.',context,None,0,120),
         ('analysis','analysis','In at most 70 words, analyse the passage’s viewpoint, immediate conflict and pacing. Ground each observation in the supplied passage. Distinguish inference from fact and do not invent relationships or later events.',context,None,0,70),
         ('continuity','fiction','Write a new continuation of 80–120 words. Preserve narrator, tense, established facts and limits on knowledge. Start immediately after the ending and show a small next development without recapping the passage. Return only new story prose.',context,None,80,120),
        ]
        for kind,task,instruction,text,reference,minimum,maximum in tasks:
            cases.append(dict(id=ident+'-'+kind,scenario_id=ident,kind=kind,task=task,context=text,prompt=instruction+'\n\nPASSAGE:\n'+text,word_count_min=minimum,word_count_max=maximum,exact_reference=reference,source_facts=facts,source_unknowns=['Other motives, relationships and later outcomes are not established.'],provenance=dict(context='Original Codex AI-authored diagnostic fiction, evaluation only; not public-domain literature or training material',instructions='Codex test design',review='AI structural review only, not human-approved formal benchmark'),context_sha256=hashlib.sha256(context.encode()).hexdigest()))
    assert len(cases)==20 and all(not c['word_count_min'] for c in cases if c['task']=='editing')
    with (P/'test.cases.jsonl').open('x') as f:
        for case in cases:f.write(json.dumps(case,ensure_ascii=False)+'\n')
    print('Twenty new AI-authored diagnostic cases created for evaluation only; formal benchmark unchanged.')
if __name__=='__main__':build()
