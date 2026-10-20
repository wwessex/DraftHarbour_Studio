# English-PD fiction subset — 18 October 2026

**Follow-up:** the [editorial triage report](english-pd-editorial-triage-2026-10-18.md)
records 46 recommended exclusions and resolves Murray's edition date as 1875
from the original scan. The initial counts and OCR-date discrepancy below are
preserved as preparation history; consult the follow-up for current findings.

Prepared a larger, traceable **review pool**, with 99 training candidates (6,497
words) from four authors and 46 reserved evaluation candidates (2,913 words)
from a fifth author. These are original-source prose paragraphs for possible
continued pretraining, not instruction/answer examples. No training was started.
Every record still has pending rights and editorial status. Nothing here grants
release approval or changes the existing rights ledger.

## Material and split

| Exact Archive item / selected work | Catalogue edition | Author | Assignment | Passages | Words |
| --- | --- | --- | --- | ---: | ---: |
| `cihm_26142` / Paul Meggitt's Delusion, main narrative only | Toronto, Methodist Book and Publishing House, 1881 | J. Jackson Wray | Training candidate | 5 | 330 |
| `threespaniardsro01walk` / The Three Spaniards, vol. I | Exeter, J. C. Gerrish, 1832 | George Walker | Training candidate | 6 | 300 |
| `mynovelorvarieti02lyttiala` / My Novel, vol. II | Edinburgh/London, William Blackwood and Sons, 1853 | Edward Bulwer Lytton | Training candidate | 80 | 5,430 |
| `talesofhear01opie` / Love, Mystery, and Superstition, within Tales of the Heart, vol. I | London, Longman, Hurst, Rees, Orme and Brown, 1820 | Amelia Opie | Training candidate | 8 | 437 |
| `cihm_11328` / The Boudoir Cabal | Toronto, Rogers & Larminie; catalogue 1875, OCR title page 1876 | E. C. Grenville Murray | Reserved author; pending edition check | 46 | 2,913 |
| `hiddenperilsano00haygoog` / Hidden Perils | Catalogue: Harper, 1876 | Mary Cecil Hay | Quarantine; no passages extracted | 0 | 0 |

Murray's entire work and author are excluded from the training pool. This is a
prospective heldout source pool, not a frozen literary benchmark, validation-loss
result or proof that the base model has never encountered the book. Existing
120 draft benchmark tasks and the 14 fresh-context test cases were retained as
protected inputs and were not added to training. Opie's earlier pilot data stay
on the training side; they cannot serve as independent evaluation.

Lytton accounts for **83.6% of candidate training words**. The pool is therefore
unbalanced and too small to support a credible claim of broad literary skill
improvement. Do not train it unchanged. Retain the surplus for review, then cap
author contributions and find better OCR sources for underrepresented authors.
The first training experiment established hardware feasibility only; its fresh
tests did not demonstrate a literary improvement.

## Provenance and bounded acquisition

Source: [PleIAs/English-PD](https://huggingface.co/datasets/PleIAs/English-PD),
revision `0d451478c7d517a72298431f47bf57aa9c4e0e1e`,
`english_pd_0.parquet`, zero-based rows 11, 154, 459, 499, 597 and 615.

Fetched one compressed text column once, transferring **496,509,980 bytes**,
with a 600 MiB hard limit. The shard's single large row group required decoding
the column containing 1,000 rows; only the six named raw texts were saved. This
was not a download of the full corpus. No Google Books system was queried.
Archive metadata and small source/terms evidence snapshots were fetched
separately. The Opie text checksum matches the prior pilot exactly.

Each candidate carries source/work/author identifiers, raw character offsets,
raw-span and normalized-text SHA-256 hashes, split, transformation and quality
metrics. The acquisition manifest records full raw and catalogue-evidence hashes.
Offsets use Unicode code points in the unchanged UTF-8 source. Whitespace is
collapsed; no OCR spelling, punctuation, dialogue or plot wording is generated.
Rejected paragraphs are never stitched together.

The local package is:

`/Users/williamwessex/Documents/Writer1/llm/Narratryx/artifacts/english-pd-fiction-v1/`

- `selection-plan.json`, `acquisition.json`, `raw/`, `evidence/`: pinned inputs.
- **`review-pack-v2/` is the current output**; `review-pack/` is a superseded
  development build retained for audit. Candidate contents are identical; v2
  includes the tested CRLF boundary handling and faster benchmark screening.
- `review-pack-v2/train_candidate.pending.jsonl`: 99 metadata-rich prose records.
- `review-pack-v2/heldout_candidate.pending.jsonl`: 46 reserved records.
- `train_candidate.REVIEW.md`, `heldout_candidate.REVIEW.md`: readable passages.
- `review-pack-v2/rejected.jsonl`, `audit.json`, `manifest.json`: decisions/hashes.
- `verification.json`, `verify-pack.py`, `tests.log`: integrity and test evidence.

Downloaded texts and review outputs stay ignored by Git. The durable candidate
record is `curation/candidates/english-pd-fiction-v1-2026-10-18.json`.

## Rights findings and remaining scope

The publisher's public-domain and training-use statements are evidence about
the dataset provider's position, not independent clearance for every row.
Catalogue rights/license fields are absent for these six items; absence grants
no permission. The following are documented **candidate conclusions**, not
new human approvals:

- Ordinary UK literary copyright is usually life plus 70 years; edition layout
  usually has a separate 25-year term. The identified authors' historical death
  dates and old printings support an expiry inference for the underlying prose.
  Exact edition/contributor/source-term checks remain necessary.
  [UK IPO guidance](https://www.gov.uk/copyright/how-long-copyright-lasts).
- US foreign-work restoration gives only the remaining applicable US term;
  the Copyright Office generally describes 95 years from first publication for
  pre-1978 works. These old editions provide conservative publication bounds
  well before the current cutoff, conditional on confirming the actual material.
  This does not clear later additions or unknown contributors.
  [Copyright Office Circular 38B](https://www.copyright.gov/circs/circ38b.pdf).
- Opie's death in 1853 is supported by the
  [National Portrait Gallery](https://www.npg.org.uk/collections/search/person/mp03370/amelia-opie).
  Lytton's death in 1873 is supported by his
  [Westminster Abbey memorial record](https://www.westminster-abbey.org/abbey-commemorations/commemorations/edward-bulwer-lytton).
  Walker's 1772–1847 identity is corroborated by the
  [Library of Virginia catalogue](https://www.lva.virginia.gov/collections/virginia-print/imprints/1803.045).
  Wray's 1892 and Murray's 1881 death years currently rely on their respective
  digitizing-library catalogue attributions; independent authority checks remain.
- Murray's OCR title page says **1876**, while catalogue metadata says **1875**.
  Both are old, but this discrepancy is unresolved; inspect the scan before
  recording the edition as verified.
- Hay's preserved raw file begins with Google usage requests concerning
  noncommercial use, automated querying and attribution. The underlying work's
  age does not settle those source-use questions. No Hay prose enters either
  candidate split; obtain a separately assessed source or resolve the terms.
- The Archive terms URL returned only a JavaScript-required shell. That snapshot
  is recorded as an **unsuccessful terms retrieval**, not reviewed contract text.
  The HF terms and pinned dataset card were saved separately. Contractual reuse,
  embedded quotations, illustrations, editorial additions and all jurisdictions
  beyond GB/US remain outside any clearance conclusion here. Evidence web pages
  and their modern text/images are never training material.

## Quality and leakage checks

The builder retained complete-looking paragraphs of 40–250 words, excluding
line-end split words, suspicious symbols, letter/digit damage, standalone page
numbers, uppercase headings, detected wrappers and paragraphs with more than
6% dictionary outliers. A local system dictionary is a heuristic: proper names
and historical vocabulary can be rejected, and plausible OCR substitutions can
pass. It is not a spelling corrector or language-quality certificate.

There were 12,360 rejected paragraphs. Rejection reasons can overlap. Among the
145 retained records, no exact duplicates or word-5-gram Jaccard similarities
of at least 0.8 were found; none shared a contiguous 12-word sequence with the
protected test inputs. This lexical screening cannot rule out semantic overlap,
shorter quotations, latent plot overlap or base-model pretraining exposure.

Spot review found remaining OCR errors despite the filters: Wray's
`cihm_26142:129208:129448` contains `husbai.'d`, and
`cihm_26142:109996:110313` contains `Kat 's`; Murray's
`cihm_11328:424803:425185` contains `spiUing`. These are explicit review defects,
not endorsed training examples. Reject or verify corrections against a facsimile
and record each change before any export. All candidates remain pending.

An independent audit checked all 145 span reconstructions, six raw-file hashes,
catalogue-evidence hashes, protected-input hashes, manifest checksums, unique
record IDs and author/work separation. **67 foundation tests passed**, including
six new tests covering CRLF/Unicode offsets, OCR rejection, split isolation,
protected text, duplicate removal, tampered sources and review-only execution.

## Reproduce the offline build

From the Narratryx directory, with the preserved inputs present:

```bash
.venv-foundation/bin/python -m foundation.english_pd \
  artifacts/english-pd-fiction-v1/selection-plan.json \
  artifacts/english-pd-fiction-v1/review-pack-new
.venv-foundation/bin/python -m unittest discover -s tests -v
```

Use a new output directory; the builder refuses overwrites. It uses only local
files, verifies raw/dictionary checksums, and has no training or network path.
It does not feed these raw-text records into the SFT validator or bypass its
rights/teacher gates. No synthetic teacher targets were created.

The next gate is an editorial and source-rights review of this concrete pool,
followed by balancing and a substantially larger clean collection before a
controlled training comparison. Existing fresh-context cases must remain held
out. Instruction-following, editing and narrative analysis still need separately
permitted, reviewed task examples; raw prose alone does not provide those labels.

All work remained within `llm/Narratryx`. Web/PWA, Tauri desktop, Capacitor iOS
and native macOS source/assets were not changed or built for this isolated task.
No inference, new training, cloud spending, upload or application integration ran.
