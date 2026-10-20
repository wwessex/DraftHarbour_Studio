# Literary model development: feasibility and implementation plan

Assessment date: 17 October 2026. Status: research and proposed implementation; no model trained, corpus cleared, cloud job submitted, or application integration changed by this assessment.

## Recommendation

Proceed with a small, independently evaluated Unsloth fine-tuning experiment alongside application development. Start with supervised fine-tuning (SFT) of an existing instruction model using LoRA/QLoRA adapters. Do not train a foundation model from scratch. Success means demonstrably better assistance on defined writing tasks, not a promise of superior novels or book-length reasoning.

Use the M5 MacBook Air with 16GB RAM for rights-record management, text processing, example authoring, evaluation review, and optional small quantized-model inference. Use a single cloud GPU for the repeatable training experiment. Unsloth's current Mac installation documentation advertises MLX training and inference; its requirements page still distinguishes the CUDA-oriented Core path and contains inconsistent Apple-support wording. Treat exact Mac/model/backend compatibility as a smoke-test question, not a guarantee that the CUDA training recipe runs unchanged on Apple Silicon. No installation or local training was attempted here. [Mac installation](https://unsloth.ai/docs/get-started/install/mac), [requirements](https://unsloth.ai/docs/get-started/fine-tuning-for-beginners/unsloth-requirements).

For ordinary Windows and Mac users, make hosted inference the broadly available AI route, with an optional small local model for suitable machines. Writing, saving, importing, exporting, and project recovery must continue without AI, network access, accounts for training services, or model downloads. Hosted AI has operating costs and needs a pricing/quota policy; universally free, powerful offline AI is not an achievable hardware-independent promise.

## Existing groundwork and readiness gaps

The repository already separates model work into `llm/Narratryx/`. Reuse that boundary and the existing provider interfaces. The existing README describes intended capabilities more confidently than the inspected implementation warrants. Findings below are source findings, not results from running GPU workloads.

| Area inspected | Finding | Required before use |
| --- | --- | --- |
| `scripts/build_datasets.py` | Loads PG-19 and NeuralNovel/Neural-Story-v1 without per-work jurisdiction/edition clearance. Generated rows retain little provenance. | Replace automatic inclusion with an approved-source manifest. Existing data remains unapproved for this initiative until audited. |
| `scripts/prepare_narratryx_data.py` | Chunks by characters; normalizes whitespace; removes Gutenberg references without a rights decision. | Preserve paragraph/dialogue structure, retain originals and notices, verify source terms first, then tokenize and segment by scene. |
| SFT data conversion | Hardcodes Qwen2.5 chat tokens; `_as_instruction` does not incorporate a separate `input` field. | Store model-neutral messages and explicit context; apply the selected tokenizer template at training time. Audit mappings before reusing local examples. |
| Preference generation | Removes descriptive words and replaces dialogue tags to manufacture rejected answers. | Do not treat these as literary preferences: concise prose and “said” can be preferable. Use reviewed, task-specific comparisons. |
| `scripts/run_training.py` | Unsloth branch invokes `python -m unsloth_cli`; dependencies do not establish this entry point. | Build a supported Unsloth Python recipe and verify it in a pinned GPU environment. Printing a command is not training validation. |
| Training YAML | Axolotl-shaped configs, small random validation split, and stage changes expressed as checkpoint resumes. | Separate trainer formats; split by work/author; explicitly load prior adapters or merged weights. Cross-stage optimizer resume is not a substitute for weight transfer. |
| `src/lib/ai/evalFramework.ts` and self-improvement scripts | Keyword, length, sensory-word and surface-form scoring. | Retain as limited smoke checks; replace literary release decisions with blind editorial evaluation and measurable task checks. No automatic self-training loop. |
| `runtime/cloud/api.py` | Authentication is optional; wildcard CORS by default; streaming uses an ordinary `Response` with an async iterator and a client scope that ends before consumption. | Repair and test streaming/client lifetime, enforce authentication and limits, restrict origins, and review privacy before deployment. |
| `runtime/cloud/modal_app.py` | Returns a vLLM app without demonstrated engine initialization; SDK and server APIs are not pinned. | Rebuild against a verified serving example, initialize an engine, load actual artifacts, and test cold starts and authentication. Deployment readiness is unproven. |
| `scripts/export_model.py` | Assumes external converter/quantizer commands and an HF model directory. | Pin tool revisions, merge adapters appropriately, verify tokenizer/template, and compare exported outputs. An adapter directory is not necessarily an exportable full model. |

PG-19's maintainers explicitly warn about dated language and historical biases. Its dataset metadata and publication cutoff are useful discovery aids, not a substitute for the proposed UK/US edition-level clearance. [PG-19 primary repository](https://github.com/google-deepmind/pg19).

## Public-domain sourcing and legal evidence

“Legally verified” must be a release condition supported by evidence, not a label inferred from a download site or an AI answer. Establish the operating/training jurisdictions and initial distribution markets first. For this UK-based development workflow, initially check UK and US rights, plus the actual cloud-processing country; add other markets before distributing there. Moving training to the US does not clear UK processing or worldwide distribution.

UK guidance generally gives literary works life plus 70 years and separately protects published-edition layout. US terms differ by publication and other circumstances. Modern translations, introductions, annotations, illustrations, and previously unpublished material require separate checks. A work's title or original publication year alone is insufficient. [UK IPO guidance](https://www.gov.uk/copyright/how-long-copyright-lasts), [US Copyright Office Circular 15A](https://www.copyright.gov/circs/circ15a.pdf).

Gutenberg primarily establishes US status and explicitly does not assure rights elsewhere. Its collection also includes some works made available by permission. Preserve source files, notices and terms; decide the permitted extraction/redistribution route before stripping wrappers. Removing a trademark string does not establish permission. [Gutenberg license](https://www.gutenberg.org/policy/license.html).

Proposed rights manifest, one record per exact source edition:

- Work ID, title, authors and their dates, original publication evidence, edition date and publisher; translators/editors and their dates where applicable.
- Exact source URL, retrieval date, source revision, raw-file SHA-256, included chapter/page boundaries, and excluded added material.
- Separate legal basis and evidence links for each relevant jurisdiction; distinguish source access terms, literary-text status, and compilation/database terms.
- Reviewer identity, review date, decision (`pending`, `approved`, `rejected`, `needs-specialist-review`), approved uses/territories, unresolved issues, and applicable notices.
- Transformation history and all downstream sample IDs so a withdrawal can trigger dataset rebuild and model retraining/release replacement.

Automate completeness checks and reject any build with missing approval, scope, evidence, or hash. Codex can collect evidence and flag cases; a named human reviewer must own clearance, with specialist review for ambiguous works. This assessment does not certify any downloaded edition.

Start a **candidate** ledger with [Pride and Prejudice](https://www.gutenberg.org/ebooks/1342), [Frankenstein](https://www.gutenberg.org/ebooks/84), and [The Yellow Wallpaper](https://www.gutenberg.org/ebooks/1952). These are source-discovery examples, not approved training records. Verify the specific edition and contributors before ingestion; then expand to 20–50 diverse works for a manageable pilot. No literature corpus needs downloading until that process is in place.

Keep three rights tracks separate: source literature; our authored/commissioned/synthetic examples and any teacher-model terms; base-model and software licenses. Fine-tuning on cleared texts does **not** establish that the underlying pretrained model used only public-domain training material. If that stronger guarantee is required, it is a separate and substantially harder base-model selection requirement.

## Dataset design

Use public-domain literature as evidence and selected examples of craft, alongside newly constructed instruction examples that teach the requested behavior. Raw novels alone do not teach editing instructions or reliable analysis. Preserve original wording for source passages; label modern rewrites as new derivatives. Keep genre, voice, era, dialect, point of view and author representation balanced, with caps on any one work/author. Include restrained prose and contemporary original scenarios so the assistant does not default to ornate nineteenth-century imitation.

Initial target: 300–500 editor-reviewed examples to validate the process, then 2,000–5,000 SFT examples if the pilot warrants expansion. Counts are planning targets, not quality guarantees. Suggested balanced task families:

| Skill | Constructed example | Review criterion |
| --- | --- | --- |
| Fiction writing | Continue a supplied scene under explicit POV, tense, length and plot constraints. | Preserves facts/voice while advancing action; does not reproduce the source's next paragraph. |
| Editing | Make a minimal correction; return revised text plus a concise change list. Include already-good passages requiring no edit. | Fixes the requested problem without changing meaning, dialect, or deliberate style. |
| Narrative analysis | Identify scene goal, conflict, turn and consequence; quote short supporting spans from the supplied text. | Distinguishes evidence from interpretation and states uncertainty. |
| Dialogue | Rewrite an exchange so one speaker conceals a motive, without naming it. | Distinct voices, subtext and continuity; avoids exposition disguised as conversation. |
| Pacing | Produce faster and slower versions of the same beat while preserving events. | Changes emphasis and rhythm intentionally; shorter is not automatically better. |
| Storytelling | Propose alternate scene sequences and explain setup/payoff and character consequences. | Causal structure and character agency; no invented canon presented as fact. |

Illustrative original training seed, constructed for this plan (pending editorial review):

> Task: Remove the adverb only. Keep every other word and all punctuation.
>
> Input: Mara quietly closed the door.
>
> Target: Mara closed the door.

Pair that with a “keep the sentence unchanged” instruction and unchanged target. This teaches instruction sensitivity rather than an absolute rule against adverbs. More demanding examples should include a text, specific intent, a reviewed target, and a short evidence-based rationale where requested. Do not manufacture hidden reasoning traces.

Proposed JSONL record fields: `id`, `task`, `messages`, `source_work_ids`, `source_spans`, `rights_record_ids`, `origin` (human/synthetic/derived), `teacher_model_and_terms`, `review_status`, `rubric`, `split_group`, `content_hash`, `dataset_version`. Retain raw text and transformation offsets outside training messages. Metadata must not accidentally become model output. Preference records additionally need the same prompt, two credible answers, reviewed preference, reason, and adjudication status.

Pipeline: approve sources → retrieve/check hashes → extract/clean → exact and near-duplicate detection → assign grouped splits → create examples within each split → editorial review → tokenize and validate → immutable release manifest. Group all editions/translations and derived variants of a work; preferably hold out entire authors. Never place overlapping chunks or a rewritten version in another split. Freeze the test set before generating training examples; keep separate validation data for tuning. Public classics may already be present in base-model pretraining, so also use newly authored private test scenarios and acknowledge that pretraining contamination cannot be ruled out.

Use synthetic assistance to draft tasks and candidate revisions, not to approve its own answers. Record the teacher and permission to use its outputs for training. Exclude unlicensed contemporary books, scraped reviews, private manuscripts, and user projects by default. A future opt-in contribution program needs a separate explicit rights/privacy process.

## Training experiment

Use `Qwen/Qwen2.5-7B-Instruct` as a reproducible control matching existing configs and `Qwen/Qwen3-8B` as a comparison candidate, not a claim that either is currently the best fiction model. Both model cards list Apache-2.0; review actual pinned license files and notices before release. Benchmark before choosing; allow a newer compatible candidate to replace either through the same gates. Explicitly configure reasoning mode and prevent reasoning-channel leakage for models that support it. [Qwen2.5 card](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct), [Qwen3 card](https://huggingface.co/Qwen/Qwen3-8B).

Proposed first recipe: single 24GB NVIDIA GPU, 4-bit QLoRA, 2,048–4,096-token sequences, microbatch 1, gradient accumulation 8–16, LoRA rank 16–32, learning rate trial around 1e-4, one epoch then inspect validation. These are starting settings requiring measurement, not a tested recipe. Mask prompt tokens for assistant-only loss, verify nonempty labels and EOS boundaries, reject harmful truncation, and check that context fits with the target. Inspect rendered examples and token masks before spending on a run. Use the supported Unsloth API/TRL path, not the current undocumented launcher. [Unsloth fine-tuning guide](https://unsloth.ai/docs/get-started/fine-tuning-llms-guide.md).

Compare the unchanged model with the same prompts/context, improved prompting alone, and SFT with identical inference settings. Add story-bible retrieval as a separate ablation. Continued pretraining on raw prose is optional only if analysis shows a gap SFT does not solve; test whether it damages modern language or instruction following. DPO comes later, only with credible human-reviewed preferences. Defer RL/GRPO: literary rewards are hard to specify and surface heuristics are easy to exploit.

Before each run, pin base/tokenizer revisions, Unsloth/PyTorch/Transformers/TRL/PEFT versions and container digest; record dataset hashes, seed, config, GPU/driver, token counts, logs, peak memory, wall time and cost. Persist adapters, tokenizer, evaluation outputs and checkpoints to private durable storage while the job runs. Smoke-test 20–50 optimization steps, save/reload, and compare a generated sample before the longer job. On stage changes, load the preceding model/adapter deliberately and initialize the new trainer as appropriate.

## Cloud options and budget

Hugging Face Jobs is a good initial batch-training option because jobs and artifacts can be scripted. Colab/Kaggle notebooks are useful for exploration but variable availability/session limits make them weaker release infrastructure. A rented GPU container is an alternative when more control is needed. Choose one provider for the first reproducible path rather than maintaining several runners. Keep inference hosting as a separate decision.

At the checked HF Jobs rates: L4 24GB is $0.80/hour, A10G 24GB small is $1/hour, L40S 48GB is $1.80/hour and A100 80GB is $2.50/hour. Jobs require a positive credit balance according to current documentation; an older skill prerequisite describing a mandatory paid subscription is superseded by that documentation. Recheck rates, availability and processing region before launch. [HF Jobs pricing](https://huggingface.co/docs/hub/en/jobs-pricing).

Proposed pilot allowance: 10–30 L4/A10G GPU hours, approximately $8–$30 in compute at those rates. This is an allocation, **not** a runtime forecast; benchmark actual tokens/second first. Reserve a total $50–$150 experiment envelope for retries, evaluation/teacher usage, storage and transfers. Human literary review and legal work are separate costs. No paid job is authorized or launched by this assessment; choose a spending cap and billing account when moving to execution. Enforce per-job timeouts, limited retries/concurrency and pre-run worst-case cost checks; a timeout alone is not an account-wide budget cap.

Serving costs can dominate training: at the same illustrative $0.80/hour, an always-running GPU would be about $584 for 730 hours before other charges. That is arithmetic, not a production hosting quote. Measure cold starts, concurrency and cost per accepted editing/generation task; compare scale-to-zero hosting against an existing provider. A custom adapter generally needs a host that explicitly loads it or a merged model; generic inference-provider access does not automatically serve arbitrary fine-tunes.

## Evaluation and promotion

Create 120 held-out tasks, 20 per skill above, plus a separate regression set for formatting, safe edit application, context limits, offline behavior and export compatibility. Use original private scenarios and held-out cleared passages. Test short, medium and multi-scene contexts; do not equate a model's advertised context window with reliable whole-novel understanding. Train craft behavior; retrieve current project facts at inference time.

Automated evaluation should check exact edit constraints, preserved named facts, requested length/format, grounded quotations, repetition, memorized-source overlap, inappropriate disclosure of hidden notes, and broken or empty responses. Report task-specific failure rates, latency to first token/completion, tokens/second, memory and cost. Use source overlap to flag copying for review; it is not a legal originality certificate.

Literary quality needs blind paired judgments, randomized answer order, a 1–5 anchored rubric for coherence, voice preservation, dialogue, pacing, usefulness and originality, and at least two reviewers on a representative subset with adjudication. A separate LLM judge can triage and assist with comparisons, but calibrate it against humans, reverse response order, and track verbosity/self-preference bias. Perplexity, word diversity, and adjective counts do not establish storytelling quality.

Proposed promotion gates, to freeze before training: all included records approved; no detected train/test near-duplicate groups; at least 95% on objectively checkable constraints; human paired win rate over the unchanged selected base above 55%, with a bootstrap confidence interval excluding 50% (ties count half; resample by scenario); no material per-skill regression hidden by the average; no critical privacy/edit-application regressions; latency and cost within agreed product budgets. Increase sample size if uncertainty is too wide. Compare against the app's existing provider too; beating a small base does not establish competitiveness. A failed gate means revise data or retain the existing model.

Evaluate the exact deployed artifact again after merging, quantization or runtime/template changes. Publish an internal model card with training scope, rights evidence, known biases, limitations, benchmark settings and results. Do not claim that passing these tests eliminates hallucinations or guarantees long-form consistency.

## Replaceable integration architecture

```text
Independent model workspace
  cleared sources → reviewed datasets → cloud training → frozen evaluation
                                                     ↓ approved versioned artifacts
Web/PWA ───────────────┐
Windows/Linux Tauri ──┤ existing provider adapters
Capacitor iOS ────────┤       ↓
Native macOS ─────────┘ authenticated inference gateway → model/runtime registry
                                     ↓                       ↓
                            existing-provider fallback   hosted model or optional local model
```

Training packages, raw books and model weights must not enter application bundles or core build dependencies. Keep project files model-neutral; store story-bible facts and accepted edits as portable application data. Use versioned prompts, context construction and capability metadata outside model weights. A model registry should record immutable base/adapter/tokenizer/template/quantization revisions, context/output limits, supported tasks, deployment status and rollback target. Adapters are base-specific; replacing the base may require retraining. Interchangeable means a stable service contract and repeatable evaluation, not binary compatibility of adapters.

Reuse OpenAI-compatible chat completions for experimental calls and retain the app's managed-broker envelope where already used. The React managed path calls `/api/ai/generate`; the PHP proxy and custom-LLM routes are separate paths. Native macOS has its own `AIProvider` protocol, factory, prompts and structured-edit handling. A new gateway therefore needs explicit adapters/contract tests rather than a URL substitution assumed to cover every client. Ensure plain-text answers and optional structured edit proposals preserve each client's contract. The native provider inspected here is non-streaming; streaming parity requires separate implementation if the product requires it.

Production requirements: TLS, short-lived user authorization, server-held provider credentials, model allowlists, request/token limits and quotas, cancellation, bounded retries, streaming disconnect cleanup, health checks, and explicit rollback. Show users when text leaves their device; send only needed context, redact content from operational logs, define retention/region policy, and do not reuse manuscripts for training by default. Treat manuscript text as untrusted data. Model output proposes edits; existing user acceptance, stale-text checks and revision history must remain authoritative. Provider fallback must respect consent and local-only policy rather than silently upload text.

## Platform parity and validation plan

| Version | Inspected now | Checks required when integration begins |
| --- | --- | --- |
| Web/PWA | React provider types/factory, managed/custom endpoint paths, evaluation and fallback code | Provider contracts, browser CORS/CSP, cancellation, offline writing/save/export, feature-off behavior, no weights in cache by default. |
| Windows/Linux desktop | Tauri shell/config confirms shared React frontend; native host still needs platform checks | OS credential storage, network permissions, updater/package behavior, same AI failures and edit acceptance; real Windows/Linux CI and runtime smoke tests. |
| Capacitor iOS | Wrapper config uses built `dist` assets | WKWebView origins, HTTPS/ATS, backgrounding/cancellation, credential handling, offline editing; sync assets only when shared implementation changes and validate Xcode/device behavior. |
| Native macOS | Separate Swift provider, factory, chat/context/edit workflow, and AI test sources | HTTP contract, secret storage, context limits, model changes, structured edits/stale-text handling, local-only and offline behavior; native tests and a macOS app smoke run. |

This assessment changes documentation only. No asset sync or application dependency change is needed. Scoped existing React AI tests and native Swift AI/parity tests are used as regression evidence; their actual results are recorded below. They cannot validate a future inference service. No Windows/Linux packaging, iOS simulator/device, native GUI, live model, cloud GPU, or quantized-artifact runtime checks were performed in this research phase.

## Implementation sequence and automation boundaries

| Stage | Deliverable and exit condition | Codex can automate | Human decision/review |
| --- | --- | --- | --- |
| 0 — feasibility (this document) | Source audit, platform map, costs, independent architecture | Inspection, documentation research, existing regression checks | Confirm product priorities when execution begins. |
| 1 — rights and evaluation foundation | Approved-source ledger, validation schema, freeze 120 test tasks and baseline protocol | Metadata collection, hash tracking, fail-closed validator, split/dedup reports, task drafts | Edition/jurisdiction clearance; literary rubric and benchmark approval. |
| 2 — reviewed pilot data | 300–500 examples; full provenance and editorial acceptance | Cleaning, task generation, corruption checks, review queues, versioned JSONL/data card | Review targets, teacher permissions, balance and quality. |
| 3 — reproducible training | Pinned Unsloth script/container, successful smoke/save/reload, then capped SFT run | Prepare/submit cloud job, checkpoints, logs, measured cost and resumability | Billing account/cap, credentials, base-model/license selection. |
| 4 — independent comparison | Base/prompt-only/SFT/retrieval ablations; promotion report | Run benchmarks, objective scoring, anonymized comparisons and statistical summaries | Blind literary judgments and model promotion. |
| 5 — staging inference | Authenticated contract-tested service, rollback and cost measurement | Package/serve approved artifact, gateway repairs, contract/load tests | Privacy/retention and serving economics. |
| 6 — optional app integration | Feature-flagged provider in every maintained runtime, core offline regressions pass | React and Swift adapters, native synchronization where relevant, CI and smoke tooling | Product rollout after parity and real-device evidence. |

Stages 1–4 can proceed before the application is finished. A useful first experiment may fit roughly 2–4 weeks of part-time work after reviewers and compute are available; that is a planning estimate, with rights research and human review likely to dominate. Do not put model readiness on the critical path for shipping the writing app. The next concrete implementation is the rights validator and frozen evaluation pack, not a bulk download or an automatic self-improvement job.

## Validation results for this assessment

- Documentation checks passed: README link target exists, code fences are balanced, both edited files have terminal newlines and no trailing whitespace; `git diff --check` passed for the tracked README change.
- Attempted React regression command: `npm run test -- src/lib/ai/openaiProvider.test.ts src/lib/ai/customLlmProvider.test.ts src/lib/ai/providerManager.test.ts src/lib/ai/fallbackProvider.test.ts src/lib/ai/evalFramework.test.ts src/lib/ai/pipelines.test.ts src/lib/ai/serverProxyProvider.test.ts`. Vitest stalled during startup without reporting test execution for several minutes and was terminated. No passing or failing test count is claimed; the startup cause remains unresolved.
- Attempted native regression command: `swift test --package-path macos --filter 'AIChatTests|AIAndSyncParityTests'`. Build failed before tests: the selected `/Library/Developer/CommandLineTools` toolchain could not resolve `XCTest` and lacked the `SwiftUIMacros` plugin. No Xcode app was found at the standard `/Applications/Xcode*.app` location. Native AI/parity tests therefore did not run; a complete compatible Xcode installation/toolchain is required for this check.
- Source inspection covered web/PWA, Windows/Linux Tauri, Capacitor iOS, and the independent native macOS implementation. It is not runtime or device validation. No platform builds or native-asset synchronization were required by these documentation-only changes.
- No training, legal-clearance certification, live endpoint, or model-quality results exist yet. Application source, dependencies, configuration and generated native assets were not edited by this assessment; pre-existing untracked files were left alone.
