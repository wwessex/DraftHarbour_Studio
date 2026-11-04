"""Read-only verification of informed AI annotations and untouched human ballots."""
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl


def verify():
    out=ROOT/'artifacts/source-training-v22-ai-review'
    run=ROOT/'artifacts/source-training-v22'
    proof=json.loads((out/'verification.json').read_text())
    for group in ['input_hashes','protected_hashes']:
        for n,h in proof[group].items():assert file_hash(ROOT/n)==h,n
    for n,h in proof['output_hashes'].items():assert file_hash(out/n)==h,n
    rows=read_jsonl(out/'ai-review.jsonl')
    cases=read_jsonl(ROOT/'artifacts/source-training-v22/cases.frozen.jsonl')
    wanted={c['id'] for c in cases if c['kind'] in ['dialogue','continue','rewrite','write']}
    assert len(rows)==len({r['case_id'] for r in rows})==21 and {r['case_id'] for r in rows}==wanted
    responses={s:{r['case_id']:r for r in read_jsonl(run/(s+'.responses.jsonl'))} for s in ['current-craft','candidate']}
    for row in rows:
        assert row['training_eligible'] is False and row['human'] is False and row['blinded'] is False and row['independent'] is False
        for side,key in [('current-craft','current_evidence'),('candidate','candidate_evidence')]:
            text=responses[side][row['case_id']]['text']
            assert all(q in text for q in row[key]) and row['word_counts'][side]==len(text.split())
    assert dict(Counter(r['preference'] for r in rows))==proof['local_preferences']
    ballots=read_jsonl(run/'human-ballots.blank.jsonl')
    assert len(ballots)==42 and all(b['preference'] is None and b['evidence'] is None and all(v is None for v in b['ratings'].values()) for b in ballots)
    assert proof['human_quality_ratings']==0 and not proof['model_promoted']
    return dict(passed=True,reviewed_pairs=21,all_evidence_anchors_verified=True,original_run_artifacts_unchanged=True,
                unchanged_blank_human_ballots=42,blinded=False,independent=False,human_quality_ratings=0,
                training_eligible=False,model_promoted=False)


if __name__=='__main__':print(json.dumps(verify(),indent=2))
