# Craft pilot: source evidence and exact scope

20 October 2026. This is a Codex AI evidence assessment for a private GB/US pilot, not a human approval, legal opinion, or certification of a particular physical copy. The user authorized proceeding with sources requiring no new rights-holder permission. No human review ballot has been invented.

## Selected material

| Source | Identified artifact and publication | Author dates | Ordinary GB literary term elapsed by | Use |
|---|---|---|---|---|
| Edith Wharton, *The Writing of Fiction* | PG72446, title matter: Scribner, 1925, copyrights 1924/1925 | 1862–1937 | 2007 | Six original craft paragraphs |
| Clayton Meeker Hamilton, *A Manual of the Art of Fiction* | PG30183, title matter: Doubleday, Page, **1919 printing** of copyright-1918 revision | 1881–1946 | 2016 | Fourteen original craft paragraphs |
| Katherine Mansfield, *The Garden Party and Other Stories* | PG1429 digital artifact; original collection 1922; exact physical printing not established | 1888–1923 | 1993 | Two contexts, evaluation only |
| Charles W. Chesnutt, *The Conjure Woman* | PG11666 digital artifact; original-publication notice 1899, Houghton, Mifflin; exact physical printing not established | 1858–1932 | 2002 | Two contexts from original collection, evaluation only |

The ledger pins each **digital artifact**, not a purported facsimile. No claim is made that Mansfield's file is a particular Constable or Knopf printing. The original collection's Constable attribution is bibliographic, not identification of the PG copy. Chesnutt's assembled digital file contains later appended works; all appendices are excluded. Mansfield's epigraph and dedication are excluded. The retained Chesnutt passages include historical diction; their spelling and dialect are not modernized.

Every included span is enumerated in `artifacts/craft-expansion-v1/scope.json`, with LF-normalized Unicode offsets. Raw downloads are retained unchanged under `rights/raw/craft-expansion-2026-10-20/`, including all provider notices. `acquisition.json` records retrieval URLs, byte counts and SHA-256s. The scoped ledger includes the scope file's hash. The two test authors receive **evaluation-only** clearance, not training clearance.

## Evidence and inference

The [UK government term guide](https://www.gov.uk/copyright/how-long-copyright-lasts) gives the ordinary literary term as 70 years after death. The author dates above are documented in the item-specific catalogues: [Wharton](https://www.gutenberg.org/ebooks/72446), [Hamilton](https://www.gutenberg.org/ebooks/30183), [Mansfield](https://www.gutenberg.org/ebooks/1429), [Chesnutt](https://www.gutenberg.org/ebooks/11666). These catalogues each identify their particular ebook as public domain in the USA. The [US Copyright Office historical-term circular](https://www.copyright.gov/circs/circ15a.pdf) corroborates expiration of historical published works before 1931 as of 2026. Applying these facts to the specified original prose supports the scoped GB/US expiry conclusion; it does not clear unidentified modern additions or all jurisdictions.

Independent supporting records include [NYPL's Wharton finding aid](https://archives.nypl.org/mss/4675), the [National Library of New Zealand's Mansfield guide](https://natlib.govt.nz/guides/katherine-mansfield), [Fisk's Chesnutt collection inventory](https://www.fisk.edu/wp-content/uploads/2020/06/chesnutt-charlesw.collectionsupplement11898-1942.pdf), and the [University of Virginia's source description of the 1922 Mansfield collection](https://anthology.lib.virginia.edu/work/Mansfield/mansfield-garden). Their modern descriptive prose/annotations are evidence, never training targets. The NYPL browser extraction was readable, but its direct local HTTP snapshot returned a 212-byte access challenge; **that snapshot is not usable archival evidence**. The PG item record remains the retained date evidence for Wharton. Hamilton's NYPL record also could not be fetched consistently; the item catalogue and historical title matter support the current record.

Provider [permission guidance](https://www.gutenberg.org/policy/permission.html), [terms](https://www.gutenberg.org/policy/terms_of_use.html), [license](https://www.gutenberg.org/policy/license.html), and [listed mirrors](https://www.gutenberg.org/MIRRORS.ALL) were checked. Acquisition used its listed `gutenberg.pglaf.org` mirror and five individual files, not a bulk corpus. Selected prose is unbranded; original notices remain with the private evidence. No separate permission request is needed for the expired original prose under this assessment. Provider trademark conditions are not treated as copyright in the underlying historical prose. No branded redistribution, external upload, publication, or provider endorsement is part of this pilot.

Local evidence snapshots and their hashes are in `rights/evidence/craft-expansion-2026-10-20/manifest.json`; a successful HTTP response alone is not proof that a snapshot contains useful evidence.

## Revision-pair finding

Hamilton's publisher foreword describes the later manual as an author-revised expansion of his earlier work. The earlier downloaded artifact, PG30776, has **1911** Chautauqua title matter and a 1908 copyright; it must not be labelled a 1908 printing. The later artifact is a **1919** printing, not a 1918 printing.

Conservative paragraph alignment has not established a substantive, correctly aligned author-revision pair. Historical bold headings, whitespace, punctuation and documented modern transcription corrections are not evidence of an author's editorial improvement. **Zero revision pairs are included.** The earlier Hamilton file is retained for comparison research only and is not in the training ledger. This part of the proposed expansion remains unfinished; a documented revised edition is not itself a usable before/after dataset.

A subsequent body-wide word comparison (ignoring topical headings for alignment) found two replacement hunks of at least five words on both sides. Both update Kipling publication references from magazine appearances to *Actions and Reactions*. These are bibliographic edition variants, not demonstrations of improving fictional prose. They remain excluded. The comparison is retained in `artifacts/craft-expansion-v1/revision-diff-research.json`; smaller differences and additions have not been exhaustively attributed to the author. This finding does not justify treating every digital difference as an author revision.

## Transformations and limits

Training answers are the historical authors' prose with whitespace collapsed and, for Hamilton where present, a leading topical heading removed. Questions are task instructions; they are masked from training loss. There are no generated literary answer targets or teacher-model outputs. The pilot contains 20 examples / 2,443 answer words / 2,850 supervised tokens including EOS, suitable only for a small exploratory comparison. Historical craft opinions are attributed to their authors; they are not asserted to be universal rules.

The 16 diagnostic tasks cover continuity, minimal editing, dialogue and compression across four source contexts. No exact canonical continuation is required. Editing has no minimum word count. Fiction quality needs human review; mechanical limits are reported separately. The formal Phase 1 benchmark and its pending human review are unchanged.

All application versions remain outside this work: web/PWA, Tauri desktop, Capacitor iOS and native macOS.
