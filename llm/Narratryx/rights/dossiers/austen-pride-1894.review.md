# Evidence review: Austen pilot source

Date: 17 October 2026. Performed by: **Codex, an AI assistant**. This is an evidence/scope review, not a named human approval or a legal opinion. This review describes the evidence before sign-off. The human user subsequently approved the limited scope; see the approval record below. The content-selection gate remains open.

**Recommendation:** the evidence supports the underlying Austen novel as a suitable GB/US public-domain pilot source. Present the corrected dossier for human sign-off on the narrow scope below. It does not support treating the complete downloaded ebook as ready-to-train data.

## Findings

| Check | Review result |
| --- | --- |
| Source identity | Original file still matches 772,386 bytes and SHA-256 `3f6bb9d6f78e0293b56acd4714dd68cb7d6d1d293402031ce9d5a216bcaf9d75`. Outer-range hash and coordinate boundaries also match. |
| Print provenance | British Library evidence identifies the 1894 George Allen illustrated edition; the transcription's title matter names Allen, Saintsbury and Thomson. The exact digital artifact is pinned. A particular physical copy/impression and its complete scan lineage have not been independently matched page by page. Do not claim a facsimile or critical-edition verification. |
| GB basis | Austen's 1817 death and the ordinary UK literary-duration rules support expiry for the original novel. The 1894 edition is not a reason to claim new rights over Austen's underlying prose. Modern additions remain outside scope. |
| US basis | Item-specific Gutenberg status supports the conclusion. Added Copyright Office Circular 38B analysis: foreign-work restoration has eligibility and remaining-term limits; it does not make Austen's expired original text newly protected. The prior reliance on a US-publication cutoff alone would have been insufficient for a London edition. |
| Excluded contributors | Saintsbury's preface and Thomson's artwork/captions stay excluded. The Edinburgh archive detail page still could not be retrieved; confirming its indexed Saintsbury dates is not needed to include Austen alone, but is required if the preface later becomes proposed data. |
| Inventory correction | **154** illustration blocks occur inside the outer narrative range: **69 captioned blocks and 85 bare `[Illustration]` markers**. The earlier total of 69 was incomplete. All 35 occurrences of the historical 1894 copyright notice are inside the captioned blocks. |
| Chapter parsing | The outer range contains all 60 chapter headers from II through LXI when matched without case sensitivity and without requiring a final period. Chapter I's heading is in artwork before the narrative start. A strict uppercase/period parser would miss headings. |
| Formatting | The source has emphasis markup. Preserve its literary meaning or document a reversible transformation; do not indiscriminately delete underscores or quoted passages. No `{number}` page markers were found in this particular outer range, so do not remove narrative numbers on that assumption. |
| Acquisition | Main-site terms discourage/prohibit automated website use. The prior snapshot was obtained programmatically; the dossier now records that fact and does not call access compliance verified. Future/replacement acquisition must follow the applicable site's permitted human-download or mirror rules. Preserve the existing audit trail. |

Evidence rechecked: [British Library edition identification](https://www.bl.uk/stories/blogs/posts/jane-austen-names-and-notability), [Austen dates/publication](https://www.bl.uk/stories/blogs/posts/jane-austen-at-250), [UK IPO duration guidance](https://www.gov.uk/copyright/how-long-copyright-lasts), [Gutenberg item record](https://www.gutenberg.org/ebooks/1342), [US Copyright Office Circular 38B](https://www.copyright.gov/circs/circ38b.pdf), [Gutenberg license](https://www.gutenberg.org/policy/license.html), [website access terms](https://www.gutenberg.org/policy/terms_of_use.html).

The copyright conclusions above are inferences from those facts and official guidance, scoped to the original novel text. Website access terms and the intended handling of derivative files are separate from copyright expiry. Gutenberg's unbranded-text guidance is not a worldwide assurance or an automatic license for every modern addition. Provenance acknowledgements can remain in internal documentation; avoid product branding or endorsement claims. No bulk access, dataset publication or model distribution has been authorized by this review.

## Scope to put before a human reviewer

- **Source:** the pinned PG #1342 artifact of the identified 1894 edition.
- **Content:** a small, inspected selection of Austen's own novel prose. Exclude the preface, all illustration blocks and captions, title/contents/credit/license material, modern additions and printer matter. A chapter or outer-range boundary alone does not implement these exclusions.
- **Uses proposed:** preparing and evaluating fiction-craft training examples; eventual training only after the examples and source spans pass their own review. This is a public-domain-expiry basis, not reliance on a commercial text-and-data-mining exception.
- **Territories proposed:** GB and US only. Choose and check the cloud processing location before sending source text there; do not infer worldwide clearance or a data-redistribution decision.
- **Source handling:** retain the raw source and notices privately, follow permitted acquisition routes, preserve exact hashes and span coordinates, and document transformations. Do not silently relabel a replacement file as this snapshot.

The human decision can approve this scope, narrow it, reject it, or request advice about a specific unresolved issue. It must identify the real reviewer and date. This review does not supply that identity or consent, and it is not an instruction to change the ledger status merely to pass validation.

## Checks performed

Recomputed source and range hashes; checked start/end anchors; counted both illustration-marker forms and historical notices; checked chapter headings; re-read public primary evidence and source terms. The corrections affect only Narratryx evidence and documentation. Application code/assets, model weights, training data and source bytes are unchanged. No source upload, cloud job, training or device/platform build was performed.


## Human scope approval recorded — 17 October 2026

The human user explicitly replied “i approve” after the corrected review. Codex recorded that decision in the [approval audit record](../approvals/austen-pride-2026-10-17.json), preserving hashes of the documents as they stood when approved. Reviewer attribution is the human user of this conversation; no legal name or legal qualification was supplied. Earlier pending-status statements above describe the pre-approval history and are superseded for the limited scope only.

GB/US training/evaluation uses are now recorded for the reviewed Austen-only scope. Exact passage selection, removal of excluded material and training-example review remain required. The raw file is not a training-ready dataset. Other books, benchmark/rubric approval, redistribution, uploads, paid jobs and training launches are outside this approval. The source-release validator must continue to reject this record until the content-selection gate is satisfied.
