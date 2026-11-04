"""Build mechanical scores and an explicitly unblinded editorial comparison packet."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from foundation.validation import read_jsonl
from foundation.fiction_questions import mechanics
RUN = ROOT / 'artifacts/fiction-questions-v19'
PLAN = ROOT / 'artifacts/fiction-questions-v19-plan'


def main():
    assert (RUN / 'service-final.json').exists()
    cases = read_jsonl(PLAN / 'cases.frozen.jsonl')
    protocol = json.loads((RUN / 'protocol.frozen.json').read_text())
    details, summary, packet = [], {}, ['# Fiction prompt comparison', '', 'Informed, unblinded AI review material. Exposed development scenarios; no human ratings or training targets. Model and prompt conditions are visible. Mechanical checks do not assess prose quality.', '']
    for side in protocol['conditions']:
        rows = read_jsonl(RUN / (side + '.responses.jsonl'))
        assert [r['case_id'] for r in rows] == [c['id'] for c in cases]
        ds = []
        for c, r in zip(cases, rows):
            assert not r['error'] and r['finish_reason'] != 'length'
            d = dict(condition=side, case_id=c['id'], parent_case_id=c['parent_case_id'], variant=c['variant'], kind=c['kind'], **mechanics(r['text'], c))
            ds.append(d)
            details.append(d)
        summary[side] = {v: {kind: dict(cases=len(subset), word_limit_passed=sum(d['word_limit_passed'] for d in subset), one_paragraph_passed=sum(d['one_paragraph_passed'] is True for d in subset) if kind != 'dialogue' else None) for kind in ['rewrite','continue','dialogue'] for subset in [[d for d in ds if d['variant']==v and d['kind']==kind]]} for v in ['original','clarified']}
        lookup = {r['case_id']: r for r in rows}
        for ident in dict.fromkeys(c['parent_case_id'] for c in cases):
            pair = {c['variant']: c for c in cases if c['parent_case_id'] == ident}
            packet += ['## ' + side + ' / ' + ident, '', '### Original prompt', '', pair['original']['prompt'], '', '### Added guidance', '', pair['clarified']['added_suffix'], '']
            for variant in ['original', 'clarified']:
                c = pair[variant]
                r = lookup[c['id']]
                packet += ['### ' + variant, '', r['text'], '', f"Mechanical checks: {json.dumps(mechanics(r['text'],c))}", '']
    with (RUN / 'scores.json').open('x') as f:
        json.dump(dict(summary=summary, details=details, literary_quality_ratings=None, training_executed=False, model_promoted=False), f, indent=2)
        f.write('\n')
    with (RUN / 'COMPARISON.md').open('x') as f:
        f.write('\n'.join(packet))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
