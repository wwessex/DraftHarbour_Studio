# Dickens structural revision: scoped evidence assessment — 26 October 2026

**AI evidence assessment complete for two exact digital original-prose spans, for private GB/US training and evaluation. No human approval or legal certification is recorded. The pair is not in the v3 training set.** This follows the [initial candidate dossier](author-revision-candidate-2026-10-25.md); that original packet is preserved as dated candidate evidence.

## What was established

Forster's *Life of Charles Dickens*, Vol III, **London: Chapman and Hall, 1874**, is available in the [Internet Archive scan](https://archive.org/details/lifecharlesdick01unkngoog). Its title leaf 13, printed page 335/leaf361 and page336/leaf362 were acquired and visually inspected. Page335 quotes Dickens's account of changing the ending after Bulwer Lytton's advice; page336 preserves the discarded ending and Forster's preference for it. These are historical printed sources, not modern teaching answers.

The selected discarded-ending words in pinned PG25851 are corroborated by that footnote. This does **not** identify the physical print copy used by PG: its displayed first-volume title page says Boston/Osgood/1875, and pagination differs. The 1874 Chapman and Hall volume is a named comparison edition.

The entire selected word sequence from pinned PG1400's final encounter matches [the scan-backed, validated 1890 Collier Chapter LIX transcription](https://en.wikisource.org/wiki/Great_Expectations_(1890)/Chapter_LIX). The comparison [index](https://en.wikisource.org/wiki/Index:Great_Expectations.djvu) identifies the edition, with all work pages validated. Word comparison normalises case, whitespace and punctuation for corroboration; it does not claim identical punctuation or layout. Direct page-image requests returned HTTP403 and were not bypassed. PG1400's exact physical source copy remains unidentified. No sentence-level typographical difference is labelled an author revision merely because editions differ.

## Bounded rights decision

PG identifies [1400](https://www.gutenberg.org/ebooks/1400) and [25851](https://www.gutenberg.org/ebooks/25851) as public domain in the USA. Dickens died1870 and Forster1876; the selected material was published in the nineteenth century. Ordinary literary life-plus-70 terms have elapsed under [UK duration guidance](https://www.gov.uk/copyright/how-long-copyright-lasts); these excerpts are not previously unpublished modern releases. [US Copyright Office Circular15A](https://www.copyright.gov/circs/circ15a.pdf) describes historical term limits. The assessment covers only the identified original author prose, not unknown modern contributions or page layouts.

[PG permission guidance](https://www.gutenberg.org/policy/permission.html) distinguishes public-domain use from its trademark/ebook terms and explains that digital transcriptions may differ from physical copies. Complete sources and notices are retained. Provider wrappers/branding, catalogue summaries, illustrations, footnote wrappers, Forster's surrounding commentary and modern introductions/annotations are excluded from literary targets. No branded redistribution, publication, paid job or external upload follows from this assessment.

The new [scoped ledger](../author-revision-followup-v1.scoped.jsonl) records two source IDs and the exact selected-span file/hash. The [assessment script](../../curation/author-revision-followup-v1/assess.py) checks pinned bytes, collation, source coordinates and schema/use decisions. Scope files and raw evidence are private local artifacts. Foundation coordinates use UTF-8 text with universal newline conversion; original CRLF coordinates remain in the earlier candidate lock. Literary wording and punctuation are not rewritten by this coordinate conversion.

## Alignment and training role

This is an alternative-ending transformation: encounter location, elapsed events, circumstances and implied future differ. It is not a minimal copyedit, an unchanged-meaning rewrite or a preference pair proving that the later ending is better. Forster's published preference itself cautions against that assumption. No generated literary target is added.

A check found no Dickens/Forster/Great Expectations restriction in the current formal evaluation/configuration files. That is a checked project boundary, not a claim about base pretraining contamination. The v3 test stories are original evaluation-only fiction.

Under the pinned tokenizer, the framed pair is **428 prompt + 1,397 answer + 1 EOS = 1,826 tokens**. It exceeds the v3 pilot's 1,024-token allowance. The pair remains outside that experiment, with no target truncation, new long-context training or model promotion. Additional independent revision pairs and a separate longer-context preflight are still needed before an author-revision curriculum is justified.
