# Tiny-set learning-path diagnostic — 1 November 2026

This follows the failed broad [v7 claim trial](arrival-claims-training-v7-2026-10-31.md). The user authorised the proposed check that the training process can learn a tiny teaching set before another broad run. Preparation began on 31 October UTC; the corrected execution is recorded separately under `artifacts/tiny-fit-training-v8b/`. This is an intentionally narrow learning diagnostic, not a literary-model upgrade, production release or app integration.

## Loss-path audit

The installed Unsloth worker recognises explicit labels and skips response-marker remasking for such pretokenised rows. Its MLX text loss shifts labels by one position and masks labels equal to −100. The trainer accumulates token-weighted gradients before optimiser updates. Source files are hashed in the local audit; no installed package files were edited or upgraded by this work.

A dynamic check passed all **12 real rows** through the installed `create_batches` function. Their input IDs and answer labels survive collation unchanged; prompt/padding labels remain masked, and the supervised count is **272 tokens**. A small fixed-logit test of the installed standard cross-entropy function counts two supervised positions: loss is **0.13920635**, stays unchanged when only masked-position logits change, and rises to **3.13920641** when answer labels change. This tests masking/target shifting without loading the four-billion-parameter model.

**Limit:** the dynamic loss control covers standard CE. Actual training uses runtime CCE. The labels-aware CCE source is inspected and hashed, but this control alone is not a dynamic gradient proof for the CCE kernel or the entire real-model pipeline. End-to-end fitting results below supply separate empirical evidence. Masked prompt positions are excluded as prediction targets; real prompt inputs still influence answer predictions.

## Frozen tiny-set experiment

The 12 unchanged structural examples are the same subset used in v7's seen-training probe: six predefined states from each of two source-schedule families, backed by the existing Doyle/Hopkins source spans. Existing GB/US training and evaluation uses were checked. Only dataset-version metadata changes; messages/targets/spans are preserved. No new books, rights grants, generated literary teaching targets, teacher model outputs or user manuscripts are used. The examples remain correlated task variants, not independent works.

The selected rows carry **272 unique supervised tokens** and at most **471 total tokens** per row. Four passes give **1,088 supervised-token exposures**. All prompts are masked and EOS retained. A separately named seen-monitor token file duplicates the teaching set; its loss is training fit, never held-out validation. The absence of prose examples is intentional isolation for this diagnostic, not a proposed replacement curriculum.

The run starts from the pinned cached Qwen3.5-4B MLX 8-bit base, not an earlier adapter. Unsloth 2026.10.10 uses LoRA rank 8/alpha 16/dropout 0, seed 42, batch 1/accumulation 1, learning rate 2e-4, two warmup updates, linear schedule and **48 maximum updates/four passes**. Relative to v7, several factors change together: isolated data, rate, accumulation and repetition. A positive result cannot identify which factor matters or establish an optimal recipe.

The same 10 GB reported-MLX/process-tree memory gates, warning/error/nonfinite gates and 20-minute training deadline apply. Seen-example inference has fresh single-user-message contexts, zero reported cached tokens, temperature 0, seed 42 and at most 96 output tokens. The base receives the 12 teaching prompts before training; the candidate receives them afterward. At least **10/12** exact generated answers is the predefined gate to run additional transfer diagnostics; it is a technical diagnostic threshold, not a literary-quality approval.

If the gate passes, 12 new state tuples are each presented with matched source context and standalone task state, for 24 candidate-only requests. They are different clock tuples from the tiny training set, but share its task/source families. The original plan did not include a fresh-base transfer comparison. After the candidate passed its fitting gate and showed promising transfer, a separate **post-hoc base control** was run on those same frozen prompts. Neither weights, prompts, scoring rules nor training parameters changed after seeing the candidate results. This is an exploratory comparison, not a preregistered confirmatory result or independent literary generalisation. If the seen gate had failed, the candidate transfer requests would have been skipped as planned.

## Corrected protocol and interrupted draft

The first draft had a correct executable 12-example/48-update request, but inherited descriptive metadata for the older 104-example/26-update mixture. The supervisor was interrupted when the mismatch was noticed. The interrupt arrived after **three completed updates were logged**, rather than before training as initially stated. No adapter weights were saved; only partial logs and row-bound metadata remain. Any in-flight work was not retained or resumed.

The draft files and frozen protocol remain intact under `artifacts/tiny-fit-training-v8/`. A new corrected protocol and separate `v8b` runner start again from the unchanged base; the old frozen evidence was not rewritten. A new consistency checker compares descriptive fields with actual request/preflight values, rejects the stale dataset/update counts, and passes for the corrected execution. Those checks are post-draft regression checks; they are not represented as having prevented the original error.

## Completed results

The corrected run completed **48 updates/four passes**, without warnings or errors, on the existing 12 examples. It reported **1,088 supervised-token exposures**, matching the prepared labels. The worker reported **241.9 seconds**; the full supervised training phase took **269.43 seconds**, at peak reported MLX memory **7.022 GB**. Seen-monitor loss fell through **0.061697 / 0.029592 / 0.010396** after the first three passes and reached **0.003318** at the end. Intermediate and final values are rounded from saved progress. This is training-set fit, not independent validation.

| Strict JSON exact-match diagnostic | Base | Trained adapter |
|---|---:|---:|
| Seen teaching prompts |1/12|12/12|
| New tuples with matched source context |0/12|12/12|
| Same new tuples as standalone task state |3/12|10/12|

The seen result is the planned fitting comparison. Both transfer base scores come from the separately labelled post-hoc control. The two transfer rows are the **same 12 tuples in two formats**, so the pooled candidate 22/24 versus base 3/24 must not be treated as 24 independent situations. All primary 48 responses and the additional 24 post-hoc control responses completed without errors or truncation, for **72 verified responses in the corrected experiment**. The interrupted draft's 12 baseline responses remain separate.

**The learning path works in this controlled setup.** The trained adapter fits all 12 teaching prompts and performs better on these narrow new-tuple diagnostics. This rules out a universally nonfunctional label/optimiser/adapter path for this configuration. It does not certify every loss/kernel mode or isolate why the earlier mixed recipe failed; rate, repetition, accumulation and task competition all changed. It also does not establish an optimal training recipe, broad arithmetic ability or literary-quality improvement.

There are no dialogue, pacing, voice or narrative-retention evaluations for this intentionally narrow adapter, and no human literary ratings. It must remain unselected and unpromoted. The next broad trial should retain source-prose teaching, monitor per-skill fitting/grounding and prose retention separately, and freeze new tests before training. The successful tiny recipe should not simply be declared safe or optimal for a full literary curriculum.


## Verification and practical limits

The [primary verification](../artifacts/tiny-fit-training-v8b/final-verification.json) and [combined primary/control verification](../artifacts/tiny-fit-training-v8b/combined-verification.json) passed. They verify the frozen inputs, exact response ordering/hashes and strict scores, correct adapter enable/disable conditions, zero reported cached tokens, context limits, 48 completed updates, 1,088 token exposures, saved adapter hash and memory/time gates. The real inference prompt-token counts also equal the masked training-prefix lengths for all seen examples. Base, selected craft manifest and protected prior artifacts remain unchanged.

The **176-test CPU suite passed in 107.574 seconds**, followed by four targeted checks (including two new protocol-consistency regressions). The targeted tests use self-contained fixtures and require no local corpus. New scripts compile. The consistency checks reject the stale draft description and accept the actual corrected request; they are added regression evidence, not claimed to have prevented the original issue. Source/link/whitespace checks also pass.

The diagnostic adapter and all responses remain local under `artifacts/tiny-fit-training-v8b/`. No model publication or application promotion follows from a fitting diagnostic. The earlier uploaded craft/v5/v6 artifacts remain unchanged. There is no new human literary-quality approval.


The base, selected craft manifest and all protected prior adapters remain unchanged. Legacy service state is preserved, with no unexpected activation. No paid jobs, corpus uploads, model-default changes, app-startup training or model promotion occur. The new diagnostic adapter remains local; existing uploaded model artifacts are not replaced.

All source changes are confined to Narratryx. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/configuration/default/generated-asset changes from this work. No app/device builds are needed or run for this isolated diagnostic. Ordinary users still do not need local training; Mac MLX execution is not Windows certification, an installer or Muse equivalence.

Read-only verification from `llm/Narratryx`, after completion:

```bash
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/tiny-fit-v8b/verify.py'); print(m['verify']()); print(m['verify_transfer_control']())"
```
