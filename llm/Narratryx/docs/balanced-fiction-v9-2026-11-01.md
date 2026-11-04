# Balanced fiction and grounding trial — 1 November 2026

The user authorised the next balanced trial after the [tiny fitting diagnostic](tiny-fitting-audit-v8-2026-11-01.md) showed that the local Unsloth path can learn the existing structured examples. This experiment restores source-prose teaching and checks whether focused reasoning can coexist with fiction writing. Training completion, symbolic accuracy, instruction adherence and literary quality remain separate claims. The selected model and all application defaults stay unchanged; there is no automatic promotion.

**Outcome:** training completed, but the candidate repeated dialogue and hit the output cap. Evaluation stopped; the model remains unpromoted.

## Mixture and provenance

The dataset has **92 unique training lessons** plus **16 exposed Wray development-monitor records**. It keeps every one of the 80 original balanced lessons, including **56 source-prose lessons**, and adds the same 12 source-backed claim examples that fitted in the tiny diagnostic. It does not retain the other 12 claim variants from v7; it makes no claim that all 104 v7 training rows are present. The original messages, targets, source spans and review fields are unchanged; only common dataset-version metadata changes.

Each original lesson is presented once; each focused claim lesson appears four times. This yields **128 presentations and 128 optimiser updates**, not 128 independent examples or newly acquired passages. Training token rows explicitly repeat the 12 focus examples; the unique dataset records remain distinct. The prepared token-file order is recorded, but the installed Unsloth worker selects its own seeded `torch_randperm` sampler. Sequential blocks are not claimed as actual optimiser order.

The original prose contains directed writing, continuation, dialogue, pacing, storytelling, two genuine stylistic revisions and attributed historical craft explanations. All prose targets are existing source-derived answers; no generated literary teaching targets, teacher-model outputs, new books or user manuscripts are added. The focused claim targets remain deterministic JSON based on explicit constructed snapshots and unchanged source quotations. They do not turn hypothetical task states into original plot facts. Two correlated source-schedule families are not new literary diversity.

Existing exact-source/per-split GB/US validation passes against the existing scoped ledger. Reserved authors/works and the evaluation-only Wray monitor are preserved. No new rights approval, human consent or legal certification is invented. Raw source files, scans and review material stay local. This run does not download a bulk corpus, upload data or publish a replacement model.

The 128 presentations contain **10,173 supervised-token exposures**: **8,686 prose** and **1,487 structural**, approximately 85.4%/14.6%. By presentation count the split is 56 prose/72 structural; by unique lesson count it is 56 prose/36 structural. These different counts do not establish an optimal loss or gradient balance. The focused 12 lessons have 272 unique supervised tokens and 1,088 repeated exposures. All answers round-trip, prompts/padding remain masked and EOS is retained. The installed collation path preserves the full 128-row multiset and supervised count. Maximum total length is **1,882 tokens** in a 2,048-token context; no target is truncated. Editing gains no minimum length.

## Frozen recipe and evaluation

Training starts from the same cached Qwen3.5-4B MLX 8-bit base, not the tiny adapter. Unsloth 2026.10.10 uses LoRA rank 8/alpha 16/dropout 0, seed 42, batch 1/accumulation 1, learning rate 2e-4, two warmup updates, linear scheduling, one pass over the 128 presentations, and no packing. This carries over focused-task repetition and single-example updates from the successful diagnostic while restoring all 80 retained lessons. It is not a single-factor ablation; success/failure cannot be attributed to one changed parameter or used to declare an optimal recipe.

The coherent plan is checked against the actual executable request before model loading. New tests distinguish unique lessons from repeated presentations and reject stale counts/caps. Existing data, the selected craft pin, base and prior adapters—including the tiny proof—are hash-protected. Stop gates remain a 10 GB reported MLX/process-tree memory cap,20-minute whole-training deadline,128-update maximum and warning/error/nonfinite failures. No paid/cloud job or model-default change is authorised by this experiment.

The comparison freezes **72 primary cases per condition** before inference: **48 fresh diagnostics** and **24 exposed writing-retention regressions**. Fresh diagnostics comprise 12 clock states,12 composite claims,16 temporal prose-transfer cases, and 8 non-temporal dialogue/pacing/continuation/scene-writing tasks. The new structured schedules differ from the training/tiny proof families. The new prose inputs are original AI-authored evaluation situations, never training answers or human-approved benchmark gold. Their constraints include limited materials and missing consent, not only clocks or Story Bible use.

Base and current-craft baselines must complete before training. The balanced candidate also receives **36 exposed tiny-proof checks**:12 teaching prompts and 12 old transfer tuples in two formats. Those extra checks test retention of the narrow learning result; they are not fresh independent tests. Planned responses total **252**:72 base,72 current craft and 108 candidate. The primary three-condition comparison covers 216 responses;36 candidate-only extras are reported separately.

Each request has one user message, no assistant history, zero reported cached prompt tokens, temperature 0 and seed 42, with at most 384 new tokens. Errors, truncation or context overflow stop the run. Strict JSON checks reject wrong fields/types/values and duplicate keys; exact selected edits ignore surrounding response whitespace only. Word counts and quotation-block counts are proxies, not literary-quality ratings. Unchanged requested rewrites are recorded as an exploratory instruction-adherence diagnostic, not a literary score. Canonical continuations are not gold answers.

## Completed training; failed evaluation stability gate

All **128 training updates** completed without warnings or errors. The worker reported **463.6 seconds**; the whole supervised training phase took **493.03 seconds**. Reported peak MLX memory was **9.856 GB**, below the 10 GB stop threshold but materially above earlier small runs. The expected **10,173 supervised-token exposures** were reported. Final exposed Wray monitor loss was **1.021717**; this is not literary-quality evidence.

The evaluation did **not** complete. Both baselines finished 72 requests each. The candidate produced 44 complete responses, then repeatedly emitted the same coat-dialogue sentence until its 45th request reached the **384-token cap**. That output had 297 whitespace-counted words against a 100-word limit,18 labelled speaker lines and 16 exact repetitions of one line. The configured truncation gate stopped the run and unloaded the model. No output cap was raised, no partial answer repaired, and no automatic retry occurred.

There are **189 attempted primary responses:188 complete and 1 truncated**. The candidate's remaining **27 primary cases** (three new coat tasks plus all 24 older writing regressions) and **36 extra exposed grounding checks** were **not attempted**. This is not the planned 252-response benchmark; no overall prose-retention or tiny-grounding-retention pass can be claimed.

The table compares only the identical 45 attempted cases across all three conditions, including the truncated response as a failure. Fresh structured and temporal-prose cohorts happened to complete before the failure; the five attempted craft cases are only a prefix of the eight-case craft cohort.

| Same attempted cases only | Base | Current craft | Candidate |
|---|---:|---:|---:|
| Fresh clock JSON exact (12) | 6/12 | 6/12 | 8/12 |
| Fresh claim JSON exact (12) | 4/12 | 4/12 | 9/12 |
| Fresh selected repair exact (4) | 4/4 | 4/4 | 4/4 |
| Fresh analysis ≤70 words (4) | 4/4 | 4/4 | 4/4 |
| Fresh rewrite ≤90 words (4) | 4/4 | 4/4 | 4/4 |
| Fresh temporal continuation 60–90 words (4) | 2/4 | 3/4 | 0/4 |
| Attempted craft dialogue ≤100 words (2) | 0/2 | 1/2 | 1/2 |
| Attempted craft pacing ≤85 words (1) | 1/1 | 1/1 | 1/1 |
| Attempted craft continuation 60–90 words (1) | 1/1 | 1/1 | 1/1 |
| Attempted craft scene writing 90–130 words (1) | 0/1 | 0/1 | 0/1 |

Structured accuracy improves on the completed diagnostic cohorts, but temporal continuation length compliance worsens and the candidate fails the writing stability gate. Word/format passes cannot rescue repetitive or unhelpful prose. The underlying per-case data is in [partial-scores.json](../artifacts/balanced-training-v9/partial-scores.json). Missing requests are explicitly unattempted, never counted as successes.


## Review and preservation

The original plan called for a 48-case prose packet. Because evaluation stopped early, only completed partial evidence is available; the details and links below explicitly distinguish that subset. No human literary ratings or approvals are invented. Named-condition observations are informed AI inspection, not blind/independent/human judgement.

### Informed AI observations, not human quality ratings

The symbolic gain does not reliably transfer into prose. The candidate calls Nabil late at 08:35 despite a 09:15 expectation, and calls Emil late at 14:25 despite 15:10. Its rope-workshop and print-shop analyses instead report no qualified inference, avoiding the unsupported lateness claim in those cases. This is limited case evidence, not a formal literary-quality score.

Writing regressions are visible before the fatal truncation. The reel dialogue repeats the same utterance in all six turns, merely alternating Jules and Anika, erasing their distinct aims despite satisfying the word limit. The pacing answer copies the supplied paragraph unchanged. The 64-word scene-writing answer largely restates the premise and misses its requested 90–130-word range. The continuation copies the provided context before adding action, contrary to the request for only a new paragraph. Mechanical counts alone would miss several of these failures.

The [failed coat case](../artifacts/balanced-training-v9/TRUNCATED-CASE.md) is saved separately and identified as truncated; it is not presented as a completed blind response. **Do not promote this candidate.** Broad prose quality and retention are not established, and generation stability has failed.

### One separate post-hoc repetition diagnostic

After the original evaluation stopped, one isolated request used the exact same failed prompt and weights with repetition penalty 1.1 instead of 1.0. Temperature 0, seed 42, the 384-token output cap and 10 GB process-memory gate were retained. Only a private inference-object wrapper changed; installed files, the frozen engine and app defaults were not edited.

The probe ended normally at 123 completion tokens, with 92 words and five named speaker lines. Maximum exact-line repetition fell from 16 to 2. However, two Cora/Devin turns still repeat verbatim and the exchange remains unconvincing. This shows decoding sensitivity, **not a quality fix**. Word/turn proxies pass in this single request, but the original failed benchmark remains failed; none of the 63 missing candidate requests was filled. The [probe result](../artifacts/balanced-training-v9/repetition-probe.complete.json) is additional post-hoc evidence, not part of the 189 primary attempts.

The next useful investigation is a small, preregistered stability ablation—for example, hold the mixture fixed and reduce adaptation strength—checking both grounding and dialogue/continuation before another full run. Decoding controls can be tested separately. This trial changes multiple factors from earlier recipes and does not isolate the cause of degeneration; simply raising output limits or promoting the isolated decode probe would be unjustified. No additional training experiment was launched after the failure.


The [partial-evidence verification](../artifacts/balanced-training-v9/partial-verification.json) passes **integrity checks**, not the experiment's quality gate. It verifies 128 completed updates,92 unique lessons/128 presentations,10,173 token exposures, both complete baselines, the exact 45-row candidate prefix, the single truncation, response hashes/context/cache conditions, unchanged frozen inputs/base/previous models and preserved initial service state. The legacy port-8890 service remains stopped. No candidate-complete or experiment-complete marker was fabricated.

**182 CPU foundation tests passed in 174.229 seconds**, including four new metadata/exposure/resource regressions. The full scripts compile; completed-evidence checks are read-only. The ordinary full-review/full-verification scripts still require a complete 252-response run and were not weakened to accept this failed evaluation.

Only a [partial blinded packet](../artifacts/balanced-training-v9/PARTIAL-REVIEW.md) was generated for the 20 complete candidate prose cases, with 40 blank human ballots and a private mode 0600 condition key. The [eight-case starting subset](../artifacts/balanced-training-v9/QUICK-PARTIAL-REVIEW.md) uses completed cases only. The planned full 48-case/96-ballot packet does not exist. Human literary-quality ratings remain zero. The new adapter is saved locally and unselected; prior uploaded models are unchanged.


All changes are confined to Narratryx. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/configuration/default/generated-asset changes from this work. No app/device builds are needed or run. The applications do not import this training workspace or train on manuscripts at startup. Mac MLX evidence does not certify Windows/Linux execution, installer readiness, ordinary-user hardware or Muse equivalence. Existing uploaded craft/v5/v6 artifacts are not replaced.

Read-only saved partial-evidence verification from `llm/Narratryx` (this does not declare the experiment complete):

```bash
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/balanced-fiction-v9/verify_partial.py'); print(m['verify']())"
```
