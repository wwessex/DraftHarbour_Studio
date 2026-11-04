# Entity-binding format and wording diagnostic — 1 November 2026

Two separately frozen **evaluation-only** phases generated **123 fresh-context responses** using the existing base, selected craft and mixed-v16 models. No weights were trained or changed. **JSON syntax is not the main observed failure:** all models can produce the requested format while selecting the wrong object. None of the adapters outperforms the base on these small tests.

This follows the [21-pair review](mixed-training-v16-ai-review-2026-11-01.md). Results support investigating task specification before more fine-tuning; they do not establish a literary-quality improvement, a general reasoning score or a single confirmed cause.

## Phase 1: balanced question/format test

Twenty-four variants cross two known-object roles, two fact orders, two direct questions and three response formats. Every combination appears once. Facts explicitly name both registers, state that one has been inspected and is readable, and state that the other's legibility is unknown. Questions ask either which register's legibility is unknown or which has not been inspected. Formats are a single entity word, JSON with an `answer` key, and JSON with an `unknown_object` key. Answer-choice order stays original then duplicate; expected target identity is balanced, but choice-order effects are not independently tested.

The exposed original prompt is regenerated separately as a control. It does not include the same direct question or explicit fact wording and requests two fields, including a readability Boolean. Its prompt is unchanged; the generation cap here is 64 tokens rather than the earlier 384. Every response ends normally below the cap.

| Phase 1 metric, per model | Base | Current craft | Mixed-v16 |
|---|---:|---:|---:|
| Entity correct on balanced variants | 24/24 | 24/24 | 24/24 |
| Format compliant on balanced variants | 24/24 | 24/24 | 24/24 |
| Single-word format entity correct | 8/8 | 8/8 | 8/8 |
| JSON `answer` entity correct | 8/8 | 8/8 | 8/8 |
| JSON `unknown_object` entity correct | 8/8 | 8/8 | 8/8 |
| Original control entity correct | 0/1 | 0/1 | 0/1 |
| Original control format compliant | 1/1 | 1/1 | 1/1 |

Question wording, known-object role and fact-order marginal scores are all perfect in this explicitly worded factorial. Targets split 12 original/12 duplicate, so this result is not an always-original answer. All three models answer the original control with the wrong entity while supplying a correctly typed readability field. There is no syntax failure to fix by merely switching from prose to JSON, or from JSON to a single word.

The contrast **does not isolate format as the cause**. The factorial also adds explicit unknown legibility, explicit known inspection, names both objects as registers and asks a direct question. These are correlated toy cases over two logical states, not 24 independent demonstrations of story understanding.

## Phase 2: exploratory unknown-cue/field-count ablation

After observing Phase 1, a separate 16-case follow-up was frozen and executed. It is **exploratory**, not an independent confirmation study. It holds the original-style instruction pattern while crossing known-object role, fact order, an explicit unknown-legibility cue and one versus two requested fields. One cell exactly reproduces the original failed prompt. All 16 cases are newly generated per model; earlier responses are not reused.

| Correct entity selections, per model | Base | Current craft | Mixed-v16 |
|---|---:|---:|---:|
| Implicit unknown, one field | 0/4 | 0/4 | 0/4 |
| Implicit unknown, two fields | 1/4 | 1/4 | 1/4 |
| Explicit unknown, one field | 2/4 | 2/4 | 2/4 |
| Explicit unknown, two fields | 2/4 | 2/4 | 2/4 |
| Total entity selections | 5/16 | 5/16 | 5/16 |
| Format compliant | 16/16 | 16/16 | 16/16 |

Reducing the field count alone does not solve the problem. An explicit unknown cue improves some cells but is insufficient. In the explicit-cue cells, all models select the first-mentioned object: this happens to be correct when the unknown object is first and wrong when the known object is first. The implicit-cue pattern differs and includes a role/order asymmetry. These are observed response patterns in this test, not a universal claim that the models always select the first object.

The follow-up omits Phase 1's direct question and retains other original-style differences: the known object is called a register, the other is introduced as an original/duplicate, and known inspection is not explicitly stated. It therefore does not isolate direct-question wording, symmetric object naming or known-inspection explicitness from each other. The key `unknown_object` also leaves the intended property less explicit than the direct question. The expected answers use the supplied-facts interpretation of unknown legibility; they are constructed diagnostic labels, not independently human-approved narrative interpretations.

Do not pool the two phases into a single accuracy number: their tasks and cues differ. They establish a useful limitation—format validity can coexist with wrong entity selection—and identify further matched wording tests, without claiming that an adapter fixed the binding error.

## Execution and scoring

Phase 1 makes 75 requests (25 per model), and Phase 2 makes 48 (16 per model). **All 123 complete without errors or truncation.** Every request contains one user message, no assistant history, zero reported cached tokens, temperature 0, seed 42, repetition penalty 1.0 and a 64-token output cap. Context is capped at 2,048 tokens. Cached tokenizer checks pass before execution. Models unload between conditions, and the initially stopped legacy service remains stopped after each phase. Resource limits retain the existing 10 GB process-tree RSS gate, 20-minute phase deadlines and error/truncation stops. No automatic retry occurs.

Entity selection and schema compliance are separate. Valid JSON with the wrong object fails entity selection. A plain unambiguous entity answer can be recognised as a lexical proxy while failing a requested JSON schema. Duplicate-key JSON is not accepted as compliant. Ambiguous answers containing both entity names are not guessed into a pass. All actual responses here are assessable and format compliant, so permissive fallback extraction does not produce the observed perfect-format scores. In Phase 1, the JSON variants use the requested field and word answers are exact requested tokens. The two-field follow-up separately validates the Boolean type and full expected value.

This is evaluation-only material, ineligible for training. No literary teaching target, manuscript, corpus download, new source span or rights grant is added. All previous model/experiment/review artifacts and human ballots retain their hashes. Human literary-quality ratings remain zero.

## Practical implication and next step

Keep the app-selected model. Do not spend another training run merely teaching the model to emit JSON: it already does so. A better next diagnostic holds the **exact same facts and output schema** fixed while varying only the direct question, then separately varies symmetric object naming and explicit inspection wording. Keep role/fact order counterbalanced and treat this as a narrow context-following test. Do not silently rewrite earlier prompts or count clearer prompts as a trained-model gain.

For application integration, clearer explicit questions and well-scoped facts are a hypothesis worth testing, not a shipped fix. Any future change still needs fiction-level evaluation and checks across maintained applications. Nothing here certifies broader narrative fidelity, robust prompt behaviour, Muse equivalence or production readiness.

## Verification and scope

The final full CPU foundation suite passed **226 tests in 42.517 seconds**, including five initial diagnostic/scoring tests and four follow-up balance/schema tests. Phase 1's earlier full suite passed 222 tests; it is superseded by the later 226-test result, not added to it. Both evidence verifiers pass frozen prompt/code/protocol hashes, all response/adapter hashes, recomputed scores, balance checks, fresh single-message/cache checks, output/context caps, service-state restoration and unchanged base/prior/selected model hashes. Python compilation and link/whitespace checks pass.

Phase 1 artifacts are in `artifacts/format-diagnostic-v17/` with frozen cases/protocol under `artifacts/format-diagnostic-v17-plan/`; Phase 2 uses `artifacts/binding-ablation-v17b/` and its corresponding plan directory. `scores.json` reports all declared factors and `counterexamples.json` preserves actual failing prompts/responses. A tracked diagnostic lock records hashes/results without response prose, private state or weights. Scripts are in `curation/format-diagnostic-v17/` and `curation/binding-ablation-v17b/`.

After reporting, read-only verification without model inference:

```bash
cd llm/Narratryx
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/format-diagnostic-v17/verify.py'); print(m['verify']())"
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/binding-ablation-v17b/verify.py'); print(m['verify']())"
```

Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/default/configuration/generated-asset changes, app builds or device/runtime checks. No training, paid job, external inference, corpus upload, publication or promotion occurs. Ordinary users do not need local training to use the application.
