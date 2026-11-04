# Broader source-only literary training — 25 October 2026

A fresh-base local Unsloth MLX LoRA completed **36 updates on 142 examples**. This expands training beyond craft explanations and Story Bible retrieval to source-conditioned continuation, constrained editing and dialogue. The adapter remains experimental; no claim of improved overall literary quality or equivalence to Sudowrite Muse is established.

The user's execution instruction was to proceed with training and improvement toward the capabilities described by [Muse](https://sudowrite.com/muse). The [capability map](muse-capability-targets-2026-10-25.md) distinguishes prose/dialogue/voice/pacing goals, multi-step inference workflows and the evidence still needed. No proprietary Muse weights, prose samples, user writing or competitor outputs were used as training data. No paid job or upload ran.

## Training material and scope

| Material | Training records | What the targets demonstrate |
|---|---:|---|
| Scoped Opie paragraphs | 54 | Continue a supplied prose fragment in the source voice; answers are unchanged source substrings |
| The same Opie paragraphs with a mechanical duplicate inserted | 54 | Remove only the duplication and preserve the remaining text; not genuine author revision |
| Scoped Opie speech | 14 | Source-derived quoted speech fragments after context; these include interrupted speech and do not demonstrate full dialogue scenes |
| Scoped Wharton/Hamilton craft prose | 20 | Attributed historical explanations, including viewpoint, dialogue, style and narrative structure; not generated literary teaching answers |
| **Total** | **142** | **12,843 supervised tokens including one structural EOS per target** |

All assistant answers come from existing approved exact source spans. New task instructions are distinct from answer provenance. The [combined ledger](../rights/literary-mix-v1.scoped.jsonl) copies existing scoped decisions without expanding their edition/span/jurisdiction/use limits or inventing new human approval. Source hashes, raw spans, transformations, target spans and previous approvals are retained in `artifacts/literary-mix-v1/records.jsonl` and `trace.jsonl`. Deterministic derivation/alignment review is labelled Codex AI, not human literary judgement or legal certification. Generated literary teaching targets and unreviewed English-PD material remain excluded.

Wray's 108 derived records are validation-only for this candidate, keeping training and validation authors/works separate. The monitor uses sixteen evenly spaced records selected before results. Wray appeared in earlier exploratory project adapters; it is not a pristine project-wide holdout. Mansfield and Chesnutt remain evaluation-only, with no training use permitted in their scoped records. Base-model pretraining contamination is unknown.

The mixture is narrow: three training authors, historical diction, repeated task views of 54 fictional paragraphs, and only 449 supervised dialogue tokens. Editing supplies 6,293 supervised tokens, continuation 3,251 and craft analysis 2,850. It does not establish broad genre coverage, modern dialogue, substantive copyediting, scene planning or long-form story quality. Pacing/storytelling training remains limited to attributed craft explanations; no fictional compression or fabricated revision targets were admitted.

## Run and validation loss

Pinned base: `mlx-community/Qwen3.5-4B-MLX-8bit`, revision `5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d`. A new adapter starts from that unchanged base, not from the prior craft adapter. Rank 8, alpha 16, dropout 0, seed 42, LR 1e-5 with linear decay and two warmup steps; batch one, accumulation four, one pass, maximum 36 updates. Context allowance 1,024, longest actual example 659 tokens. All prompt tokens have label -100; each source answer round-trips through the tokenizer and only its tokens plus EOS receive loss. Installed explicit-label detection passed.

The worker reported **218.0 seconds**, **6.854 GB peak MLX allocation** and exactly **12,843 supervised tokens**, matching preflight. No training warning, error or nonfinite loss was reported. The allocation guard was 10 GB; this is measured evidence for the bounded run on the 16 GB development Mac, not a general hardware guarantee.

The fixed validation monitor loss was 1.135485 at update 18 and 1.124875 at update 36. Final optimizer-step training loss was 2.615313; the worker's aggregate training loss was 1.4879. These describe different aggregations/sets. The small validation-loss change does not establish better fiction and is not comparable to earlier runs with different data/objectives. This fixed pilot kept its final adapter; validation was monitored, not used for a hyperparameter search or a test-driven checkpoint selection.

Adapter SHA-256: `f41cb31a1a6d92bd6fef37d5d92275d7514a2a8064f94593e9aacf12d6a8bfc9`.

## Independent requests and frozen comparison

Twenty-four tasks cover four sourced contexts times six skills: continuation, minimal editing, dialogue, pacing, voice-preserving rewriting and grounded passage analysis. Each condition uses a fresh one-user-message request, no history/tools, empty system prompt, disabled prompt cache, temperature zero, seed 42, thinking disabled and a 512-token generation allowance. The base, prior craft adapter and new candidate receive the same prompts and settings. Models load serially and unload between conditions; no inference-speed comparison is claimed. The four contexts were used in earlier diagnostics, so this is not described as a wholly new independent research benchmark or the pending formal original-synthetic benchmark.

A pretraining audit caught a minimum length in the voice-preserving rewrite task. Nine exploratory base responses were preserved separately, the rewrite minimum was removed, the amendment and prior protocol hash were recorded, and the entire baseline was restarted before training. All editing tasks in the executed comparison have no minimum length. The matched primary comparison uses the revised protocol; no superseded outputs are pooled into it.

| Mechanical check | Base | Current craft | New mixture |
|---|---:|---:|---:|
| Exact minimal duplicate repair | 2/4 | 2/4 | 2/4 |
| Continuation: 80–140 words | 3/4 | 2/4 | 4/4 |
| Dialogue: at most 200 words | 4/4 | 3/4 | 4/4 |
| Compression: 80–120 words | 3/4 | 3/4 | 4/4 |
| Voice-preserving rewrite: at most 140 words | 0/4 | 0/4 | 0/4 |
| Analysis: at most 120 words | 0/4 | 0/4 | 0/4 |
| Request errors / truncated outputs | 0 / 0 | 0 / 0 | 0 / 0 |

All **72 matched requests** completed with zero cached prompt tokens, request errors or output truncation. The allocation outside the model backend enforces prompt-plus-output token limits; the audit verifies actual totals. The new mixture meets continuation, dialogue and compression limits on 4/4 cases each, compared with 2/4, 3/4 and 3/4 for the current craft adapter. Exact minimal editing remains 2/4 in all conditions; both Mansfield cases still normalise typography rather than preserving the exact source.

**Voice-rewrite and analysis length control remains poor:** every condition exceeds the stated upper cap in all four cases for each task. No broad improvement in these skills is claimed. Automatically satisfied empty editing word ranges are deliberately omitted from the table. These are mechanical constraints, not ratings of prose, dialogue, pacing, originality, factual grounding or overall literary quality. Four source scenarios reused across skills are correlated; do not treat the 24 prompts as 24 independent story worlds. The [scores](../artifacts/literary-mix-training-v1/scores.json) and raw responses preserve all results.

## Quality decision and next work

Human quality ratings remain **zero**. The blinded three-condition packet and blank two-reviewer ballots are under `artifacts/literary-mix-training-v1/`; the condition key is separate. Review only the requested skill, known facts and limits on knowledge. Record evidence for voice, coherence, dialogue/subtext, pacing and grounded analysis; adjudicate disagreements before promotion. A good invented continuation need not match the published next paragraph. Word counts and minimal duplicate repair do not measure fiction quality.

Do not replace the app's current model on this evidence. The next useful data work is source-traceable directed-Write tasks, genuine author revision pairs and more authors/genres with exact-edition clearance. Task instructions can be constructed from verified passage facts while retaining an unchanged source passage as the answer; this does not permit generated literary teaching targets. Longer scenes and draft/review/revise workflows require separate inference/runtime tests, not a claim that this short-context pilot already delivers them. Any future larger-model cloud job requires a concrete budget and upload approval.

## Evidence and application boundary

Preparation: `artifacts/literary-mix-v1/` — source records/traces, tokenizer and loss-mask audit, training review, full validation records and frozen test inputs.

Execution: `artifacts/literary-mix-training-v1/` — protocols/amendment, request and worker configuration, baseline/current/candidate responses, training progress, isolated adapter, scores, blind review and final verification. Local generated artifacts/model weights are excluded from Git. Scripts under `curation/literary-mix-v1/` refuse overwriting experiment evidence; exact local prior source artifacts are required. They are bounded experiment scripts, not a general corpus downloader or unattended training service.

The foundation suite passed **97 tests**, including four new derivation guards. This model task changes no web/PWA, Windows/Linux Tauri, Capacitor iOS or independent native macOS runtime, feature, default, installer or model package. Pre-existing application work was preserved; no fresh app build/device test is claimed for this isolated training task. The developer inference service was paused to keep one model loaded, then restarted with its existing current craft model/credentials. The new adapter was not published, fused, quantised, installed, or automatically promoted.
