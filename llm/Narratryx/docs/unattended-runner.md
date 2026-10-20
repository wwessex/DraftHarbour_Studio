# Offline automation runner

The first automation layer is implemented. It prepares local review material,
checks release gates, exports eligible SFT data and benchmark prompts, scores
imported responses, and prepares blind comparisons. It **does not yet run an
unattended training service**. No scheduler, network client, cloud submission,
automatic literary judge, inference worker, or application integration is added.

## Run on the MacBook

From the repository root:

```bash
cd llm/Narratryx
.venv-foundation/bin/python -m foundation.runner \
  --run-dir artifacts/unattended-preflight-v2
```

The default configuration is `configs/offline-runner.json`. Paths in a configuration
are relative to that configuration file. A first run currently prepares six local
Austen excerpts and twelve draft examples, then reports the existing source,
dataset and benchmark blockers. This is the expected result, not a training failure.
`report.json` explains the gates; `state.json` stores completed-stage hashes.
Exit codes: **0** offline stages completed, **2** release/evaluation gates blocked,
**1** invalid configuration, changed inputs/outputs, or execution error.

Run the same command again to resume. Completed stage files are hash-checked and
reused. An interrupted, uncommitted stage is rebuilt from the unchanged inputs.
Concurrent runs in the same directory are rejected by an OS lock that releases
on process exit. Changed inputs, code, schemas or outputs require a **new run
directory**, preserving the earlier audit trail. Local temporary stage directories
left by a hard process kill can be removed after the process has ended; they are
never treated as completed stages. This is not automatic GPU checkpoint recovery.

## What remains pending

- Austen has approval of a limited source scope; its passage-selection release
  condition remains unresolved. No broader approval is inferred from “keep”.
- The twelve examples and synthetic-teacher terms are not released for training.
  The existing two editorial keeps remain recorded separately and unchanged.
- The benchmark tasks and rubric require review and a frozen hash lock.
- A base model, exact revision, license review, GPU provider, private durable
  storage, pinned software environment, job timeout and spending authorization
  remain unconfigured.

The runner checks only the sources referenced by the selected dataset. Unrelated
candidate books can remain pending. It never changes review status, rights
records, original review packs or previous human decisions. Preparation generates
new pending drafts; it does not replace the dataset path in the configuration.
Point `dataset` to a separately reviewed release when one exists.

## Export and evaluation

After the recorded dataset and frozen benchmark gates pass, `bundle/` contains:

- `train.jsonl`: messages from **train records only**; no validation/test records.
- `provenance.json`: source dataset/ledger hashes and ordered record IDs.
- `prompts.jsonl`: benchmark contexts/instructions without checks or rubrics.
- `unsloth_sft.py` and `job-plan.json`: an exported GPU recipe and its input hashes.

`model` may remain null for offline export. To prepare an executable recipe later,
configure `id`, a full 40-character Hub commit `revision`, `license_url`, and
`license_review` using the existing review structure. This is a recorded review,
not a way to establish legal permission merely by changing a JSON field.
The runner cannot enable paid execution: the schema requires
`paid_execution_enabled: false` and there is no execution switch.

For saved inference outputs, set `baseline` and/or `candidate` to objects with
`responses` and `run` paths. They use the existing `eval-response` and `eval-run`
schemas. The runner checks benchmark hashes, counts absent/error responses as
failures, and writes objective reports. Two complete runs with distinct run IDs
and artifact hashes, matching generation settings and prompt versions produce
`evaluation/review.jsonl` plus a private assignment key. Keep that key private.
Use the Phase 1 `review-report` command to summarize later human ballots.
Imported model identities/hashes are supplied metadata; this offline runner does
not independently attest a remote inference service's identity.

Objective pass rates are not literary judgments. Promotion is always disabled.
There is no automatic publication, upload or replacement of an application model.

## GPU recipe limits and the next implementation stage

The CUDA recipe uses Unsloth LoRA and TRL SFT with assistant-only loss, bounded
steps, periodic local checkpoints, and local Trackio logging. It refuses missing
model-license review, changed training/script hashes, unsupported assistant-mask
templates, examples longer than the configured sequence length, and an existing
output directory. It requires an explicit `--execute` argument when run separately.
The offline runner never calls it. No ML packages are added to the Mac validation
environment, and no model is downloaded by the runner.

The recipe has only CPU-side checks and syntax validation here. Its CUDA training,
model compatibility, dependency versions, throughput and quality remain untested.
Its local checkpoints must be persisted by a separately configured GPU worker;
it is not ready for an ephemeral cloud machine without durable storage. Step
limits do **not** enforce a monetary budget. No budget is charged or enforced in
this offline version because it has no paid execution path.

The next implementation stage is a provider adapter with a reviewed operating
policy: permitted sources/models, optional machine curation and spot-check rules,
private storage, per-job and total cost limits, bounded retries, provider timeout,
durable checkpoints, baseline/candidate inference, and failure notifications.
That adapter needs a GPU smoke test before any claim of unattended training.
It must preserve the existing rights conditions and record machine decisions as
machine decisions. Automatic literary judging would require its own validation.

API references used for the recipe: [Unsloth fine-tuning guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide),
[TRL SFT and assistant-only loss](https://huggingface.co/docs/trl/en/sft_trainer).
The Hugging Face training skill used is
`hugging-face:huggingface-llm-trainer` (local `SKILL.md` in the installed plugin).

## Validation and application isolation

```bash
.venv-foundation/bin/python -m unittest discover -s tests -v
.venv-foundation/bin/python -m compileall -q foundation training
```

Tests use invented temporary approvals, not approvals of real literature. They
exercise blocked releases, resumability, interruption recovery, output tampering,
source changes, concurrent locking, disabled execution, imported scoring and
comparison failures. No external service is contacted by these tests.

All changes are confined to `llm/Narratryx`. Web/PWA, Windows/Linux Tauri,
Capacitor iOS, and separate native macOS application sources/assets/dependencies
are unchanged. No application builds or device tests are needed or claimed for
this independent tooling change. The runner is exercised on macOS; Windows
locking has a code path but has not been runtime-tested on Windows. GPU/cloud
execution is not tested on any platform.
