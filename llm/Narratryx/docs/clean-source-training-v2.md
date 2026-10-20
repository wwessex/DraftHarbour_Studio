# Public-domain-only experiment v2 — 19 October 2026

Training completed on 19 October. The interrupted evaluation was resumed and
completed on **20 October 2026**; the results below include all 28 requests.

The user requested continued training using only sources that require no new
permission. This experiment uses exclusively the **108 previously approved
Opie/Wray public-domain prose passages**, within the recorded GB/US scope. All
Codex-generated instruction examples are excluded. A separate fresh-base
adapter completed two passes of this data; the earlier adapter is preserved.

## Data and execution

| Item | Observed value |
| --- | --- |
| Sources | Opie, *The Father and Daughter*, PG49621; Wray, *Nestleton Magna*, PG41916 |
| Exact selection | 54 approved paragraphs per author, 108 total |
| Distinct data | 9,871 words; 12,487 text tokens |
| Training input | Unchanged `clean-source-approved-v1/train.text.jsonl` |
| Input SHA-256 | `5dd6caa711c4d72daaa92b14d83d99f953337329c638ff54521cd01c82e75d38` |
| Base | `mlx-community/Qwen3.5-4B-MLX-8bit` |
| Base revision | `5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d` |
| Initialization | Fresh adapters, no checkpoint or old adapter resumed |
| Backend | Installed Unsloth MLX CLI trainer adapter, local and offline |
| Objective | Raw-prose next-token prediction, not instruction/answer SFT |
| Epochs / optimizer updates | 2 / 54, all completed |
| Text tokens processed | 24,974 across the two passes |
| Precision | Cached 8-bit base preserved |
| Context / batch / accumulation | 512 / 1 / 4; packing disabled |
| LoRA rank / alpha / dropout | 8 / 16 / 0 |
| Optimizer / schedule | AdamW; LR `1e-5`; linear decay; 3 warmup steps; seed 42 |
| Internal evaluation split | Disabled |
| Training duration | 152.7 seconds, excluding setup and inference |
| Peak MLX allocation | 6.50 GB, not total system RAM |
| Worker aggregate training loss | 3.2339, not an independent evaluation score |
| Final optimizer-step loss | 3.2174; batches differ, so this is not evidence of generalisation |
| Adapter size | 47,616,418 bytes |
| Adapter SHA-256 | `4fe3e3ab36011b0a48cc2b2419df729432f5f8bb4b0df65d4e6982fe5f4b8eab` |

All 54 step losses and gradient norms were finite. Progress reports two epochs
and no training warnings. Final adapters and checkpoints at steps 27 and 54 are
saved separately from v1. The final base-weight hash is unchanged.

Compared with v1, this is a new two-epoch run with a 54-step linear-decay
schedule. It does not resume v1's completed optimizer state. The longer decay
horizon means v2's first 27 steps are not identical to v1's first epoch; interpret
this as a comparison of two training configurations rather than an isolated
estimate of epoch count alone.

The sole training-file path is checked explicitly against the approved export.
The source approval, raw spans, export, model and tokenizer pins were checked.
Both approved rights records again passed GB/US training/evaluation release-
evidence validation. This is validation of recorded evidence, not a new legal
certification or worldwide clearance of either entire edition.

The record retains Opie's ninth-edition title matter dated 1824 and Wray's
undated “Thirtieth Thousand” printing; Wray's first-publication year is not
silently used as the printing's date. The same approved selections exclude
provider notices and material outside their approved scope.

## Evaluation protocol

A separate inference process loads the final adapter and pinned base, then runs
28 matched requests across the existing 14 exploratory cases. Each request uses
one new user message, no earlier assistant turns, no system prompt or tools,
zero prompt cache, temperature 0, seed 42, disabled thinking and a 512-token
output cap. Adapter-off responses control for the same loaded base weights;
condition order alternates by case.

The existing constructed diagnostic prompts are **evaluation inputs only**;
they and their answers never enter the public-domain training corpus. They have
been used before, are unfrozen and cannot establish unseen generalisation or a
broad literary-quality claim. There is no newly cleared independent prose-loss
holdout. No heldout paragraphs from these training works are presented as an
independent author test.

The MLX inference backend retains its warning that the configured 2,048-token
context limit is not enforced by every cache layer. These short prompts and the
512-token output cap fit below that size; the warning remains in the log.

## Completed comparison — 20 October 2026

| Mechanical checks | Unchanged base | One-pass v1 | Two-pass v2 |
| --- | --- | --- | --- |
| All cases | 5/14 | 6/14 | 7/14 |
| Editing, including exact controls | 4/4 | 4/4 | 4/4 |
| Dialogue | 1/2 | 2/2 | 2/2 |
| Pacing | 0/2 | 0/2 | 1/2 |
| Fiction | 0/2 | 0/2 | 0/2 |
| Analysis | 0/2 | 0/2 | 0/2 |
| Storytelling | 0/2 | 0/2 | 0/2 |

The additional whole-case pass over v1 is `pacing-orchard`: v2 produced 209
words, within the requested 100–220 range, compared with 248 words for v1.
The labels also matched. All 14 base responses exactly match the earlier
comparison, providing a useful reproducibility check. Both exact-output
editing controls pass in every condition.

All 28 final requests completed without inference errors, empty outputs or
truncation. Prompt hashes match between conditions, with one message per
request, no prior assistant turns and zero cached tokens. The final adapter
hash is unchanged and the resumed inference process unloaded its model.

Evaluation initially stopped after 18 complete responses, with no process
still running when work continued. The original 18 were preserved byte for
byte. Only the ten missing requests were generated after checking the adapter,
adapter configuration, packages, backend source and adapter-module count against
the original runtime. `resume-audit.json` pins the saved prefix; the separate
resume log and runtime record document this recovery. No interrupted or partial
response was silently treated as complete, and no training was repeated.

AI editorial inspection with model identities visible still finds substantive
defects that the mechanical score does not measure:

- The ferry edit changes “was holding” to “held” but reports no changes.
- The ferry continuation reverses the supplied promise when it says leaving
  breaks her promise, although the promise was to take the ferry home.
- The orchard analysis invents an inspection-before-harvest goal and treats
  the shears as proof of a family decision. It supplies one quotation rather
  than the requested two and exceeds the word limit.
- The orchard dialogue fits the line limit but includes narrative action and
  explicitly describes “unspoken fear”, despite the dialogue-only brief.
- The newly passing orchard pacing answer adds speech and running away, and
  has Leena snatch, then grab, the same shears. Its length improvement does not
  establish that both versions preserve the original beat.
- The orchard plan demands that her father fetch a map from his study when
  the supplied passage places the map in Leena's pocket. The ferry plan also
  reverses who gave whom the coat. Both exceed the planning word limit.

**Decision:** retain v2 as a separate experimental adapter. Mechanical
compliance improved on one additional reused case; broad literary improvement
and release readiness remain unproven. These results do not justify automatic
promotion, application adoption or indefinite additional epochs on the same
small selection. No blind human preference result has been recorded.

The final paired outputs and review criteria are in
`fresh-context-v1/BLIND-REVIEW.md`, with identities concealed and its assignment
key kept separately. Reviewers who have already seen the named outputs cannot
claim an independent blind judgment. The review packet is evaluation material,
not a training dataset.

## Isolation and artifacts

The run uses the installed backend directly. The Studio browser form or its
old selected pilot dataset does not describe this run. No cloud job, paid
inference, model publication, merge, serving change or application integration
was performed. Execution stops after this bounded experiment and diagnostics.

Artifacts are under:

`/Users/williamwessex/Documents/Writer1/llm/Narratryx/artifacts/clean-source-training-v2/`

- `source-policy.json`: the user's material restriction and exact inclusion/exclusion scope.
- `launch-audit.json`, `request.json`, `worker-config.json`: requested and resolved settings.
- `protected-inputs.json`: prior adapter, sources, dataset, benchmark and other protected hashes.
- `training.log`, `progress.jsonl`, `final-progress.json`, `training-summary.json`.
- `completion.json`, `adapter/`: final hash and saved model/checkpoints.
- `fresh-context-v1/`: paired protocol, raw responses, scores and review material.
- `comparison-v1-v2.json`: matched comparison with the previous one-pass run.
- `fresh-context-v1/run-remaining.py`, `resume-audit.json` and `runtime.resume.json`:
  recovery of the ten missing requests without replacing the first eighteen.
- `final-verification.json`: post-evaluation source, adapter and artifact checks.

All work stays inside `llm/Narratryx`. Web/PWA, Tauri desktop, Capacitor iOS and
native macOS application code, assets, feature behaviour and project-data
formats are unchanged. Application builds and device tests were not run for
this isolated model experiment. The foundation implementation did not change;
its earlier 72-test result is historical, not a claim of a fresh suite run here.
