# Phase 1: rights, dataset validation and independent evaluation

This is a CPU-only, offline toolset inside Narratryx. It does not import the writing application, call model APIs, download literature, train a model or launch cloud jobs. It uses Python 3.10+ and an isolated JSON Schema dependency. The implementation was tested on this development Mac with Python 3.14; Windows/Linux Python execution and application/device builds have not been performed.

## Start here

From the repository root:

```sh
cd llm/Narratryx
python3 -m venv .venv-foundation
.venv-foundation/bin/python -m pip install -r requirements-foundation.txt
.venv-foundation/bin/python -m unittest discover -s tests -v
.venv-foundation/bin/python -m foundation validate-ledger rights/ledger.jsonl
```

On Windows, use `python` to create the environment and `.venv-foundation\Scripts\python.exe` in place of `.venv-foundation/bin/python`. All subsequent commands below assume the Narratryx directory and that Python environment. Installation fetches Python dependencies only; commands themselves have no network client or model dependencies.

The ledger’s structural validation currently reports **one human scope approval** (Austen) and three pending records; Austen still has an unresolved content-selection gate, so its raw source is not release-ready. It contains three literature candidates from the assessment and one original synthetic example candidate. The Austen candidate now has a [researched 1894 edition dossier](../rights/dossiers/austen-pride-1894.md) and one pinned local source snapshot for evidence; the user has since approved the reviewed Austen-only GB/US pilot scope; its content-selection gate remains open, and the other three records remain pending. The other candidates have no source downloads. The sample `data/phase1-example.pending.jsonl` demonstrates the SFT format and also remains unapproved.

## Rights and source evidence

`schemas/rights-record.schema.json` defines one exact source edition or original-work record. Do not approve the named book generically. Complete the contributor identities/dates, edition and publication evidence, exact included/excluded material, source terms and notices, retrieval date/revision, local file path and SHA-256. Evidence URLs are references for human review; the validator does not fetch or adjudicate them. Use stable archived evidence where possible. Original material also needs a recorded permission basis; synthetic material is not automatically rights-free.

Approval records require a reviewer attribution and valid review date. To pass source-release validation, there must also be no unresolved issues, and each requested jurisdiction must have one unambiguous clearance covering the requested use. A human-approved scope can therefore remain blocked on unfinished content-selection work. Literature candidates additionally require edition/publication evidence and contributor dates/status. Keeping the `source_kind` value `public_domain_candidate` after review preserves provenance; actual eligibility is determined by the recorded approval and evidence checks.

`raw_path` is relative to the ledger's directory and must resolve inside it, including through symlinks. Preserve original UTF-8 text unchanged, with notices; use `rights/raw/` for local sources. The foundation commands never download raw files. One Austen source snapshot was retrieved separately for the edition dossier and remains local, ignored by Git and unapproved for training. The validator checks the real local file's SHA-256 against the recorded value. Source spans use Unicode code-point offsets into that unchanged decoded file, not byte offsets or offsets into cleaned text.

After completing actual human clearance, check a ledger of sources intended for release:

```sh
.venv-foundation/bin/python -m foundation validate-ledger rights/ledger.jsonl \
  --release --jurisdictions GB US --use training
```

This command deliberately fails while a record has pending approval or an unresolved content-selection gate; the complete ledger also contains three pending records. Add the actual cloud-processing country and intended distribution territories as appropriate; the tool does not infer them. `--release` checks every record in the supplied ledger. A dataset validation checks the records it actually references, so unrelated pending candidates may remain in the main ledger. These are checks of **recorded evidence and decisions**, not automated legal certification. Withdrawing approval or changing raw text invalidates a subsequent validation; an old report alone is not permission to keep using withdrawn data.

## Dataset contract and validation

`schemas/dataset-record.schema.json` describes model-neutral SFT messages plus provenance. It deliberately rejects unknown fields. Required fields include unique ID, dataset version, skill, split, split group, source work and rights IDs, origin, source spans, teacher/terms record where applicable, review, rubric, and message hash. No hardcoded tokenizer/chat markers are added. All examples in one release must share a dataset version.

Messages must alternate user/assistant turns, optionally preceded by one system message, and end with an assistant target. `content_hash` is SHA-256 over UTF-8 JSON of `messages` with sorted keys, `ensure_ascii=False`, and separators `(',', ':')`; use `foundation.validation.digest(messages)` rather than hashing a pretty-printed line. Metadata is never exported as a model target. Synthetic examples require teacher identity/revision, applicable terms, a training-permission statement, and a separately approved terms review. Human approval of the sample does not bypass that check.

Referenced source IDs and work IDs must match. Literature-derived records require an exact source span for every referenced literature source. Training rows require the `training` use; validation/test rows require `evaluation`. Every row and referenced source must be approved. The validator rejects cross-split reuse of split groups, works or authors and screens for exact/near-duplicate text across splits and against benchmark contexts. The lexical screen uses case-folded five-word shingles with 80% containment and a 20-word minimum, plus normalized exact matching; it cannot detect all paraphrases, semantic leakage or base-model pretraining contamination. Pairwise screening is intended for pilot-size datasets, not millions of rows.

Once the benchmark and editorial rubric are reviewed and frozen:

```sh
.venv-foundation/bin/python -m foundation validate-dataset data/reviewed-v1.jsonl \
  --ledger rights/ledger.jsonl --jurisdictions GB US \
  --benchmark evaluation/tasks.reviewed-v1.jsonl --lock artifacts/benchmark-v1.lock.json \
  --rubric evaluation/rubric.reviewed-v1.json \
  --output artifacts/dataset-v1.validation.json
```

The report records dataset, ledger and benchmark hashes, selected jurisdictions, record/source IDs and split counts. Revalidate the exact files immediately before future training. This command validates and writes a manifest; it does not train or convert data. Existing legacy datasets and training launchers do **not** enforce this new gate. Do not use them to bypass Phase 1 review. DPO validation, tokenization/truncation checks and a gate wired into a new training runner belong to later phases.

## Draft benchmark and freezing

`evaluation/tasks.draft.jsonl` contains **120 pending tasks: 20 original scenarios × six skills** (fiction, editing, narrative analysis, dialogue, pacing and storytelling). The scenarios were drafted synthetically for this work; no literary corpus was used. Every task carries explicit provenance and pending review. Related skill tasks share a scenario and split group. They are not 120 independent observations.

Review the prompts, contexts, checks, provenance/terms and task-specific rubrics before approval. `evaluation/rubric.json` supplies anchored 1–5 ratings and instructions against length/ornament bias. Treat every benchmark scenario as held out: do not generate training examples from it. Repeated evaluation-guided tuning eventually overfits a benchmark; reserve a fresh final set before product promotion. These short draft scenarios do not establish long-context or whole-novel competence. Later phases must add longer reviewed cases and application-specific regressions.

Create reviewed versions of both the tasks and `rubric.json` by copying and editing them after genuine review. Both need named approval records. Then freeze them:

```sh
.venv-foundation/bin/python -m foundation freeze \
  --tasks evaluation/tasks.reviewed-v1.jsonl --rubric evaluation/rubric.reviewed-v1.json \
  --output artifacts/benchmark-v1.lock.json
```

Freezing rejects pending tasks or an unapproved editorial rubric. The lock pins task-file bytes, task IDs/count, task schema and rubric hashes; any changes require a new lock/version. It is a local integrity check, not a signed attestation or immutable remote registry. Outputs are created exclusively and existing outputs are never overwritten.

To inspect inputs now without approving anything:

```sh
.venv-foundation/bin/python -m foundation export-prompts \
  --tasks evaluation/tasks.draft.jsonl --allow-draft \
  --output artifacts/draft-prompts.jsonl
```

This makes **zero inference calls**. It exports task IDs and user messages containing context/instructions, withholding checks, targets, rubric and review metadata. `--allow-draft` is explicit and reports are marked as draft. Normal evaluation requires an approved benchmark and matching lock.

## Imported responses and objective scoring

The evaluation runner accepts saved responses from any model/runtime; Phase 1 deliberately has no live API adapter. Collection through a paid endpoint or a future local runner is a separate operation. Never fabricate actual model responses or measured latency to fill a report.

Each line follows `schemas/eval-response.schema.json`: `schema_version`, `task_id`, `text`, `error` (null on success), `latency_ms` (nonnegative completion latency), and `completion_tokens` (nonnegative integer or null). Record failures explicitly. Missing, empty and errored responses fail checks rather than disappearing from the denominator. Duplicate/unknown task IDs and malformed JSON are rejected.

Provide a separate JSON run record following `schemas/eval-run.schema.json`: run/model IDs, immutable model and tokenizer revisions, prompt version, runtime, generation settings, model-artifact SHA-256 and benchmark-file SHA-256. The latter must match the actual task file. Caller-supplied model metadata and timing are provenance claims, not independently verified measurements. Record token counts when available; current scoring reports completion latency, not first-token latency, GPU throughput or hosting cost.

```sh
.venv-foundation/bin/python -m foundation score \
  --tasks evaluation/tasks.reviewed-v1.jsonl --lock artifacts/benchmark-v1.lock.json \
  --rubric evaluation/rubric.reviewed-v1.json \
  --responses evaluation/runs/base.responses.jsonl --run evaluation/runs/base.run.json \
  --output artifacts/base.objective.json
```

Supported checks: word range, nonblank-line range, exact output, case-sensitive literal inclusion/exclusion, JSON parsing and exact quoted evidence from context. Quote checks require the configured number of distinct spans; use double quotes only for source evidence in analysis tasks. The report includes per-skill results, missing counts, response hash and mean completion latency for successful nonempty responses. These are mechanical checks, not scores for creativity or literary quality. No command declares a model ready for promotion.

## Blind comparisons and review reports

Import baseline and candidate runs using the same benchmark and comparable prompts/generation settings. Prefer to compare prompt-only and fine-tuned variants separately from retrieval changes.

```sh
.venv-foundation/bin/python -m foundation blind \
  --tasks evaluation/tasks.reviewed-v1.jsonl --lock artifacts/benchmark-v1.lock.json \
  --rubric evaluation/rubric.reviewed-v1.json \
  --left evaluation/runs/base.responses.jsonl --left-run evaluation/runs/base.run.json \
  --right evaluation/runs/candidate.responses.jsonl --right-run evaluation/runs/candidate.run.json \
  --seed 42 --output-dir evaluation/runs/comparison-v1
```

The command requires complete responses for both runs (explicit failure records count as responses), checks run metadata, randomizes A/B order per task and shuffles presentation order. Share only `review.jsonl` and the rubric. Keep `private-key.json` private; it records model identities, response hashes and label assignments, with owner-only permissions where supported. Windows filesystem permissions need separate consideration. Answer wording may itself reveal a model identity; anonymization cannot guarantee blinding if outputs self-identify. Failed answers are marked for reviewers.

Reviewers supply JSONL ballots following `schemas/review-ballot.schema.json`: task ID, reviewer identifier, preference (`A`, `B` or `tie`), rationale and overall 1–5 ratings for A and B. The ratings support editorial review; the paired win-rate calculation uses the stated preference. Use two reviewers on a representative subset and retain disagreements for adjudication.

```sh
.venv-foundation/bin/python -m foundation review-report \
  --tasks evaluation/tasks.reviewed-v1.jsonl --lock artifacts/benchmark-v1.lock.json \
  --rubric evaluation/rubric.reviewed-v1.json \
  --packet evaluation/runs/comparison-v1/review.jsonl \
  --key evaluation/runs/comparison-v1/private-key.json \
  --ballots evaluation/runs/comparison-v1/ballots.jsonl \
  --output artifacts/comparison-v1.review.json
```

This validates packet integrity, task IDs and unique reviewer/task votes. Ties count half. Votes are averaged within task, then task results within scenario; a seeded 2,000-resample bootstrap operates on scenarios. The report includes coverage, missing tasks, two-reviewer counts, per-skill rates and an interval (null with fewer than two reviewed scenarios). Partial review cannot establish improvement. The tool does not independently verify reviewer identity and local hashes do not protect against deliberate alteration of both data and manifests. Reversing comparison order for a second blind review and adjudication remain review-protocol responsibilities.

## Isolation and remaining work

All new code, schemas, draft examples and instructions live under `llm/Narratryx/`. No React/PWA, Tauri Windows/Linux, Capacitor iOS or Swift/AppKit macOS source, dependency, asset or project-data format changes are required. Do not sync native assets for this work. Foundation tests validate the independent tooling; they are not claims of application/device regression testing or trained-model performance.

The immediate human work is to review the draft benchmark and establish exact-source rights dossiers. Following phases add reviewed training data, a pinned Unsloth GPU runner, measured baseline/model responses, expanded long-context evaluation and only then staging/app integration. No model weights, corpus downloads, legal approvals, paid jobs or automatic self-improvement are included here.

## Implementation validation

On 17 October 2026, all **35 foundation tests passed** under Python 3.14.6 with `jsonschema==4.23.0`. Tests include the full CLI dataset-validation/imported-response/blind-review/report path using invented temporary evidence, pending-rights and pending-rubric rejection, altered-file/hash/span rejection, work/author/group and lexical leakage, failed/missing responses, benchmark locks, duplicate ballots and scenario-level statistics. Temporary test approvals are explicitly fictional and do not approve the shipped candidates.

Python compilation and `pip check` passed. A real CLI draft export produced 120 prompt inputs under ignored `artifacts/phase1-smoke/` with zero inference calls; the ledger check reported four structurally valid records and zero approvals. Documentation links/formatting and tracked whitespace checks passed. Source-import inspection found only the standard library and `jsonschema` in the foundation package. Git checks found no tracked changes to the web/PWA, Tauri Windows/Linux, Capacitor iOS, native macOS or application dependency files. Their builds and device/runtime behavior were not retested in this isolated phase; no cross-platform runtime or trained-model quality result is claimed.
