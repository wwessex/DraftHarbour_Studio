# Author-revision sourcing candidate — 25 October 2026

**Excluded from training.** One structural revision candidate has been prepared locally. No rights-ledger entry, human approval, training release, adapter promotion or application model change was made.

## Sources and evidence

- John Forster, *The Life of Charles Dickens*, Project Gutenberg [25851](https://www.gutenberg.org/ebooks/25851), specifically Vol. III, discussion of *Great Expectations* and footnote 270. The [transcription](https://www.gutenberg.org/cache/epub/25851/pg25851-images.html) reports Dickens changing the ending after Bulwer Lytton's advice, quotes his letter and preserves the discarded ending. Forster explicitly preferred the earlier ending; the published revision is not evidence of universally better writing.
- Charles Dickens, *Great Expectations*, Project Gutenberg [1400](https://www.gutenberg.org/ebooks/1400), Chapter LIX. Only the final encounter, beginning with Pip's intention to revisit the old house, is proposed as an answer. The whole chapter is retained locally for alignment review.

The catalogue identifies Forster as 1812–1876 and Dickens as 1812–1870; PG identifies 25851 as public domain in the USA. These are evidence leads, not exact per-edition clearance for training in GB and US. The biography's displayed first-volume title page says Boston, James R. Osgood & Company, 1875. Do not substitute the original biography publication dates for the identity of this digital copy, assume every bound volume has that date, or call it an 1874 first edition. PG1400's physical source edition has not been established here. No modern commentary, catalogue summary, illustrations or PG wrapper is a literary target.

## Local review packet

`artifacts/author-revision-candidate-2026-10-25/` contains raw-decoded source copies, the discarded-ending footnote, published final chapter, revision-history evidence, source manifest and one draft `candidate.json`. Raw downloads retain notices under `rights/raw/author-revision-candidate-2026-10-25/`; both locations are ignored by Git.

The tracked [source lock](../../curation/author-revision-candidate-v1/source-lock.json) records URLs, exact SHA-256 values, source character offsets and excerpt hashes. [Preparation script](../../curation/author-revision-candidate-v1/prepare.py) uses cached bytes by default; `--fetch` explicitly acquires only the two pinned sources and rejects changed bytes. Input/answer text is copied unchanged from those sources. Only the task framing is AI-constructed. No literary teacher answer was generated.

This is an **alternative ending**, allowing changes to the encounter, plot circumstances and implied future. It is unsuitable as a minimal-copyedit or unchanged-meaning gold answer. Source editions also differ in typography and potentially wording, which must not be silently normalised as Dickens's own revisions.

## Required before training eligibility

1. Identify scan-backed historical editions and compare the exact selected text, including the final sentence and Forster's transcription of the discarded ending. Separate author changes from editorial/transcription variants.
2. Complete exact-span GB/US rights and digital-source terms evidence in the existing ledger format. No new human approval is recorded by this packet.
3. Check all held-out-author/work restrictions before deciding whether this pair belongs in training or evaluation. This packet reserves neither role and does not alter benchmark hashes.
4. Review task framing and alignment. Keep both defensible endings as choices; do not teach that the later one is always better. Obtain further independent author-revision pairs before claiming a useful editing curriculum.

No further training has run. The current craft model remains selected; the wider mixtures remain experimental, with no completed blinded human literary ratings.
