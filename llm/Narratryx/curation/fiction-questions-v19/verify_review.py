"""Audit evidence anchors and provenance of informed, training-ineligible AI notes."""
import hashlib
import json
import runpy
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import read_jsonl,file_hash
RUN=ROOT/'artifacts/fiction-questions-v19'


def verify():
    mechanical=runpy.run_path(str(ROOT/'curation/fiction-questions-v19/verify.py'))['verify']()
    cases=read_jsonl(ROOT/'artifacts/fiction-questions-v19-plan/cases.frozen.jsonl')
    notes=json.loads((ROOT/'artifacts/fiction-questions-v19-review-notes.json').read_text())
    rows=read_jsonl(RUN/'ai-review.jsonl')
    summary=json.loads((RUN/'review-summary.json').read_text())
    assert len(rows)==len(notes)==18 and len({(n['condition'],n['parent_case_id']) for n in notes})==18
    for note,row in zip(notes,rows):
        assert all(row[k]==v for k,v in note.items())
        assert row['training_eligible'] is False and row['human'] is False and row['blinded'] is False and row['independent'] is False
        side=note['condition'];parent=note['parent_case_id'];path=RUN/(side+'.responses.jsonl')
        lookup={r['case_id']:r for r in read_jsonl(path)}
        pair={c['variant']:lookup[c['id']] for c in cases if c['parent_case_id']==parent}
        assert set(pair)=={'original','clarified'}
        for v,r in pair.items():
            assert row['response_text_sha256'][v]==hashlib.sha256(r['text'].encode()).hexdigest()
            assert all(q in r['text'] for q in note['evidence'][v])
            if 'dialogue_turns' in note:
                # All actual reviewed outputs have exactly one speaking turn per nonempty line.
                assert note['dialogue_turns'][v]==len([l for l in r['text'].splitlines() if l.strip()])
        assert row['response_file_sha256']==file_hash(path)
    assert summary['local_preferences_by_condition']=={side:dict(Counter(n['preference'] for n in notes if n['condition']==side)) for side in ['base','current-craft','mixed-v16']}
    assert summary['input_notes_sha256']==file_hash(ROOT/'artifacts/fiction-questions-v19-review-notes.json')
    return dict(mechanical_verification=mechanical,review_pairs=18,evidence_quotes_verified=True,dialogue_turns_checked=True,blinded=False,independent=False,human_quality_ratings=0,training_eligible=False)


if __name__=='__main__':
    result=verify()
    with (RUN/'review-verification.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
