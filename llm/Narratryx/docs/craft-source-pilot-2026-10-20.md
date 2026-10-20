# Public-domain craft pilot — 20 October 2026

One fresh-base local Unsloth MLX pilot completed. It does **not establish improved literary quality**, and the new adapter has not been promoted, merged into a base model, or connected to the application. The next decision is a blinded human comparison, followed by better task demonstrations rather than more repetitions of this tiny dataset.

## Data and source evidence

Twenty attributed craft questions/answers use six paragraphs from Edith Wharton's *The Writing of Fiction* and fourteen from Clayton Meeker Hamilton's *A Manual of the Art of Fiction*. Answers contain only historical source prose: 2,443 whitespace-counted words, 2,850 supervised tokens including EOS. Questions and chat formatting are masked from loss. No generated creative targets, teacher outputs or unreviewed English-PD rows are included.

The [scoped rights dossier](../rights/dossiers/craft-expansion-2026-10-20.md) documents GB/US expiry evidence, exact digital hashes, edition distinctions, exclusions and provider terms. These are explicitly attributed AI evidence decisions under the user's permission-free-source instruction, not fabricated human approvals or legal certification. Wharton title matter identifies 1925; Hamilton is a **1919 printing of a copyright-1918 revision**, not a 1918 printing. The earlier Hamilton comparison artifact has a 1911 imprint and 1908 copyright.

[Training review](../artifacts/craft-expansion-v1/TRAINING-REVIEW.md) contains every question and source answer. Source spans, transformations and label checks are retained in that artifact directory. The source/answer/tokenizer checks pass for all twenty examples. Four fresh contexts from Mansfield and Chesnutt are **evaluation-only**; author/work separation and a lexical leakage screen pass. Their exact physical print copies remain unidentified; the pinned digital artifacts and selected original prose are identified without inventing physical-edition certainty.

A broader Hamilton body comparison identified publication-reference updates, not useful before/after fiction edits. Zero revision pairs were admitted. Obtaining demonstrably author-revised fictional passages remains unfinished; no typography or transcriber correction was mislabelled an authored revision.

## Training

The cached base is `mlx-community/Qwen3.5-4B-MLX-8bit`, revision `5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d`. A new LoRA starts from that base, rather than continuing an old experimental adapter. Rank 8, alpha 16, dropout 0, learning rate 1e-5, seed 42, one epoch, batch 1, gradient accumulation 4, context 1024, explicit answer-only labels. Maximum actual training sequence: 266 tokens.

The five updates completed in **29.82 seconds**, reported peak **6.34 GB**, with finite loss and no training warnings. Final loss 2.6685 is training loss only; no held-out loss was measured. Adapter SHA-256: `09f950e0954105b4b5bf1cdd5c7a4ee882d617742aadad6ec33c1dda5af84688`. Base weights and three prior adapters remain hash-verified and unchanged.

This ran through the installed Unsloth MLX backend on the Mac, without a paid/cloud job or upload. The Studio browser's previously displayed training/chat selection was not updated to advertise this run. The adapter is an independent local artifact under `artifacts/craft-training-v2/adapter`.

## Frozen comparison and correction

The experiment-specific protocol was frozen before its baseline and training. Each response uses one user message, no history, no tools, empty system prompt, disabled prompt cache, temperature 0, seed 42, thinking disabled and a 512-token generation allowance. Base adapter-off responses were recorded first, then training, then candidate adapter-on responses. No latency comparison is claimed.

An earlier exploratory baseline exposed a test-design mistake: the dialogue score had a word cap absent from its prompt. That first 16-response pass is preserved under `artifacts/craft-training-v1`; **no training ran on that superseded protocol**. The corrected protocol explicitly requests at most 200 dialogue words and increases the generation allowance for both conditions. All sixteen baseline requests were rerun before training. The amendment and prior-protocol hash are recorded, rather than silently rewriting the first pass. Including that exploratory pass, 48 inference responses were produced; the primary matched comparison contains 32.

Sixteen tasks cover four contexts times four skills. Continuations are new plausible fiction, never an exact-match test against the published next paragraph. Minimal editing has no minimum word count and requires retaining original typography; dialogue also needs human checks for spoken turns and subtext. Compression requires retaining facts and chronology. This is a sourced-context diagnostic, not the pending formal 120-task original-synthetic benchmark; its provenance is not falsely labelled synthetic to fit that schema.

## Mechanical results

| Check | Base | New craft adapter |
|---|---:|---:|
| Exact minimal-edit reference (4 tasks) | 2/4 | 2/4 |
| Continuation word range, 80–140 (4 tasks) | 2/4 | 1/4 |
| Dialogue at most 200 words (4 tasks) | 2/4 | 2/4 |
| Compression word range, 80–120 (4 tasks) | 3/4 | 4/4 |
| Request errors / truncated outputs (16 each) | 0 / 0 | 0 / 0 |

Word counts use whitespace-separated tokens. Editing has no word-range gate, so its four automatically satisfied empty ranges are not counted as word-limit achievements in this table. Both conditions remove the injected duplicate in all four editing cases, but both normalize curly quotes/apostrophes in the two Mansfield passages despite the instruction to preserve punctuation. This accounts for the two strict editing mismatches; it is not four independent demonstrations of broad editing competence.

These are formatting and narrowly specified repair checks, **not literary-quality ratings**. Named, nonblind AI spot inspection also flags unsupported character relationships/conflation in the garden scene; that is an observation for review, not a human ballot or a canonical-continuation score. The prompt supplies limited context, so reviewers must distinguish contradictions from permissible new developments and avoid relying on knowledge of the rest of the published story.

## Human review and next work

The [blinded comparison packet](../artifacts/craft-training-v2/BLIND-REVIEW.md) randomizes A/B by case and includes source facts, unknowns and the exact task. [Blank ballots](../artifacts/craft-training-v2/human-ballots.blank.jsonl) contain no invented ratings. The condition key is stored separately; reviewers should not consult it before submitting decisions. Obtain two independent reviewers on a representative subset, record concrete evidence and adjudicate disagreements before a quality/promotion claim. Current human quality ratings: **zero**.

This pilot offers no reason to keep repeating five-step runs or to deploy the adapter. Next data work should prioritize genuine author revision pairs and permission-free demonstrations of the target tasks, then expand beyond twenty craft explanations. The explanations alone do not supervise the creation of new dialogue, restrained line editing or continuity management. The small sample, historical prescriptions and possible occurrence of test authors in base pretraining limit generalization.

## Validation and application scope

All **72 foundation tests passed**. Exact raw-file hashes, scoped source spans, answer transformations, tokenizer round trips and installed MLX explicit-label handling pass. The final audit verifies protocol inputs, 32 complete fresh-context responses, zero cached prompt tokens, inference token totals within 2048, test-author training exclusion, unchanged base/prior-adapter hashes and experiment-model unloads. [Audit](../artifacts/craft-training-v2/final-verification.json); [raw mechanical scores](../artifacts/craft-training-v2/scores.json).

All changes in this work are confined to `llm/Narratryx`. **Web/PWA, Windows/Linux Tauri desktop, Capacitor iOS and the independent SwiftUI/AppKit macOS application are unchanged.** No application builds, platform runtime checks or device tests were run for this isolated model experiment. Pre-existing unrelated working-tree changes were left intact. No model integration, publication, paid job or automatic promotion occurred.
