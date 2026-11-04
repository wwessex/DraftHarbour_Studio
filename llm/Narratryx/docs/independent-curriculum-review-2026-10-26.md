# Independent source review and expansion — 26 October 2026

The [seven-example draft](independent-scenes-preparation-2026-10-26.md) has received an **informed AI editorial review**. Six examples were retained for a future experiment; the James dogs pair is reference-only because its single lexical substitution offers little additional teaching value. Four original-prose examples from two further authors were prepared and checked against historical page images. The combined candidate selection contains **ten examples from four works/authors**, with no generated literary teaching answers.

No human approval, independent blinded quality review, new training, inference, app modification or model promotion was performed. This is a source-curation result, not evidence that the model now writes better.

## Decisions on the existing packet

The [recorded decisions](../curation/independent-scenes-review-v1/decisions.json) cover every draft example exactly once. Hopkins’s room, embroidery exchange, work exchange, invitation and host-motivation selections fit their task instructions and the previously inspected pp 98–102 scans. The retained James face pair matches the two editions and explicitly permits a nuance change from “expression” to “representation”; it is stylistic rewriting, not minimal copyedit gold. The later edition is not labelled universally preferable.

The original pending records, review packet, source files and ledger remain unchanged. A separate `artifacts/independent-scenes-reviewed-v1/records.jsonl` records six source/instruction approvals explicitly attributed to Codex AI. It does not manufacture human consent or literary-quality ratings. The original `prepare.py verify` still correctly rejects that historical pending packet for dataset release.

## Newly sourced editions

| Work | Exact selected edition | Included spans |
|---|---|---|
| Frances E. W. Harper, *Iola Leroy; or, Shadows Uplifted* | [Emory scan, IA 09509719.4821.emory.edu](https://archive.org/details/09509719.4821.emory.edu), **second edition**, Garrigues Brothers, Philadelphia, **1893**. Title page leaf 5 inspected. | Two exchanges on printed pp 8–10, scan leaves 16–18: coded market news and Robert/Linda’s contrasting ways of reading war news. |
| Harriet E. Wilson, *Our Nig; or, Sketches from the Life of a Free Black* | [UC Libraries scan, IA ournigorsketches00wilsrich](https://archive.org/details/ournigorsketches00wilsrich), Boston, printed by Geo. C. Rand & Avery, **1859**. Title page leaf 7 inspected. | Jim/Mag’s practical-help exchange on pp 9–10, leaves 15–16; Frado’s resistance and its immediate consequences on p 105, leaf 111. |

The first Harper discovery was an **undated third edition** from James H. Earle. Its 1892 catalogue date did not establish the imprint year. That OCR and metadata remain local discovery evidence only; no excerpt from that artifact enters the selection. The selected second edition visibly prints 1893, agreeing with Emory’s catalogue. No date was inferred from the copyright notice alone.

[Library of Congress authority data](https://lccn.loc.gov/n50026651) records Harper as 1825–1911. Its [Wilson catalogue record](https://www.loc.gov/item/2005577156/) records 1825–1900 and the 1859 publication. These dates and original publication evidence support the bounded GB ordinary-term assessment using [UK guidance](https://www.gov.uk/copyright/how-long-copyright-lasts). The inspected US publications are beyond the historical maximum term described in [Copyright Office Circular15A](https://www.copyright.gov/circs/circ15a.pdf). Wilson’s IA item says `NOT_IN_COPYRIGHT`; Emory’s description identifies its digital edition as public domain. Provider metadata is corroboration, not a substitute for edition checks.

The combined [five-record scoped ledger](../rights/independent-curriculum-v1.scoped.jsonl) covers exact selected prose only, private GB/US training/evaluation uses. Three records are unchanged copies for Hopkins and the two James editions; two records add Harper and Wilson. This is an AI evidence assessment, not legal certification. Introductions, other authors’ letters, appendices, epigraphs, poetry, artwork, captions, layout, modern additions and site apparatus are excluded. Full IA site terms were not retrieved; no upload, publication or redistribution is authorised. The LOC Wilson resource endpoint returned 403; the accessible catalogue/search evidence is cited without claiming a successful full-page download.

## Source fidelity and sampling limits

All selected new prose was transcribed against original page images. OCR was used to locate candidates. In particular, Wilson’s p 105 scan reads **“sent after”**, where the OCR says “pent after”. The canonical file follows the scan. Printed line breaks and line-end hyphenation, contraction spacing and quotation glyphs were normalised; lexical wording, historical dialect and punctuation choices were retained. Page headers, numbers and emphasis styling are outside the plain-text representation.

The new instructions were constructed after reading each passage; answers are exact canonical source spans. Harper’s coded exchanges and Jim/Mag’s exchange include reciprocal speech rather than isolated monologues. Frado’s passage is a pacing/causal-action example, not a reciprocal dialogue or a general claim about how to stop abuse. Historical language belongs to the particular narrator and characters; these examples are not modern factual analysis or universal social advice. No synthetic analysis answers or editing minimum lengths were added.

Composition is five Hopkins, one James, two Harper and two Wilson examples. Half the selection still comes from one Hopkins chapter; the Harper scenes share one chapter. Four works do not establish genre breadth, a modern narrative voice, long-form coherence or a substantial author-revision curriculum. Only one stylistic editing pair remains. The retained examples have source/instruction approval, **not human literary-quality approval**.

## Artifacts and checks

- [Expanded review packet](../artifacts/independent-curriculum-v1/REVIEW.md): new tasks, source answers and exact scan links. Existing decisions remain separately linked above.
- `artifacts/independent-curriculum-v1/records.jsonl`: ten AI-reviewed candidate records, prospective train split only, not trained.
- [Expansion script](../curation/independent-expansion-v1/prepare.py), its [source lock](../curation/independent-expansion-v1/source-lock.json) and [packet lock](../curation/independent-expansion-v1/packet-lock.json): hashes bind transcriptions, original OCR, metadata, images, selected records and the reused helper. Raw texts, images and answer packets remain ignored by Git.
- `verification.json`: dataset schema/provenance/source hash/offset checks passed; all answers match exact source spans. Author/work split and lexical overlap checks against the v2/v3 datasets and three evaluation packs passed. The original formal pack remains a **draft**, not a newly approved benchmark. These checks are bounded lexical screens, not a semantic contamination guarantee.
- `preservation.json`: all 20 frozen v3 inputs, all 12 protected artifacts and the active craft model configuration hash are unchanged.

From `llm/Narratryx`:

```bash
.venv-foundation/bin/python curation/independent-scenes-review-v1/review.py verify
.venv-foundation/bin/python curation/independent-expansion-v1/prepare.py verify
.venv-foundation/bin/python -m foundation validate-ledger rights/independent-curriculum-v1.scoped.jsonl \
  --release --jurisdictions GB US --use training
.venv-foundation/bin/python -m unittest discover -s tests -v
```

Fresh CPU validation: **130 tests passed in 39.697 seconds** on 26 October, including four new review-decision guards. The first invocation from the repository root failed eight imports because the foundation package was outside the working-directory import path; the documented command was rerun successfully from Narratryx. Packet checks, five-record GB/US ledger release-evidence validation and whitespace/ignored-literature checks passed. These checks do not establish literary quality or legal certification.

The two build commands refuse to overwrite their existing outputs. Hash locks identify evidence and decisions; they do not establish correctness by themselves. The formal dataset CLI release workflow still requires an independently reviewed benchmark/rubric lock. The lower-level dataset provenance check is not presented as that complete workflow.

All work is isolated in Narratryx. Web/PWA, Tauri Windows/Linux, Capacitor iOS and independent native macOS received no source, asset or configuration changes from this task. No app/device builds were run. No service restart or model loading was necessary.

## Next training gate

Expand substantive author revisions and independently sourced scenes before another experiment, with a cap on repeated scenes from the same work. Add held-out tests targeting the specific chronology and grounded-analysis failures already observed, plus dialogue, pacing and restrained editing. Freeze source membership, token budgets, loss masks and evaluation settings before the run; no token truncation or same-author random split. Human quality judgements remain separate from AI reviews and mechanical scores. The current craft model stays selected until a candidate demonstrates improvement.
