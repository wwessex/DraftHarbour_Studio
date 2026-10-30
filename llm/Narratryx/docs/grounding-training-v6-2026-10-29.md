# Learning-rate ablation and model archive — 29 October 2026

Training/evaluation ran on 29 October UTC; final v6 remote-download verification completed on **30 October 2026 UTC**.

The user explicitly requested repository upload of the custom model and the next training step. This work archives actual adapter weights and runs one bounded local learning-rate comparison. Neither operation promotes a model or changes application defaults. The previous recommendation for human review is not represented as a completed review; human literary-quality ratings remain zero.

## Verified model upload

The public [experimental GitHub release](https://github.com/wwessex/DraftHarbour_Studio/releases/tag/narratryx-experimental-2026-10-29) contains the existing craft adapter and completed grounding-v5 adapter, plus ZIP checksums. Model metadata and the allowlisted package builder are pushed on `codex/narratryx-model-archive`; unrelated application work is excluded from those commits. Large binaries are release assets, not ordinary Git blobs or pointers to absent local files. The prerelease is explicitly excluded from the latest production release designation.

The [model card and manifest](../models/experimental-2026-10-29/README.md) identify the exact separately required Qwen3.5-4B MLX 8-bit base, its revision and hashes, adapter/configuration hashes, training status and limitations. Each ZIP contains only `adapters.safetensors`, `adapter_config.json`, card, manifest, upstream Apache-2.0 licence and modification notice. No raw source books, training records, scans, evaluation answers, manuscripts, credentials, private reviewer keys, base weights or executable runtime are uploaded.

Both assets were downloaded again from GitHub. ZIP hashes, ZIP integrity and extracted weight/configuration hashes matched. The [upload verification](../models/experimental-2026-10-29/upload-verification.json) records the actual remote evidence. The original craft adapter SHA-256 is `09f950e0954105b4b5bf1cdd5c7a4ee882d617742aadad6ec33c1dda5af84688`; grounding-v5 is `a3ceee1009b0744df22f544ab837223b2e267b10efd6c97f19e295917cf421f3`.

The pinned quantised base card identifies Apache-2.0 and Qwen/Qwen3.5-4B. The full upstream licence is included with attribution and a notice of training modifications. Existing source-rights records remain unchanged: their earlier local-only authorisation is not claimed to have authorised publication. The user's present request authorises publication of these model artifacts, not corpus redistribution. Underlying selected original prose was assessed within the documented GB/US scope; no human legal certification or blanket worldwide clearance is invented. The archives remain research artifacts, not complete apps or Windows installers.

## One changed training parameter

The [archived v5 trial](../models/experimental-2026-10-29/README.md) completed safely but showed no clock-state accuracy gain and persistent unsupported temporal/attribution claims. Instead of treating those results as approval or adding generated literary targets, v6 tests one parameter: **learning rate 5e-6 → 5e-5**. This is a controlled diagnostic of update strength, not an established optimal rate or a promised quality improvement.

The exact v5 request is copied; the execution wrapper checks that `learning_rate` is its only changed key. All 80 training records, 16 exposed Wray monitor records, source-rights ledger, token order, prompt/answer masks, base, LoRA rank 8/alpha 16/dropout 0, seed 42, batch 1/accumulation 4, context 2,048, maximum 20 updates, one epoch, linear scheduler and no packing remain fixed. Training is fresh-base, not stacked onto the previous adapter. The 9,085 supervised tokens still comprise 8,686 source-prose and 399 structural tokens. The low structural token share is acknowledged, not changed in this experiment.

Execution scripts require the frozen local datasets and prior-run inputs; this publication does not make training replayable from a clean clone alone. Inference uses the published adapter and pinned base without local training.

The new runner pins its execution inputs and protects prior adapters/configuration, including the v5 adapter, completion and protocol. Both 64-case base/current baselines must complete before training. The same 10 GB MLX-peak and subprocess-RSS gates, warning/error/nonfinite stop conditions, 20-update cap and 20-minute whole-training-phase deadline apply. No paid jobs, remote training, uploads of corpus material, downloads of additional books, synthetic literary teaching answers or app integration are added.

All 64 evaluation cases are **now exposed diagnostics**, reused for this paired comparison. The `new-clock` and `new-prose-transfer` role names identify their original v5 cohorts, not current novelty or independent benchmark status. Fresh one-message contexts, zero reported cached tokens, temperature 0, seed 42 and at most 384 generated tokens are retained. Fresh baselines are rerun rather than assumed; base answers reproduce v5 exactly in all 64 cases. A higher score on these reused cases alone cannot establish generalisation or literary improvement.

## Completed results

All **20 updates** completed without warnings or errors. The worker reported **275.6 seconds**; the whole supervised training phase took **299.89 seconds**. Reported peak MLX memory was **7.167 GB**. Development loss was **1.084245** at update 10 and **1.056323** at update 20, versus the previous trial's final reported **1.147302**. The lower loss is on the exposed Wray monitor and is not independent quality evidence.

All **192 responses** completed without errors or truncation, with one-message fresh contexts, zero reported cached tokens and no context overflow. The new base and current baselines reproduce their previous answers exactly, 64/64 each. Roles below are the original cohorts; every case is now exposed.

| Diagnostic cohort/check | Base | Current craft | v5 | v6 |
|---|---:|---:|---:|---:|
| Clock JSON exact (24) | 6/24 | 6/24 | 6/24 | 5/24 |
| Selected repair exact (4) | 4/4 | 4/4 | 4/4 | 4/4 |
| Analysis ≤70 words (4) | 4/4 | 3/4 | 3/4 | 3/4 |
| Rewrite ≤90 words (4) | 4/4 | 4/4 | 4/4 | 4/4 |
| Continuation 60–90 words (4) | 2/4 | 3/4 | 2/4 | 1/4 |
| Retention repair exact (4) | 4/4 | 4/4 | 4/4 | 4/4 |
| Retention dialogue ≤100 words (4) | 3/4 | 1/4 | 1/4 | 4/4 |
| Retention 4–6 dialogue blocks (4) | 4/4 | 4/4 | 4/4 | 4/4 |
| Retention pacing ≤85 words (4) | 4/4 | 4/4 | 4/4 | 4/4 |
| Retention continuation 60–90 words (4) | 3/4 | 4/4 | 4/4 | 3/4 |

The paired comparison finds **zero clock fail→pass changes and one pass→fail change**; all eight exact repairs are stable. Among the 32 cases with actual word bounds, three failures become passes and two passes become failures. Dialogue quote-block compliance is stable. These are format/task checks, not a combined quality score. Editing retains no minimum length. Full local per-case evidence is in [scores.json](../artifacts/grounding-training-v6/scores.json) and [paired comparison](../artifacts/grounding-training-v6/paired-v5-v6.json).


## Human review and next decision

The [v6 blinded packet](../artifacts/grounding-training-v6/BLIND-REVIEW.md) and [eight-case starting packet](../artifacts/grounding-training-v6/QUICK-REVIEW.md) randomise condition labels per case. Eighty blank ballots support two reviewers; the key stays separate with mode 0600. There are no invented human ratings. The packet compares base/current/v6, while the mechanical report also compares v5 on the same cases. Prospective reviewers should use blinded material before reading the named-condition observations below.

### Informed AI observations, not blind/human ratings

All four original prose-transfer analyses still incorrectly call an expected visitor late before their stated arrival time. The canal analysis calls Ivo late at 10:35 despite the 11:20 expectation, then says not to assume lateness. Saffron still incorrectly calls Lin late and attributes the label to her; kiln still invents that Niko was the last person present.

The lost clock case is `ge-clock-test-07`: the state remains `not_established`, but v6 returns **+15** rather than the required **−15** minutes. Its previously correct v5 response returned −15. This is an arithmetic-sign regression, not a JSON whitespace or key-order penalty.

A post-hoc exact comparison also finds **three of four transfer rewrites repeat the source paragraph unchanged**, contrary to their explicit rewrite instruction. This preserves times but fails the requested transformation. New continuation length compliance falls from v5's 2/4 to 1/4. Retention dialogue brevity rises from 1/4 to 4/4, while retention continuation length falls from 4/4 to 3/4. These mixed results do not establish more compelling dialogue, pacing, voice or storytelling.

**Do not promote v6.** Lower development loss did not fix the targeted reasoning failures, and several regressions remain. A further blind increase in rate or duration is unsupported. The next curriculum experiment should target the failed distinction itself—for example, source-grounded claim/contradiction labels connecting current time, scheduled time and uncertainty—while retaining prose craft supervision and respecting the exclusion of generated literary teaching targets. Freeze new situations before that experiment, and obtain independent prose review before selecting a model. This suggestion is not another launched run.


The [final verification](../artifacts/grounding-training-v6/final-verification.json) passed: 192 matched responses, 20 steps, 9,085 supervised tokens, saved adapter hash, 80 training/16 monitor records, resource limits, unchanged frozen inputs/base/protected prior artifacts, initial service state preserved and 80 blank human ballots. It also checks that learning rate is the request's only changed key. **166 CPU foundation tests passed in 162.822 seconds** during the fresh run. New execution, packaging, review and comparison modules compile; report links and source whitespace checks pass. The paired comparison verifies actual baseline reproduction rather than assuming it. No human quality approval is recorded.

The [v6 model archive](../models/grounding-v6-2026-10-29/README.md) publishes the completed adapter separately as a research artifact, including its regressions; the selected craft model is not replaced. Model publication is authorised by the user's current instruction and is distinct from production promotion. The v6 ZIP was downloaded again from its public prerelease, and ZIP integrity, ZIP checksum and embedded weight/configuration hashes passed; see the [dated remote verification](../models/grounding-v6-2026-10-29/upload-verification.json). Evaluation responses and private review keys remain local.


The selected craft profile, all application defaults, cached base and protected previous adapters remain unchanged. The legacy port-8890 service was initially stopped and remains stopped; no experiment restores it into a state it did not previously have. Training/data preparation remain outside application startup and manuscript storage.

Recheck completed evidence without training or inference from `llm/Narratryx`:

```bash
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/grounding-training-v6/verify.py'); print(m['verify']())"
```

This is isolated Narratryx research and artifact publication. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source, configuration, defaults or generated-asset changes from this work. No app builds or device acceptance checks are needed or run. Apple Silicon MLX results do not certify Windows/Linux inference, user hardware, installers or Muse-equivalent quality. Ordinary users still do not need to train a model.
