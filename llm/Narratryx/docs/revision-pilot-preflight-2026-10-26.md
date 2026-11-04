# Revision pilot: source expansion and preflight — 26 October 2026

The next bounded experiment is prepared: **30 prospective training examples**, including **12 not used in earlier training runs**, plus the same 16 exposed Wray development-monitor records. CPU tokenizer preflight passed with a maximum of **1,882 tokens** against a proposed 2,048-token context, **5,417 supervised training tokens**, no answer truncation and all prompt tokens masked out of loss. A new 24-case/eight-scenario diagnostic and proposed maximum-eight-update local recipe are frozen. **No model training, inference, service restart or application change occurred.**

## Substantive author revision

A new James pair is transcribed from the already identified historical editions of *The Portrait of a Lady*:

- [Macmillan 1881 scan](https://archive.org/details/portraitoflady01jamerich), printed pp 138–139, image leaves 152–153.
- [Scribner 1908 scan](https://archive.org/details/portraitlady103jameuoft), printed pp 152–153, image leaves 178–179.

The complete selected paragraph begins “These words were uttered” and ends with Isabel’s request to postpone further discussion. The original describes tender eagerness and an imagination charmed but not captive. The revised paragraph adds sensory immediacy and a caged-creature image, making admiration coexist with a stronger sense of confinement. Both versions preserve the decision to defer the answer. This is a deliberate stylistic and interpretive transformation, not minimal copyediting or a label proving that later is better.

All four relevant page images were inspected. The initially acquired 1908 leaf 177 is printed 151 and is contextual evidence only; the selected paragraph actually crosses leaves 178–179. Printed page numbers establish the citation. Line wrapping, line-end hyphenation, punctuation spacing, quotation glyphs and contraction spacing are normalised; the 1908 italic emphasis on “not” is omitted in plain text. No lexical wording was modernised. The new [source lock](../curation/revision-preflight-v1/source-lock.json) binds the image files, canonical transcriptions and earlier assessed source material. Canonical raw files contain only the selected paragraph and a final newline.

The combined ledger uses **two new, narrowly scoped James records**, rather than extending the rights of the earlier opening selections silently. Exact scanned editions, author/date evidence and the private GB/US use assessment carry forward from the [independent source dossier](independent-scenes-preparation-2026-10-26.md). The review is explicitly an AI evidence/alignment assessment, not human approval or legal certification. Artwork, apparatus and all nonselected prose remain excluded; no upload or redistribution follows.

The [previously reviewed Dickens pair](../rights/dossiers/author-revision-followup-2026-10-26.md) is now included as a **structural alternative-ending** example. Its prompt explicitly permits changed events, location, remarriage uncertainty and implied future. It is not fact-preserving gold. Its source-copy and punctuation-equivalence limitations remain attached to the original scoped records. No Dickens prose was newly generated or acquired. Under this pilot’s fuller instructions, the pair measures **484 prompt + 1,397 literary-answer + 1 EOS = 1,882 tokens**, so it is retained whole rather than truncated to the old 1,024-token allowance.

## Fixed selection and supervision

| Portion | Count | Purpose |
|---|---:|---|
| Earlier directed writing |4| Two Wells and two Doyle selections |
| Earlier attributed craft explanation |4| Two Wharton and two Hamilton selections; historical explanations, not new analysis of unseen fiction |
| Earlier continuation, pacing and dialogue |6| Two examples of each kind from Opie |
| Earlier anchored Copyedit |4| Two exact repair examples and two unchanged cases; source-derived replacements/structural JSON |
| Reviewed independent curriculum |10| Hopkins, James, Harper and Wilson selections from the previous packet |
| Substantive James revision |1| New scan-verified stylistic/interpretive pair |
| Dickens alternative ending |1| Previously assessed but untrained structural pair |

The 18 retained examples preserve their exact messages; only dataset-version metadata changes. The 12 other candidates have unchanged historical prose as answers. Instructions were constructed after reading sources. No generated literary teaching answer is introduced. Mechanical Copyedit JSON remains structural supervision with source-derived words. Editing receives no minimum output length.

Opie reaches the fixed record cap of 10/30; no contributor exceeds 40% of supervised training tokens. Attribution counters include Forster as the historical transmitter/editor of the Dickens excerpt, so author-credit totals overlap and must not be summed as extra tokens or counted as another independent fiction author. There are ten primary teaching-text authors plus that historical editorial credit. Same-author/work examples remain in one split. The 16 Wray monitor records were exposed in prior exploratory work and remain **development monitoring**, not an independent quality test.

This is a small task-training experiment, not a broad fiction corpus. Source-only supervision still has limited modern voice, genre breadth, extended continuity and grounded narrative-analysis coverage. Two substantive revisions do not establish a mature revision curriculum. The pilot is intended to test a change in task framing and source diversity, not to claim Muse equivalence.

## Fresh evaluation and proposed run

The [new diagnostic](../artifacts/revision-preflight-v1/test.cases.jsonl) contains four cases each for exact minimal repair, chronology-preserving rewriting, grounded analysis, reciprocal dialogue, pacing and continuation. Eight original scenarios cover conservation, food production, a kiln, ferry parcels, a seed library, rehearsal, a mountain shelter and a community kitchen. These are AI-authored **evaluation-only** situations, never literary teaching targets. The original formal benchmark remains a draft; this diagnostic is not its human-approved replacement.

The proposed sequence is serial base/current-craft baselines first, then one fresh-base adapter run, then candidate responses to the same 24 cases. Each call must use a fresh context, no prior assistant messages and no cached prompt tokens. Freeze inputs before collecting outputs. Keep errors, truncations, failed constraints, exact repair results and semantic/literary judgements distinct. Cases within one situation are correlated; 24 cases do not mean 24 independent story worlds.

The [proposed frozen protocol](../artifacts/revision-preflight-v1/protocol.proposed.frozen.json) records the pinned base, all input hashes, protected adapters, generation settings and limits. The [request](../artifacts/revision-preflight-v1/request.proposed.json) proposes rank 8/alpha 16 LoRA, learning rate 5e-6, seed 42, batch 1 with accumulation 4, context 2,048 and **at most eight updates**. Stop on a 10 GB MLX peak, 20-minute limit, memory error or unsupported runtime; do not automatically retry at a larger resource budget. Training memory at this longer length has not been measured. No paid cloud job is required or authorised by this preparation.

No training runner was launched or model weights loaded during preflight. Tokenizer configuration was loaded locally through the installed Unsloth compatibility path. A proposed request and protocol are not evidence that training has completed or that a live runner enforces their limits. The subsequent execution must implement and verify those guards, finish both baselines before training, and retain the current model if any gate fails. Promotion requires separate quality evidence; it is never automatic.

## Artifacts and validation

- [Dataset builder](../curation/revision-preflight-v1/build.py), [evaluation-case generator](../curation/revision-preflight-v1/evaluation_cases.py) and [token preflight](../curation/revision-preflight-v1/preflight.py).
- `artifacts/revision-preflight-v1/records.jsonl`, `membership.json` and `selection.json` record exact membership and prior/new status.
- [Mixed-use scoped ledger](../rights/revision-preflight-v1.scoped.jsonl) has 15 referenced rights records, including the evaluation-only Wray source. Do not run an all-records training-use release check against that evaluation-only entry; the dataset validator selects the proper use by split.
- `tokenizer-preflight.json` records every prompt/answer length and contributor token count; `train.tokens.jsonl` and `validation.tokens.jsonl` contain explicit labels, masks and EOS.
- **138 CPU foundation tests passed in 40.246 seconds** on 26 October, including eight new quota, loss-mask, truncation, tokenizer and diagnostic guards. Source hashes, offsets, split boundaries and overlap checks against earlier evaluation packs passed. These are bounded lexical screens, not proof of semantic independence or absence from base pretraining.
- The old frozen v3 files, protected adapters, base weight hash and current craft configuration are checked separately in `preservation.json`. The original candidate packets and benchmarks are preserved.

Verify the prepared dataset from `llm/Narratryx`:

```bash
.venv-foundation/bin/python curation/revision-preflight-v1/build.py verify
.venv-foundation/bin/python -m unittest discover -s tests -v
```

Build/preflight commands use exclusive output creation and are not rerun over a frozen packet. Tokenizer preflight uses the existing Unsloth Python environment; the CPU foundation environment intentionally does not install the ML training stack.

Work is confined to Narratryx. Web/PWA, Tauri Windows/Linux, Capacitor iOS and independent native macOS received no source, generated-asset or configuration changes from this task. No app/device build was needed or run; no training, cloud spending, model publication or app-default change occurred.
