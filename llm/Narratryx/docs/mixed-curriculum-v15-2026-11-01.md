# Mixed source-prose and repair proposal — 1 November 2026

The next pilot's selection is frozen as **22 unique training examples: 14 broader prose tasks, five semantic repairs and three structural editing controls**, each presented once. This follows the [semantic-repair preparation](semantic-restoration-v14-2026-11-01.md). It is a checked proposal, not a training run or a model-quality upgrade. All applications and the selected craft model remain unchanged.

The corrected proposal is `artifacts/mixed-curriculum-v15b/`. The first preparation draft is preserved under `artifacts/mixed-curriculum-v15/` with a withdrawal note and snapshots of its code. Neither draft trained or inferred a model.

## Selection and source balance

| Part | Records | Selection |
|---|---:|---|
| Broader prose | 14 | Retained scene/dialogue/pacing work, two author revisions and three complete-paragraph continuations. |
| Semantic repairs | 5 | Material assignment, lever direction, future announced visit, reception-versus-refreshment time and explicit consent to a condition. |
| Structural editing | 3 | Two duplicate-word repairs and one clean-target/outside-error no-change control. No minimum editing length. |
| Validation monitor | 16 | Previously exposed Wray records, still outside training. Not independent new quality evidence. |

Three prose variants are replaced: the Hopkins room description, Hopkins invitation and Opie explicit-condition scene receive their corresponding source-exact semantic-repair briefs. Two repairs use already scoped Doyle/Wells training material not otherwise selected in this mixture. Four semantic candidates remain reserved: deferred proposal, unanswered question, promise and chair-offer action. Their broader revision/continuation variants stay in the mixture instead of appending another presentation of the same scene.

Five overlapping editing variants are excluded: Doyle duplicate repair (its no-change variant is retained), Hopkins room duplicate repair (the semantic repair uses that source), Opie/Wells no-change variants (their repair variants remain), and the grammatical `had had` control (its James source is already represented by author revision). Historical candidates and tests are preserved; exclusion does not declare them bad lessons. A later release would still need dedicated grammatical-repetition and no-change evaluation.

Unlike the older 25-example mixture, no two selected training records have overlapping source intervals from the same underlying canonical source hash. Rights-record aliases cannot hide overlap. This means one selected source variant, not one passage per author or independent new source diversity. Source passages and works remain previously exposed material. The selection contains no newly generated literary answers and does not expand source rights. Existing GB/US rights/span and held-out author/work validation passes.

The [full proposal packet](../artifacts/mixed-curriculum-v15b/REVIEW.md) contains all selected prompts and source-derived answers. `selection.jsonl` records every retained, replaced, excluded or added record. All record content/provenance stays identical to its selected parent except the new dataset-version tag; monitors remain validation-only.

## Frozen preparation and proposed pilot

The cached tokenizer and installed Unsloth MLX collation path pass **22 one-time training presentations and 16 monitor records**. Answers round-trip exactly, prompt labels remain masked, EOS is retained, nothing truncates and the entire collated input/label multiset matches the intended examples. Maximum record length is **499 tokens** against 2,048.

Supervised exposure is **2,449 tokens**: 1,711 broader-prose tokens, 695 semantic-repair tokens and 43 structural-edit tokens, including EOS. Record counts and token exposure are different measures; repair answers are published prose but their task is minimal editing. No repetition is counted as added diversity.

The executable **proposed** request starts from the pinned cached base without checkpoint resume: 22 maximum updates, one epoch, batch 1/accumulation 1, learning rate 5e-5, LoRA rank 8/alpha 16/dropout 0, seed 42 and 2,048-token context. The request and descriptive protocol agree with the actual token counts and membership. This changes data and update budget relative to v13, so it is not a single-factor causal experiment.

Proposed gates retain the 10 GB reported MLX/process-tree RSS limits, 20-minute phase deadlines and stopping on warnings, errors, nonfinite progress or truncated diagnostic outputs. Fresh-context inference would retain temperature 0, seed 42, repetition penalty 1.0 and a 384-token output cap. These are a frozen plan; no runner or job has been launched, no service is paused and no model weights are loaded by the preparation.

## Evaluation separation

The primary suite has **44 cases: eight unrun semantic-transfer cases plus 36 exposed v13 regressions**. Primary prompts do not equal selected training prompts. No generated evaluation output is a teaching answer. The new cases have clearer permission/resource rules, but are cue-rich correlated development tests, not an independent human benchmark.

Five additional cases deliberately repeat the selected repair **training prompts**. They are labelled seen-training-fit diagnostics, scored separately and never pooled into transfer or literary-quality results. Their exact published references are legitimate for the expressly minimal repair task, not canonical answers to creative writing.

Three future conditions—base, current craft and a new candidate—would make **132 primary requests plus 15 seen-fit requests: 147 total**, all freshly generated. No responses are reused by the proposal. There is no planned fresh fourth v13-adapter condition, so historical v13 results would not become a matched new control for the eight new cases. Each condition has 49 requests. Maximum evaluation prompt length is 271 tokens, leaving room within the context cap.

Repair diagnostics separate exact full-answer correctness, preservation outside the corrected slot, correction at the slot when boundaries remain intact, and a lexical-anchor proxy. Anchor presence alone cannot rescue changed surrounding prose or added commentary. Human judgement remains necessary for free prose, permissions and practical action.

### Corrected preparation draft

During preparation, a scoring edge case was found: the deliberately wrong phrase can also legitimately occur elsewhere in the correct source. For example, window muslin must remain even when a mistaken bed-material assignment is repaired. The first lexical proxy wrongly required that phrase to disappear entirely. It now compares its occurrence count with the original answer; slot correctness and full-answer preservation remain separate checks. A regression test covers this case. The old draft/code snapshots and withdrawal reason remain local, and the corrected proposal is separately frozen as v15b. Neither version executed training or model inference.

## Verification and scope

The corrected full CPU foundation suite passed **209 tests in 39.119 seconds**, including five new source-overlap and repair-diagnostic checks. The final verifier passes selection identity, source-hash overlap protection, GB/US rights/splits, unchanged record content, monitor separation, all five deliberately seen diagnostic bindings, exact-answer scorer checks, token/collation hashes, request/update consistency and all 147 proposed-request counts. Original experiments, base weights and selected/prior models retain their pinned hashes. Python compilation and link/whitespace checks pass. The withdrawn first draft is not counted as a completed experiment. Human quality ratings remain zero.

Source preparation/preflight/verification scripts are in `curation/mixed-curriculum-v15/`; source-overlap and repair-diagnostic guards are in `foundation/mixed_curriculum.py`. Candidate prose, token files, frozen cases and proposed request/protocol remain under ignored `artifacts/`. A tracked preparation lock records corrected code/artifact hashes and dated checks without prose or weights. Read-only verification:

```bash
cd llm/Narratryx
.venv-foundation/bin/python curation/mixed-curriculum-v15/verify.py
```

Next is implementation/execution of this bounded pilot with the frozen scoring separation and resource gates, followed by writing review before any selection change. A prepared request is not training completion, a literary gain or approval to publish/promote a model. Human literary ratings remain zero.

Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/default/configuration/generated-asset changes, app builds or device/runtime checks. Manuscripts and app startup are untouched. No training, model inference, paid job, corpus upload, publication, source acquisition or model promotion occurred.
