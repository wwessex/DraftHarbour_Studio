# Source-only 28-update pilot — 2 November 2026

**Unsloth MLX completed 28 updates and all 147 fresh-context evaluation responses.** No request errors, truncation or training warnings occurred. The candidate has some local improvements but **no reliable overall literary upgrade is established**. Keep the selected craft model. The new adapter remains a separate local experiment; application code, prompts and defaults are unchanged.

The run began on 1 November and completed on 2 November. It uses the [28-record source proposal](source-candidates-v20-2026-11-01.md), following the [installed-trainer recipe](trainer-recipe-v21-2026-11-01.md).

## Explicit environment amendment before execution

The first preflight stopped **before any run directory, model call or training** because installed source hashes differed from the original v21 audit. Inspection found Unsloth had changed from 2026.10.10 to **2026.10.11**, and mlx-vlm from 0.7.9 to **0.7.11**. The cause of that installation change was not established; this task did not install or upgrade packages.

The original v21 evidence is preserved. An explicit amended audit, `trainer-recipe-v21b`, rechecks the actual installed preprocessing, full batch multisets, worker configuration and cached tokenizer metadata. Every token dataset and evaluation-case file remains byte-identical to v21. Worker configuration differs only in the two dataset paths pointing to the amended directory. Data, update count, seeds, learning rate and resource gates are unchanged. The old audit's installed-code pins should not be expected to match the changed installation.

Only after that audit passed was a new execution frozen and launched. This was not an automatic retry of a failed training run. All model comparisons below are freshly generated in the amended environment. Historical cross-run differences cannot be attributed solely to the dataset or training because package versions, mixture and update count differ from earlier pilots.

## Training and technical completion

The fresh cached Qwen3.5-4B MLX 8-bit base receives a separate rank-8 LoRA adapter: alpha 16, dropout 0, learning rate 5e-5, two warmup steps and linear schedule, batch size one, accumulation one, seed 42, context 2,048 and packing disabled. Resume is unset. There is one presentation of each of the **28 source-derived lessons**: 20 broader prose/revision, five semantic repairs and three structural editing controls. Sixteen exposed Wray monitors remain validation-only.

The installed worker configuration exactly matches the amended audit. Explicit labels mask prompts and supervise **3,033 training tokens**. Maximum example length is 499 tokens; no target is truncated. Answers remain published source text within the existing GB/US rights records. No generated evaluation fiction or AI review note enters training, and no source/edition clearance is expanded.

The full guarded training phase takes **123.71 seconds**, including checks, setup and saving; the final worker progress reports **82.01 seconds**. Reported MLX peak is **6.923 GB** and exposed-monitor loss is **1.0624**. Monitor loss is not independent literary-quality evidence. All 28 updates complete with finite reported losses and no training warnings/errors. The declared 10 GB memory gates and 20-minute phase deadlines are retained, with the outer process-tree RSS monitor stopping only experiment children on failure. There is no automatic retry.

Base and current-craft reference runs finish before training. Each condition produces 49 responses: 44 primary and five separately labelled seen-training-fit cases. Every request has one user message, no previous assistant messages and zero reported cached tokens, with temperature 0, seed 42, repetition penalty 1.0 and a 384-token cap. Models unload between conditions. The initially stopped legacy service stays stopped.

## Mechanical results

All primary cases are **exposed development diagnostics**, not new independent quality tests. The focused group is the previously exposed eight-case semantic-transfer set, not a fresh cohort.

| Metric | Base | Current craft | Candidate |
|---|---:|---:|---:|
| Primary responses completed | 44/44 | 44/44 | 44/44 |
| Focused closed labels | 3/4 | 3/4 | 3/4 |
| Legacy clock labels | 3/6 | 3/6 | 3/6 |
| Legacy claim labels | 2/6 | 2/6 | 2/6 |
| Selected-text edits exact | 7/7 | 7/7 | 7/7 |
| Focused prose word limits | 4/4 | 4/4 | 4/4 |
| Legacy dialogue word limits | 2/5 | 3/5 | 3/5 |
| Legacy Continue word limits | 5/7 | 5/7 | 3/7 |
| Legacy Rewrite word limits | 3/3 | 3/3 | 3/3 |
| Legacy Write word limits | 1/2 | 0/2 | 1/2 |
| Long repeated dialogue flags | 0 | 0 | 0 |

Word limits and exact labels are mechanical checks, not prose-quality scores. Editing has no minimum length. The repeated-dialogue proxy detects repeated long utterances, not every form of semantic repetition. There is no exact canonical-continuation quality metric.

The original object-selection control still returns the wrong register in valid JSON. Earlier [matched-question diagnostics](question-ablation-v18-2026-11-01.md) showed that explicit questions can make all models answer correctly; this failure does not establish universal inability to track objects or a JSON syntax problem.

## Seen training fit and limited prose observations

Five deliberately exposed repair prompts remain outside primary scores. Full-source restoration rises from **1/5 to 2/5**, and preservation outside the repair slot from **1/5 to 4/5**. Exact restorations are the lever and explicit-condition passages. The lexical-anchor proxy stays **3/5**. Slot correctness is 2/4 among candidate outputs that preserve surrounding prose, versus 1/1 for each reference; these conditional denominators must not be compared as an overall success rate.

The candidate restores the event time to “nine” but omits “sharp”; it restores the room material while altering other wording. Most seriously, the announced-visit repair retains the corrupted past event (“called upon you last night”) rather than restoring the future appointment. Better formatting preservation therefore does not establish reliable semantic editing.

Limited, informed AI inspection identifies both benefits and failures:

- The inventory rewrite falls from the craft model's **40 words to 24**, preserving the readable original, uninspected duplicate and missing agreement without repeated closing statements. This is a useful local improvement.
- The candidate's conservatory continuation is **30 words**, below the requested 60–90, and jumps to “Nabil still had not arrived by 09:15” rather than preserving the supplied current-time/future-arrival frame. The craft answer meets the length limit, though it also mostly waits rather than advancing the mystery.
- The reel continuation is **59 words**, just below the 60-word minimum; the craft answer is 82. This and the conservatory account for the two additional legacy continuation length failures. The new scene details require literary review rather than automatic treatment as resource violations in a prompt without a closed equipment list. Playback is not itself erasure.
- The courier dialogue still has seven turns and confusing conditional lateness wording. Missing original-alteration consent remains distinct from already allowed copy inspection. Completing the request and meeting its word cap do not make the dialogue a successful scene.

These are informed observations with model conditions known, not blinded ratings, a complete independent editorial review or a fiction-quality pass rate. No overall improvement or Muse equivalence is established.

## Evidence, review and scope

The **21-pair randomized writing packet** is `artifacts/source-training-v22/REVIEW.md`. It has **42 blank human ballots** for two reviewers; human quality ratings remain zero. The private answer key has mode 0600 and is excluded from publication. The creating AI already knows model conditions; future independent reviewers should keep the key separate. Seen-fit outputs are excluded from this packet.

Scripts are in `curation/source-training-v22/`. Training progress, actual worker configuration, frozen protocol, all responses, mechanical scores and completion/service markers are in `artifacts/source-training-v22/`. The new adapter is `artifacts/source-training-v22/adapter`; it requires the separately pinned base and is not a standalone model, signed installer or approved app package.

The read-only verifier checks frozen source/data/model and installed-code hashes, amended tokenizer metadata, actual worker-config equality, all response hashes, fresh-context/cache limits, training step/token/memory completion, recomputed mechanical row scores, separate evaluation cohorts, blank ballots and service state. Prior adapters, selected profile, source records, earlier experiments and human ballots retain their hashes. A tracked execution lock records evidence hashes without weights, response prose or private keys.

The full CPU foundation suite passes **242 tests in 70.728 seconds**, including three executor/scoring regression tests for resource caps, exposed/seen cohort separation and repetition flags independent of word limits. The suite runs after all model phases stop. Python compilation and the evidence verifier pass. These checks validate execution and scoring, not literary quality or app/native behaviour.

```bash
cd llm/Narratryx
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/source-training-v22/verify.py'); print(m['verify']())"
```

Next, review the paired writing packet before proposing more training. Prioritise the continuation regressions and the failed seen announced-visit repair, alongside the inventory improvement. Additional updates alone are not supported as the next quality strategy; broader task-matched demonstrations and independent literary review remain necessary evidence gaps.

Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no application source, prompt, configuration, default or generated-asset changes. No app builds or device tests are run. There are no paid/cloud jobs, corpus downloads, uploads, model publication or promotion. Ordinary users do not need local training; this Mac experiment does not certify Windows inference or production hardware requirements.
