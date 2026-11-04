# Lower-rate source pilot — 3 November 2026

The local pilot changed the learning rate from 5e-5 to 2.5e-5 and retained the same fresh base, seed, 34 training examples and 16 exposed monitors. It completed 34 updates and 3,706 supervised tokens in 86.64 seconds at a reported MLX peak of 6.92 GB. The training record contains zero warnings and errors.

The comparison used 49 new candidate responses and 98 hash-verified base and craft responses from v26. The new responses completed without errors or truncation. They used fresh contexts. The automatic gate kept craft because the candidate passed five of seven explicit single-paragraph continuation checks, compared with six of seven for craft.

| Check | Craft | v26 | v27 |
|---|---:|---:|---:|
| Legacy dialogue word limits | 3/5 | 5/5 | 4/5 |
| Dialogue turns | 3/6 | 1/6 | 3/6 |
| Legacy continuation word limits | 5/7 | 1/7 | 5/7 |
| Single-paragraph continuations | 6/7 | 6/7 | 5/7 |
| Changed rewrites | 4/4 | 1/4 | 4/4 |

The lower rate recovered continuation length, dialogue turn compliance and rewrite behavior relative to v26 on these exposed prompts. These mechanical checks leave literary quality unresolved. The gate runs automatically. This model experiment was isolated from application builds and runtime testing.

[Automatic decision](../artifacts/source-training-v27/automatic-decision.json)
