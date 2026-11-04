# Continuation instruction pilot — 3 November 2026

The pilot compared four revised length instructions with v27's training recipe at 2.5e-5. It trained a fresh adapter for 34 updates in 66.78 seconds. The batching audit verified that only the four prompt rows changed and that every supervised token stayed identical. Unsloth processed 3,706 supervised training tokens and reported a 6.92 GB MLX peak with zero training warnings or errors.

All 49 new candidate responses completed in fresh contexts without errors or truncation. The comparison reused 98 hash-verified base and craft responses. The gate covered both forms of the single-paragraph instruction and kept craft automatically.

| Check | Craft | v27 | v29 |
|---|---:|---:|---:|
| Legacy continuation word limits | 5/7 | 5/7 | 5/7 |
| Single-paragraph continuations | 8/9 | 7/9 | 7/9 |
| Dialogue turns | 3/6 | 3/6 | 1/6 |
| Legacy dialogue word limits | 3/5 | 4/5 | 4/5 |
| Changed rewrites | 4/4 | 4/4 | 4/4 |

The revised briefs produced no gain on these continuation checks and dialogue turn compliance worsened. These exposed cases measure instruction adherence. Application builds and device checks were outside this Apple Silicon model experiment.

[Automatic decision](../artifacts/source-training-v29/automatic-decision.json)
