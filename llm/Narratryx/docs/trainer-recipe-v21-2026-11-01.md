# Installed trainer audit and bounded recipe — 1 November 2026

The installed Unsloth MLX preprocessing and batching functions preserve every example in the [28-record source proposal](source-candidates-v20-2026-11-01.md). A **28-update, one-pass LoRA recipe** and **147-request evaluation plan** are frozen. **No training worker, optimizer, inference request or model-weight load occurs.** This is preparation for a pilot, not a completed training run or evidence of improved fiction.

## What was actually checked

All 28 training records and 16 exposed Wray monitors are tokenized with the cached model's compatible tokenizer. Each answer round-trips exactly. Explicit labels mask every prompt and supervise the complete published answer plus one EOS. The longest record is **499 tokens** against a 2,048-token context limit.

The installed pre-tokenized-data preparation function is exercised on both complete splits, with the worker's MLX settings. It leaves tokens, labels and masks unchanged. The installed batcher is then exercised with batch size one, seed 42 and `append_eos=False`. Full token/label multisets match before and after batching, including multiplicity, so a duplicated record cannot conceal a missing record. All padding labels are ignored. There is no duplicated EOS or target truncation.

Training supervision totals **3,033 tokens**: 2,295 broader prose/revision, 695 semantic repairs and 43 structural controls. Validation supervision totals **1,709 tokens** across the 16 existing monitors. Validation records do not become training presentations.

The installed adapter's model/setup calls queue metadata. Its dataset call queues file configuration. These calls and worker-config construction are exercised without calling `start_training`; no training thread or event-pump thread starts. Static inspection of the pinned worker confirms the pre-tokenized branch uses supplied labels and disables extra EOS insertion for this SFT path. This is **not** an end-to-end training-worker dry run: model loading, optimizer construction, forward/backward passes, runtime memory and schedule execution remain untested for this proposal.

Environment versions match the prior pinned local setup: Unsloth 2026.10.10, MLX 0.32.4, mlx-lm 0.32.2 and mlx-vlm 0.7.9. The default Transformers installation reports 5.5.0; the cached model activates the separate compatible 5.3.0 tokenizer tier. Installed preprocessing, batching, adapter, CLI and worker source files are hash-pinned for revalidation before execution. Import-time platform messages are not represented as successful training or hardware certification.

Cached tokenizer, chat-template and model/processor metadata are pinned separately. All 44 token rows are reproduced exactly against those metadata pins, with hashes unchanged before/after that check. The full CPU foundation suite passes **239 tests in 72.305 seconds**, including four new recipe-cap, cohort, token-mask and record-multiset regression tests. The evidence verifier and Python compilation pass; no optimizer execution is implied by these results.

## Frozen training recipe

| Setting | Proposed value |
|---|---|
| Base | Existing cached Qwen3.5-4B MLX 8-bit snapshot, exact weight hash pinned |
| Adapter | Fresh separate LoRA; resume unset |
| Dataset | 28 unique records, one presentation each; no oversampling |
| Mix | 20 prose/revision, five semantic repairs, three structural controls |
| Validation | 16 previously exposed Wray monitors |
| Updates / epochs | Maximum 28 updates, one epoch |
| Batch / accumulation | 1 / 1 |
| Learning rate / warmup | 5e-5 / two steps; linear schedule |
| LoRA | Rank 8, alpha 16, dropout 0; same target modules as the prior pilot |
| Context / packing | 2,048 tokens / disabled |
| Seeds | Model, LoRA and training seed 42 |
| Save / evaluation interval | At update 28 |

The executable request and installed adapter's proposed worker configuration agree on paths, limits, masking and LoRA settings. The recipe changes dataset composition and update count relative to v16; it is not a single-variable experiment. No claim is made that 28 historical examples will deliver broad modern fiction quality or Muse equivalence.

## Evaluation and execution gates

The plan compares cached base, selected craft and a future candidate using **44 primary cases plus five separately labelled seen-training-fit cases per model**: 132 primary and 15 fit requests, **147 total**. All 44 primary cases have been exposed in earlier development; none is described as fresh or independent. Original prompt text is preserved. Five seen-fit prompts intentionally equal retained repair prompts and cannot establish generalisation.

Requests use one fresh user message, no assistant history or reported cached tokens, temperature 0, seed 42, repetition penalty 1.0 and a 384-token output cap. Tokenizer context checks pass for every planned prompt. Baseline responses are to be generated before training, with no earlier output reused.

Execution requirements are frozen with the recipe:

- Revalidate source, dataset, tokenizer, installed code, base and previous-adapter hashes and package versions before starting.
- Enforce the 28-update cap, reported MLX peak threshold of 10 GB, process-tree RSS cap of 10,000,000,000 bytes and 20-minute phase deadlines.
- Stop on training warnings, errors, nonfinite values, cap violations or evaluation errors/truncation; preserve partial evidence and do not retry automatically.
- Preserve a recognised legacy service's initial state and stop only the experiment's own children. Do not interrupt unrelated apps or their manuscripts.
- Score exact closed labels, selected-text preservation, length/paragraph/turn requirements and repeated-utterance flags separately. Record source-repair matches as seen fit, not fiction quality.
- Review chronology, claims, objects, permission/resources, progression, voice and dialogue aims separately from completion and mechanical compliance. Independent human literary review is required before promotion; human ratings are currently zero.

**These outer process/deadline checks require the future execution wrapper.** Passing the raw request to Studio does not itself enforce them. No pilot execution wrapper is launched by this preparation. A future run must stop if its environment or pinned inputs differ, rather than silently regenerate the frozen plan. No automatic model promotion, app prompt/default changes, paid/cloud execution, publication or upload is authorised by the recipe.

## Artifacts and verification

Scripts live in `curation/trainer-recipe-v21/`; recipe guards and regression tests are in `foundation/trainer_recipe.py` and `tests/test_trainer_recipe.py`. Local artifacts under `artifacts/trainer-recipe-v21/` contain:

- Explicit `train.tokens.jsonl` and `validation.tokens.jsonl` with prompt masks.
- `installed-audit.json`, including split counts, token totals and installed source hashes.
- `model-metadata.pins.json`, binding the cached tokenizer, template and configuration to the reproduced token rows.
- `request.proposed.json`, `worker-config.proposed.json` and `protocol.proposed.frozen.json`.
- Separately frozen primary and seen-fit case files and read-only verification results.

The tracked preparation lock records hashes and results; token datasets, model weights, private state and literary outputs remain outside Git. Existing source/rights decisions, prior experiments, selected profile, adapters, evaluation responses and blank human ballots retain their hashes. Generated evaluation fiction and notes remain outside training. No new rights clearance, source acquisition or author diversity is claimed.

Read-only verification, without model calls:

```bash
cd llm/Narratryx
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/trainer-recipe-v21/verify.py'); print(m['verify']())"
```

The next execution step is to bind this frozen plan to a new controlled pilot wrapper, check its guards, and run the bounded base/craft/candidate comparison. Completion will still be separate from literary improvement, and the selected craft model stays in place unless later evidence supports a reviewed replacement.

Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS have no source, configuration, default or generated-asset changes. No app builds or device tests are run for this isolated trainer audit. The installed Mac/MLX checks do not establish Windows training/inference support or production hardware requirements.
