"""Mechanical diagnostics and blinded human packet; never assigns literary ratings."""
from pathlib import Path
import hashlib,json,random
ROOT=Path(__file__).resolve().parents[2]
RUN=ROOT/'artifacts/craft-training-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    protocol=json.loads((RUN/'protocol.frozen.json').read_text())
    cases=[json.loads(l) for l in (ROOT/protocol['test_cases_path']).read_text().splitlines()]
    responses={side:{r['case_id']:r for r in map(json.loads,(RUN/f'{side}.responses.jsonl').read_text().splitlines())} for side in ['base','candidate']}
    results=[];summary={}
    for side,answers in responses.items():
        assert len(answers)==16
        for c in cases:
            r=answers[c['id']];text=r['text'];wc=len(text.split())
            assert r['prompt_sha256']==hashlib.sha256(c['prompt'].encode()).hexdigest()
            assert r['protocol_sha256']==sha(RUN/'protocol.frozen.json')
            assert r['stats']['usage']['prompt_tokens_details']['cached_tokens']==0
            results.append(dict(case_id=c['id'],condition=side,kind=c['kind'],words=wc,error=r['error'],
                truncated=r['stats'].get('finish_reason')=='length',
                word_limit_passed=(not c['word_count_min'] or wc>=c['word_count_min']) and (c['word_count_max'] is None or wc<=c['word_count_max']),
                minimal_repair_exact=(text.strip()==c['exact_reference']) if c['kind']=='editing' else None))
        rows=[r for r in results if r['condition']==side]
        summary[side]=dict(cases=len(rows),errors=sum(bool(r['error']) for r in rows),truncated=sum(r['truncated'] for r in rows),
            exact_minimal_repairs=sum(r['minimal_repair_exact'] is True for r in rows),editing_cases=4,
            word_limit_passes=sum(r['word_limit_passed'] for r in rows),
            word_limits_by_kind={k:dict(passed=sum(r['word_limit_passed'] for r in rows if r['kind']==k),total=4) for k in ['continuity','editing','dialogue','pacing']})
    with (RUN/'scores.json').open('x') as f:json.dump(dict(summary=summary,details=results,quality_ratings=None,meaning='Formatting and narrowly specified minimal repair only; no literary-quality score.'),f,indent=2)
    rng=random.Random(271828);key=[];packet=['# Blinded pilot comparison','',
        'No human ratings have been recorded. A/B are randomized separately per case. Read the passage, check facts and unknowns, then compare only the requested skill. Do not reward extra explanation or length. The editing task has no minimum length. Canonical continuations are not reference answers.',
        '', 'Rate 1 (fails), 2 (major revision), 3 (usable with revision), 4 (minor revision), 5 (strong). Review continuity/knowledge limits, voice, subtext or pacing as applicable; record concrete evidence. Obtain two independent reviewers for a representative subset and adjudicate disagreements before promotion. The answer key is stored separately.','']
    ballots=[]
    for c in cases:
        sides=['base','candidate'];rng.shuffle(sides)
        key.append(dict(case_id=c['id'],A=sides[0],B=sides[1]))
        packet.extend([f'## {c["id"]}', '', c['prompt'], '', '**Known facts:** '+ '; '.join(c['source_facts']), '', '**Unknowns / cautions:** '+'; '.join(c['source_unknowns']), ''])
        for label,side in zip(['A','B'],sides):packet.extend([f'### Response {label}', '', responses[side][c['id']]['text'],''])
        packet.extend(['**Reviewer decision:** A / B / tie; ratings A __, B __; evidence: __',''])
        for reviewer in ['reviewer-1','reviewer-2']:
            ballots.append(dict(case_id=c['id'],reviewer=reviewer,rating_A=None,rating_B=None,preference=None,evidence=None))
    (RUN/'BLIND-REVIEW.md').write_text('\n'.join(packet)+'\n')
    with (RUN/'blind-key.private.json').open('x') as f:json.dump(key,f,indent=2)
    with (RUN/'human-ballots.blank.jsonl').open('x') as f:
        for b in ballots:f.write(json.dumps(b)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
