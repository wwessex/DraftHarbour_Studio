# Eight-update revision trial — 26 October 2026

**The local trial completed, but it does not establish a better literary model.** Both baselines finished before training; all eight candidate updates completed, followed by 24 candidate responses. The 72 matched responses have no errors or truncation. Mechanical results are mixed, and an informed AI check still finds unsupported attribution and temporal reasoning errors. The development service is restored with **the original craft model selected**; no adapter was promoted, exported, published or integrated into an app.

This executes the [frozen revision preflight](revision-pilot-preflight-2026-10-26.md) under the user’s instruction to proceed. It used the development Mac and existing Unsloth MLX installation, not a cloud job. No paid service, corpus upload or generated literary teaching target was introduced.

## Training and resource evidence

| Item | Actual result |
|---|---|
| Training mixture |30 examples: 18 retained and 12 not previously trained |
| Development monitor |16 exposed Wray records, not an independent project-wide test set |
| Base |Pinned `mlx-community/Qwen3.5-4B-MLX-8bit`, fresh base weights rather than continuing the current adapter |
| Adapter |LoRA rank 8/alpha 16, batch 1, accumulation 4, seed 42, learning rate 5e-6 with the frozen scheduler |
| Context |2,048-token allowance; maximum prepared example 1,882 tokens, no target truncation |
| Supervision |5,417 answer/EOS tokens; prompts masked out of loss |
| Updates |8 of 8 completed; no warnings/errors |
| Training time |Worker reported 79.4 seconds; supervised phase including startup/saving took 99.68 seconds |
| Peak MLX memory |7.142 GB reported, below the 10 GB stop threshold |
| Final development loss |1.148294; not a literary-quality rating |

The runner enforced the 20-minute training deadline, checked process-tree resident memory and stopped on reported MLX peaks above 10 GB, nonfinite metrics, warnings/errors or more than eight updates. The memory checks act on observed telemetry; they are not a guarantee that allocation can never briefly cross a threshold. No limit was triggered, no automatic retry occurred and no resource budget was enlarged.

The development inference service was paused to avoid holding its model in memory alongside the experiment. A `finally` path restored the same command, environment, token-file use and model configuration. HTTP health returned 200, and the original model-configuration hash is unchanged. No writing app was stopped or manuscript edited.

## Matched diagnostic results

The 24 evaluation-only cases span eight new situations, with a fresh single user message for each response, no prior assistant messages and zero reported cached prompt tokens. Generation settings are identical across base, current craft and candidate. Four cases per task are too few for population claims, and three tasks sharing one situation are correlated.

| Check | Base | Current craft | Candidate |
|---|---:|---:|---:|
| Exact minimal duplicate-word repair |4/4|4/4|4/4|
| Chronology rewrite within 90 words |4/4|4/4|4/4|
| Grounded analysis within 70 words |4/4|4/4|4/4|
| Dialogue within 100 words |3/4|1/4|2/4|
| Dialogue quote-block proxy, 4–6 |4/4|4/4|4/4|
| Pacing within 85 words |4/4|4/4|4/4|
| Continuation within 60–90 words |3/4|4/4|3/4|

These are exact repair, length and formatting checks, **not scores for chronology, grounding, dialogue or pacing quality**. Candidate dialogue length compliance is between the two baselines, while continuation length compliance is below current craft. Eleven of 24 cases have exactly identical output across all three conditions. This benchmark differs from v3, so its 4/4 editing result must not be presented as a longitudinal improvement from the earlier 2/4 score.

## Semantic observations

An **informed, named-condition AI review** inspected all four chronology rewrites and all four grounded-analysis cases, plus two story spot checks. It is not an independent or blinded review, and no human literary ratings have been completed.

- In the saffron analysis, all three models infer Lin likely left a label because she is “late”. The present is 12:40 and the expected arrival 13:15, so that premise is false. Marking an unsupported inference uncertain does not fix it.
- In the kiln analysis, all call Niko the last person present, which the source does not establish. Their question about Maren arriving after 17:45 also fails to respect that 17:45 is the current time and she has not arrived.
- In the ferry analysis, all infer the expected visitor left twine because he has not yet arrived. The stated facts do not support the attribution. The silk analysis similarly assumes an object’s appearance history beyond what was given.
- Chronology rewrites preserve the stated times and non-arrivals, but all are identical across conditions and three largely copy the input. The kiln rewrite adds a floor location and gender not established by the context. A word-limit pass does not establish effective rewriting.
- Candidate seed-library dialogue preserves uncertainty about viability, but its proposed coin toss does not explain a useful difference between the two half-packet allocations. It escalates blame rather than resolving the shared problem.
- Current craft and candidate give identical mountain continuations that invent a nail deliberately left by the missing companion and treat it as proof. They also change Orla to Oria. These problems are invisible to the continuation length check.

The detailed observations are in `ai-grounding-review.json` and `ai-story-spotcheck.json`. No overall AI preference score or fictional human approval has been added. These failures support keeping the candidate experimental; they do not establish that another condition is best at fiction generally.

## Evidence and safeguards

- [Eight-case blinded quick review](../artifacts/revision-training-v4/QUICK-REVIEW.md) and [full 24-case packet](../artifacts/revision-training-v4/BLIND-REVIEW.md) randomise A/B/C independently by case. Keep named results, AI observations and `blind-key.private.json` away from future reviewers until their ballots are submitted. The key has private file permissions. All 48 human ballot rows remain blank; the quick packet selects eight cases from that same review rather than creating duplicate ratings.
- `protocol.frozen.json` preserves the preflight hashes and adds execution-script/request hashes. The frozen execution recipe, datasets, source ledger, old experiment inputs, base weights and 14 protected adapter/configuration files verify unchanged.
- `derivation-audit.json` verifies all 30 training examples: 26 source-derived literary answers and four source-anchored structural Copyedit responses. All 18 retained examples preserve their earlier messages exactly; all 12 new candidates match their canonical source text exactly. Explicit loss-mask arrays are checked against the frozen counts.
- The extra derivation check initially flagged a retained Doyle paragraph because the acquired ebook has physical line breaks and the already curated answer joins those lines. The supervisor was paused before training while all 18 retained records were checked. Only their previously documented whitespace reflow was accepted; no wording, prompt, answer or source record changed. Baseline responses were preserved and the supervisor resumed after the audit passed.
- `completion.json`, `final-progress.json`, three response/completion pairs, `scores.json`, `service-restored.json` and `final-verification.json` retain the actual execution evidence. The adapter remains solely under `artifacts/revision-training-v4/adapter` and is ignored by Git.
- **142 CPU foundation tests passed** in 47.232 seconds, including four new resource/failure guards. Final execution verification independently confirms 72 complete matched responses, eight updates, the resource limits, unchanged pins/artifacts, restored service and blank human ballots.

The model tests and training ran on the development Mac only. Web/PWA, Tauri Windows/Linux, Capacitor iOS and independent native macOS received no source, asset, configuration or installer changes from this task, and no app/device builds were run. This trial does not certify Windows inference or ordinary-user hardware support.

## Next decision

Keep the current craft model selected. The saved blinded comparisons are ready for independent human review. Before another training experiment, prioritise source-supported evidence and uncertainty supervision within the existing restrictions on literary targets, plus focused regression cases for the observed semantic errors. More epochs on these same 30 examples are not justified by this result. This small pilot does not demonstrate Muse-equivalent capability or production readiness.
