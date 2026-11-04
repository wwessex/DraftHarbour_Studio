"""Freeze fresh evaluation cases and comparison rules before training."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import file_hash, read_jsonl

HERE = Path(__file__).resolve().parent
CASES = {
    'continuation': [
        ('floodgate', 'A floodgate lever has jammed. Remi can see a loose twig wedged in the external linkage. He has a hook and must stay on the walkway. Show one feasible action and an observable result. Leave the condition of the gate uncertain.',
         'The action uses the hook from the walkway and yields a visible result without declaring the gate sound.'),
        ('marionette', 'A marionette has stopped moving during a rehearsal. Sal can see two strings crossed above the wooden hand. A second performer is holding the puppet steady. Show Sal taking a practical step and observing an immediate effect. Leave the cause of the crossing unknown.',
         'Uncrossing or isolating the strings advances the rehearsal while the cause stays open.'),
        ('greenhouse', 'An overnight frost is forecast. Tess has a cracked greenhouse vent and one sheet of cloth. She can reach the lower frame but has no ladder. Show her doing something within reach and seeing what it accomplishes. Leave the overnight outcome uncertain.',
         'Action stays at reachable height and yields a limited observable effect.'),
        ('dispatch', 'A bicycle courier reaches a courtyard where the loading gate is locked. A porter is visible behind glass, and the courier can show the delivery slip. Show a complete attempt to make contact, followed by its immediate result. Leave delivery unresolved.',
         'A visible signal produces an observable response without assuming the package was delivered.'),
    ],
    'dialogue': [
        ('tailor', 'A tailor wants to keep a fitting on schedule. The customer needs one sleeve left unpinned so she can lift her arm. Let them agree on a concrete way to continue.',
         'Each speaker pursues a distinct aim and the agreement leaves one sleeve unpinned.'),
        ('school-radio', 'A pupil wants to announce a missing trumpet on the school radio. The presenter can spare one sentence between songs, and wants to avoid accusing anyone. Let the offer change and end with a usable agreement.',
         'The deal respects the one-sentence slot and implies no culprit.'),
        ('rowing', 'One rower wants to leave the dock now. The other wants to check a loose foot strap first. Both need the same pair of oars. Let their negotiation change what they do next without declaring the strap repaired.',
         'The decision follows from both aims and leaves the strap condition unresolved.'),
        ('costume', 'A director wants the stage cloak for tonight. The dresser can lend it only after a photograph and wants it returned dry. Let an apparent refusal turn into a specific conditional offer.',
         'A changed offer retains both lending conditions.'),
    ],
    'rewrite': [
        ('lift', 'Make the narrator sound impatient while preserving sequence and uncertainty. PARAGRAPH: I pressed the lift button. The light did not come on. I heard someone above me. I could not tell whether they had heard me. I pressed the button again.',
         'The rewrite changes cadence and implication while preserving the events and unknown response.'),
        ('harbour', 'Rewrite for a calmer rhythm, keeping the same viewpoint and facts. PARAGRAPH: I ran to the railing. The red launch was already past the harbour mouth. I could see a figure on the stern. I could not see their face. I put the ticket back in my pocket.',
         'Pacing changes without changing who can be identified, where the boat is, or what happens to the ticket.'),
        ('suitcase', 'Make regret implicit through rhythm and emphasis. PARAGRAPH: Dev shut the suitcase. A glove lay on the dresser. He picked it up, then put it back. He heard the car outside. He did not know if Mina was in it.',
         'Regret arises from existing actions and Dev still cannot identify the passenger.'),
        ('trolley', 'Make the paragraph more urgent while preserving chronology and who saw what. PARAGRAPH: Lin noticed the empty trolley first. I turned when she spoke. A door was closing at the end of the passage. Neither of us saw who pushed it.',
         'Urgency increases while observations and uncertainty stay assigned to the right people.'),
    ],
    'scene': [
        ('fiddle', 'A violinist has loaned her only spare bow to a beginner. A second player arrives needing one before the concert. Keep the violinist’s viewpoint. End at a concrete unresolved choice.',
         'Both competing needs emerge through behavior and the spare remains accounted for.'),
        ('drawbridge', 'A bridge attendant sees a cyclist on the span as a boat signals below. The attendant has a public-address microphone and cannot see the cyclist’s face. Use the attendant’s viewpoint. End just after one feasible intervention.',
         'Uses a feasible signal and keeps the cyclist’s identity and eventual outcome open.'),
        ('darkroom', 'A photographer realizes a print with a private note is on the drying rack just as a visitor enters. The visitor wants to see the exhibition. The photographer wants to delay without explaining why. Use the photographer’s viewpoint and end with the choice unresolved.',
         'The privacy concern is dramatized through behavior and the note remains undisclosed.'),
        ('postbag', 'A village clerk has one delivery bag left. A neighbour needs medicine delivered and a teacher needs exam papers collected. The two stops are in opposite directions. Show the clerk’s conflicting obligations through action and end with a specific decision still open.',
         'The one-bag constraint and opposing routes remain clear.'),
    ],
    'pacing': [
        ('sail', 'A crew member coils a rope slowly until a sudden gust loosens the sail. Accelerate in paragraph two through a feasible response. Leave the extent of damage unknown.',
         'Tempo shifts into observable action while damage stays unknown.'),
        ('ball', 'Two children hurry through a corridor to retrieve a ball. Slow the second paragraph when they hear someone crying behind a door, while keeping them moving toward a choice.',
         'The pause changes the rhythm and leads toward an action.'),
        ('projection', 'An usher quietly counts empty seats until the projector stops. Accelerate the second paragraph through a response using the usher’s torch and voice. Leave the cause unknown.',
         'The response uses available resources and does not diagnose the projector.'),
        ('soup', 'A kitchen runner hurries with two bowls until one starts slipping. Slow the second paragraph through perception and a concrete effort to steady it. Leave the outcome open.',
         'Slower perception accompanies an action while the outcome remains open.'),
    ],
    'analysis': [
        ('calendar', 'PASSAGE: Jan took down the calendar before the visitors came. When one asked about Thursday, she said the room was free. After they left she put the calendar back, face to the wall.',
         'Quotes two actual details and treats the reason for hiding the calendar as an inference.'),
        ('umbrella', 'PASSAGE: Peter handed me the umbrella without looking up. I knew it was mine because the handle was cracked. He said he had found it at the gate. The clasp was still warm.',
         'Distinguishes the narrator’s evidence from Peter’s claim and avoids asserting where it was found.'),
        ('flowers', 'PASSAGE: A vase stood beside the unused place setting. Ruth moved it to the sill when her uncle arrived. He counted the plates, then asked only for water.',
         'Links behavior to tension or omission while leaving the reason for the place setting uncertain.'),
        ('whistle', 'PASSAGE: The foreman whistled twice. Len carried his lunch tin down the stairs, then brought it back unopened. At the second whistle, he set it beside the foreman’s coat.',
         'Quotes two details and preserves uncertainty about the whistle and Len’s motive.'),
    ],
}
INSTRUCTIONS = {
    'continuation': 'Continue in one paragraph of 70–110 words. ',
    'dialogue': 'Write four to six labelled dialogue turns, at most 115 words. Return only dialogue. ',
    'rewrite': 'Return only revised prose. ',
    'scene': 'Write a scene of 100–150 words. ',
    'pacing': 'Write two paragraphs of at most 130 words total. ',
    'analysis': 'In at most 100 words, quote two short details and explain their effect. Distinguish observation from inference. ',
}
CONSTRAINTS = {
    'continuation': dict(min_words=70, max_words=110, paragraphs=1),
    'dialogue': dict(max_words=115, min_turns=4, max_turns=6),
    'rewrite': dict(changed=True),
    'scene': dict(min_words=100, max_words=150),
    'pacing': dict(max_words=130, paragraphs=2),
    'analysis': dict(max_words=100, exact_quotes=2),
}


def main():
    rows = [dict(id=f'v36-{name}', skill=skill, prompt=INSTRUCTIONS[skill] + brief,
                 quality_focus=focus, constraints=CONSTRAINTS[skill], training_eligible=False)
            for skill, cases in CASES.items() for name, brief, focus in cases]
    existing = read_jsonl(ROOT / 'curation/curriculum-reset-v30/fresh-screen.jsonl')
    legacy = read_jsonl(ROOT / 'artifacts/source-training-v29/cases.frozen.jsonl')
    training = read_jsonl(ROOT / 'artifacts/practical-scenes-v34/records.review-only.jsonl')
    earlier = {r['prompt'] for r in existing + legacy}
    earlier.update(r['messages'][0]['content'] for r in training)
    assert len(rows) == len({r['id'] for r in rows}) == len({r['prompt'] for r in rows}) == 24
    assert all(len(cases) == 4 for cases in CASES.values())
    assert not {r['prompt'] for r in rows} & earlier
    output = HERE / 'holdout.jsonl'
    with output.open('x') as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + '\n')
    protocol = dict(status='frozen-unrun', cases=24, skills=list(CASES), seeds=[42, 43, 44],
                    temperature=0.7, max_new_tokens=384, fresh_context=True,
                    conditions=['current-craft', 'candidate'], planned_responses=144,
                    source_match_threshold_words=12, training_eligible=False,
                    holdout_sha256=file_hash(output), preparation_sha256=file_hash(Path(__file__)))
    with (HERE / 'holdout.lock.json').open('x') as stream:
        json.dump(protocol, stream, indent=2)
        stream.write('\n')


if __name__ == '__main__':
    main()
