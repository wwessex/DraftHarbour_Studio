# Independent dialogue and revision sources — 26 October 2026

Seven **pending review examples** are prepared from two new works/authors: five selections from Pauline Hopkins’s *Contending Forces* and two stylistic revision pairs from Henry James’s *The Portrait of a Lady*. No new training, inference, model promotion, application change or paid job was performed. These selections address the lack of fresh source material identified by the [v3 quality review](task-matched-v3-quality-review-2026-10-26.md); they do not establish improved model quality.

## Exact editions and bounded rights assessment

| Source | Original edition acquired | Included scope |
|---|---|---|
| Pauline E. Hopkins, *Contending Forces* | [IA `contending-forces`](https://archive.org/details/contending-forces), Boston, Colored Co-operative Publishing Co., 1900 | Selected original prose on printed pp98–99 and 101–102, Chapter VI |
| Henry James, *The Portrait of a Lady*, Vol I | [IA `portraitoflady01jamerich`](https://archive.org/details/portraitoflady01jamerich), London, Macmillan, 1881 | Two portions of the opening character description on printed p4 |
| Henry James, *The Portrait of a Lady*, Vol I | [IA `portraitlady103jameuoft`](https://archive.org/details/portraitlady103jameuoft), New York, Charles Scribner’s Sons, 1908 | Corresponding portions on printed pp4–5 |

Title pages and each selected prose page were inspected as images. The Hopkins scan is the original 1900 book, not a modern reprint. This resolves the acquisition obstacle in the [earlier Hopkins candidate dossier](../rights/dossiers/hopkins-candidate-2026-10-26.md); that historical account of failed access remains intact.

The [Smithsonian’s Hopkins biography](https://www.searchablemuseum.com/pauline-elizabeth-hopkins/) records her life as 1859–1930 and the book’s 1900 publication. [Project Gutenberg’s James catalogue](https://www.gutenberg.org/ebooks/2833) records 1843–1916. The scoped assessment applies the ordinary term for literary works in [UK government guidance](https://www.gov.uk/copyright/how-long-copyright-lasts) and the historical maximum duration described in [US Copyright Office Circular15A](https://www.copyright.gov/circs/circ15a.pdf). The original publications are beyond these terms. IA metadata independently marks Hopkins/1908 James public domain and 1881 James `NOT_IN_COPYRIGHT`; those labels are corroboration, not dataset-wide clearance.

The new [scoped ledger](../rights/independent-scenes-v1.scoped.jsonl) has three AI evidence-reviewed records for selected original prose and private GB/US training/evaluation uses only. **No human approval or legal certification is recorded.** All artwork, captions, epigraphs, scripture, nonselected prose, front matter, site apparatus and modern editorial additions are excluded. Historical copyright notices identify past claims and do not establish an additional prose coauthor. No claim about the rights to all scanned images or a full modern edition is made.

The [PSU New York Edition editorial account](https://portraitofalady.la.psu.edu/new-york-edition-1908/) corroborates James’s author revision for the collected edition. It was consulted for bibliography only: its modern scholarly electronic text and commentary are not training material. The paired wording was transcribed independently from the original 1881/1908 page images. Individual punctuation differences are not attributed at manuscript level, and the later reading is not declared objectively better.

Full IA site terms were not retrievable through the web text interface. The evidence retains the item metadata and its public-domain signals. This assessment authorises no upload, publication, branded redistribution or reuse of independently protected provider material.

## What the packet teaches

| Draft examples | Intended task | Review considerations |
|---|---|---|
| Hopkins: room | Fiction/setting | Practical objects convey how the lodger makes a temporary room welcoming. |
| Hopkins: embroidery | Dialogue | Four speech paragraphs, warmth and a politely unanswered question, with narration. |
| Hopkins: typewriting | Dialogue | Question/answer, a qualified opinion and the physical action of offering a chair. |
| Hopkins: invitation | Dialogue | Mock formality, matching acceptance and a farewell; period diction retained. |
| Hopkins: host’s goal | Storytelling | Two complete sentences linking a desire to a social action; historical social judgements stay attributed to the narrator. |
| James: face | Stylistic editing | Syntax, contrast and “expression”/“representation” change. This permits an interpretive nuance shift and is unsuitable as minimal copyedit gold. |
| James: dogs | Stylistic editing | A small lexical revision from “contemplated” to “took in”; modest teaching value, not a broad preference example. |

All literary answers are exact spans of scan-transcribed author prose. AI constructed the task instructions after reading those passages. No generated literary answer, invented analysis, artificial corruption, preference ranking or minimum editing length has been added. The historical tasks are candidates for review, not a claim that the original authors responded to these instructions.

The five Hopkins examples come from **one connected chapter**. The two James pairs come from **one character description**. Seven examples therefore represent two works, not seven independent stories; the James pairs are too few and subtle to constitute a revision curriculum. No new pacing or narrative-analysis gold is claimed.

## Traceability and fail-closed review

- [Review packet](../artifacts/independent-scenes-v1/REVIEW.md) contains each instruction, source answer, original text for revision pairs and scan links.
- `artifacts/independent-scenes-v1/draft.records.jsonl` contains seven schema-valid records with `review.status: pending`. `split: train` is prospective membership only. The existing dataset validator rejects the packet because its example reviews are pending.
- [Preparation/check script](../curation/independent-scenes-v1/prepare.py), [source lock](../curation/independent-scenes-v1/source-lock.json) and [packet lock](../curation/independent-scenes-v1/packet-lock.json) bind three OCR discoveries, three canonical transcriptions, nine exact segments, metadata, images and packet bytes. Raw literature, scans and review answers stay ignored by Git.
- Canonical coordinates use Python UTF-8 text code points with LF newlines. Printed line wrapping, line-end hyphenation and spacing were normalised; wording/spelling was retained and quotation marks encoded consistently. OCR was used for discovery, not as gold. These transcriptions still require accuracy review; hashes establish identity, not correctness.
- The 1908 scan’s generic page metadata disagreed with processed JP2 images: leaves43/44 actually show printed17/18. Selected opening pages are **leaf30=printed4** and **leaf31=printed5**, verified visually. The wrong-page discovery images remain evidence only. Hopkins leaves99/100=printed98/99; leaves102/103=printed101/102. James1881 leaf18=printed4.
- `verification.json` records exact target-to-source checks, two prior dataset screens, and overlap checks against the original **draft** formal evaluation pack plus v2/v3 diagnostic packs. No exact prior answer reuse or cross-split author/work/near-duplicate conflict was found by these bounded lexical checks. This is not a semantic contamination guarantee.
- `preservation.json` verifies all20 frozen v3 inputs, all12 protected artifacts and the active craft model configuration hash remained unchanged. No old benchmark, held-out text or recorded judgement was modified.

From this directory’s parent workspace (`llm/Narratryx`), verify the local packet with:

```bash
.venv-foundation/bin/python curation/independent-scenes-v1/prepare.py verify
.venv-foundation/bin/python -m foundation validate-ledger rights/independent-scenes-v1.scoped.jsonl \
  --release --jurisdictions GB US --use training
.venv-foundation/bin/python -m unittest discover -s tests -v
```

`prepare.py build` creates a new packet from the pinned local evidence/transcriptions and refuses to overwrite an existing packet or ledger. The initial preparation caught a reference to a nonexistent reviewed formal benchmark; the screen now explicitly uses the actual draft and labels its status accurately. No missing benchmark was silently invented or skipped.

Fresh validation on 26 October: **126 CPU foundation tests passed** in 40.625 seconds, including six new transcription/evidence guards. Packet verification passed; the three-record scoped ledger passed release-evidence validation for GB/US training, with `legal_certification: false`. Draft dataset release validation correctly fails on pending example reviews. Git whitespace and ignored-literature checks passed. These checks establish structural safeguards, not literary quality or human transcription approval.

## Next model-development gate

Review this packet’s transcription and task fit before approving any example. Then expand the independent author/work coverage, especially complete dialogue, causally coherent scenes and substantive revision pairs. Reject low-value variants rather than counting every punctuation difference as training progress. Retain this work as one sampling group per author/work; avoid random excerpt splits.

Before a further run, freeze a broader source mixture and a separate diagnostic covering chronology, factual grounding, instruction adherence, dialogue and restrained editing. Measure token budgets without truncating source pairs. Compare the same base, current craft adapter and new candidate in fresh contexts, with human literary judgements recorded separately from AI/mechanical checks. Keep the current app model until an upgrade is supported by evidence.

All changes in this preparation are confined to Narratryx. Web/PWA, Tauri Windows/Linux, Capacitor iOS and independent native macOS received no source, asset or configuration changes from this task; no app/device builds were needed or run.
