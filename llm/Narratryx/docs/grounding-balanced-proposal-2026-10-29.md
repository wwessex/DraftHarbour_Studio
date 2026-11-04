# Reviewed grounding/prose proposal — 29 October 2026

**The semantic review and balanced proposal are complete; training has not started.** The frozen selection contains **80 prospective training records: 56 retained prose lessons and 24 structural lessons**, plus the same 16 exposed Wray development-monitor records. All inputs fit the 2,048-token allowance without truncation. No generated literary teaching answer, model promotion, service action or application change occurred.

This follows the [179-lesson preparation](grounding-editing-curriculum-2026-10-29.md), preserving that packet, its one-record grammatical supplement, earlier evaluations and all model artifacts. The proposal is an experiment specification, not a claim that the model has learned better factual discipline or fiction writing.

## Semantic decisions

All 24 evidence annotations received an **informed Codex AI review of its own annotations**, not an independent, blinded or human assessment. Twenty-three retain their original messages. One promise example was clarified: instead of classifying Jim’s reassurance about starvation, it now classifies his explicit offer to help later in the same passage. The `plan` label remains; only the classification quotation and corresponding evidence string change. The source body and source spans are unchanged.

The [recorded decisions](../curation/grounding-balanced-v1/review-decisions.json) describe the interpretation of each category: unqualified narration within the supplied fiction, character claims, plans/promises, requests, hypothetical content, qualified inference, hearsay and information the excerpt does not establish. Exact quote membership is machine checked; that does not prove semantic labels correct. No human gold, preference ranking or literary-quality score has been invented.

The revised records live in `semantic-reviewed.records.jsonl`. Original annotations and earlier dated approvals are untouched. The selected eight evidence lessons cover every category, across several excerpts and authors. These symbolic answers and copied evidence quotations remain distinct from generated creative prose, which is excluded under the current scope.

## Fixed mixture

| Component | Records |
|---|---:|
| Directed writing |25|
| Continuation |8|
| Dialogue exchanges |8|
| Pacing |3|
| Storytelling / structural alternative |2|
| Genuine stylistic revisions |2|
| Attributed historical craft explanations |8|
| Selected duplicate-word repair |4|
| Unchanged selected text, including grammatical repetition |4|
| Reviewed evidence classification |8|
| Constructed clock states |8|
| **Total** |**80**|

The first 56 are retained prose messages, unchanged from previous validated datasets, with 56 distinct normalised supporting passages. The two genuine revisions retain their explicit permission to change stylistic emphasis; the Dickens alternative ending explicitly changes circumstances. They are not minimal-copyedit gold. The eight historical craft explanations are attributed original author text, not new gold analyses of unseen stories.

The structural sample retains four repairs and four unchanged cases, including the valid James “had had” construction; all eight semantic categories; and pending, due-now, overdue, arrived and unknown-arrival clock states. Repeated schedules and matched edit pairs remain correlated examples, not independent story worlds.

No work exceeds 24/80 record credits. The largest is Opie at 22/80. Multi-work and historical editorial credits can overlap; they must not be summed as additional examples or independent authors. The 70/30 prose/structural row split is a hypothesis to test, not an established optimal ratio. Its **supervised-token** split is very different: 8,686 prose tokens and 399 structural tokens, approximately 95.6%/4.4%. Token shares alone do not establish gradient influence or an optimal balance.

No source book was newly acquired or newly cleared. Sources and much of their prose have been used in earlier experiments. This proposal adds task-specific supervision and retention balance; it does not create new literary diversity by changing prompts.

## Preflight and frozen execution proposal

Offline tokenizer checks passed for all 96 training/monitor records: maximum **1,882 tokens**, **9,085 supervised training tokens**, exact answer round trips, explicit EOS, prompt tokens masked and no target truncation. Training token rows are deterministically shuffled with seed 42, with their record order preserved in the preflight report. Contributor token credits are recorded, including overlapping historical editorial transmission. No contributor exceeds the experimental 40% supervised-token cap.

The [proposed frozen protocol](../artifacts/grounding-balanced-v1/protocol.proposed.frozen.json) and `request.proposed.json` specify a future local fresh-base LoRA trial: rank 8/alpha 16, learning rate 5e-6, seed 42, batch 1/accumulation 4, context 2,048, one epoch and **at most 20 updates**. Proposed stop conditions remain 10 GB reported MLX peak, 20 minutes, warnings/errors or nonfinite training metrics. These are proposed limits, not evidence of enforcement or successful training at this recipe.

A separately verified execution wrapper is still required. The old eight-update runner must not silently execute the new 20-update request. Both base/current-craft baselines must complete before training, conditions must run serially in fresh contexts, and no paid job, upload or automatic promotion follows from this preparation. The 16 Wray records are the old exposed development monitor, not an independent project-wide quality test.

## Evaluation boundaries

The [40-case frozen evaluation](../artifacts/grounding-balanced-v1/evaluation.cases.frozen.jsonl) preserves the prepared 24 deterministic clock states and 16 prose-transfer cases across four new fictional situations. Clock tuples are disjoint from training, but the parametric task family is familiar; closed JSON correctness is not literary quality. Prose cases test selection boundaries, unsupported attribution, chronology and continuation while preserving names and unresolved facts. No new model responses exist for this proposal.

The protocol also binds the prior 24-case/eight-situation diagnostic as an **exposed retention regression**, never as a new benchmark. A full proposed comparison therefore has 40 new diagnostic cases plus 24 exposed regressions per condition. Errors, truncations, JSON accuracy, exact repair, format checks and semantic/literary judgements must be reported separately. The original formal benchmark remains a draft; this packet does not create human-approved benchmark or rubric clearance.

## Verification and practical limits

**160 CPU foundation tests passed in 97.928 seconds**, including six new distinct-source selection and semantic-review guards. Dataset schema, exact source offsets, appropriate per-split GB/US rights uses, source-group/author separation, prior evaluation overlap screens, held-out clock tuples and explicit loss masks passed. The frozen [mixed-use ledger](../rights/grounding-balanced-v1.scoped.jsonl) retains the existing decisions; do not apply an all-records training-use check to its evaluation-only Wray source.

The review audit confirms 23 unchanged annotations, one clarified query/evidence pair and unchanged source bodies/spans. The base weight hash, 16 protected adapter/configuration files, selected model pin and 21 earlier execution input files verify unchanged. No model weights were loaded for preflight, no inference/training ran and no AI service was started, stopped or restarted.

One validation read stalled on the existing review-generator script. After requesting local availability with Apple’s [FileManager download API](https://developer.apple.com/documentation/foundation/filemanager/startdownloadingubiquitousitem(at:)), the read completed and its original frozen hash matched. No source file was overwritten, evicted or removed, and no account or sync settings changed. This observation does not establish a definitive filesystem root cause. The completed checks above are actual runs, not assumptions based on the stall.

Verify from `llm/Narratryx`:

```bash
.venv-foundation/bin/python curation/grounding-balanced-v1/build.py verify
.venv-foundation/bin/python -m unittest discover -s tests -v
```

The [builder](../curation/grounding-balanced-v1/build.py), [selection helper](../foundation/balanced_curriculum.py) and [token preflight](../curation/grounding-balanced-v1/preflight.py) use existing pinned local inputs and refuse to replace outputs. Raw teaching quotations, token rows and review material remain local and ignored by Git. Human literary-quality ratings remain zero. A model upgrade can only be decided after actual comparisons; a better structural score alone is insufficient.

All source changes are confined to Narratryx. Web/PWA, Tauri Windows/Linux, Capacitor iOS and independent native macOS received no source/configuration/generated-asset changes; no app/device builds were needed or run. The temporary Swift filesystem call was not a native app build or launch. Ordinary users still do not need local training or these research dependencies.
