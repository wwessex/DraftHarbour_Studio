# Complete-paragraph and dialogue preparation — 1 November 2026

Following the [task-alignment audit](task-alignment-v11-2026-11-01.md), five source-derived lessons are prepared inside **existing exact rights-scoped spans**. Four replace their full-scene parents in a revised 25-example proposal. This is data preparation, not another training run or evidence of literary improvement. All applications and the selected craft model remain unchanged.

## Prepared lessons

| Candidate | Exact source operation | What it teaches; limits |
|---|---|---|
| `pd12-embroidery` | Hopkins: four complete preceding paragraphs, then the next complete paragraph | Sappho offers to teach embroidery while the place where she learned stays unknown; Dora notices the omission. No invented explanation. The answer is only 21 words, appropriately short for the source. |
| `pd12-support` | Wilson: three preceding paragraphs, then Mag's complete response paragraph | Emotional movement after Jim's promise. His offer is not presented as money/work already delivered. Historical speech remains unchanged; no claim of modern dialogue style. |
| `pd12-work` | Hopkins: Dora's complete question paragraph, then Sappho's complete answer paragraph | Distinguishes preference from dictation frustrations and ends with the concrete action of offering a chair. Mixed speech/narration is explicitly permitted. |
| `pd12-news` | Harper: introductory paragraph, then Robert's complete reported-news paragraph | New paragraph after finished prose; coded speech is attributed to a character. Reserved as an alternative, outside the revised mixture. |
| `pd12-rumour-dialogue` | Harper: preceding context and question, then three consecutive quoted paragraphs | Exactly three bare spoken turns: rejection, a report of hearing the rumour, and a challenge. No narration, invented speaker labels or manufactured evidence. This is dialogue-only output but **not** a four-to-six-turn resource negotiation. |

The [review packet](../artifacts/paragraph-dialogue-v12/REVIEW.md) shows every instruction, context and answer. Instructions are new AI-authored descriptions; **all literary answers are exact contiguous substrings of the existing scoped source text**. No prose is generated, modernised, reassembled from separated utterances or rewritten to satisfy an unsuitable prompt. Historical dialect is retained as these characters' speech.

Each derivation records parent lesson, exact full scoped span, relative context/answer offsets and absolute Unicode source offsets. Context ends at a complete paragraph; only whitespace separates it from the answer. The answer is either one complete paragraph or the three contiguous quoted paragraphs explicitly requested. Checks reject altered answers, overlapping intervals, missing context and skipped intervening prose. These checks demonstrate faithful derivation, not literary merit.

## Mixture and provenance

The revised proposal remains **25 training examples: 17 prose and eight structural copyediting controls**, with 16 previously exposed Wray monitor records kept validation-only. Four full-scene records are replaced, rather than retained alongside their derived variants:

- Hopkins embroidery → its final paragraph with the preceding scene supplied as context.
- Wilson help → Mag's final response with Jim's promise supplied as context.
- Hopkins work → Sappho's next paragraph after Dora's question.
- Harper newspaper → the final three bare dialogue turns after the question.

The alternate Robert news candidate is excluded from this mixture. No new repetitions or source diversity are claimed. The other 21 training records and all monitor records retain their content and metadata apart from the new dataset-version tag. Original v11 files and earlier adapters remain frozen.

The candidate source spans are byte-for-byte the parent records' spans, remain within their recorded bounds and preserve the same work, rights, author split, origin and teacher metadata. Existing GB/US training/evaluation record checks and author/work leakage checks pass against `rights/grounding-balanced-v1.scoped.jsonl`. This is a check against recorded scope, not new legal certification or human approval. No whole book, newly cleared edition, expanded span, corpus download or remote upload is involved. The previous scan evidence is reused; no new independent transcription review is claimed.

The cached-tokenizer preflight passes all 41 proposed records, with a maximum **499 tokens** against the 2,048-token limit and **2,298 supervised training tokens** including EOS. Prompt labels are masked, answers round-trip exactly and targets do not truncate. Tokenizer files are loaded offline; model weights are not loaded. This is label construction only; executable token files and installed trainer/collator verification remain to be frozen before a run. The reserved news alternative is not included in those 41-record token totals.

## Evaluation and remaining coverage

The twelve new, unrun v11 development prompts remain unchanged and outside training, alongside the existing exposed v10 regression suite. No model has been evaluated on the twelve new prompts. Creating these lessons does not turn their published continuations into a fiction-quality answer key: other continuations can be valid, and source-exact matching would measure memorisation rather than literary ability.

This closes part of the formatting/context gap: the model can now be shown a **finished preceding paragraph** with only the next paragraph as its target, and a genuine dialogue-only exchange. It does not complete the broader curriculum. Resource scarcity, untested spares and missing permission are still not jointly demonstrated in a modern practical negotiation; neither historical register nor three brief turns satisfies that stronger requirement. The short embroidery answer should not be padded to meet an arbitrary minimum. Editing likewise retains no minimum length.

The next bounded pilot should freeze the 25-example mixture, one presentation per example, prompt masking and the installed collation path before training. Compare a fresh-base adapter with fresh base/current craft responses on the twelve new cases and the exposed stability regression cases. Fix the update/memory/time limits and decoding settings before execution; retain truncation stops and explicit human review. Choosing a new recipe and mixture together would be a candidate comparison, not a single-variable causal experiment. **No training request, job or model promotion is launched here.**

## Validation and application scope

The full CPU foundation suite passed **196 tests in 39.777 seconds**, including four new exact-paragraph derivation tests. The final verifier passed source/protocol/artifact hashes, five exact context/answer derivations, four exclusive parent replacements, unchanged reserved/test material, rights/split checks and tokenizer-preflight integrity. Base/prior/selected model hashes remain unchanged. Python compilation and whitespace/link checks pass. A tracked `curation/paragraph-dialogue-v12/preparation.lock.json` preserves code/artifact hashes and dated test results without including literary quotations or weights. Human literary-quality ratings remain zero.

Preparation, offline tokenizer preflight and read-only verification are in `curation/paragraph-dialogue-v12/`; exact paragraph derivation is in `foundation/paragraph_lessons.py`. Local data, review text and derivations remain in ignored `artifacts/paragraph-dialogue-v12/`. Read-only verification:

```bash
cd llm/Narratryx
.venv-foundation/bin/python curation/paragraph-dialogue-v12/verify.py
```

Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/default/configuration or generated-asset changes. No app/device build or runtime test is needed or performed for this isolated preparation. No paid job, remote inference, publication or new release asset is created. Training completion and literary improvement are not claimed.
