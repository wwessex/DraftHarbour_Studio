# Matched direct-question diagnostic — 1 November 2026

Adding a direct question changes entity selection from **5/16 to 16/16 for each of the base, current craft and mixed-v16 models**. All responses satisfy the JSON schema. This is a prompt effect on a narrow constructed test, with **no adapter advantage or training gain**.

This follows the [v17/v17b diagnostic](format-diagnostic-v17-2026-11-01.md). The new protocol was frozen before generating responses, but designed after seeing those earlier results; it is exploratory development evidence, not an independent benchmark.

## What changed within each pair

The 16 v17b backgrounds are reproduced exactly. They cross known-object identity, first-mentioned object, implicit versus explicit unknown legibility, and one versus two JSON fields. Each receives a second version with only this sentence inserted between facts and output instructions:

> Which register's legibility is unknown?

Facts, order, requested keys, allowed values and expected answers remain identical within each pair. No symmetric renaming or explicit known-inspection statement is added. Each question condition has eight original and eight duplicate targets. Cases run in a fixed shared sequence, with no-question then question within each pair; presentation order is not independently counterbalanced. Every call has a fresh single-message context and zero reported cached tokens.

For example, the original failed control asks for `unknown_object` and `original_readable` after “The original register is readable. A duplicate has not been inspected.” All three models again select `original` without the question, and correctly select `duplicate` with the question; both versions correctly return the readability Boolean.

## Results

| Metric | Base | Current craft | Mixed-v16 |
|---|---:|---:|---:|
| Entity correct without direct question | 5/16 | 5/16 | 5/16 |
| Entity correct with direct question | 16/16 | 16/16 | 16/16 |
| Schema compliant, all cases | 32/32 | 32/32 | 32/32 |
| Pairs correct in both versions | 5/16 | 5/16 | 5/16 |
| Pairs corrected by question addition | 11/16 | 11/16 | 11/16 |
| Pairs worsened by question addition | 0/16 | 0/16 | 0/16 |

Exact full-task correctness matches entity correctness, including the additional Boolean when requested. All 96 responses complete without request errors or truncation. No earlier response is reused. The no-question arm reproduces v17b's aggregate result on fresh calls; the question arm succeeds in every role/order/cue/field combination tested.

This isolates the effect of **adding this particular question in these contexts**. It does not isolate interrogative grammar from extra semantic information or repetition: explicitly asking about legibility clarifies what the otherwise underspecified `unknown_object` key means. It does not establish robustness across synonyms, distractors, other objects or long narratives. There are only two underlying logical role states, repeated across correlated cells, not 32 independent reasoning problems. Do not pool these results with earlier diagnostic phases or treat this as literary quality, Muse equivalence or production certification.

The previously unresolved naming and known-inspection differences are not necessary to obtain correct answers in this test. Further toggling of those differences is lower priority than testing whether explicit task questions help actual fiction workflows.

## Execution and evidence

The existing local cached base and adapters are used serially through the pinned engine, with thinking disabled, temperature 0, seed 42, repetition penalty 1.0, context limit 2,048 and maximum 64 output tokens. Tokenizer preflight passes before execution. Each condition unloads its model. Existing resource stops retain a 10 GB process-tree RSS ceiling, 20-minute phase deadline and immediate error/truncation stop without automatic retries.

The initially stopped legacy service remains stopped. Hash checks preserve the selected craft profile, base, adapters, prior experiment data, review evidence and blank human ballots. Prompts and generated responses are evaluation-only and ineligible for training. No source acquisition, new rights assertion or generated literary teaching target is added. Human literary ratings remain zero.

Scripts are in `curation/question-ablation-v18/`; cases and proposed protocol are in `artifacts/question-ablation-v18-plan/`. Responses, scores, counterexamples, environment and execution markers are in `artifacts/question-ablation-v18/`. `diagnostic.lock.json` records code/evidence hashes without publishing weights, response prose or private service state. The verifier recomputes row scores, question-arm totals and paired outcomes, validates exact within-pair differences, and checks prompt/protocol/response hashes, adapter identity, context/cache limits and service state.

The final full CPU foundation run passes **229 tests in 70.351 seconds**, including three new pair-balance, exact-change and scoring tests. The first concurrent run has one error among 229 tests: an existing early-runtime-exit fixture reaches its three-second startup deadline instead of observing the fixture exit. The full rerun with inference stopped passes without code or timeout changes; resource contention is a possible explanation, not a proven cause. Both test logs are retained in the external DraftHarbour cache. Evidence verification and Python compilation pass. These checks validate execution and scoring, not literary quality.

Read-only verification, without inference:

```bash
cd llm/Narratryx
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/question-ablation-v18/verify.py'); print(m['verify']())"
```

## Next work and application scope

Keep the selected craft model. Before another fine-tune, compare explicit task questions on a small representative set of Rewrite, Continue and dialogue tasks, including chronology, object ownership and permission constraints. Freeze original/clarified prompts and review prose quality alongside constraint compliance. Preserve original results and require human literary review before promotion. A clearer prompt succeeding is an inference-workflow improvement, not evidence that more training worked.

Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS have no source, configuration, default or generated-asset changes from this work. No app builds or device checks are run for this isolated diagnostic. There is no training, paid job, external inference, upload, publication or model promotion.
