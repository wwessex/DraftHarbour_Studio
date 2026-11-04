# Source-backed claim-reasoning trial — 31 October 2026

The user authorised further local training. This trial adds explicit supervision for the recurring premature-lateness error while preserving the previous prose lessons. It uses Unsloth's MLX trainer on the development Mac, separate from every application. Training completion, mechanical reasoning accuracy and literary improvement remain separate claims. No app default or selected model is changed, and no automatic promotion is permitted.

## Prepared curriculum and source audit

The mixture contains **104 training records** and the same **16 exposed Wray development-monitor records**. It retains all 80 previous training examples, including 56 source-prose lessons, and adds 24 deterministic claim exercises. The original messages, spans and other record fields are preserved; only their dataset-version metadata changes to satisfy the common-version schema. No books, source works or rights clearances are added. Existing per-span/per-split GB/US checks pass against the existing scoped ledger.

The new claim is deliberately composite and current: **“The expected visitor is already late and still absent.”** Known arrival contradicts the absence clause. At/before the scheduled time, “already late” is contradicted even if arrival is unknown. After the deadline, known absence supports the claim; unknown arrival leaves it unestablished. This does not infer whether a visitor who has already arrived was late earlier. Targets contain only a verdict, signed minutes-to-schedule and arrival-state label. No generated literary teaching prose or teacher-model outputs are added.

Twenty-four records cover the existing two source-schedule families, four time offsets and three arrival states. They are correlated task variants, not 24 independent stories or new authors. New labels are deterministic Codex annotations audited against a tested truth table; they are not human literary gold. Attribution discipline remains covered by retained evidence lessons and evaluation; this addition specifically targets temporal claims rather than claiming new attribution supervision.

The [source audit](../artifacts/arrival-claims-v1/source-audit.json) checks the retained records against the previous raw dataset, unchanged source spans/quotations, exact recomputed targets, no teacher outputs and disjoint training/test clock tuples. Early preparation attempts failed schema checks for validator-added internal metadata and mixed dataset versions. Their partial outputs were preserved separately, the builder was corrected before freezing, and no model trained on rejected outputs.

Offline tokenizer preflight passes without truncation at a maximum **1,882 tokens**. The **9,623 supervised training tokens** comprise 8,686 prose and 937 structural tokens: approximately 90.3%/9.7% by tokens, although prose is only 56/104 records. All prompt labels are masked and answers/EOS retained; targets round-trip exactly. This balance is experimental, not established as optimal. No editing minimum word count is introduced.

## Frozen execution and evaluation

The new dataset and separate execution scripts pin their inputs and preserve earlier weights/configurations, including v6. Training starts from the same cached Qwen3.5-4B MLX 8-bit base, with LoRA rank 8/alpha 16/dropout 0, learning rate 5e-5, seed 42, batch 1/accumulation 4, context 2,048 and no packing. One pass over 104 rows requires **26 updates**. This changes both curriculum and update count relative to v6; it is not a single-parameter ablation or proof of which factor caused any difference. The installed Unsloth version is now 2026.10.10 (previous run 2026.10.8); this work did not install that update. MLX 0.32.4, mlx-lm 0.32.2 and mlx-vlm 0.7.9 are unchanged. Fresh base/current outputs reproduce all24 shared retention cases exactly, but that does not eliminate software-version differences as a cross-run confound.

The supervisor retains a 20-minute whole-training deadline, 10 GB MLX-peak and process-tree-RSS limits, and warning/error/nonfinite gates. More than 26 updates stops the run. Base/current baselines must complete before training. Each condition runs serially in one-message fresh contexts, with zero reported cached tokens, temperature 0, seed 42 and maximum 384 output tokens. Any request error, context overflow or truncation stops the experiment.

Each of three conditions receives **64 cases**: 12 new clock states, 12 new composite-claim checks, 16 prose-transfer tasks across four new fictional situations, and 24 exposed retention regressions. New tuples use schedules distinct from training and previous clock tests, but the symbolic task family is familiar. The 40 new diagnostics were frozen before model inference/training. They are not a human-approved formal benchmark or independent literary-quality certification. The prose cases are original AI-authored evaluation-only situations, never training answers.

Strict clock and claim scoring rejects extra/duplicate fields, wrong types, wrong signs and non-JSON wrappers; it does not repair model answers. Exact editing ignores surrounding response whitespace only. Word counts and dialogue quotation counts are format proxies. No combined literary score is inferred from them. Canonical novel continuations are not reference answers.

## Completed results

All **26 updates** completed without warnings or errors. The worker reported **373.1 seconds**; the supervised whole training phase took **403.83 seconds**. Reported peak MLX memory was **7.167 GB**. Development loss was **1.087867** at update 13 and **1.056618** at update 26. This is the exposed Wray monitor, not independent literary evaluation. Average training loss is not used to claim improvement, especially with a changed mix of easy structural targets.

All **192 primary responses** completed without errors or truncation, one-message fresh contexts, zero reported cached tokens and no context overflow. All 24 shared retention answers reproduce exactly in each fresh base/current baseline. The new 12-clock/12-claim cohorts are different from v6's tests, so their fractions must not be compared directly with v6's 24-clock score.

| Diagnostic | Base | Current craft | Candidate |
|---|---:|---:|---:|
| Fresh clock JSON exact (12) | 5/12 | 5/12 | 4/12 |
| Fresh composite claim JSON exact (12) | 2/12 | 2/12 | 2/12 |
| Fresh selected repair exact (4) | 4/4 | 4/4 | 4/4 |
| Fresh analysis ≤70 words (4) | 4/4 | 4/4 | 4/4 |
| Fresh rewrite ≤90 words (4) | 4/4 | 4/4 | 4/4 |
| Fresh continuation 60–90 words (4) | 0/4 | 0/4 | 0/4 |
| Retention repair exact (4) | 4/4 | 4/4 | 4/4 |
| Retention dialogue ≤100 words (4) | 3/4 | 1/4 | 4/4 |
| Retention dialogue 4–6 quotation blocks (4) | 4/4 | 4/4 | 4/4 |
| Retention pacing ≤85 words (4) | 4/4 | 4/4 | 4/4 |
| Retention continuation 60–90 words (4) | 3/4 | 4/4 | 3/4 |

The exposed chronology-rewrite and grounded-analysis word limits also pass 4/4 in all conditions. Eight exact editing checks are stable. Fresh continuation length compliance is 0/4 for every condition; this is not a candidate-specific regression. Joint claim accuracy does not improve, and clock accuracy regresses against the fresh controls. These format/closed-task checks do not establish fiction quality.

Exploratory component diagnostics separate the errors rather than replacing the primary joint score: clock-state field correctness is 6/12 for the controls and 5/12 for the candidate, while signed arithmetic rises from 10/12 to 11/12. In claim tasks, verdict correctness falls from 6/12 to 4/12, signed arithmetic falls from 6/12 to 5/12, and arrival-state correctness stays 8/12. All outputs pass the strict JSON structure/type/category checks; these failures concern values. This decomposition was added after inspecting baseline failures and is exploratory, not preregistered evidence of a quality gain.


## Review, limits and preservation

The [full blinded prose packet](../artifacts/grounding-training-v7/BLIND-REVIEW.md) and [eight-case starting packet](../artifacts/grounding-training-v7/QUICK-REVIEW.md) randomise A/B/C separately per prose case. Forty prose cases produce 80 blank ballots for two reviewers; the private key has mode 0600. No human scores or approvals are invented. Named-condition Codex observations below are informed AI inspection, not blind, independent or human ratings.

### Informed AI observations

The candidate still calls Kiran late at 09:25 despite an expectation of 10:05, and calls Omar late at 12:20 despite 13:10. In the costume-room analysis it describes Lena as likely late, although Pavel is the person whose arrival is expected: an additional role-attribution error. The weather-station answer speculates that Soren may be late without evidence supporting that prediction. Passing the analysis word limit does not establish grounded reasoning.

**No quality upgrade or model promotion is justified.** New prose tasks retain temporal/attribution defects, and primary structured accuracy does not improve. No human literary-quality scores exist.

### Separate seen-training fit probe

After the primary evaluation, a separately frozen diagnostic tested 12 of the 24 new claim-training rows: six predefined state variants from each schedule family. Existing GB/US evaluation uses were checked for both source records; no rights scope was expanded. Full original training prompts were used, with fresh contexts, temperature 0, seed 42 and at most 96 output tokens. It ran under the same 10 GB process-tree memory gate and a separate 10-minute deadline. No further weights were trained.

The candidate passes **4/12 exact checks** on this seen subset. All 12 requests completed without errors or truncation; the adapter remained unchanged. These twelve responses are **additional diagnostics**, not part of the 192 primary responses, and not an unseen benchmark. No base/current fit-probe comparison was run, so this result cannot establish a before/after gain on seen examples. It does show that this recipe has not reliably fitted even these teaching rows; the problem cannot be described solely as failure to transfer to new stories.

The result does not isolate undertraining, competing tasks, prompt/context effects, optimisation or runtime/loss-path issues. Before another broader literary run, the useful next step is a tiny controlled fitting/overfitting sanity experiment with an audited label/loss path, followed by genuinely held-out tests and prose-retention checks. Do not simply increase broad training duration or claim that lower development loss means better storytelling. That next experiment has not been launched.


The [final verification](../artifacts/grounding-training-v7/final-verification.json) passed: 104 training/16 monitor records, 26 steps, 9,623 supervised tokens, 192 matched primary responses, saved adapter hash, resource gates, unchanged frozen inputs/base/previous artifacts and initial service state preserved. The selected craft profile remains unchanged. **174 CPU foundation tests passed in 228.605 seconds**, including eight new claim/JSON/boundary regressions. New Python modules compile. The [source audit](../artifacts/arrival-claims-v1/source-audit.json), strict scorer, [retention reproduction check](../artifacts/grounding-training-v7/retention-v6-v7.json), and [fit-probe completion](../artifacts/grounding-training-v7/fit-probe.complete.json) are separate evidence. The previously stopped legacy port-8890 service remains stopped.

The new adapter is saved locally under `artifacts/grounding-training-v7/adapter`; its SHA-256 is `7d3caade582192897ec5f2f8bf00a9ac47e69f38fc983bc3f1ac5d0e0d4f828a`. This run does not replace existing uploaded craft/v5/v6 assets or any app model. Human quality ratings remain zero; the 80 human ballots stay blank.


Selected craft/base/previous adapter hashes are preserved. Source preparation and training stay outside app startup, installers and manuscript storage. There are no paid jobs, corpus uploads, model-default changes or new model downloads. Existing experimental model uploads remain separate from quality promotion; this run does not silently replace published artifacts.

All changes are confined to Narratryx. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/configuration/default/generated-asset changes from this work. No application builds or device acceptance checks are needed or run. Mac MLX evidence does not certify Windows/Linux execution, ordinary-user hardware or Muse-equivalent quality. Users do not need local training.

Recheck completed evidence without training or inference from `llm/Narratryx`:

```bash
.venv-foundation/bin/python curation/arrival-claims-v1/audit.py
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/grounding-training-v7/verify.py'); print(m['verify']())"
```
