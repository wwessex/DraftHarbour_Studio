# Cleaner source expansion — 18 October 2026

**Approval update:** the human user has now approved the documented GB/US scope
and exact 108 passages. The [approved experiment report](clean-source-experiment-v1.md)
records the decision, successful source release checks and prepared local run.
The pre-approval findings below are preserved as history; no training has run.

Obtained two new proofread works and prepared **108 traceable candidate
passages / 9,871 words**. Completed an evidence-based GB/US original-prose rights
and source-terms assessment. The concrete scope is ready for review; **human
scope approval and editorial acceptance remain pending**, and training is off.

| New source | Passages | Words | Share of new pool |
| --- | ---: | ---: | ---: |
| Amelia Opie, The Father and Daughter, PG 49621 | 54 | 4,969 | 50.3% |
| J. Jackson Wray, Nestleton Magna, PG 41916 | 54 | 4,902 | 49.7% |

These books improve author balance without silently replacing the earlier
English-PD works or importing their approvals. This expansion is a separate
two-author pool, not a claim of broad genre/style coverage. The 70 surviving
Lytton paragraphs were not merged: their legacy source gates remain separate.
Walker was researched but no suitable clean openly reusable transcription was
established; his damaged OCR is not promoted just to increase author count.

## Rights checks completed

Read the [source dossier](../rights/dossiers/clean-source-expansion-2026-10-18.md)
for the exact scope, facts, evidence, exclusions and limitations.

- **Identity and dates:** exact ebook IDs and SHA-256 hashes pinned. Opie title
  matter identifies the ninth edition, London, 1824. Wray's “Thirtieth Thousand”
  printing is undated; 1876 is independently documented as the underlying
  work's first publication, not invented as this printing's date.
- **Authorship:** Opie's 1853 death and Wray's 1892 death are corroborated.
  Scholarly Wray biography and first-edition records resolve the earlier
  single-catalogue evidence gap.
- **GB/US basis:** ordinary UK author-life term supports expiry of their
  original prose; each selected provider item reports US-public-domain status.
  Foreign-work restoration limits were considered. Modern additions, illustrations,
  verse and other excluded material are not cleared merely by author age.
- **Acquisition:** two books downloaded via an officially listed Gutenberg
  mirror, following its documented automated-download route. Full originals and
  licences are preserved privately. Total ebook transfer, including both body
  and full-licence variants, was about 1.53 MB.
- **Reuse conditions:** unbranded original prose only; provider licences,
  branding, credits and catalogue summaries are outside the model inputs.
  Original files/notices and provenance stay intact privately. No branded ebook
  redistribution, endorsement, worldwide clearance or source publication is
  implied. Prior Archive/Google questions remain attached to their old copies.

These are source evidence conclusions, not a legal certification or invented
human sign-off. The independent pending ledger is
`rights/clean-sources.pending.jsonl`. It has two structurally valid records and
zero approved records. Release validation correctly refuses them until a scoped
approval is recorded. Editorial acceptance is a separate gate.

## Text preparation

Selected complete-looking source paragraphs of 40–250 words, with exact raw
spans and hashes. Collapsed whitespace only: historical spellings, dialect,
punctuation and wording are unchanged. No OCR corrections or teacher answers
were generated.

Excluded front/back matter, illustrations/captions, footnotes, indented verse
and attribution blocks, headings, malformed boundaries and detected provider
matter. Wray selection conservatively avoids detected scripture/hymn/religious
reference contexts; it is not representative of that entire religious novel.
Short allusions and fictional dialogue remain in the narrative scope.

The system dictionary rate is retained as a review metric, **not a rejection
rule** for these proofread transcriptions: names such as Fitzhenry and Yorkshire
dialect otherwise look like OCR errors. Consequently pass rates cannot be
compared directly with the earlier raw-OCR builder. This change does not
modernize dialect or certify that every unusual token is correct.

The builder initially selected 109 passages under a 5,000-word budget per
author. Spot review found an apparent character-name error, `Adam Quiver`, in
the proofread Wray text. That passage was excluded without rewriting it,
leaving the 108-record screened pool. Remaining passages still need editorial
acceptance; a proofreader credit and a machine pass are not a guarantee of
error-free or facsimile-verified text.

Murray remains reserved for evaluation. The existing 120 draft benchmark tasks,
14 fresh-context cases and reserved Murray passages are hash-protected inputs.
No selected passage shared a contiguous 12-word sequence with those inputs,
and no exact/high-similarity duplicates were found among retained records.
This lexical screening does not detect all semantic overlap or establish
absence from the base model's pretraining data.

## Review and reproduce

Local bundle:

`/Users/williamwessex/Documents/Writer1/llm/Narratryx/artifacts/clean-source-expansion-v1/`

- **`REVIEW.md`**: the exact 108 proposed passages, ordered by source position.
- **`train-candidates.screened.pending.jsonl`**: current 108-record review pool.
- `review-pack/`: the earlier 109-record machine selection plus audit/rejections.
- `editorial-exclusion.json`: the one subsequent exclusion and its source hash.
- `selection-plan.json`, `raw/`, `acquisition.json`, `full-header-acquisition.json`:
  pinned source inputs and download history.
- `evidence/`: scholarly/official snapshots and web observation records.
- `verification.json`, `verify.py`, `tests.log`: integrity and test evidence.

From `llm/Narratryx`, reproduce the machine selection into a **new** directory:

```bash
.venv-foundation/bin/python -m foundation.proofread_expansion \
  artifacts/clean-source-expansion-v1/selection-plan.json \
  artifacts/clean-source-expansion-v1/review-pack-new
.venv-foundation/bin/python -m foundation validate-ledger rights/clean-sources.pending.jsonl
.venv-foundation/bin/python -m unittest discover -s tests -v
```

The machine selection has 109 records; the documented editorial exclusion is
an additional step. The offline builder does not download, export runnable
training jobs, approve records or call a model. The general offline runner is
not wired to consume this pending prose pool. Raw continued-pretraining records
are not passed off as message/answer SFT examples.

**Validation:** 72 foundation tests passed, including five new tests for
source-span preservation and deduplication, protected-text exclusion, reserved
authors, tampering, retained licences, scope filters, dictionary behaviour and
disabled training. A separate audit checked all 108 retained records against
the 109 originals, both raw files and pending rights records, source/span/text
hashes, author/word counts, protected inputs and duplicate screening. It did not
perform a new model benchmark or complete facsimile proofreading.

The review dossier and hashed passage file now make the next scope decision
concrete. Their approval would concern these original-prose passages and GB/US
training/evaluation only. Training itself was not requested in this step and
was not launched. No cloud spending, upload or integration occurred. Web/PWA,
Tauri desktop, Capacitor iOS and native macOS applications were unchanged; no
application builds or device checks were run for this independent data work.
