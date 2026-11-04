"""Freeze an explicitly informed AI editorial review; never touch human ballots."""
import json
import sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
RUN=ROOT/'artifacts/source-training-v22'
OUT=ROOT/'artifacts/source-training-v22-ai-review'
NOTES=ROOT/'artifacts/source-training-v22-review-notes.json'


def main():
    if OUT.exists():raise ValueError('Refuse overwrite')
    lock_path=ROOT/'curation/source-training-v22/execution.lock.json'
    lock=json.loads(lock_path.read_text())
    protected=dict(lock['source_hashes']) | dict(lock['artifact_hashes'])
    protocol=json.loads((RUN/'protocol.frozen.json').read_text())
    protected.update(protocol['input_hashes']);protected.update(protocol['protected_artifacts'])
    protected[str(Path(protocol['base_path'])/'model.safetensors')]=protocol['base_weights_sha256']
    protected[str((RUN/'blind-key.private.json').relative_to(ROOT))]=file_hash(RUN/'blind-key.private.json')
    for n,h in protected.items():assert file_hash(ROOT/n)==h,n
    cases=read_jsonl(ROOT/'artifacts/source-training-v22/cases.frozen.jsonl')
    writing={c['id']:c for c in cases if c['kind'] in ['dialogue','continue','rewrite','write']}
    notes=json.loads(NOTES.read_text())
    assert len(notes)==21 and len({n['case_id'] for n in notes})==21 and {n['case_id'] for n in notes}==set(writing)
    responses={s:{r['case_id']:r for r in read_jsonl(RUN/(s+'.responses.jsonl'))} for s in ['current-craft','candidate']}
    ballots_path=RUN/'human-ballots.blank.jsonl';ballot_hash=file_hash(ballots_path)
    ballots=read_jsonl(ballots_path)
    assert len(ballots)==42 and all(b['preference'] is None and b['evidence'] is None and all(v is None for v in b['ratings'].values()) for b in ballots)
    rows=[]
    packet=['# Informed AI review of 21 paired writing cases','','Model conditions and earlier failure analyses were already known. This review is not independent, blinded, human or a quality benchmark. Local preferences compare particular flaws; they are not counts of acceptable answers. These annotations and generated evaluation outputs are not eligible training targets. Original responses, randomised packet, private key and blank human ballots are unchanged.','']
    for note in notes:
        ident=note['case_id'];c=writing[ident]
        assert note['preference'] in ['candidate','current-craft','tie','neither']
        for side,key in [('current-craft','current_evidence'),('candidate','candidate_evidence')]:
            r=responses[side][ident]
            assert not r['error'] and r['finish_reason']!='length'
            assert note[key] and all(quote in r['text'] for quote in note[key]),(ident,side)
        row=dict(note,kind=c['kind'],reviewer='Codex AI: informed editorial comparison',blinded=False,independent=False,human=False,
                 training_eligible=False,word_counts={side:len(responses[side][ident]['text'].split()) for side in responses})
        rows.append(row)
        packet+=['## '+ident,'',f"Local preference: **{note['preference']}**. {note['scope']}",'',note['assessment'],'','Curriculum gap: '+note['training_gap'],'']
    OUT.mkdir()
    with (OUT/'ai-review.jsonl').open('x') as f:
        for row in rows:f.write(json.dumps(row,ensure_ascii=False)+'\n')
    with (OUT/'REVIEW.md').open('x') as f:f.write('\n'.join(packet))
    for n,h in protected.items():assert file_hash(ROOT/n)==h,n
    assert file_hash(ballots_path)==ballot_hash
    summary=dict(passed=True,cases_reviewed=21,local_preferences=dict(Counter(n['preference'] for n in notes)),
                 interpretation='Counts are informed local preferences, not pass rates, independent votes or reliable quality improvement.',
                 blinded=False,independent=False,human_quality_ratings=0,training_eligible=False,
                 prior_artifacts_and_blank_human_ballots_unchanged=True,new_inference_requests=0,new_training_runs=0,model_promoted=False,
                 input_hashes={str(p.relative_to(ROOT)):file_hash(p) for p in [NOTES,lock_path,Path(__file__)]},
                 protected_hashes=protected,output_hashes={n:file_hash(OUT/n) for n in ['ai-review.jsonl','REVIEW.md']})
    with (OUT/'verification.json').open('x') as f:json.dump(summary,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in summary.items() if not k.endswith('hashes')},indent=2))


if __name__=='__main__':main()
