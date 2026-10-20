# Rights evidence: Pride and Prejudice, George Allen edition (1894)

Research date: 17 October 2026. Ledger ID: `austen-pride-candidate`. Decision: **selected for a pilot; pending named human review**. This is a researched evidence dossier, not a legal certificate or permission to train. No clearance entry or human signature has been fabricated.

## Exact edition and scope

Selected print edition: Jane Austen, *Pride and Prejudice*, London: George Allen, **1894**, with a preface by George Saintsbury and illustrations by Hugh Thomson. The British Library identifies this edition and its illustrator. The digitized title matter names the same publisher and contributors; historical copyright lines also identify 1894. [British Library edition evidence](https://www.bl.uk/stories/blogs/posts/jane-austen-names-and-notability), [digitized title matter](https://www.gutenberg.org/files/1342/1342-h/1342-h.htm).

Selected digital source: **Project Gutenberg eBook 1342**, plain-text UTF-8 transcription. This is a modern transcription of the selected historical edition, not an 1813 first-edition facsimile or a guarantee of exact textual identity with every 1894 impression. The catalogue credits Chuck Greif and the Online Distributed Proofreading Team, using Internet Archive source images. It identifies the work as public domain in the USA. [Source catalogue](https://www.gutenberg.org/ebooks/1342).

Proposed inclusion is **Austen's novel text only, Chapters I–LXI**. Exclude the preface, illustrations and their captions, ornamental material, contents/list of illustrations, dedication, page markers, printer matter, historical copyright lines, modern summaries, transcription/editorial additions, credits, and Gutenberg wrapper/license/trademark material from model inputs. Retain the complete source and notices unchanged as private evidence. Neither the British Library's modern article nor other research pages are proposed training material.

## Pinned source artifact

One book file was retrieved solely to document this edition. No bulk corpus was downloaded, no source text was uploaded to Unsloth, and no training dataset was produced.

| Item | Recorded value |
| --- | --- |
| Retrieval | 17 October 2026, 22:48:15 UTC |
| Requested URL | `https://www.gutenberg.org/ebooks/1342.txt.utf-8` |
| Resolved URL | `https://www.gutenberg.org/cache/epub/1342/pg1342.txt` |
| Original bytes | 772,386; UTF-8 with CRLF line endings; no BOM |
| SHA-256 | `3f6bb9d6f78e0293b56acd4714dd68cb7d6d1d293402031ce9d5a216bcaf9d75` |
| Local evidence file | `rights/raw/austen-pride-1894-pg1342-2026-10-17/pg1342.txt` relative to Narratryx |
| Machine-readable record | [Source manifest](../evidence/austen-pride-1894-source.json) |

The downloaded text's header reports an update on **1 September 2026**; the web catalogue observed during research reports **29 September 2026**; the download response's Last-Modified header reports **1 October 2026**. These are different metadata labels, not a resolved version history. Use the byte hash above as the artifact identity, and do not silently replace this file with a later download. The raw directory is ignored by Git: the dossier/manifest will travel with the repository, but this local evidence file will not.

The manifest records an outer novel range in the validator's text view: start **35,259**, end-exclusive **729,437** Unicode code points. That view uses Python `Path.read_text(encoding='utf-8')`, which normalizes CRLF to LF. These are **not byte offsets**. The byte snapshot remains unchanged. The outer range begins at the first narrative paragraph and ends at the final narrative paragraph; it still contains **154 illustration blocks** (69 captioned blocks and 85 bare markers) and other non-novel material. The initial inventory counted only captioned blocks; the evidence review corrected that error. It is an inspection aid, **not a cleaned or approved source selection**. Final training spans must avoid excluded material and use the same coordinate convention as the validator.

## Contributor and publication evidence

| Contributor/material | Evidence | Treatment |
| --- | --- | --- |
| Jane Austen, 1775–1817; novel first published 1813 | [British Library, Jane Austen at 250](https://www.bl.uk/stories/blogs/posts/jane-austen-at-250) | Only included literary author. |
| George Saintsbury, 1845–1933; edition's preface | [University of Edinburgh archive description](https://archives.collections.ed.ac.uk/repositories/2/resources/348); title matter above | Record identity, but exclude the preface. The archive search result supplied the life dates; direct retrieval of its detail page failed during research, so confirm the cited record if this contribution is ever brought into scope. |
| Hugh Thomson, 1860–1920; illustrations | [University of Glasgow biography](https://www.whistler.arts.gla.ac.uk/correspondence/people/biog/?bid=Thoms_H&initial=); British Library edition evidence above | Exclude illustrations and captions; no permission to use a different modern reproduction is inferred. |
| Modern digitizers and hosting institutions | Source catalogue and embedded credits | Keep provenance privately; do not treat modern additions as Austen's text. |

## Jurisdiction findings

**GB — research finding supports public-domain use of the underlying novel text.** Austen's death in 1817 is established by the British Library. UK IPO guidance gives a usual literary copyright duration of 70 years after the author's death and separately gives published-edition layout a 25-year term. The novel and this historical edition are well beyond those periods. The intended input is the author's literary text, not modern editorial material or a reproduction of a newly typeset edition. This conclusion concerns the stated scope; it does not establish rights in every modern version. [UK IPO duration guidance](https://www.gov.uk/copyright/how-long-copyright-lasts).

**US — research finding supports public-domain use of the underlying novel text.** Gutenberg's record expressly assigns US public-domain status to this item. The original novel was published in 1813 and the selected edition in 1894. The Copyright Office describes the duration rules and the maximum 95-year term for applicable older copyrights. Its specific pre-1931 statement refers to US publication, so it should not be mechanically substituted for an analysis of every foreign edition; the item-specific Gutenberg determination is additional evidence here. The Copyright Office’s foreign-work restoration guidance further explains that restoration requires the source-country term not to have expired and restores only the remainder of the otherwise applicable US term. Austen’s 1813 text was already far beyond its UK term by the relevant restoration period; the 1894 print date does not give the underlying novel a new copyright term. This addresses foreign origin rather than treating the London edition as a US publication. No item-specific permission-only restriction was observed in the opening metadata of the pinned text. [Copyright Office Circular 38B](https://www.copyright.gov/circs/circ38b.pdf), [Source catalogue](https://www.gutenberg.org/ebooks/1342), [US Copyright Office Circular 15A](https://www.copyright.gov/circs/circ15a.pdf).

These findings are ready for review. The ledger's `clearances` array deliberately remains empty until a named human records a decision. Other processing/training countries and distribution markets have not been assessed. This dossier does not say that a future base model was itself pretrained exclusively on public-domain material.

## Source terms and handling proposal

Gutenberg distinguishes the literary text from its trademark/license material, limits its copyright assurances to the US, and explains a route for using unrestricted text with its branding removed. It also warns that items supplied by permission can have separate restrictions. Keep the source's complete embedded license as evidence; do not infer that every downloaded ebook is freely reusable. [License and text/branding distinction](https://www.gutenberg.org/policy/license.html).

The proposed workflow uses separately reviewed, unbranded Austen-only text for training/evaluation, while internal provenance continues to identify its origin. It does not publish a Gutenberg-branded ebook, sell access to the raw source, or imply Gutenberg endorsement. Source credit in research documentation is separate from product branding. The reviewer should confirm this handling before approving a derivative dataset or model release; removing a name alone is not legal verification. Gutenberg's permission guidance also distinguishes faithful formatting/transcription from protected added material, and its website has separate access terms. [Permission guidance](https://www.gutenberg.org/policy/permission.html), [website terms](https://www.gutenberg.org/policy/terms_of_use.html).

Acquisition is a separate issue from the novel’s copyright status: Gutenberg’s main-site terms say the website is intended for human users and warn against automated access. The earlier pinned snapshot was retrieved programmatically; that fact is preserved in the audit record, not described as verified compliance. Do not repeat direct automated main-site downloads. Use a human browser download or a mirror/acquisition route expressly permitted by the relevant site’s rules, and record its own retrieval details and hash. An identical replacement can be checked against this fingerprint; changed bytes require a new source version. This process issue does not by itself renew Austen’s expired literary copyright. [Website access terms](https://www.gutenberg.org/policy/terms_of_use.html).

No website evidence page is treated as an open training-data grant. Later dataset or model distribution requires its own packaging/notice review; no `redistribution` clearance is proposed by this dossier.

## Concrete review and next preparation

1. A named human reviews the edition identity, GB/US findings, intended training/evaluation uses, source terms and scope above. Record actual findings and review date; do not change status simply to make a command pass. Escalate a genuine ambiguity if one is found.
2. After that decision, record only the jurisdictions and uses actually approved. The other three ledger records remain pending; the all-record `validate-ledger --release` command will still reject them.
3. Before training, prepare a small selection of Austen-only paragraphs with exact source spans, manually check it against the pinned source, and review any transformations. Do not use the raw full book or the outer range as a clean dataset.
4. Construct and review a few craft examples from those passages, keeping the work/author in one split and out of the held-out benchmark. No fine-tuning starts as part of this evidence task.

## Validation and application boundary

The ledger remains pending. Structural/schema checks and the raw artifact hash can be verified now; release validation is expected to reject pending approval. Work is confined to Narratryx rights documentation, provenance and the ignored single-source evidence file. Web/PWA, Windows/Linux Tauri, Capacitor iOS and native macOS application source/assets are unchanged; their builds and device behavior are outside this documentation task.

Executed checks: structural ledger validation passed (four records, zero approved); the existing pending-candidate regression test passed; source bytes, outer-range coordinates and both stored hashes matched. GB/US training release validation failed as expected with `austen-pride-candidate: review status is pending, not approved`. Tracked whitespace checks passed and no application-source/dependency changes were found. No dataset, inference, model-quality, platform-build or device tests were performed for this evidence task.


## Evidence-review result

See the [17 October evidence review](austen-pride-1894.review.md) for corrections, the precise recommended scope and remaining human decision. This AI review does not change `review.status` or create a clearance.
