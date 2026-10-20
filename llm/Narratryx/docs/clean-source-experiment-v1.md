# Approved Opie/Wray experiment — preparation record

**Execution update:** The user subsequently requested “Time to train?”. The
bounded local run completed all 27 updates on the approved 108 passages. Its
launch audit, actual configuration, checkpoints and comparison outputs are in
`artifacts/clean-source-training-v1/`. See the
[execution report](clean-source-training-v1.md) for results. The preparation and
source-approval artifacts below retain their original historical status.

The user replied **“ok i approve”** after the source dossier and exact 108
passages were presented for approval. This decision is recorded for those
passages and the GB/US training/evaluation scope in
[the approval record](../rights/approvals/clean-source-expansion-human-approval-2026-10-18.json).
The reviewer's identity is the human user of this conversation; no legal name
or legal qualification was supplied or inferred.

The original pending records, raw sources and candidate passages are unchanged.
The approved source ledger is
`rights/clean-sources.approved-v1.jsonl`. Snapshots of the dossier, preparation
report and original pending ledger are preserved with the approval. The
recorded acceptance does not claim that a new facsimile proofread occurred.

## Completed checks and export

- Both source records pass release-evidence validation for **GB/US training and
  evaluation**. This checks recorded approval/evidence, not legal certification.
- All **108 approved paragraphs / 9,871 words** match the exact selection the
  user approved. Source-file, raw-span, text and approval hashes were checked.
- A model-neutral `{"text": "..."}` export contains only those approved original
  prose strings. No instructions, assistant answers, teacher outputs, provider
  notices or new source works were added.
- The cached base tokenizer counted **12,487 text tokens**, with a maximum of
  **313 tokens per paragraph**, excluding special tokens. Every paragraph fits
  the proposed 512-token context, including the worker's raw-text EOS handling.
  No text truncation, model loading or training occurred in this preflight.
- Existing diagnostic cases and reserved Murray passages remain protected and
  unchanged. Approval did not extend to Murray, other books, the draft benchmark,
  uploads, corpus redistribution, paid/cloud jobs, deployment or application
  integration.

This export is raw prose for next-token prediction with adapters. It is not
passed to the foundation's instruction/answer SFT validator. Its separate
validation report checks the approved source scope and CRLF-preserved raw-span
coordinates explicitly; it does not confuse them with the SFT validator's
universal-newline coordinate view.

## Proposed local run

| Setting | Prepared value |
| --- | --- |
| Base | `mlx-community/Qwen3.5-4B-MLX-8bit` |
| Revision | `5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d` |
| Initialization | Fresh adapters on the pinned base; no resume from the earlier pilot |
| Backend | Local Apple Silicon MLX, one process |
| Objective | Raw-prose next-token prediction using LoRA |
| Records | All 108 approved paragraphs |
| Epochs / optimizer updates | One pass / 27 updates |
| Context / packing | 512 tokens / disabled |
| Batch / accumulation | 1 / 4 |
| LoRA rank / alpha / dropout | 8 / 16 / 0 |
| Learning rate / schedule | `1e-5` / linear, 3 warmup updates |
| Seed | 42 |
| Internal evaluation split | Disabled; no random same-work split presented as independent evidence |
| Output | A new adapter directory; preserve previous pilot |

The installed Studio worker rejects its separate `Continued Pretraining`
training-type setting on MLX. Its supported configuration is **LoRA/QLoRA with
raw format**, which supplies the intended raw-text objective and EOS handling.
This distinction was checked in the installed worker source. The prepared
request also passed the installed `TrainingStartRequest` schema without being
submitted to the training API.

The cached base weight file and model/tokenizer configuration are pinned by
hash. The selected 8-bit base is preserved; no forced 4-bit conversion or remote
model code is enabled. No cloud resources are needed for this proposed small
experiment. Actual runtime memory and loader behaviour must be checked when it
runs; the new training graph and optimizer have not been exercised in this step.

## Comparison and interpretation

After a separately requested training launch, compare the unchanged base with
the new adapter on the existing 14 diagnostic cases. Run each request with a
fresh one-message context, no system prompt/tools/history, prompt caching off,
identical deterministic generation settings and alternating condition order.
Record adapter state and source/model/response hashes. Use a fresh evaluation
process and preserve raw outputs before scoring or reviewing them.

Those cases have already been used. They are useful regression diagnostics,
not unseen generalization evidence or a frozen broad literary benchmark. Assess
exact-output/editing controls, length/line/quote constraints, source fidelity and
blind literary comparisons separately. Training loss alone cannot show better
fiction writing. No approved independent prose-loss evaluation set is supplied
by this approval; do not silently score uncleared Murray text or select heldout
paragraphs from the same training works and call them author-independent.

Stop on non-finite loss/gradients, OOM or memory pressure, changed inputs,
unexpected row counts, truncation or runtime failures. Report failures and
quality regressions; do not automatically extend training or promote a model.
There is no automatic publishing, model merge, serving change or app adoption.

## Prepared files

Directory:

`/Users/williamwessex/Documents/Writer1/llm/Narratryx/artifacts/clean-source-approved-v1/`

- `prose.approved.jsonl`: approved records and their provenance.
- `train.text.jsonl`: 108 text-only records for a future local run.
- `dataset.validation.json`: source approval, exact span and export checks.
- `approval-export.json`: approval/export identities and hashes.
- `tokenizer-preflight.json`: per-record lengths and tokenizer identity.
- `base-model-pin.json`: cached base revision, weights and config hashes.
- `experiment.json`: run/comparison protocol and execution limits.
- `studio-request.prepared-not-submitted.json`: schema-checked local request.
- `request-preflight.json`: request-schema result; API not called.

Recheck the recorded source approvals with:

```bash
.venv-foundation/bin/python -m foundation validate-ledger \
  rights/clean-sources.approved-v1.jsonl --release --jurisdictions GB US --use training
```

This step recorded the approval and prepared a concrete experiment. **Training
has not started and its launch is not authorized by this source approval.**
Web/PWA, Tauri desktop, Capacitor iOS and native macOS applications remain
unchanged. No application builds or device checks were needed for this isolated
approval, data export and local preflight work.
