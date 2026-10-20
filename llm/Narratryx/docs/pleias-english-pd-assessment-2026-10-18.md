# PleIAs/English-PD: candidate assessment

The dataset selected by the user can be investigated as an original-text source
for Narratryx. It is not yet a reviewed training release, and no training has been
started. Its canonical ID is **PleIAs/English-PD**.

Repository revision inspected: `0d451478c7d517a72298431f47bf57aa9c4e0e1e`.
The [pinned publisher card](https://huggingface.co/datasets/PleIAs/English-PD/blob/0d451478c7d517a72298431f47bf57aa9c4e0e1e/README.md)
describes public-domain books, permits model training, and says its initial
selection predates 1884. It acknowledges OCR and document-structure problems.
These are publisher statements; individual editions/contributors and intended
processing territories still need evidence. The card's worldwide public-domain
claim is not adopted here as an independent legal conclusion.

The [Hub page](https://huggingface.co/datasets/PleIAs/English-PD) currently reports
inconsistent Parquet columns and oversized row groups. Its preview includes
scanning debris, non-fiction and titles in other languages. The row API failed
with HTTP 500. The size endpoint also failed; its zero counters are not a usable
size estimate. No complete record was retrieved through that API and no Parquet
shard or full corpus was downloaded. Metadata and the short dataset card were
read, together with the visible Hub preview.

## How to use it

Use a small, selected fiction subset for a **raw-text continued-pretraining**
experiment if it passes review. Learning to continue book prose is a different
objective from following instructions to edit, analyse or plan a story. It does
not replace the later instruction/answer dataset or independent evaluations.
Using original literature also does not retroactively resolve permission for the
existing Codex-generated targets or benchmark material.

The next preparation stage should inspect bounded shard metadata, normalize
per-shard fields, identify English fiction and verify selected editions. Preserve
identifiers, authors/contributors, source references and hashes. Screen OCR and
scan wrappers, document transformations, deduplicate, and group by author/work
before splitting. Withhold unresolved works. Do not silently substitute title or
publication-year filters for rights verification.

The observed common fields include `identifier`, `title`, `publication_date`,
`word_count` and `text`; other shards expose extra provenance/language fields.
An importer must handle this variation explicitly. A bounded row request or
streaming interface can still read large row groups: enforce actual byte/storage
limits, rather than assuming a small row count makes the download small.

The current foundation export/Unsloth recipe expects reviewed SFT `messages`.
It cannot consume this corpus unchanged. A separate raw-text importer, provenance
mapping and training recipe are needed. Do not turn every book into an assistant
answer merely to satisfy a chat schema. Validate the chosen base model, training
mode and tokenizer with a small GPU smoke test before scaling.

## Current state

The user selecting a dataset in Studio is not evidence that its format has passed
loading or that a training job has run. This assessment did not inspect or change
the local Studio configuration. No local model training, source upload, paid job,
or full-corpus acquisition is authorized by this assessment.

Discovery evidence and the proposed intake steps are recorded in
`curation/candidates/pleias-english-pd-2026-10-18.json`, separate from the rights
ledger. Existing Austen material and all approvals remain unchanged. Web/PWA,
Tauri desktop, Capacitor iOS and native macOS application versions are unchanged;
this documentation/metadata work needs no app builds or device checks.
