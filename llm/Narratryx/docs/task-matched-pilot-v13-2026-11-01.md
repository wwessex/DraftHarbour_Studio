# Task-matched 25-example pilot — 1 November 2026

The user authorised the bounded pilot proposed after [complete-paragraph/dialogue preparation](paragraph-dialogue-v12-2026-11-01.md). It uses the frozen **25 training examples once each**, including 17 source-prose lessons and eight selection-safe structural editing controls. Four complete-scene targets were replaced by three exact next-paragraph targets and one three-turn dialogue-only exchange. Published answers remain source-derived; no literary teaching answer is generated. Sixteen previously exposed Wray records monitor loss, not independent literary quality.

## Frozen recipe and evaluation

Training starts fresh from the cached Qwen3.5-4B MLX 8-bit base through the local Unsloth MLX worker. The request caps training at **25 updates**, one epoch, batch 1/accumulation 1, learning rate 5e-5, two warmup updates, linear schedule, LoRA rank 8/alpha 16/dropout 0, seed 42 and 2,048-token context. There is no checkpoint resume or oversampling. Dataset and update-budget changes mean this is a candidate comparison, not a single-variable causal explanation of v9/v10 repetition.

Offline preparation audits the installed `create_batches` path: the complete input/label multiset matches all 25 intended presentations, prompts remain masked, EOS is retained and supervised training exposure is **2,298 tokens**. Maximum record length is 499 tokens. Original source spans, GB/US scope, author/work split boundaries and reserved alternative material remain unchanged. This checks existing rights records; it does not invent human approval or legal certification. Installed package versions match the pinned v10 environment: Unsloth 2026.10.10, MLX 0.32.4, mlx-lm 0.32.2, mlx-vlm 0.7.9 and default Transformers 5.5.0; the CLI selects its existing Transformers 5.3.0 compatibility tier for this base.

The evaluation plan makes **108 new requests**: 36 each for adapter-off base, current craft and the candidate. There is no reused response evidence. Each request contains one user message, no assistant history, zero reported cached tokens, temperature 0, seed 42, repetition penalty 1.0 and a 384-token output cap. The two controls run before training. Models unload between conditions. A warning, error, nonfinite progress, output truncation, 10 GB reported MLX/process-tree RSS limit or 20-minute phase deadline stops execution without automatic retry. The memory gates do not imply hardware certification.

Each condition receives the same ordered suite: twelve newly authored development cases first, then the 24 exposed v10 regression cases. The twelve cases share three constructed settings and are correlated diagnostics, not an independent human benchmark. They were unrun at freeze; after this evaluation they are exposed. Case prompts never become teaching targets. The suite includes nine new writing tasks, eight exposed writing tasks, seven exact selected-word edits, six clock states and six composite arrival claims. Editing has no minimum length; exact canonical continuation is not a fiction-quality score.

## Results

**Training completed all 25 updates, and all 108 evaluation requests completed without errors or truncation.** The training phase took 67.02 seconds including setup/save; worker-reported elapsed time was 38.78 seconds. Peak MLX memory was 6.92 GB. The worker recorded all 2,298 supervised-token exposures, no warnings/errors and exposed monitor loss 1.0808. That loss is not an independent quality rating.

| Diagnostic on this suite | Fresh base | Current craft | Candidate |
|---|---:|---:|---:|
| Complete responses | 36/36 | 36/36 | 36/36 |
| Truncated/error responses | 0 | 0 | 0 |
| Long repeated-dialogue flags | 0/5 | 0/5 | 0/5 |
| Exact clocks | 3/6 | 3/6 | 3/6 |
| Exact composite claims | 2/6 | 2/6 | 2/6 |
| Exact selected-word repairs | 7/7 | 7/7 | 7/7 |
| New dialogue word limits | 2/3 | 2/3 | 2/3 |
| New continuation word limits | 2/3 | 2/3 | 3/3 |
| New rewrite word limits | 3/3 | 3/3 | 3/3 |
| Exposed dialogue word limits | 0/2 | 1/2 | 1/2 |
| Exposed continuation word limits | 3/4 | 3/4 | 1/4 |
| Exposed scene-writing word limits | 1/2 | 0/2 | 1/2 |

The candidate completes the coat/reel dialogues without the v9/v10 repeated-line loops on those prompts. This is encouraging stability evidence for this small pilot, not proof that changing the dataset caused the difference: update count and the mixture also changed. Structured scores are unchanged, and improving one cohort's length compliance while worsening another's is not a general writing-quality gain. All figures are small development-case counts, not statistical evidence of population-level improvement.

## Writing inspection and review

An informed AI inspection after model conditions were visible finds ongoing semantic and instruction failures:

- Archive dialogue says there are ten minutes until 11:00 although the prompt states 10:20. Current craft also gets this interval wrong, saying five minutes. The candidate changes the error rather than solving it.
- Seed-label dialogue calls the supervisor late at 09:10 despite an expected 09:55 arrival. Current craft makes the same premature-lateness error. Candidate continuation correctly retains the future time but mostly pauses the action instead of advancing the practical problem.
- Candidate coat dialogue declares the untested lining too thin and predicts tearing. It has seven turns and 107 words against four–six turns and at most 100 words. It then supplies an agreement and a replacement-material plan instead of preserving the constrained problem.
- Candidate reel dialogue is shorter than current craft's overlong exchange and uses six distinct turns, but it changes the practical test into supervised playback and introduces master-copy language. Removing loops does not demonstrate resource/permission fidelity.
- Reel scene writing conflates the untested spare with the choir reel and invents Anika's need to recover her own voice. Its 150 words exceed the requested 90–130. The coat scene meets its word range but still confuses cutting a scrap with destroying original lining.
- Coat continuation contains two paragraphs despite the one-paragraph instruction and introduces an unestablished iron/tool kit. Conservatory and rope continuations have 48 and 50 words against 60–90. A word-limit pass alone would miss the coat's paragraph/resource failures.
- New rewrite answers retain several explicit constraints in restrained prose, but limited improvement in phrasing is not independently rated. New continuations sometimes turn permission uncertainty into an invented requirement for the absent supervisor's approval rather than finding an authorised next action.

These are AI observations, not blinded human ratings or an exhaustive gold-standard semantic score. Both controls have substantial flaws; the candidate is not promoted. The next useful step is to review the paired writing outputs and identify source-backed lessons for the persistent time/resource/permission failures before increasing updates or adding more repeated examples. The twelve new tasks are now exposed and must not be described as untouched tests in a later experiment.

The [paired writing packet](../artifacts/task-matched-training-v13/REVIEW.md) compares current craft and candidate responses only when both completed without truncation/error. A/B labels are independently randomised per case; the condition key is private mode 0600. There can be at most 17 writing pairs and 34 blank ballots for two reviewers. Missing outputs stay missing and are never presented as successful prose. Human literary-quality ratings remain zero.

Exact JSON/selected-edit matches, word-limit compliance and a repeated-dialogue-line proxy are reported separately. The proxy counts normalised dialogue bodies of at least six words repeated twice or more, ignoring named speaker prefixes and outer quotes. Deliberate repetition can be valid and formatting can evade the proxy; it is not an automatic literary verdict. No metric auto-selects this adapter.

## Validation and scope

The full CPU foundation suite passed **200 tests in 40.957 seconds**, including four new recipe/cap guards. The post-run verifier passed frozen dataset/token/protocol/code hashes, GB/US rights/split checks, base/prior/selected adapter hashes, actual training completion and supervised-token count, all 108 response prompt/protocol/adapter hashes, zero reported cached tokens, single-message contexts and untruncated responses. All models unloaded, and the initially stopped legacy service remains stopped. The writing packet contains 17 pairs and 34 blank human ballots; its condition key is mode 0600.

Python compilation, new-file whitespace and report-link checks pass. `verification.json`, `scores.json`, per-condition completion/hash markers and resource/phase logs preserve local evidence. The tracked `curation/task-matched-v13/execution.lock.json` records source/artifact hashes and dated results without literary quotations, credentials or model weights. The candidate adapter remains local and unpromoted. Human quality ratings remain zero.

Frozen data/tokens/request/cases are in `artifacts/task-matched-v13-plan/`; run evidence, responses and the candidate adapter are in `artifacts/task-matched-training-v13/`. Both remain local under ignored artifacts. Preparation, execution, resource guards, reporting and read-only verification are in `curation/task-matched-v13/`. Read-only verification after the run/report is complete:

```bash
cd llm/Narratryx
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/task-matched-v13/verify.py'); print(m['verify']())"
```

The legacy service's initial state is preserved. No selected profile, app-owned runtime, installer, manuscript store or release asset changes. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/default/configuration/generated-asset changes and no app/device build or runtime check. Mac MLX evidence does not establish Windows support, Muse equivalence or a production release. There is no cloud spending, remote inference, corpus upload, publication or model promotion.
