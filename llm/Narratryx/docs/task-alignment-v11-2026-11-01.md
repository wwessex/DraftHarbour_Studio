# Source-only lesson alignment audit — 1 November 2026

Following the [failed lower-rate stability gate](stability-v10-2026-11-01.md), this preparation audits all **92 unique training lessons** used by v9/v10 and prepares a smaller **25-example proposal**. It does not train or select another adapter. Misalignment is a plausible curriculum weakness, not a demonstrated cause of the observed repetition.

## Findings

| Existing lesson form | Unique lessons | Finding and disposition |
|---|---:|---|
| Fixed opening/closing paragraph reconstruction | 24 | Valid reconstruction exercises, poorly matched to scene writing from facts. Repair two briefs around their source's practical agreements; quarantine 22 from this proposal. |
| Sentence-fragment continuation | 6 | Adds the next words without repeating the input. Useful for sentence completion; not a demonstration of adding a paragraph after a finished paragraph. Reference only. |
| Paragraph continuation | 2 | Returns new source prose, but sparse input omits substantial surrounding story state. Reference only for this constrained transfer trial. |
| Quoted historical craft explanation | 8 | Relevant advice about viewpoint, narration and dialogue. Does not supply a worked application to a new scene. Reference only. |
| Author revision | 2 | Genuine stylistic changes, explicitly distinguished from minimal copyediting. Retain. |
| Directed scene/narration, including the alternative ending | 14 | Retain 13 short examples; defer the 1,035-word Dickens structural ending with unintroduced opening referents. |
| Structured editing/evidence/clock/claim answers | 36 | Keep eight anchored-edit controls. Defer 28 evidence/clock/claim examples to a separate diagnostic arm. Their labels are not found incorrect by this audit. |

The machine-readable [audit](../artifacts/task-alignment-v11/audit.jsonl) records each ID, original content hash, answer digest, decision, rationale and observable checks. These include word maxima, whole-fragment copying, exact repeated sentences and source-span equality. None of the original answers trips those first three simple checks; this does **not** establish semantic quality, diverse dialogue or task transfer. A paragraph can comply with its own reconstruction prompt while poorly matching the application's Write operation. Generated v9/v10 dialogue repetition is not evidence that their training answers contained the same loops.

The original 92 lessons had 56 prose targets and 36 structured targets. Oversampling increased presentations to 128; it did not add authors or scenes. This audit uses unique records and does not call repetitions independent literary material.

## Retained source-prose evidence

The following are informed AI editorial assessments against the actual prompts and answers, not independent human approval:

| ID or group | Answer evidence and limits |
|---|---|
| `gb-hopkins-host` | Two narrated sentences connect the landlady's assessment, desire and reception arrangements. Historical class judgements are framed as the narrator's perspective. |
| `gb-hopkins-room` | Drapery, packing cases, a spring and the typewriter give concrete evidence of a transformed lodging. Retains description, not a negotiation lesson. |
| `gb-james-face-1908` | Word order and the interpretation of the face change; most prose remains close to the earlier edition. Small stylistic revision, not general correction. |
| `gb-james-proposal-revision` | Sensory imagery and confinement sharpen Isabel's response while she defers her answer. Substantive author revision; not an anchored Copyedit target. |
| `gb-wilson-resistance` | Threat, refusal and the mistress carrying the wood supply a clear reversal and change of pace. A particular historical scene, not general advice about abuse. |
| `gb-v3-022-paced-scene` | Landscape, anticipation and fearful recollection delay the action before Agnes hurries onward. |
| `gb-v3-023-paced-scene` | The called hour triggers a remembered coach and an immediate practical journey. The vacancy is given in this source scene, not permission to invent convenient resources elsewhere. |
| `gb-harper-market` | Reciprocal coded market talk contrasts cheerful servants with the post-office faces. Historical dialect and mixed narration are explicit. |
| `gb-hopkins-embroidery` | Sappho offers instruction while leaving the location where she learned unanswered; Dora notices the omission. A useful example of a question remaining unresolved. |
| `gb-wilson-help` | Mag's fear elicits Jim's work-backed promise and a wounded response. Support is explicitly offered in this scene, not inferred consent. |
| `gb-v3-016-dialogue-scene` | Agnes's interruptions meet Fanny's longer reassurance and offer of help. Strong emotion, but not a strict dialogue-only, four-to-six-turn negotiation. |
| `gb-harper-newspaper` | Robert's news contrasts with Linda's reading of the mistress; the rumour is challenged in speech. Character claims are not independent narrator verification. |
| `gb-hopkins-work` | Sappho distinguishes satisfying work from frustrating dictation and ends with the concrete action of offering a chair. |
| `gb-v3-017-dialogue-scene` | Two spoken turns establish the child's identity, followed by a restrained physical expression of affection. |
| `gb-hopkins-invitation` | Specific future times, mock formality, explicit acceptance and departure to prepare. An invitation is not proof an event has already occurred. |
| `gb-v2-directed-opie-0256` | Repair the brief to ask for Agnes and Fanny's livelihood discussion and agreed work/room arrangement. The unchanged answer supplies the agreement. |
| `gb-v2-directed-opie-0262` | Repair the brief to ask for Fanny's marriage condition, the suitor's explicit consent and the later wedding. Resolution is allowed by this brief. It must not be presented as preserving absent permission. |

All 17 literary answers remain byte-identical to their parent targets. No source spans, rights IDs, author/work splits, origin or teacher metadata change. The two repaired instructions are AI-authored task descriptions of existing source answers; they are not newly generated literary teaching answers. The eight editing targets retain four accidental-duplicate repairs, three clean-target/outside-error controls and one grammatical `had had` control. Exact anchor application checks the target boundary, and the repaired target is compared with its source suffix allowing existing scan-line whitespace normalisation. Editing has no minimum word count.

## Prepared artifacts and evaluation

The [proposal review packet](../artifacts/task-alignment-v11/REVIEW.md) contains the 25 training examples: 17 prose and eight structural edits, each once. Sixteen **previously exposed Wray monitor records** remain validation-only. They are not an independent new test or a human-approved quality benchmark. Existing per-span GB/US rights and author/work leakage validation passes against `rights/grounding-balanced-v1.scoped.jsonl`; no new book, edition, source use, rights grant or human/legal certification is added.

The offline cached-tokenizer preflight covers all 41 proposed records: **maximum 499 tokens**, within 2,048; **2,890 supervised training tokens** including EOS. Answers round-trip exactly, proposed labels mask prompts and nothing truncates. This loads tokenizer files, not model weights. It is label-construction evidence, not a fresh installed-collator/trainer verification. No executable token dataset, training request or runner has been created for this proposal.

Twelve new prompts are frozen in `cases.frozen.jsonl`: three situations each with dialogue, continuation, rewrite and selection-only copyediting. They check resource uncertainty, missing permission and future arrival while allowing concrete action. They have not been sent to a model or put in training. They contain no literary answer targets; the simple exact selected-edit answer is evaluation-only. They differ from the frozen v9/v10 prompts and from proposed training prompts. Shared construction across three settings makes them correlated development tests, not an independent broad benchmark. Human review and another independent reviewer remain necessary before claiming literary gains.

## Remaining gaps and next experiment

The proposal is deliberately smaller, not a complete curriculum for a Muse-equivalent model. Historical mixed prose/dialogue does not directly teach modern dialogue-only negotiation. There is still no strong source-backed training example of a whole new paragraph that preserves explicit unknowns, scarce resources and missing permission. Analysis examples here are historical craft quotations or structured classification, not modern narrative critiques. Merely running more epochs would not fill those gaps.

Before another run, find appropriate **whole exchanges and adjacent paragraphs inside the already scoped source spans**. Use them only where the exact source supports the task; expanded spans require further rights/split validation. Keep unknown facts unknown in the brief and do not impose a constraint the published answer violates. Source prose can demonstrate an agreement only when the task permits agreement. Do not manufacture a literary answer to make an attractive prompt trainable.

A subsequent bounded experiment can compare this task-matched proposal with the current craft model and fresh base using the new cases plus the exposed v10 regression suite. Freeze the recipe, token/collation checks, fresh-context inference and independent review procedure before execution. Avoid oversampling clock labels in that writing trial; measure grounding separately. Because data, sampling and update budget would change together, that experiment would assess a candidate, not isolate a single causal variable. No new job is launched by this report.

## Validation and scope

The full CPU foundation suite passed **192 tests in 47.134 seconds**, including five new checks for task-form separation, observable limits and immutable answers/source/splits. The proposal verifier passes exact parent/protected hashes, unchanged source/answer metadata for all 41 records, the two intended brief repairs, eight anchored-edit controls, rights/leakage checks, case separation and token-preflight inputs. The pinned base weight hash is unchanged. Python compilation and whitespace checks pass. A tracked `curation/task-alignment-v11/preparation.lock.json` records code/artifact hashes and these dated results; it contains no teaching quotations or model weights.

Preparation and verification scripts are in `curation/task-alignment-v11/`; observable checks and target/provenance guards are in `foundation/task_alignment.py`. Output files remain under ignored `artifacts/task-alignment-v11/`; previous datasets, protocols, adapters, release assets and the app-selected model are preserved. The preparation script refuses overwrite. Read-only verification:

```bash
cd llm/Narratryx
.venv-foundation/bin/python curation/task-alignment-v11/verify.py
```

No source/default/configuration/generated-asset changes, app builds or device tests were made for web/PWA, Windows/Linux Tauri, Capacitor iOS or independent native macOS. This isolated CPU/tokenizer preparation does not establish Windows inference support or deploy a model. No paid job, remote inference, corpus upload, publication or human approval occurred.
