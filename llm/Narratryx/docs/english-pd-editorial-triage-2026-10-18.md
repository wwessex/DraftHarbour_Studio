# English-PD editorial triage — 18 October 2026

Completed an AI-assisted text review of all 145 candidate passages. Recommended
excluding **46 current OCR passages** and retaining **99 for facsimile review**:
82 on the training side and 17 from the reserved author. This is a text-screening
recommendation, not human approval, proofreading against scans or legal clearance.
No model calls, training or application changes were made.

## Results

| Source / author | Assignment | Retained passages | Retained words | Excluded |
| --- | --- | ---: | ---: | ---: |
| Paul Meggitt's Delusion / Wray | Training candidate | 1 | 127 | 4 |
| The Three Spaniards / Walker | Training candidate | 3 | 161 | 3 |
| My Novel / Lytton | Training candidate | 70 | 4,517 | 10 |
| Love, Mystery, and Superstition / Opie | Training candidate | 8 | 437 | 0 |
| The Boudoir Cabal / Murray | Reserved evaluation candidate | 17 | 925 | 29 |

The retained training pool has **5,242 words**, with **86.2% from Lytton**.
Removing damaged passages has increased the imbalance. Do not treat the retained
pool as a balanced or training-ready dataset. The earlier larger pool remains
unchanged as an audit input; these screening decisions supersede its membership
recommendations, not its raw text or provenance.

Exclusions include damaged words/names (`husbai.'d`, `Eichard`, `spiUing`),
digit/pronoun or punctuation substitutions, and paragraph fragments created by
page boundaries. Three fragment decisions were checked against preceding raw
text: Wray's isolated `Christ.` follows `be with` across page furniture; Murray's
isolated `Board` follows `Managing`; another Murray passage starts with the
continuation of `courting Mary`. Other reasons, including suspected missing
words, remain cautious editorial flags rather than confirmed facsimile readings.

No corrections were guessed or applied. Historical spelling and dialect were
not modernized. A retain recommendation means only that this text screening
found no obvious defect. It does not verify every spelling, contextual boundary,
quotation, contributor or fact against the printed source.

## A source question resolved

Inspected leaf 7 of the original *Boudoir Cabal* scan. The title page visibly
prints **Toronto: Rogers & Larminie, Publishers, 1875**. The previous report's
1876 reading was the OCR text, which is incorrect. The catalogue and scan agree.
The raw OCR and earlier candidate dossier remain preserved; a separate evidence
supplement records the correction to the edition interpretation.

[Original source item](https://archive.org/details/cihm_11328).

The University of Pennsylvania's
[Online Books Page](https://onlinebooks.library.upenn.edu/webbin/book/lookupname?key=Murray%2C+Eustace+Clare+Grenville%2C+1824-1881)
also corroborates Murray's 1824–1881 attribution. This is catalogue corroboration,
not a civil death-record verification or approval of every contribution in the
selected edition.

The Internet Archive's official
[rights guidance](https://archivesupport.zendesk.com/hc/en-us/articles/360014759692-Rights)
leaves users responsible for checking their intended use. It does not provide
per-item clearance for this model project. The intended source-use terms remain
under review; neither public-domain age nor the HF publisher statement alone
settles those contractual questions. The earlier Archive terms retrieval returned
a JavaScript shell. The help page was readable through web retrieval; saving its
HTML directly returned HTTP 403. Both limits are recorded, not treated as cleared
checks. Wray's independent biographical authority check remains pending.

## Review artifacts

Local directory:

`/Users/williamwessex/Documents/Writer1/llm/Narratryx/artifacts/english-pd-fiction-review-v1/`

- `decisions.jsonl`: all 145 recommendations, specific exclusion reasons and
  source-text/span hashes.
- `train_candidate.screened.pending.jsonl`: 82 unchanged source records.
- `heldout_candidate.screened.pending.jsonl`: 17 unchanged reserved records.
- `summary.json`, `verification.json`: counts, provenance checks and unresolved
  eligibility.
- `evidence/murray-title-leaf7.jpg`: the inspected title page.
- `evidence/index.json`: successful and failed evidence retrievals and hashes.
- `build-review.py`: reproducible application of the recorded recommendations.

Durable records are
`curation/reviews/english-pd-fiction-ai-triage-2026-10-18.json` and
`rights/evidence/murray-boudoir-titlepage-supplement-2026-10-18.json`.
Every human-approval field is empty; every retained passage remains pending.
AI editorial reasons are review metadata, not teacher answers for training.

## Next development step

Prioritize cleaner, edition-traceable texts from the underrepresented authors
before adding more Lytton. Compare retained passages against scans, and reject
or document verified OCR corrections. Resolve source-use and contributor evidence
before requesting a scoped human rights decision on the concrete records.
Reassess author balance after that work; discarding most of Lytton now would
produce an even smaller experiment rather than adequate literary coverage.

Keep Murray out of training and keep the existing task benchmarks protected.
Raw prose prepares a continued-pretraining experiment; editing, analysis and
instruction-following still require separately permitted, reviewed task examples.
Another training comparison should follow a materially better dataset and
specified evaluation criteria. This screening supplies neither a new trained
model nor evidence of improved literary quality.

All work is isolated to Narratryx. Web/PWA, Tauri desktop, Capacitor iOS and native
macOS implementations remain unchanged; no application builds or device tests
were needed for these data/evidence records.
