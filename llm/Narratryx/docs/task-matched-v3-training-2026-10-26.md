# Task-matched v3: bounded local experiment — 26 October 2026

A new source-only adapter completed **13 updates on 50 examples** and **72 matched fresh-context responses**. Dialogue formatting improved on this small diagnostic; exact editing did not. An unblinded AI spot-check found persistent semantic weaknesses. **Keep this candidate experimental and leave the current craft model selected.** No human literary-quality ratings are complete, and no Muse-equivalence claim is supported.

## Dataset and actual change

The curriculum changes task framing rather than adding independent literary source material. All fifty selected source spans appeared in the prior v2 corpus; this candidate starts from the pinned base, not from the v2 adapter. There are fifty distinct underlying spans, each used once in training:

| Category | Examples | Answer provenance |
|---|---:|---|
| Directed Write | 16 | Unchanged Wells/Doyle paragraphs paired with semantic briefs read against the actual source; no forced opening/closing anchors |
| Dialogue scene | 6 | Whole Opie paragraphs including speech and narration; includes short exchanges and narrated negotiation, not six uniformly long scenes |
| Pacing-directed scene | 4 | Unchanged Opie paragraphs matched to action/pacing briefs; not before/after author revisions |
| Continuation | 6 | Exact source suffix after a supplied complete first sentence |
| Anchored Copyedit | 8 | Six deterministic duplicate-removal proposals plus two no-change proposals; JSON wrappers are structural labels, replacement words come from the source |
| Attributed craft explanation | 10 | Unchanged Wharton/Hamilton explanations, expressly attributed in the question |

There are **zero generated literary teaching answers**. Task instructions are AI-constructed after reading the source; the historical writers did not receive those briefs. The craft examples explain historical methods rather than analysing previously unseen fiction. No user manuscript, Story Bible, competitor output or unreviewed English-PD row is used.

The unchanged scoped rights ledger is `rights/literary-mix-v2.scoped.jsonl`. Exact source spans, target derivations and model-free audits are in `artifacts/task-matched-v3/`. The separate validation set retains 108 Wray records; a fixed sixteen-record monitor is selected before inference/training. Wray's author/work are excluded from this candidate's training, but prior exploratory project adapters saw Wray: it is not an independent project-wide test corpus. Neither historical source prose nor base pretraining contamination can establish modern-register or broad literary capability.

## Frozen comparison and run

The new diagnostic contains **24 cases across eight original AI-authored story situations**, four cases per skill: directed writing, exact editing, analysis, continuation, dialogue and pacing rewrite. These synthetic contexts are **evaluation only**, not training answers or a human-approved formal benchmark. Three tasks share each situation; cases are correlated and are not 24 independent story worlds. The older diagnostic packs and formal 120-task draft remain unchanged.

Prompts, case hashes, data, explicit loss masks, scripts, source ledger and protected model files were frozen before baselines and training. Each request has one user message, no prior assistant turn or tools, no prompt cache, temperature zero, seed 42, thinking disabled and at most 384 generated tokens within a 2,048-token context. Editing has no minimum length. Creative continuations have no canonical reference answer. Word limits and quoted-block counts are mechanical measures, not literary-quality scores.

The base completed all 24 requests on 25 October; the current craft baseline completed four before process interruption. On 26 October those four original response bytes were verified and retained, and the remaining twenty resumed with unchanged prompts/model pins/generation settings. Recovery code is separately hashed in the resume audit. Training had not started at interruption. No completed response was replaced and no hyperparameter choice was based on reviewing baseline prose. Timing comparisons are not claimed.

The fresh adapter uses cached `mlx-community/Qwen3.5-4B-MLX-8bit`, revision `5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d`, Unsloth MLX, rank 8/alpha 16, dropout zero, LR 5e-6, linear schedule, one warmup step, batch one/accumulation four, seed 42, one reported epoch and a thirteen-update maximum. All prompt labels are masked. Targets round-trip exactly. The training sequences reach **327 tokens**, with an overall train/validation maximum of 659, below the 1,024-token training allowance. Nothing was truncated.

Training completed thirteen updates in **64.1 seconds**, with **5,879 supervised tokens** and **6.635 GB reported peak MLX allocation**. The ten-GB allocation stop was not reached. Validation-monitor losses were 1.148358 at update six and 1.147842 at update twelve; the final optimizer-step training loss was 2.684925. The worker separately reported aggregate loss 2.6534. These are different aggregations; neither is a fiction-quality score. No warning/error/nonfinite loss was reported. The final bounded checkpoint was retained without a sweep or test-selected checkpoint.

Adapter SHA-256: `c34ef997723677dddda5ea0dfe02794f596e6ed2ffb2849bab941a77463c3bd3`.

## Results

| Mechanical check, four cases each | Base | Current craft | Candidate v3 |
|---|---:|---:|---:|
| Exact minimal duplicate repair | 2/4 | 2/4 | 2/4 |
| Directed Write, 60–90 words | 4/4 | 4/4 | 4/4 |
| Continuation, 60–90 words | 4/4 | 4/4 | 4/4 |
| Dialogue, at most 100 words | 2/4 | 1/4 | 3/4 |
| Dialogue, 4–6 quoted-block proxy | 3/4 | 3/4 | 4/4 |
| Pacing rewrite, at most 85 words | 4/4 | 4/4 | 4/4 |
| Analysis, at most 70 words | 3/4 | 3/4 | 3/4 |
| Request errors / truncations | 0 / 0 | 0 / 0 | 0 / 0 |

The dialogue proxy counts quoted blocks, not verified speaker turns or subtext. Changes to layout can affect it. The exact-edit cases ask for corrected prose, so these scores do not establish the candidate's JSON Copyedit performance in the app. No post-processing was applied to improve model scores.

An **unblinded, non-independent Codex AI spot-check** of selected outputs found: unqualified attribution of guilt in the seed-bank analysis; an unexplained safety rationale for cancelling astronomy viewing in the observatory continuation; and a pacing rewrite that moves a notice from a pocket to a hand, changes past narration into present tense and adds repetitive statements. Some answers are identical to the current craft/base answer; these are persistent weaknesses, not evidence that the candidate newly caused every fault. See the private run's `AI-SPOT-CHECK.md`. This check is not a human ballot or a completed independent quality evaluation.

`artifacts/task-matched-training-v3/QUICK-REVIEW.md` contains eight blinded cases covering all eight situations and all six skills. The full packet, blank two-reviewer ballots and private condition key are separate. Human ratings remain **zero**. Administrative character-name notes must not be mistaken for facts visible in prompts that leave a first-person narrator unnamed.

## Rights work and remaining data gaps

The separate [Dickens follow-up](../rights/dossiers/author-revision-followup-2026-10-26.md) completes a bounded AI evidence assessment of two exact historical-prose spans. This is not human approval or legal certification. It distinguishes a structural alternative ending from Copyedit. The full pair requires 1,826 training tokens under the pinned tokenizer, exceeding this pilot's 1,024-token allowance. It stays separate rather than being truncated or slipped into the frozen dataset.

The [Hopkins sourcing note](../rights/dossiers/hopkins-candidate-2026-10-26.md) identifies a prospective independent author/work and exclusions. Original chapter acquisition was blocked by HTTP403, so there is no invented clean text, no approved training row and no inclusion in this run.

Substantive independent author-revision pairs, modern-register sources, broader genres, longer conversational scenes and genuinely grounded source-based analysis remain data gaps. Reframing fifty existing passages cannot replace that work. Repeated exposed tests must remain development evidence; future final evaluation needs a separately frozen version.

## Validation, recovery and application boundary

The foundation suite passed **120 tests on 26 October 2026**, including four new evaluation-design tests. Separate audits verify source spans/derivations, all fifty distinct training spans, author/work separation, no generated literary targets, masks/token lengths, 72 response/prompt hashes, frozen snapshot copies, preserved pre-interruption bytes and blank human ballots. Base weights and every protected prior adapter/configuration match their frozen hashes. Scoped source-ledger validation remains distinct from legal certification or human approval.

The developer serving process was restored and its health checked as ready, with the same configuration, credentials and current craft model. No candidate was fused, quantised, packaged, published or promoted. No paid/cloud job or corpus upload occurred.

This work stays under `llm/Narratryx/`. **Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS application source, defaults, packages and manuscripts were not changed by this model task.** No fresh application build or platform-device run is claimed for it. Other concurrent checkout changes are not this experiment's changes.
