# Selective timeline diagnostic

A post-hoc replay of the 49 saved v45 responses routes seven explicit structured clock-state checks to v45 and uses craft for every other task. Strict JSON scores rise from 4/7 to 6/7, with two corrected cases and zero new errors on those seven. The rule was chosen after observing the v45 results. The replay uses exposed prompts and cannot establish transfer or writing improvement.

Six new evaluation-only timeline cases are frozen for a direct comparison. They distinguish scheduled from actual arrival and cover early, late, absent and unknown arrivals, including a midnight boundary. A fresh matched run is needed before considering this route for real use.

This is an offline model diagnostic. Application build and runtime checks were outside scope.

[Replay evidence](../artifacts/clock-routing-v46/replay.json) · [Fresh cases](../curation/clock-routing-v46/fresh-clock-cases.jsonl)

## Fresh comparison

All 12 fresh requests completed without errors or truncation on Apple Silicon. Craft and v45 returned identical text on all six cases and both scored **1/6** under strict JSON comparison. Both got every current time and scheduled arrival time right. They returned null for three known absences, used an actual arrival time as the value of the arrived field in one case, and substituted actual arrival for the completed event in another.

The brief said to use null for unknown arrival but omitted an explicit Boolean type for known arrival. This limits the interpretation of the strict scores. The matched tie provides no evidence for routing timeline requests to v45. Keep craft as the selected model. [Fresh scores](../artifacts/clock-routing-v46/fresh/comparison.json)
