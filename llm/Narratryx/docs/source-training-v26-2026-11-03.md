# Source-only pilot results — 3 November 2026

The local Unsloth MLX pilot completed 34 updates on 3,706 supervised tokens. The training phase took 93.12 seconds and Unsloth reported a 6.923 GB MLX peak and monitor loss of 1.04946. The final training record contains zero warnings or errors.

All 147 comparison requests completed with fresh contexts, zero cached prompt tokens, zero request errors and zero truncations. Response hashes, prompt hashes and adapter identities verified. Each model answered 44 exposed regression prompts and five separate prompts that overlap training.

| Check | Base | Current craft | Candidate |
|---|---:|---:|---:|
| Legacy dialogue word limits | 2/5 | 3/5 | 5/5 |
| Legacy continuation word limits | 5/7 | 5/7 | 1/7 |
| Focused closed answers | 3/4 | 3/4 | 3/4 |
| Clock state | 3/6 | 3/6 | 3/6 |
| Arrival claims | 2/6 | 2/6 | 2/6 |
| Selected edits | 7/7 | 7/7 | 7/7 |
| Seen exact source restoration | 1/5 | 1/5 | 2/5 |
| Seen surrounding text preservation | 1/5 | 1/5 | 4/5 |

The candidate met more dialogue limits and fewer continuation limits. Grounding and selected-edit scores tied. The five seen cases measure fit on training material. The exposed prompts and word counts leave literary quality unresolved. The review packet contains 21 randomized writing pairs and 42 blank human ballots. The candidate remains experimental.

The run was isolated to Narratryx on Apple Silicon. Web/PWA, Windows/Linux Tauri, Capacitor iOS and native macOS builds and runtime checks were outside this experiment.

[Writing review packet](../artifacts/source-training-v26/REVIEW.md) · [Mechanical scores](../artifacts/source-training-v26/scores.json)
