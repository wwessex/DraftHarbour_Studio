"""Record informed AI comparisons after inspecting outputs; no human ballots or training export."""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import read_jsonl,file_hash
RUN=ROOT/'artifacts/fiction-questions-v19'
NOTES=ROOT/'artifacts/fiction-questions-v19-review-notes.json'


def main():
    cases=read_jsonl(ROOT/'artifacts/fiction-questions-v19-plan/cases.frozen.jsonl')
    p=json.loads((RUN/'protocol.frozen.json').read_text())
    notes=json.loads(NOTES.read_text())
    expected={(side,c['parent_case_id']) for side in p['conditions'] for c in cases}
    assert len(notes)==18 and {(n['condition'],n['parent_case_id']) for n in notes}==expected
    rows=[];packet=['# Informed AI editorial review','','Conditions are visible and earlier failures are known. These are local comparisons, not independent, blinded or human quality ratings. Generated outputs and notes are ineligible for training.','']
    for n in notes:
        side=n['condition'];parent=n['parent_case_id']
        lookup={r['case_id']:r for r in read_jsonl(RUN/(side+'.responses.jsonl'))}
        pair={c['variant']:lookup[c['id']] for c in cases if c['parent_case_id']==parent}
        assert n['preference'] in ['original','clarified','tie','neither']
        for v in ['original','clarified']:
            assert n['evidence'][v] and all(q in pair[v]['text'] for q in n['evidence'][v]),(side,parent,v)
        for k in ['constraint_assessment','prose_assessment','progression_assessment']:
            assert n[k]
        row=dict(n,reviewer='Codex AI, informed',blinded=False,independent=False,human=False,training_eligible=False,
                 response_text_sha256={v:hashlib.sha256(pair[v]['text'].encode()).hexdigest() for v in pair}, response_file_sha256=file_hash(RUN/(side+'.responses.jsonl')))
        rows.append(row)
        packet+=['## '+side+' / '+parent,'',f"Local preference: **{n['preference']}**; not an acceptability rating.",'',n['constraint_assessment'],'',n['prose_assessment'],'',n['progression_assessment'],'']
    with (RUN/'ai-review.jsonl').open('x') as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    with (RUN/'AI-REVIEW.md').open('x') as f:f.write('\n'.join(packet))
    summary=dict(pairs_reviewed=18,local_preferences_by_condition={side:dict(Counter(n['preference'] for n in notes if n['condition']==side)) for side in p['conditions']},human_quality_ratings=0,blinded=False,independent=False,training_eligible=False,input_notes_sha256=file_hash(NOTES),interpretation='Informed local preferences, not quality pass rates or an adapter comparison.')
    with (RUN/'review-summary.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
