# Narratryx — independent literary model development

Status reviewed **20 October 2026**. This workspace contains source-rights evidence, traceable datasets, CPU validation, evaluations and experimental model runs for DraftHarbour. It is independent of all application runtimes. It is not a released specialist model, production serving service or prerequisite for ordinary users.

## Current position

- Phase 1 rights/dataset/evaluation tooling is implemented. The foundation suite last ran successfully with **72 tests on 20 October 2026**; this is dated evidence, not a permanent test count.
- Several local Unsloth MLX pilots have completed on the development Mac. They establish that bounded training/inference can run locally, not that literary quality improved.
- The latest craft pilot uses **20 source-only Wharton/Hamilton answers**, 2,443 answer words and 2,850 supervised tokens. Five updates completed in about 30 seconds at reported peak 6.34 GB. Its 16 before/after cases produced 32 complete responses without errors/truncation.
- Mechanical results are mixed. Exact minimal-edit matches remain 2/4; compression word limits improve from 3/4 to 4/4 while continuation word limits fall from 2/4 to 1/4. These are not literary-quality ratings. No blinded human quality ballots have been completed; no adapter has been promoted.
- Substantive verified author-revision pairs remain unfinished. Hamilton edition comparison found publication-reference updates, not useful fiction-editing demonstrations.
- Opt-in experimental setup is implemented in every maintained application. The separate local service verified exact model/adapter hashes, authenticated base/candidate completions and the actual shared provider path. Target-device acceptance and hosted deployment remain separate. No app startup imports this training workspace.

Start with the [latest pilot report](docs/craft-source-pilot-2026-10-20.md), [scoped rights dossier](rights/dossiers/craft-expansion-2026-10-20.md), [integration readiness assessment](../../docs/narratryx-integration-readiness-2026-10-20.md) and [original feasibility assessment](docs/feasibility-and-implementation-plan-2026-10-17.md).

## CPU foundation setup

From the repository root:

```bash
cd llm/Narratryx
python3 -m venv .venv-foundation
.venv-foundation/bin/python -m pip install -r requirements-foundation.txt
.venv-foundation/bin/python -m unittest discover -s tests -v
.venv-foundation/bin/python -m foundation validate-ledger rights/ledger.jsonl
```

These install/run CPU validation only; they do not install Unsloth/MLX, download literature, infer or train. The last command checks ledger structure; it does not grant rights or make every record release-ready. The original ledger and formal benchmark retain pending items; scoped later records do not silently overwrite them.

To inspect the latest training records against their specific ledger, run this lower-level provenance check from `llm/Narratryx`:

```bash
.venv-foundation/bin/python - <<'PY'
from pathlib import Path
from foundation.validation import validate_dataset
records = validate_dataset(
    Path('artifacts/craft-expansion-v1/train.records.jsonl'),
    Path('rights/craft-expansion-v1.scoped.jsonl'),
    ['GB', 'US'],
)
print(f'{len(records)} records passed provenance validation')
PY
```

This is not the formal CLI release check: `foundation validate-dataset` additionally requires `--benchmark`, `--lock` and `--output`, with a reviewed matching rubric. The sourced-context craft diagnostic does not satisfy the original-synthetic benchmark schema and must not be passed off as its reviewed replacement.

Artifacts are local generated inputs/outputs and may be absent in a fresh clone. Builders under `curation/` depend on exact local source/input artifacts; they are not a corpus downloader or a universal one-command reproduction environment. Do not substitute another text/version merely to make a hash check pass.

For the separate draft formal benchmark:

```bash
.venv-foundation/bin/python -m foundation export-prompts \
  --tasks evaluation/tasks.draft.jsonl --allow-draft \
  --output artifacts/draft-prompts.jsonl
```

This is an explicit draft export, not a reviewed benchmark freeze. Read the [Phase 1 guide](docs/phase1-foundation.md) for release validation, locks, imported-response scoring and human comparisons.

## Sources and provenance

The current training scope is **permission-free, verified historical source prose within recorded GB/US limits**. Public-domain status must be assessed for the exact included edition/material/contributors and source terms, not inferred for an entire Hugging Face dataset. `PleIAs/English-PD` remains a discovery/candidate resource; selecting it in Studio does not clear all its rows for training.

Raw source bytes/notices, acquisition hashes, exact Unicode spans and transformations remain in the rights/artifact records. Clearance is limited to the recorded use: the latest Mansfield/Chesnutt contexts are **evaluation-only**, not training data. Physical-print-copy uncertainty is disclosed rather than replaced with invented edition claims. AI evidence assessments are labelled AI; existing human decisions are recorded separately. Structural validation is not legal certification.

Generated literary teaching examples remain excluded under the user's current restriction, including unresolved Austen/remediation teacher-output candidates. Questions/instructions are distinct from source-derived answer targets; the recent pilots train explicit source-answer labels with prompts masked. Do not invent human approval, synthetic-teacher permission, or an author-revision pair to fill a dataset category.

Austen's limited six-passage scope has later recorded approval and evaluation use; historical pending dossiers/runner configurations do not become globally approved as a result. The original candidate ledgers and formal 120-task benchmark are preserved separately.

## Experiment history

| Work | What happened | Evidence |
|---|---|---|
| Early English-PD subset/pilot | Candidate triage and a bounded local smoke test; no broad corpus clearance | [Subset report](docs/english-pd-fiction-subset-2026-10-18.md) |
| Opie/Wray prose v1 | 108 scoped paragraphs; fresh-base 27-update pilot | [Report](docs/clean-source-training-v1.md) |
| Opie/Wray prose v2 | Fresh-base 54-update pilot; 14 diagnostic cases, mixed mechanical results | [Report](docs/clean-source-training-v2.md) |
| Source-task pilot | 324 source-derived training tasks, 81 updates, 18 held-out Austen tasks; punctuation-related restoration gain, weak quotation/continuation | [Report](docs/source-task-experiment-v1.md) |
| Craft-source pilot | 20 attributed craft answers, five updates, 16 fresh-author cases, mixed mechanical results | [Report](docs/craft-source-pilot-2026-10-20.md) |

The craft data lives in `artifacts/craft-expansion-v1`. Its primary model/comparison run is **`artifacts/craft-training-v2`**. `craft-training-v1` is a preserved exploratory baseline whose dialogue prompt omitted a scored cap; it was superseded **before any training**. The correction/rerun is documented in the frozen amended protocol. Do not confuse these run numbers with the earlier raw-prose v1/v2 adapters.

## Review and next work

The local [blinded packet](artifacts/craft-training-v2/BLIND-REVIEW.md) includes source facts/unknowns and randomized A/B outputs; [blank ballots](artifacts/craft-training-v2/human-ballots.blank.jsonl) contain no assigned ratings. Keep the answer key separate until reviews are submitted. Obtain two independent reviewers on a representative subset and adjudicate disagreements before quality/promotion claims.

Continuation tasks allow new plausible fiction instead of requiring the published next paragraph. Editing has no minimum length. Word caps, exact minimal-repair matches and request completion are mechanical checks, not proxies for coherence, voice, dialogue or pacing quality. The craft diagnostic has sourced contexts and a separate protocol; it is not mislabelled as the formal original-synthetic benchmark.

Prioritize verified substantive revision pairs and demonstrations of the target tasks before scaling training. Twenty craft explanations do not supervise all desired fiction/editing behaviors. Repeating small runs without better data/evidence is not a quality strategy.

## Automation and execution boundaries

[The offline runner](docs/unattended-runner.md) prepares review material, checks gates, exports eligible data/recipes and scores imported responses. It does **not** launch a scheduled/unattended training service, inference worker, paid cloud job or automatic literary judge. Its original default configuration can still report unresolved gates even though separate scoped local experiments have completed. Use a fresh run directory when inputs/code change; do not overwrite frozen evidence.

The completed local experiments used a separately installed Unsloth MLX environment, cached model revision and explicit bounded scripts. That path is distinct from the runner's exported CUDA/TRL recipe. `requirements-foundation.txt` supplies neither training nor serving dependencies. Do not describe the default runner as automatically training on the Mac or cloud.

`runtime/cloud/`, older YAML configs and `scripts/` contain legacy experiments. Their presence is not a validated serving/deployment path for the current MLX adapter. vLLM/Modal workflows do not automatically consume an Apple MLX LoRA. Validate model format, licensing, authentication, limits, persistence and costs before any new authorized deployment.

## Application integration

Use the separate `runtime/local/` service through existing app providers, with explicit `narratryx-craft-v1` / `narratryx-base` selection and rollback. See the [current app trial guide](../../docs/narratryx-app-trial.md) for the exact manifest, installed inference environment, startup, token handling and validation limits. Foundation requirements do not install serving dependencies. The authenticated local service is separate from Studio's UI on port 8888 and defaults to port 8890. Keep model development/storage outside manuscript formats and app startup.

An optional hosted inference service is the intended accessible path for ordinary Windows/Mac users. They must not need training libraries, a local GPU or an MLX-compatible computer. Local inference is optional. No paid hosting, model publication, app-default change or promotion has been performed by the current pilot or documentation update.

## Workspace map

- `foundation/`, `schemas/`, `tests/`: CPU provenance, schema, split, benchmark and response tooling.
- `rights/`: ledgers, dossiers, approvals, retained raw material and evidence; statuses are scoped.
- `curation/`, `evaluation/`, `training/`: dataset/task preparation and supporting workflows.
- `artifacts/`: ignored local checkpoints, inputs, reports, protocols and response/review packs; not shipped app assets.
- `runtime/local/`, `configs/narratryx-craft-v1.json`: optional authenticated, pinned MLX developer serving; separate from CPU tooling/apps.
- Other `configs/`, `scripts/`, `runtime/cloud/`: historical/configured workflows requiring their own validation.
- `docs/`: dated findings and guides. Historical pending states must be read alongside newer scoped decisions, not rewritten as if earlier review had happened.
