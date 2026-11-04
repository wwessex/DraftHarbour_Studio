"""Apply the editorial gate to completed, anonymised rewrite ratings."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / 'artifacts/rewrite-specialist-v57'


def main():
    key = json.loads((RUN / 'blind-key.json').read_text())
    ratings = json.loads(Path(sys.argv[1]).read_text())
    if ratings.keys() != key.keys():
        raise ValueError('Ratings must cover every frozen case')
    scores = {}
    for case, labels in key.items():
        if ratings[case].keys() != labels.keys():
            raise ValueError(f'{case} ratings must cover all labels')
        for label, model in labels.items():
            fidelity, craft, reason = ratings[case][label]
            if type(fidelity) is not bool or type(craft) is not bool or not reason.strip():
                raise ValueError(f'{case} {label} has an invalid rating')
            scores.setdefault(model, {})[case] = dict(fidelity=fidelity, craft=craft, reason=reason)
    totals = {}
    for model, cases in scores.items():
        totals[model] = dict(fidelity=sum(r['fidelity'] for r in cases.values()),
                             craft=sum(r['craft'] for r in cases.values()),
                             both=sum(r['fidelity'] and r['craft'] for r in cases.values()))
    candidate, craft = scores['candidate'], scores['current-craft']
    lost = [case for case in craft if craft[case]['fidelity'] and not candidate[case]['fidelity']]
    advances = not lost and totals['candidate']['both'] > max(totals['current-craft']['both'], totals['base']['both'])
    result = dict(decision='advance-to-larger-evaluation' if advances else 'keep-craft',
                  totals=totals, lost_fidelity_against_craft=lost, scores=scores,
                  method='Single AI editorial review with shuffled model labels', model_promoted=False)
    with (RUN / 'editorial-decision.json').open('x') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
    print(json.dumps(dict(decision=result['decision'], totals=totals, lost=lost), indent=2))


if __name__ == '__main__':
    main()
