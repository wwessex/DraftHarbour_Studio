# Austen excerpt and training-example review pack

Prepared on 18 October 2026 (Europe/London). The pack contains **six excerpts and twelve draft examples**, two each for fiction, editing, narrative analysis, dialogue, pacing and storytelling. The user’s existing approval covers the GB/US Austen-only source scope; it does not approve these exact excerpts, generated targets or synthetic-output terms.

Open the local review document at `artifacts/austen-pilot-review-v1/REVIEW.md`. It presents each source excerpt, its chapter/line/character locations, the proposed instructions, draft answers and editorial criteria. The generated files stay under ignored `artifacts/`: this work does not publish a dataset or authorize redistribution.

## What was selected

| Excerpt ID | Chapter | Craft focus | Draft tasks |
| --- | --- | --- | --- |
| `austen-opening` | I | Narratorial irony and social assumptions | Original fiction exercise; grounded analysis |
| `austen-ball` | III | Insult, emotional reaction and comic reframing | New dialogue; pacing through condensation |
| `austen-charlotte` | VI | Competing positions on marriage | One-word accessibility edit; alternative scene plans |
| `austen-pause` | XXXIV | Pauses, composure and contradictory speech | New dialogue; urgent/reflective pacing |
| `austen-self-judgment` | XXXVI | A concise internal turn | Grounded analysis; action and consequence planning |
| `austen-gratitude` | LXI | Lasting gratitude and narrative summary | New contemporary fiction; no-change editing |

Selections are short, contiguous narrative passages with none of the excluded illustration or notice blocks. The builder does not strip illustrations from the whole book and assume the result is clean. It rejects a selected span containing captioned **or bare** illustration markers, notices or printer material, and verifies chapter labels and exact source coordinates.

The only applied text transformation joins isolated print-wrap line breaks into spaces. Paragraph breaks, original spelling/diction, Unicode punctuation and underscore emphasis are retained. No spelling modernization, word substitution, summary or sentence removal is applied to the source excerpts. One **training target**, explicitly requested by its instruction, replaces `felicity` with `happiness`; it is clearly separated from the unchanged source selection. Another editing example deliberately leaves a grammatical passage alone. Editing targets have no minimum word-count requirement.

Fiction and dialogue targets are newly authored alternatives or technique exercises, not Austen quotations or claims about the novel’s canonical continuation. Story plans label proposed inventions. Analyses distinguish evidence in the supplied excerpt from facts that would require reading other chapters. These are candidate answers for editorial review, not independently established gold-standard responses.

## Files and provenance

- `excerpts.pending.jsonl`: each clean passage, its exact unmodified source span, source SHA-256, raw-span/clean-text hashes, chapter, source lines, transformation record and pending review.
- `examples.pending.jsonl`: model-neutral SFT messages, exact supporting source span, source-work/rights IDs, task rubric, pending sample/teacher-term reviews and message-content hash. It follows the existing dataset schema.
- `REVIEW.md`: readable source/instruction/answer review document with local source links.
- `manifest.json`: source/approval/input/output hashes, counts, checks, limitations and an explicit `training_ready: false` marker.

Offsets count Unicode code points in the source as read by Python with CRLF converted to LF; ends are exclusive. They are not byte offsets into the downloaded file. Original source bytes remain unchanged. Each displayed paragraph can be reconstructed from its exact raw span and the named `join-soft-wraps-v1` transformation. Both forms remain available for comparison.

All twelve records use `author-austen` and the proposed `train` split. No excerpt or derivative is assigned to validation/test. A lexical screen against the independent draft benchmark passed; it cannot establish freedom from semantic leakage or base-model pretraining contamination. The benchmark file was not edited. No tokenizer, model, literature download, inference endpoint, Unsloth upload or paid job is needed to create this pack.

## Reproduce locally

From `llm/Narratryx`, using the installed foundation environment and the existing private source snapshot:

```sh
.venv-foundation/bin/python -m foundation.austen_review \
  --output-dir artifacts/austen-pilot-review-v1
```

The delivered directory already exists, so the builder will refuse that exact command rather than overwrite review notes. Choose a fresh output directory when reproducing. If the pinned raw source is absent in another checkout, the builder stops; it never downloads a replacement or silently uses another edition. New acquisition must follow the approved source-handling conditions.

The authored selection/target specification is `curation/austen-pilot-review-v1.json`; the builder is `foundation/austen_review.py`; excerpt structure is defined by `schemas/excerpt-record.schema.json`. The builder verifies the source against the ledger, approval, manifest and specification, and verifies the preserved documents actually reviewed at source-scope approval. It generates review artifacts only. It does **not** invoke the source-release validator under a waiver, remove the source-selection gate, mark examples approved, or freeze the benchmark.

## Review decisions

For each excerpt, check that the scope is Austen-only, the source is faithfully displayed, and the chapter boundaries and emphasis make sense. For each example, decide **keep**, **revise** or **reject** based on the stated instruction, grounding, voice preservation and actual usefulness. Corrections to a synthetic target are separate from corrections to source transcription.

All excerpt and example review statuses remain pending. Teacher provenance identifies the conversation-generated draft and does not pretend to pin a provider checkpoint. Applicable synthetic-output terms need their own review; the recorded source approval does not automatically settle them. The source content-selection gate stays open until exact passages are approved. No training-ready dataset, training run or literary quality improvement is claimed.

The work is isolated to Narratryx. Web/PWA, Windows/Linux Tauri, Capacitor iOS and the separate Swift/AppKit macOS app remain unchanged; no native asset sync or platform/device builds are needed for this review pack.

## Validation

All **44 foundation/curation tests passed**, including CRLF/Unicode span handling, preservation of paragraphs/emphasis, rejection of bare and captioned illustration spans, out-of-scope or ambiguous anchors, wrong/cross-chapter selections, altered source/snapshot hashes, unrecorded rewrites, incorrect line/transformation metadata, and existing-output protection. Full-pack tests use invented temporary evidence and approvals; they do not approve the real samples.

The actual local pack was also checked against the pinned source and existing approval. Its JSONL files pass their schemas, its hashes and source spans match, and all six skills have two examples. The editing instructions/targets, analytical quotations, dialogue line constraints and condensation limit were checked separately. All approval gates remain intact. Application/runtime/device or live-model tests were not run for this isolated preparation task.
