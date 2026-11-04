# Local literary model improvement plan

25 October 2026. Planning only: no training run, paid job, corpus upload, model publication or default model change is authorised by this document.

## Starting evidence and goal

The [latest craft pilot](craft-source-pilot-2026-10-20.md) trained twenty source-only Wharton/Hamilton answers (2,850 supervised tokens) for five updates. Its matched sixteen-task comparison had no request errors or truncation, but minimal-edit exactness was unchanged (2/4), continuation length adherence fell (2/4 to 1/4), dialogue limits were unchanged (2/4), and compression limits improved (3/4 to 4/4). No blinded human literary-quality ratings are complete. Training loss and successful export do not establish better fiction.

The next candidate must improve the actual app tasks: restrained rewriting, continuation, directed writing, dialogue, pacing and narrative analysis. Preserve voice, viewpoint, chronology and known facts; avoid commentary where only prose was requested. Support a replaceable model through the existing provider boundary and a separate inference runtime. End users install/use inference; they never train a model as part of app setup.

## 1. Establish project-context behaviour before training

Story Bible retrieval supplies changing project facts at inference time. Fine-tuning should teach task behaviour; it should not memorise a user's Bible. Supply a bounded relevant subset of live canon plus existing author character/world references. Label these as read-only data, keep editable passages separate, report omitted references, and never silently promote draft, disputed, research or AI-suggestion entries. A reference not retrieved is not proof a fact does not exist. Temporal notes need explicit interpretation rather than automatically becoming current truth.

Add an independent context evaluation set with author names/aliases, canonical attributes, conflicting references, unknown facts, old versus current facts and oversized Bibles. Check highlighted-span replacement, facts retained, unsupported assertions, unwanted copying and instruction-like text inside reference data. Do not equate prompt-level instructions with a security guarantee or claim the model cannot hallucinate.

For the new study compare four conditions on the same frozen fresh-context tasks: base without references, base with references, candidate without references, candidate with references. Use matching decoding settings, template and generation allowance. This separates retrieval gains from training gains. Keep the historical pilot protocol and outputs unchanged.

## 2. Build task-matched, rights-traceable examples

Start with an audited inventory rather than more training updates. Record each example's skill, source edition/locator/hash, rights-ledger identifier, GB/US/use/span scope, transformations, target provenance and reviewer decision. Reuse existing validators and benchmark locks. Public-domain dataset metadata, including PleIAs/English-PD, is candidate discovery, not per-edition clearance. Exclude unclear rows until the exact source passes the existing rights process; this plan records no new clearance or human approval.

The current user scope excludes generated literary teaching targets. Continue using source-derived answers with task instructions distinguished from answer provenance. Do not manufacture creative answers, critiques, summaries, preference pairs or alleged author revisions to fill gaps. User manuscripts, feedback and Story Bibles are not a training corpus without separate explicit consent and appropriate rights handling.

Prioritise:

| Skill | Admissible next material | Important limit |
|---|---|---|
| Restrained editing | Genuine author-revised fictional passages from cleared editions, with aligned before/after spans | Establish authorship of changes; typography/transcriber corrections are not evidence of an author's revision |
| Continuation and directed prose | Cleared fiction excerpts used as source-derived completions with sufficient preceding context | Published continuation likelihood is a training signal, not an exact-match fiction-quality benchmark |
| Dialogue and pacing | Clearly scoped dialogue/scenes from cleared works, tagged with mechanically verifiable structure | Historical examples do not automatically teach modern pacing, subtext or screenplay format |
| Craft and analysis | Existing cleared craft explanations and genuinely sourced commentary | Do not relabel extracted passages as original analytical answers |
| Bible consistency | Only task examples whose reference facts and answers have an admissible, documented derivation | If no suitable targets exist, evaluate retrieval first and leave this training category empty |

Deliver a reviewed manifest and gap report before setting corpus size. Aim first for a reviewable 50-example candidate packet, then a broader 200-example packet **only if enough admissible examples exist**. These are curation milestones, not a quality guarantee or permission to backfill with generated targets. Keep author/work splits disjoint; deduplicate overlapping passages and editions before splitting. Mansfield/Chesnutt evaluation-only materials remain excluded from training. Base pretraining contamination is unknown and must be disclosed.

## 3. Freeze evaluation and promotion criteria

Resolve the existing blind packet with two independent reviewers on a representative subset, recording evidence and adjudicating disagreements. Do not invent scores or treat Codex's inspection as a human ballot. Create a versioned new task pack for the expanded study, lock prompts/rubrics/source hashes before recording its baseline, and keep final test data separate from validation and hyperparameter selection.

Score mechanical constraints separately from literary judgements. Mechanical checks cover selected-span application, duplicate removal, typography, output-only format, requested word limits, truncation and errors. Editing retains **no minimum length**. Human criteria cover voice, coherence, continuity, character distinction, dialogue subtext, pacing and usefulness. Never require an invented continuation to match the published next paragraph.

Predeclare the release gate: no critical selected-span/data-loss or privacy regression; no increase in explicit canon contradictions on the paired context cases; human-reviewed evidence of improvement on the targeted skills with disagreements and uncertainty reported. Small samples with ambiguous results require more independent evaluation, not a claimed win. Final test failures are reported, not patched by training on those cases. Retire exposed tests and create a new frozen version when needed.

## 4. Train a bounded candidate, after the data gates pass

Keep the current base revision and all earlier adapters immutable. Pin model/tokenizer/chat template, training backend, dependency versions, dataset hashes and seed. Start a fresh adapter from the same base to isolate the effect of the new dataset; compare against the current craft adapter as well. Mask prompt tokens and verify actual supervised token spans. Include a separate author/work validation set; select checkpoints on validation evidence and stop on deterioration or memory pressure. Record train/validation loss, effective batch, steps/epochs, sequence lengths, peak memory, duration and truncation counts. Avoid a broad hyperparameter sweep on a tiny dataset.

On the 16 GB M5 Air, begin with the already demonstrated small-model MLX path: batch one, gradient accumulation and bounded sequences. The earlier 6.34 GB peak is evidence for that tiny run only, not a guarantee for longer sequences or a larger dataset. Measure available memory and swap; halt cleanly rather than competing with the user's writing session. Never truncate away targets or critical context merely to fit memory.

MLX LM supports LoRA/quantised LoRA, prompt masking and separate validation/test files; its [official training guide](https://github.com/ml-explore/mlx-lm/blob/main/mlx_lm/LORA.md) describes the options. The current [Unsloth repository](https://github.com/unslothai/unsloth) advertises MLX/macOS support, while its [requirements page](https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements) still describes Apple support as forthcoming. Verify the **installed version, actual backend and model support** before choosing commands. Do not infer CUDA support from the presence of the Studio UI. Preserve the working local environment instead of updating dependencies in place.

If required sequence length/model size does not fit, prepare a pinned Unsloth NVIDIA cloud recipe and a reviewed data-only export. Before launching, obtain a concrete budget and approval for the provider, uploaded files, storage/retention and maximum runtime. Use a hard spending/runtime stop, saved checkpoints and explicit cleanup. No cloud jobs start under this planning request.

## 5. Validate the model ordinary users will run

Repeat the frozen independent comparison after training. Then fuse/export a candidate, quantise to the supported GGUF format, and repeat representative prompts on the exact packaged runtime. Check chat-template/stop-token equivalence, output truncation, quantisation regressions, memory and latency. Test macOS ARM64 and actual supported Windows/Linux machines separately; CI compilation does not qualify their hardware or packages. Keep iOS/web online connections explicit: another computer's loopback address is not a shared service.

Issue a new versioned package/catalog entry only after review, with checksums, base/model licensing records, runtime identity, supported platforms and rollback path. Keep the existing model selectable and leave ordinary drafting available offline if AI is unavailable. No automatic promotion, training on app startup, or paid service activation.

## Automation boundary and immediate next deliverable

Codex can inventory/deduplicate admissible source spans, assemble traceable review packets, run validators, export masked datasets/recipes, execute approved bounded training, collect fresh-context responses, calculate mechanical scores, build blinded packets and prepare runtime packages. Rights uncertainty, any required human approvals, independent human quality ratings, budgets and model promotion remain explicit decisions. An AI evidence review must be labelled as such.

**Next deliverable:** a skill-by-skill inventory of already eligible sources plus the first review packet and a new context-aware evaluation protocol. Resolve missing admissible editing/dialogue/analysis targets before spending on training. This document is the plan; it does not claim that the new dataset or protocol has already been prepared.
