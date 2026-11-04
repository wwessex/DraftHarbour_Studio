# Limited-observation training pilot

The fresh local adapter completed 55 updates at 2.5e-5 in 92.35 seconds, processing 6,765 supervised tokens. Reported MLX peak memory was 8.39 GB. The worker recorded zero training warnings or errors. An initial two-record batching probe failed exact membership on the odd-sized training split before training. The successful run verified every row at the recipe's one-record batch size and retained the original 16 monitor token rows.

The automatic screen used 49 new candidate responses and 98 verified references. All new responses completed. The gate kept craft.

| Check | Craft | Candidate |
|---|---:|---:|
| Clock state | 3/6 | 5/6 |
| Single-paragraph continuations | 8/9 | 9/9 |
| Legacy continuation length | 5/7 | 3/7 |
| Dialogue turns | 3/6 | 1/6 |
| Changed rewrites | 4/4 | 1/4 |

A separate six-case comparison reused the prose-format craft responses from the scene brief diagnostic. The candidate kept gauge accuracy uncertain, described the chart copy as partial, stopped short of declaring the sealed pouch dry inside, and left the bell unanswered. The gauge action still produces only a smudge. The curtain scene invents a secret and reveals a figure. The shelf scene claims stability and suggests that the back wall moved. These are informed AI observations on exposed scenes. They show a promising change in some consequences without a broad writing gain.

The curriculum and update budget both grew. This experiment cannot attribute changes to particular examples. The originality holdout remains reserved. The local training and inference checks ran on Apple Silicon. Application builds and device tests were outside scope.

[Automatic decision](../artifacts/source-training-v45/automatic-decision.json) · [Separate comparison](../artifacts/limited-observation-v45/comparison.json)
