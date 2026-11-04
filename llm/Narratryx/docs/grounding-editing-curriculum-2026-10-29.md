# Grounding and restrained editing curriculum — 29 October 2026

**179 structured lessons are prepared; no training or inference ran.** They target the unsupported assumptions, future-event errors and overediting risks identified by the [eight-update trial](revision-training-v4-2026-10-26.md). Literary answer prose was not generated. The apps, selected model configuration and previous experiments remain unchanged.

This is a task curriculum built from existing cleared material, not a new bulk corpus or 179 independent stories. It needs a balanced prose-retention mixture and a fixed comparison plan before another model run. Successful compilation does not establish that the model has learned these behaviours.

## What was prepared

| Component | Lessons | Purpose |
|---|---:|---|
| Minimal repair inside a selection |65| Repair one deliberately duplicated word using an exact anchor; preserve every other selected character. |
| Unchanged selection with an error outside it |65| Return `{"edits":[]}` when the selected text is clean, even though visible context contains a duplicate. |
| Evidence classification |24| Distinguish narration, character claims, plans, requests, hypothetical content, qualified inference, hearsay and missing information. |
| Constructed schedule snapshots |24| Distinguish not-yet-due, due-now, overdue, arrived and unknown states. Unknown arrival must not become absence. |
| Grammatical-repetition control |1| Preserve the valid past-perfect “had had” in the previously scan-checked 1908 James passage. |

The 178-record main packet uses 65 distinct editing passages across nine works, capped at 20 passages per work. Its 24 semantic annotations concern ten excerpts, and its 24 clock exercises reuse two source schedules. The grammatical control adds no independent work. Counts must not be summed as new source diversity: the material largely comes from previously trained sources, with new task framing and structural targets.

Editing tasks here concern accidental duplicate words and selection boundaries. They do not establish general proofreading, better style or the correctness of every historical grammatical construction. The generator excludes existing natural repetitions so they cannot silently become corrupted/no-op gold; the separately reviewed James control explicitly demonstrates a legitimate repetition that must remain.

## Source and target restrictions

The [12-record scoped ledger](../rights/grounding-editing-v1.scoped.jsonl) copies existing source decisions for private GB/US training uses. No new work was downloaded or declared public domain. Exact original source spans, local hashes, author/work IDs and prior scope remain attached. The ledger passed release-evidence validation with `legal_certification: false`; this is not a new human/legal certification or redistribution permission.

All answers are structural JSON: finite labels, calculated minute differences, source quotations, minimal source-derived replacements or empty edit lists. The metadata and task instructions are constructed exercises. No generated literary teaching answer, invented human approval or teacher-model completion was added. Source quotations and answer packets remain local/ignored by Git; tracked locks bind their bytes.

The semantic labels are an **informed Codex AI annotation**, not independent human gold. Exact quotation membership can be checked mechanically; the correctness of a semantic interpretation cannot. In particular:

- An announced visit or refreshments time is a plan, not evidence it happened.
- A quoted assertion or report of something heard is not independent verification.
- James’s imagined response to a proposal is hypothetical; quotation marks do not make it actual speech.
- Conditional predictions and “it seemed” interpretations are qualified, not certain narration.
- An excerpt that does not name a visitor, explain where a skill was learned or specify a payment must not acquire that information from invention or memory of the wider book.

The clock exercises separate an exact source schedule from an explicitly **hypothetical task snapshot**. The document supplies no evidence of actual arrival. `arrived:null` means unknown; `false` explicitly means not arrived; `true` means arrived. All calculations assume the same constructed day, using explicit 24-hour clocks. They do not cover overnight dates, time zones or general natural-language time parsing, and they do not add events to the original novel.

## Review and evaluation material

- [Main review packet](../artifacts/grounding-editing-v1/REVIEW.md) groups the semantic questions by excerpt, shows paired editing cases and illustrates the constructed clock states.
- [Grammatical-repetition control](../artifacts/grounding-editing-restraint-v1/records.jsonl) is a separate one-record supplement. The original 178-record packet remains immutable; these are not yet a merged training mixture.
- `clock-tests.evaluation-only.jsonl` contains 24 deterministic test states with clock tuples disjoint from training. They test a narrow symbolic operation, not prose quality or independent source generalisation.
- `prose-transfer.evaluation-only.jsonl` contains 16 original AI-authored evaluation-only cases across four new situations: selected editing, grounded analysis, chronology rewriting and continuation. These test whether structural supervision transfers to ordinary prose; they are never teaching targets. The related templates/scenarios are correlated, and this is not a human-approved formal benchmark.
- Prior validation authors and exposed diagnostics remain separate. Wray, Mansfield, Chesnutt and Austen were not introduced into training. The source/split and lexical-overlap screens passed; those screens do not guarantee semantic independence or absence from base pretraining.

The prose transfer cases deliberately test future arrivals, unknown object authorship, unchanged names and out-of-selection errors. Their expected repair strings are limited to mechanical editing; creative/analysis reference prose is unfilled. There are no new human literary-quality ratings.

## Actual checks

**154 CPU foundation tests passed in 39.404 seconds**, including 12 new evidence, temporal-state and selection-boundary tests. The main 178-record dataset passed schema, rights-use, source-span, JSON target, exact-anchor recovery, unknown-state and prior-heldout checks. The separate grammatical control also passed provenance validation. The first suite invocation caught an undersized test fixture; only that fixture was lengthened, and the full suite was rerun successfully. No curriculum source or frozen dataset was altered to bypass a failing check.

Offline tokenizer preflight passed for all 178 main lessons: maximum **1,647 tokens**, **2,450 supervised JSON/quote/EOS tokens**, exact answer round trips, prompt tokens masked and no truncation. These low supervised-token counts underscore that 179 rows do not constitute a large literary corpus. The grammatical control passed a separate token-budget check at 193 tokens, also without truncation. Tokenization did not load model weights, generate responses, certify training memory or launch a trainer.

All four main packet/support locks and the separate restraint lock were checked. The previous run’s 21 frozen input files, 14 protected adapter/configuration files and selected model pin match their recorded hashes. This task did not start, stop or restart the inference service. A final optional check could not reach the legacy service at 127.0.0.1:8890; no runtime availability claim is made and no service action followed.

## Reproduce and next experiment

From `llm/Narratryx`, verification is read-only:

```bash
.venv-foundation/bin/python curation/grounding-editing-v1/build.py verify
.venv-foundation/bin/python -m foundation validate-ledger rights/grounding-editing-v1.scoped.jsonl \
  --release --jurisdictions GB US --use training
.venv-foundation/bin/python -m unittest discover -s tests -v
```

The [builder](../curation/grounding-editing-v1/build.py), [pure label/edit helpers](../foundation/grounding_lessons.py), [tokenizer preflight](../curation/grounding-editing-v1/preflight.py) and [review generator](../curation/grounding-editing-v1/review.py) refuse to replace existing artifacts. Rebuilding requires the pinned local source artifacts and local semantic specifications; it does not download books or reconstruct missing annotations automatically. Foundation Python is for CPU validation; tokenizer preflight uses the separate installed Unsloth environment.

Before training, review the semantic labels and grammatical control, select a balanced sample of these structural lessons, retain substantial Write/Rewrite/Continue/dialogue/pacing source-prose supervision, and freeze the mixture, budgets and fresh comparisons. Do not use this JSON-only packet as the entire fiction curriculum. Compare a matched-budget control where practical, evaluate both structural accuracy and transfer to prose, and keep source-similar cases grouped. A better JSON score alone must not trigger promotion.

No paid job, upload, publication, model promotion or application-default change occurred. Web/PWA, Tauri Windows/Linux, Capacitor iOS and independent native macOS received no source/configuration/generated-asset changes from this task; no app/device builds were required or run.
