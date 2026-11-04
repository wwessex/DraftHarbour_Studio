# Additional source-backed candidates — 2 November 2026

Prepared **four additional candidates** after the [21-pair review](source-training-v22-ai-review-2026-11-02.md): one substantive James author-revision pair, one narrated dialogue and two complete-paragraph continuations by Alice Dunbar-Nelson. There is **one additional author and one additional collection relative to the latest training proposal**, plus new passages from an already represented James novel. This is source/data preparation; no model training, inference or application changes occur.

These candidates improve coverage without using generated literary teaching targets. They do **not** yet fill the gaps in concise substantive revisions or four-to-six-turn dialogue-only output. They remain a separate packet, not additions silently merged into the 28-example recipe.

## The four candidates

| Candidate | Source and demonstration | Limit |
|---|---|---|
| `v23-james-reaction-revision` | Isabel's post-proposal reflection in the inspected 1881 and 1908 *Portrait of a Lady* scans | Genuine substantive revision, but expands from 439 to 483 words; not a concision lesson |
| `v23-violin-refusal` | *M'sieu Fortier's Violin*: owner, buyer and owner again, with the violinist refusing a sale and gripping the case | Three spoken turns with narration; not dialogue-only |
| `v23-search-departure` | *Titee*: after searching at home, the party actually sets out with lanterns, sticks and the dog | One new 95-word paragraph; child remains missing |
| `v23-wade-return` | *The Fisherman of Pass Christian*: adapt the route to Annette's bare feet, wade back, return to the group and depart | Two new source paragraphs; the brief explicitly permits the completed return |

The James revision changes psychological interpretation, imagery and sentence structure rather than merely substituting a verb. It is not a human preference label or proof that the later edition is universally better. Both published texts are retained. Five original page images were inspected: 1881 printed pp141–142, scan leaves155–156; 1908 printed pp155–157, leaves181–183. OCR differences were checked against those images. The unusual printed phrase “might contain oppressive” is preserved rather than silently repaired.

Canonical James transcription normalises printed line-wrap hyphenation, spacing, quotation/apostrophe glyphs and split contractions, and omits italic emphasis. It does not modernise lexical content. This is **AI scan transcription**, not generated literary prose or human-verified transcription.

The three Dunbar-Nelson answers are unchanged substrings of the pinned PG688 text, using foundation's universal-newline coordinates. Context and continuation are contiguous, with only source paragraph whitespace between them. No paraphrase, stitched dialogue, new speech label or synthetic ending is substituted for the published answer. Briefs are AI-authored after reading the source; they are not historically commissioned writing requests.

## Exact rights scope and evidence

The new ledger is `rights/source-expansion-v23.scoped.jsonl`: **15 earlier records copied unchanged plus three new records**, two James edition-specific records and one Dunbar-Nelson digital-artifact record. Only the explicitly selected spans receive the new GB/US training assessment. Existing ledgers, source approvals and frozen experiments are unchanged. No whole book or anthology is cleared by this work.

For James, the assessment retains the earlier exact scan identities, author dates, title evidence and expired-original-prose reasoning, while explicitly recording the new paragraph boundaries. Both versions were historically published, so this is not an undated-manuscript clearance. Only original authored text enters candidates; photographs, running heads, page layout and other contributions are excluded. The refreshed Internet Archive terms page exposed only a JavaScript placeholder. The record discloses that a complete current site-terms review was unavailable and does not claim scan/digital-object redistribution rights.

For Dunbar-Nelson, the exact artifact is the retrieved PG688 plain text, with full bytes/notices and SHA256 retained. The [item catalogue](https://www.gutenberg.org/ebooks/688) identifies the author as 1875–1935 and the item as US public domain. [NYPL's bibliographic transcription](https://s3.amazonaws.com/nypl-aaww/SCAAWW_book_11_The_goodness_of_St_Rocque_and_other_stories.pdf) corroborates the original collection's Dodd, Mead, New York, 1899 publication. NYPL's text is evidence only, not a teaching target. The physical print copy behind PG is unidentified; the record does not claim facsimile equivalence to the 1899 edition.

The GB expiry assessment uses the identified original author's death and the ordinary life-plus-70 term; the US assessment combines the item-specific public-domain statement with the historical publication date. These are scoped AI evidence assessments, **not human legal approval or legal certification**. The basis and its limits are recorded alongside [UK duration guidance](https://www.gov.uk/copyright/how-long-copyright-lasts) and the [US Copyright Office duration circular](https://www.copyright.gov/circs/circ15a.pdf).

[PG's permissions guidance](https://www.gutenberg.org/policy/permission.html) distinguishes reuse of public-domain original content from use of its trademark and warns that digital editions need not match one print source exactly. The retained header contains no special copyright-holder permission notice for these selected passages. Provider notices, branding, catalogue summaries, songs, prayers, poems, third-party quotations and unselected material are excluded from model data. The assessment is limited to private local GB/US preparation/training of original prose; it authorises no branded ebook redistribution, corpus upload or model publication.

The direct Copyright Office PDF download returned HTTP403; the official PDF was inspected with the web tool. The acquisition manifest records that failure instead of inventing a local PDF. Successful source files and five page images are retained and hashed. Redirect URLs for the initial acquisition batch were not retained; the manifest distinguishes known request URLs from unrecorded redirects.

## Sources deliberately excluded

Three attractive *Mine Eyes Have Seen* source options remain **discovery-only and training-ineligible**:

- The [Delaware undated typescript](https://udspace.udel.edu/items/70811104-6a69-4610-ba55-dd61cf91a340/full) has autograph corrections and a US-only no-copyright label, but its publication history and GB status are not resolved. It is not used as a revision pair.
- The [Modernist Journals Project's 1918 issue](https://modjourn.org/issue/bdr511177/) labels underlying contents US public domain but separately specifies permission for certain digital-object reproductions. Applicability to the intended extraction was not resolved; no material from that digital edition enters training.
- The independently retrieved 1920 *Dunbar Speaker* Google-scan OCR contains non-commercial-file and automated-query usage guidance. That wording is retained, not treated as a determination of enforceability or silently bypassed. The play, anthology introduction and other authors are excluded.

The selected PG collection is a different work and artifact; it is not a mirror used to evade those source conditions. This leaves the compact dialogue-only gap visible rather than manufacturing a clean-looking example from uncertain material.

## Validation and next work

Source/schema checks pass for all four candidates. The ledger's old records match their originals exactly. A separate **split-check-only** artifact combines these candidates with the 16 unchanged exposed Wray monitors and confirms author separation. The original draft benchmark and configured evaluation sources are checked; Dunbar-Nelson is not introduced into an existing held-out author group. The new answers do not duplicate the latest proposal's assistant targets. This is not a claim that a base model has never encountered these books during pretraining.

Cached-tokenizer preflight passes with **924 supervised tokens** and a maximum of **1,205 tokens**, below the 2,048 context limit. Answers round-trip exactly, proposed labels mask prompts, and no target is truncated. No weights are loaded. This is label-construction/tokenization preflight, not installed-collator or optimizer validation for the new candidates.

The full CPU foundation suite passes **245 tests in 70.742 seconds**, including three new exact-boundary, ambiguous-marker rejection and complete-paragraph derivation tests. Final evidence verification and Python compilation pass. These checks establish structural/provenance consistency, not legal certification, human literary approval or model improvement.

`artifacts/source-expansion-v23/REVIEW.md` contains the four briefs and published answers. Scope coordinates, exact derivations, OCR collation, source exclusions and verification records accompany it. `curation/source-expansion-v23/source-lock.json` binds retained source/evidence hashes; scans, raw texts and candidate answers remain ignored local files. `foundation/scoped_excerpt.py` rejects ambiguous boundaries and sentence-fragment substitutions for complete-paragraph continuation. Tracked locks contain hashes rather than the literary corpus.

```bash
cd llm/Narratryx
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/source-expansion-v23/verify.py'); print(m['verify']())"
```

Next, review task fit and sampling value before combining these with the existing mixture. The longer revision changes sequence-length distribution and needs a fresh installed-collator/resource audit for any proposed run. Further source work should target authentic concise revisions and compact dialogue-only exchanges; these four examples do not justify another immediate fine-tune or a quality promotion.

Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS have no source, prompt, default, configuration or generated-asset changes. No app builds or device tests are run. There are no training jobs, inference requests, paid/cloud jobs, corpus uploads, model publication or promotion. Current models, earlier source decisions and human ballots remain unchanged.
