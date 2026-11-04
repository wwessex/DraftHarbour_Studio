# Expanded 50-example local pilot

A fresh LoRA adapter completed one pass over the 50-example source curriculum at 2.5e-5, using the existing base, seed and adapter settings. The installed batcher preserved all 6,221 supervised tokens and the 16 existing monitors. Training took 92 seconds with a reported MLX peak of 8.39 GB and no training warnings or errors.

The automatic screen used 49 new candidate responses and 98 verified reference responses. All new responses completed in fresh contexts with no errors or truncation.

| Check | Craft | Expanded candidate |
|---|---:|---:|
| Single-paragraph continuations | 8/9 | 8/9 |
| Legacy continuation word limits | 5/7 | 4/7 |
| Dialogue turns | 3/6 | 2/6 |
| Changed rewrites | 4/4 | 3/4 |

Dialogue word-limit compliance improved. Continuation length, dialogue turns and rewrite completion regressed, so the gate kept craft. The 24-case originality holdout remains reserved. The comparison changed both the curriculum and the number of supervised tokens. Its scores cannot isolate the effect of any one new lesson or establish originality gains.

This experiment ran on Apple Silicon. Application builds and runtime checks were outside the model research scope.

[Automatic decision](../artifacts/source-training-v38/automatic-decision.json)
