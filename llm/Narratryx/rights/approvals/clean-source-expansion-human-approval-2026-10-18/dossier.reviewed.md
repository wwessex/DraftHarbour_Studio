# Rights and source review: Opie and Wray expansion

Reviewed 18 October 2026 by Codex, an AI assistant. **The evidence supports the
proposed GB/US original-prose scope below. No human scope approval has been
recorded.** Two structurally valid pending records are in
`rights/clean-sources.pending.jsonl`; the established release validator correctly
refuses to release them while their review status is pending. The main ledger,
earlier approvals and source bytes have not been changed.

## Exact sources obtained

| Work | Selected transcription and print description | Original work | Author |
| --- | --- | --- | --- |
| The Father and Daughter: A Tale, in Prose | PG 49621, ninth edition; title matter reads London, Longman, Hurst, Rees, Orme, Brown & Green, 1824 | First published 1801 | Amelia Opie, 1769–1853 |
| Nestleton Magna: A Story of Yorkshire Methodism | PG 41916, “Thirtieth Thousand”; James Nisbet & Co., 21 Berners Street, London; **undated** title matter | First edition: Elliot Stock, London, 1876 | J. Jackson Wray, 1832–1892 |

These are new works, not the previous English-PD *Tales of the Heart* or *Paul
Meggitt's Delusion*. They have separate work/source IDs. Their provider records
credit distributed proofreading and classify both ebooks as public domain in
the USA: [Opie](https://www.gutenberg.org/ebooks/49621),
[Wray](https://www.gutenberg.org/ebooks/41916).

The exact digital editions are identified by these full-source SHA-256 hashes:

- Opie: `c7211c15f1242d55b25f35d02fb39b35be98d1c1e59cff6b9fb80182726801ac`
- Wray: `02f3ab051a0529e3ee32c7061e98213437a43e5dc923ce37d4cd2ab8d5abc07d`

The selected full files retain their original notices and normative licence.
They are stored privately under `rights/raw/clean-source-expansion-2026-10-18/`.
Plain-body versions were obtained first, then the full-header/licence versions;
all four original downloads are preserved. Their combined size is **1,534,163
bytes**. No bulk corpus or scan collection was downloaded.

Wray's 1876 date is the **first publication of the work**, not a date assigned
to this undated printing. The transcription's preface describes authorial
revision, but we have not matched it to a particular dated physical impression.
The proposed inclusion is Wray's expired original narrative prose; it does not
claim that an unspecified modern critical edition or later contributor's
additions are cleared. Provider permissions explicitly do not promise exact
fidelity to a particular physical copy. No facsimile collation is claimed.

## Evidence and copyright conclusions

Opie's death in 1853 is corroborated by the
[National Portrait Gallery](https://www.npg.org.uk/collections/search/person/mp03370/amelia-opie).
The [University of Toronto bibliography](https://jacksonbibliography.library.utoronto.ca/author/details/opie-amelia/10714)
corroborates the original work's 1801 publication. Wray's 1832–1892 attribution
is independently corroborated by the scholarly
[At the Circulating Library author record](https://victorianresearch.org/atcl/show_author.php?aid=6059),
which cites biographical/probate sources. Its
[title record](https://victorianresearch.org/atcl/show_title.php?aid=6059&tid=25415)
identifies the 1876 first edition and cites BL/EC. This resolves the earlier
single-catalogue gap in Wray's biographical evidence; it is not a claim that a
civil register was personally examined.

**GB:** The ordinary literary term is life plus 70 years. On the identified
authorship, Opie's underlying prose term ended no later than 31 December 1923,
and Wray's no later than 31 December 1962. No original printed-page layout is
being copied into the paragraph dataset. The conclusion concerns these authors'
prose, not unknown modern additions or other contributors' work.
[UK IPO duration guidance](https://www.gov.uk/copyright/how-long-copyright-lasts).

**US:** Each selected provider item explicitly reports US-public-domain status.
The historical publication facts support the underlying-work conclusion.
Foreign-work restoration is limited to any remaining applicable US term; an
old foreign publication is not assessed by assuming a US publication alone.
The conclusion does not turn the undated Wray printing into a verified 1876
copy or clear an unidentified later contribution.
[Copyright Office Circular 38B](https://www.copyright.gov/circs/circ38b.pdf).

Neither basis relies on a research-only text-and-data-mining exception. Proposed
training/evaluation may support the eventual commercial writing application,
subject to the source scope and handling conditions. No worldwide conclusion,
model-distribution review or corpus-redistribution decision is supplied here.

## Source access and reuse terms

Book downloads used `gutenberg.pglaf.org`, named in the
[official mirror list](https://www.gutenberg.org/MIRRORS.ALL). Gutenberg's
[website terms](https://www.gutenberg.org/policy/terms_of_use.html) direct
automated download software to mirrors. This acquisition followed that route;
there were no automated book-file downloads from the main website. Policy and
catalogue research used web retrieval; mirror directory listings are retained.
The mirror's `robots.txt` returned 404; the documented mirror route, rather than
that absence, is the access basis.

Both full-source files were checked for their individual headers and complete
licence. Neither book-specific header carries a special copyright-holder
permission restriction. General conditional examples in the standard licence
are not such an item-specific restriction.

The [licence](https://www.gutenberg.org/policy/license.html), including clause
1.C preserved in each source, distinguishes unprotected book text from provider
branding and notices. The [permissions guidance](https://www.gutenberg.org/policy/permission.html)
allows commercial reuse of US-public-domain text, while requiring separate
non-US checks. This review supplies the scoped GB assessment above. Keep full
original files/notices private; derived model-input paragraphs contain no
Gutenberg branding, licence, credits, catalogue summaries or endorsement. Retain
source attribution in internal provenance. Distribution of branded ebooks and
product marketing using the provider trademark are outside this proposal.

The prior Archive/Google-source contractual questions do **not** disappear for
the old files. They are avoided for these independently acquired sources; no
old record is relabelled, approved or silently substituted.

## Concrete inclusion scope

The review file is:

`artifacts/clean-source-expansion-v1/train-candidates.screened.pending.jsonl`

SHA-256: `b575358cf5c419545c27326ec6e9e04076aad886c0d0fb38b3e6f9ad6e6d907e`.

It contains **108 passages / 9,871 words**:

- Opie: 54 passages / 4,969 words.
- Wray: 54 passages / 4,902 words.

Each record pins its full raw file, Unicode code-point span, raw-span and text
hashes. CRLF characters are preserved in the coordinate source; only whitespace
is collapsed in the derived paragraph. No historical spelling, dialect, plot,
wording or punctuation is rewritten. The readable `REVIEW.md` contains the
exact proposed passages and their IDs.

Exclude title/credit/licence matter; dedications, prefaces and contents;
illustrations/captions; printer matter and advertisements; footnotes and
footnote-bearing paragraphs; indented verse/attribution blocks; unverified modern
additions and rejected passages. Wray selection also conservatively excludes
detected scripture/hymn/religious-reference paragraphs, rather than including
whole Bible or poetic passages on the strength of Wray's death date. This is a
selection scope, not an assertion that all religious prose has separate rights.
The remaining sample is not representative of the whole religious novel.

General historical allusions, proverbs and fictional dialogue remain within
the selected prose. Complete contributor/facsimile scrutiny of every candidate
has not been performed. Apparent problems discovered during editorial review
must be excluded or verified, not guessed away. One proofread-source name error,
`Adam Quiver` for the otherwise named Adam Olliver, was already excluded without
rewriting the source. The other passages remain pending editorial acceptance.

## Other source decisions and gates

George Walker's underlying works remain promising public-domain material, but
this search did not establish a suitably clean, openly reusable transcription.
The [Wellcome catalogue result](https://wellcomecollection.org/works/n644wpbv)
for *The Vagabond* identifies an ECCO electronic resource; it was not treated as
an open corpus licence or used to obtain text. Walker's earlier OCR candidates
are not promoted. Google-derived Hay remains quarantined. The two new sources
can be assessed independently of those unresolved legacy copies.

Murray stays reserved for evaluation. His source, the 120 draft benchmark tasks
and 14 fresh-context cases are protected from the expansion. No synthetic
teacher answers were created, and no teacher-output permission was inferred.

The two new rights records pass structural validation and have zero approved
records. Release validation fails as expected because their review status is
pending. A future scoped human decision must refer to this dossier and the
specific hashed passage file; no such decision is invented here. Even source
approval alone does not turn unreviewed passages into a training-ready dataset.

Evidence notes, acquired metadata, original files, exclusions, source selection,
test log and verification report are in
`artifacts/clean-source-expansion-v1/`. No uploads, inference, paid jobs or
training ran. All work is isolated from the web/PWA, Tauri desktop, Capacitor
iOS and native macOS applications.
