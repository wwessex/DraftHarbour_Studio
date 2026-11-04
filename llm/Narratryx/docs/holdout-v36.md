# Fresh originality and writing holdout

The holdout contains 24 new evaluation-only briefs, four each for continuation, dialogue, rewriting, scene writing, pacing and analysis. Their exact prompts are absent from the 12-case development screen, legacy comparison and current training proposal. The holdout and its rules were frozen before any responses were generated.

The comparison calls for three seeds per brief for both craft and the next candidate, with temperature 0.7 and a fresh context for each of the 144 requests. The seeds reproduce individual attempts and provide alternatives within each brief. Preserve the same inference settings and corpus snapshot for both models.

Report three separate outcomes per skill.

1. Mechanical adherence checks word ranges, labelled turns, paragraph count, changed rewrites and exact supporting quotations where applicable.
2. Originality checks normalized 12-word runs against the known source files and repeated wording between alternatives. Record detected overlap with the source identity and review whether it was required by the brief, particularly in analysis and rewriting.
3. An automated evaluator reads anonymized, order-swapped pairs for each seed and scores the case's quality criterion with quoted evidence. For the alternatives to each brief, it also records whether the action, negotiation or interpretation changes materially while preserving the brief. Disagreement across orderings is inconclusive. Record the evaluator and configuration before scoring.

Treat a failed or incomplete comparison as inconclusive. A candidate must pass the existing regression gate, show a quality gain on the fresh briefs, and avoid worse fidelity or more flagged copying before it advances. Preserve results by skill so gains in one task cannot hide losses in another. This holdout provides evidence about the tested briefs and known corpus. A further set is needed if these cases inform later training choices.

The freeze checks and representative mechanical scoring checks passed. The holdout awaits a candidate from the expanded curriculum.

[Frozen protocol](../curation/holdout-v36/holdout.lock.json)
