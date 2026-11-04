# Literary curriculum v2 — 25 October 2026

A second fresh-base local Unsloth MLX experiment completed **61 updates on 244 source-only examples**. Its new diagnostic comparison does **not justify replacing the existing app model**. Dialogue block-count compliance improved, but several brevity measures regressed and exact typography preservation remained unreliable. No human literary-quality or Muse-equivalence claim is made.

The [research follow-up](muse-followup-2026-10-25.md) explains how the additional Muse and Saliency Engine links informed the work, the separate AI review of v1, and the isolated context-selection prototype. Vendor descriptions are requirements/research references, not a disclosed recipe or training corpus.

## Curriculum and source scope

Training uses 244 instruction examples drawn from **90 underlying source paragraphs across five authors**. Repeated task views are not 244 independent literary demonstrations:

| Training category | Records | Target provenance |
|---|---:|---|
| Continuation and anchored Write | 140 | Unchanged source substrings/paragraphs; anchored Write is conditional reconstruction, not original author-created prose in response to a new semantic outline |
| Duplicate/reference-based repairs | 70 | Original source targets with constructed input corruption; not genuine author revision pairs |
| Quoted dialogue fragments | 14 | Existing Opie speech spans; not complete multi-turn scene demonstrations |
| Historical craft explanations | 20 | Existing attributed Wharton/Hamilton prose |

The new material comprises eight Wells and eight Doyle paragraphs under the [scoped source assessment](../rights/dossiers/literary-expansion-2026-10-25.md). It records exact digital hashes/spans, original publication/contributor evidence, GB/US limits, crosschecks and uncertainty about physical print copies. It is an attributed **Codex AI evidence assessment**, not new human approval, author consent or legal certification. No complete-book, external-upload or publication clearance is inferred. Full notices/source files remain private; provider wrappers, modern descriptions, illustrations and annotations are excluded.

There are **zero generated literary teaching targets**. New task instructions are distinct from assistant-answer provenance. No user manuscript, Story Bible data, Muse sample prose, competitor output or unreviewed English-PD row enters training. genuine author-revision and substantive narrative-analysis demonstrations remain missing.

Wray's 108 records remain separate validation data. They were used in older exploratory project adapters, but not in either fresh literary-mixture candidate. All 108 token records and the fixed sixteen-record monitor are byte-identical to v1. Base pretraining contamination remains unknown.

## Local run

Base: `mlx-community/Qwen3.5-4B-MLX-8bit`, revision `5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d`. Fresh rank-8, alpha-16 LoRA, dropout zero, LR 1e-5 with linear decay/two warmup steps, seed 42, batch one, accumulation four, one pass, 61 updates. The previous adapter is a comparison condition, not the starting weights.

All prompt tokens are masked from loss. Targets round-trip exactly through the pinned tokenizer; installed explicit-label detection passed. Longest actual sequence: 659 tokens within a 1,024-token training allowance. The worker reported **23,851 supervised tokens**, matching preflight, **378.6 seconds** and **7.270 GB peak MLX allocation**. The allocation guard was ten GB on the sixteen-GB development Mac. No training warning, error or nonfinite loss was reported.

The fixed Wray monitor loss was 1.116835 at update 30 and 1.093776 at update 60. The final optimizer-step training loss was 2.053654; the worker's aggregate was 1.7803. These are different aggregations/data roles. The lower monitor loss is not evidence of better fiction. Multiple curriculum elements changed together, so changes cannot be causally attributed to one source or instruction modification. The final bounded checkpoint was retained without test-driven checkpoint selection or a hyperparameter sweep.

Adapter SHA-256: `bbcb229ad407e6305752a6063b5f9916d2069f34e320ae0f45cdfd7c802c45e7`.

## Frozen new diagnostic

The prior 24-case pack is exposed development evidence and remains unchanged. A new set of twenty original Codex AI-authored fictional diagnostic cases was frozen before baselines and training. Four story worlds each have minimal editing, concise voice-preserving rewrite, dialogue, grounded analysis and continuation tasks. The contexts and exact repair references are **evaluation-only**, not literary training/teacher targets. This is an experimental AI-structurally-reviewed diagnostic; it does not bypass or replace the separate formal benchmark's pending human review.

Three conditions receive identical one-user-message inputs with no prior turns/tools, empty system prompt, disabled prompt cache, temperature zero, seed 42, thinking disabled and 512 output tokens. Models load serially. No latency comparison is claimed. All editing tasks have no minimum length. The dialogue-block proxy was declared before inference; it counts quoted lines, not definitive speaker turns. Multiple speakers on one line or quoted fragments in narration can affect it, so manual checks remain necessary.

| Mechanical check | Base | Prior mixture v1 | New v2 |
|---|---:|---:|---:|
| Exact minimal duplicate repair | 0/4 | 0/4 | 0/4 |
| Continuation: 80–120 words | 4/4 | 3/4 | 2/4 |
| Dialogue: at most 120 words | 3/4 | 3/4 | 2/4 |
| Voice-preserving rewrite: at most 85 words | 1/4 | 1/4 | 0/4 |
| Analysis: at most 70 words | 3/4 | 2/4 | 2/4 |
| Dialogue: 4–6 quoted-block proxy | 1/4 | 1/4 | 3/4 |
| Dialogue: both length and block-count proxy | 1/4 | 0/4 | 1/4 |
| Request errors / truncated outputs | 0 / 0 | 0 / 0 | 0 / 0 |

All **60 matched requests** completed without errors or truncation, with no cached prompt tokens. Exact-repair and format metrics are not measures of prose quality, factual grounding, viewpoint, subtext or originality. Compared with v1 on this same new pack, v2 improves the dialogue-block proxy but regresses on continuation, dialogue length and voice-rewrite length; analysis limits are unchanged. These checks do not establish an overall upgrade. No outputs were trimmed or repaired to obtain these model scores.

Every exact-repair failure in the new candidate disappears when quotation/apostrophe typography is normalised for diagnosis. That relaxed observation is not substituted for the strict metric: the instruction required preserving those characters. No human literary-quality ballots have been completed. The [six-case blind review subset](../artifacts/literary-mix-training-v2/QUICK-REVIEW.md) is a practical starting point; condition labels remain separate. The four correlated source scenarios are not twenty independent story worlds, and no claim of parity with Muse is supported.

## Decision

**Hold v2 as experimental.** Do not overwrite the prior candidates or change app defaults. The results support changing the precision-editing workflow and obtaining better task-matched demonstrations rather than assuming that more source prose or additional epochs will solve the problems. Genuine author revisions, substantive grounded analysis, modern register, diverse scenes and independent quality review remain necessary. The user's generated-literary-target exclusion remains unchanged.

The separate [anchored-edit inference pilot](anchored-edit-inference-2026-10-25.md) tests a practical application mechanism on the existing craft model. Its results, if useful, are a workflow/application effect—not improved v2 weights or a general literary benchmark. The context-selection prototype is also separate from the model and remains outside app runtimes.

## Validation and operational state

The **110-test foundation suite passed before the training experiment**. After adding the edit-preview helper, the current foundation suite passed **116 tests**. Frozen model inputs, protected base/prior-adapter hashes, source spans/rights scopes, explicit labels, response hashes and blank human ballots passed final verification. Exact copies of the 23 frozen input files are retained with a snapshot manifest for historical inspection; the original protocol and source decisions remain intact.

Run evidence is under `artifacts/literary-mix-training-v2/`; data and traceability are under `artifacts/literary-mix-v2/`; source snapshots/notices are under `rights/raw/` and `rights/evidence/literary-expansion-2026-10-25/`. Generated data, keys and model artifacts remain excluded from Git. The private blinded condition key is separate from review packets. No human ratings were invented or filled into ballots.

The existing authenticated developer inference service was paused for serial model work and restored with the same selected craft model/configuration and credentials. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS application code, defaults, packages and manuscripts were unchanged by this isolated model task. No fresh app build or target-device check is claimed. No paid/cloud job, upload, model publication, GGUF replacement or automatic promotion occurred.
