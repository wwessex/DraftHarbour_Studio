# Public-domain source-task experiment — 20 October 2026

This experiment replaces generated literary targets with mechanically derived
answers copied from already approved public-domain prose. The user's instruction
was “proceed with that”: prepare task-specific source material, reserve different
authors/books for evaluation, run one small experiment, and keep the application
unchanged.

## Data, rights and source traceability

- **Training:** 324 tasks, three per approved paragraph, from 54 Opie and 54 Wray
  paragraphs. The exact 108 source selections and GB/US scope were approved in
  `rights/approvals/clean-source-expansion-human-approval-2026-10-18.json`.
- **Evaluation:** 18 tasks from the six exact Austen passages accepted in
  `rights/approvals/austen-six-passage-selection-2026-10-18.json`. The same
  paragraphs, author and work do not appear in this project's training runs.
- All assistant targets are verbatim slices of the approved text after its
  previously recorded whitespace transformation. No teacher-model generation,
  synthetic literary answers, benchmark scenarios or new books were used.
- Source originals, approved ledgers and human decisions remain unchanged.
  `rights/source-tasks-v1.scoped.jsonl` is a separate three-source ledger. Its
  Austen record records the existing six-passage decision, resolving the old
  selection-pending condition only for those spans. Austen is evaluation-only
  in this ledger. No new human approval is fabricated.
- Task-record acceptance is an explicitly attributed **AI deterministic
  derivation audit**, authorised by the current request. It is not a human
  literary-quality review. The teacher field is null and origin is `derived`.

Each record has a source ID, exact raw source span, target span within the
transformed excerpt, target hash and source-approval reference. Opie/Wray's
original approval coordinates preserve CRLF; the build verifies those first,
then maps them to the universal-newline view used by the foundation validator.
Austen's accepted coordinates already use that view. These coordinate systems
are recorded separately, not silently interchanged.

All 342 records pass the existing foundation dataset validation, including
source hashes, approved scoped rights evidence, exact source spans, message
hashes, and split boundaries by author/work/group and lexical overlap. The
original 120-task draft benchmark and generated review material remain intact.

## Tasks and limitations

| Task | Construction | What its score can establish |
| --- | --- | --- |
| Restoration | Duplicate one word mechanically; target is the original passage | Constrained correction and source fidelity |
| Exact quotation | Request eight words at specified positions; target is the exact source substring | Position-following and literal extraction, not interpretive analysis |
| Continuation | Supply the beginning of a paragraph; target is its original remaining text | Reproduction of a canonical continuation, not uniquely correct creative writing |

The framework's broad task labels (`editing`, `analysis`, `fiction`) retain
schema compatibility. They do not expand the three narrow proxy tasks into
claims about all editing, narrative analysis or fiction-writing abilities.
No dialogue, pacing or causal-planning improvement is established by this test.

Austen is held out from **project fine-tuning**, not proven absent from the base
model's pretraining. These famous passages may reward memorisation. Other
continuations may be good fiction while scoring poorly against a canonical
reference. Six related excerpts and 18 correlated tasks are a small diagnostic
set, not a broad independent literary benchmark.

## Frozen training and comparison plan

Before training, `protocol.frozen.json` pinned the training tokens, task records,
trace file, held-out test cases, tokenizer audit and configuration hashes. The
held-out examples are not supplied to the training worker or used for checkpoint
selection. The one bounded final adapter is evaluated without tuning against
its results.

The cached `mlx-community/Qwen3.5-4B-MLX-8bit` base remains pinned to revision
`5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d`. A fresh rank-8, alpha-16 LoRA adapter
uses one pass, 81 updates, batch 1, accumulation 4, LR `1e-5`, linear decay,
three warmup steps and seed 42. The cached 8-bit base is preserved. Maximum
sequence length is 1,024; the longest prepared sequence is 659 tokens, so no
training truncation is required. Internal random evaluation splits are disabled.

The training file is pretokenised with explicit labels. Every user/prompt token
has label `-100`. Only the copied source answer plus one structural EOS token
receives training loss. All 324 decoded answer-token spans match their source
targets, and the installed MLX label reader preserves the explicit masks on all
324 records. No automatic masking fallback or prompt supervision is accepted.

The run completed all **81 steps in 382.1 seconds**, with peak MLX allocation
**7.39 GB** and no training warnings. All losses were finite. The worker reports
20,204 supervised tokens: 19,880 copied source tokens plus 324 end markers,
matching the prepared labels exactly. The final optimizer-step loss is 2.7691;
the worker aggregate is 1.0012. These masked losses use a different objective
from the raw-prose experiments and must not be compared directly with their
training losses. The unchanged base and training-input hashes were rechecked.

Three conditions are compared on the same 18 held-out tasks:

1. Unchanged base, with adapters disabled.
2. Previously saved two-pass raw-prose adapter.
3. New source-task adapter.

The comparison uses separate one-message requests, no earlier assistant turns,
no system prompt or tools, no prompt cache, temperature 0, seed 42, disabled
thinking and a maximum of 384 output tokens. Base/new order alternates by case;
the raw-prose adapter runs in a separate stage after unloading the first model.
Only one model is loaded at a time; no inference-speed comparison is claimed.

Predeclared scores are exact raw-response match, whitespace-normalised exact
match and mean word-token multiset F1. Whitespace normalisation changes only
spacing, not spelling or punctuation. No model judge, human preference vote or
aggregate literary-quality grade is manufactured. The configurations differ in
training objective, examples and step count; a difference is not a controlled
causal estimate of the objective alone.

## Completed held-out results

All **54 requests completed without errors or truncation**, with zero cached
prompt tokens. The three conditions use the same prompts and predeclared
generation settings. Models were unloaded afterwards and adapter/base hashes
remained unchanged.

| Source-fidelity measure | Base | Raw-prose v2 | Source-task adapter |
| --- | --- | --- | --- |
| Exact matches, all tasks | 4/18 | 4/18 | 6/18 |
| Whitespace-normalised exact matches | 4/18 | 4/18 | 6/18 |
| Exact restoration | 4/6 | 4/6 | 6/6 |
| Exact positional quotation | 0/6 | 0/6 | 0/6 |
| Exact canonical continuation | 0/6 | 0/6 | 0/6 |
| Mean word-token F1, all tasks | 0.478 | 0.476 | 0.434 |
| Mean word-token F1, restoration | 0.999 | 0.999 | 1.000 |
| Mean word-token F1, quotation | 0.256 | 0.256 | 0.140 |
| Mean word-token F1, continuation | 0.179 | 0.174 | 0.162 |

The two additional exact restorations preserve the source's curly quotation
marks in the Charlotte passage and curly quotation/apostrophe characters in the
Darcy pause passage. The base and raw-prose adapter corrected the duplicated
word but also replaced those characters with straight punctuation. The new
adapter performed the requested correction without that extra change.
This is a narrow punctuation-preservation improvement, not evidence of deeper
editing or narrative judgment. Baseline restoration already has near-perfect
word-token overlap.

Positional quotation remains unreliable: the new adapter often selects a
different fragment or wrong number of words. In the short self-judgment passage,
it returns the closing list rather than the requested eight-word span. Reference
continuation also remains incorrect; in the gratitude passage it invents a
description rather than reproducing the original remaining text. Alternative
creative continuations cannot be judged solely by this exact-reference test,
but these responses do not satisfy the requested original wording.

**Decision: preserve this adapter as experimental; do not replace the existing
model or promote it to the application.** It improves exact punctuation fidelity
on two restoration cases while quotation and continuation token overlap decline.
The aggregate overlap metric does not improve. Six source passages are too few
for a broad capability claim, and no human literary preference rating is supplied.
Additional epochs or model promotion are not automatically triggered by this run.

The source-only data builder, explicit assistant-only loss masks, frozen test
protocol and three-condition evaluation are complete and reproducible from the
pinned evidence. The builder refuses to overwrite its existing review artifacts.
Future experiments need a new version, suitable task revisions and a separately
reserved evaluation set, rather than tuning this model against these 18 cases.

Final verification rechecked all 342 source-linked records, author/work split
guards, target/training/test hashes, original protected inputs, all 81 finite
step losses and model hashes. The evaluation-only Austen clearance also
correctly rejects attempted training use in the scoped ledger. No core
foundation code changed; the earlier 72-test suite result is not presented as a
fresh run for this experiment.

## Files and application scope

Preparation artifacts:

`/Users/williamwessex/Documents/Writer1/llm/Narratryx/artifacts/source-tasks-v1/`

- `records.jsonl`, `trace.jsonl`, `excerpts.jsonl`: source-linked records and transformations.
- `train.messages.jsonl`, `train.tokens.jsonl`: sole training materials.
- `test.cases.jsonl`: Austen-only evaluation inputs and source references.
- `validation.json`, `tokenizer-preflight.json`, `mlx-label-handler-check.json`.
- Reproducible builder: `curation/source-tasks-v1/build.py`.

Experiment artifacts:

`/Users/williamwessex/Documents/Writer1/llm/Narratryx/artifacts/source-task-training-v1/`

- `protocol.frozen.json`, `request.json`, `worker-config.json`, `launch-audit.json`.
- `training.log`, `progress.jsonl`, `final-progress.json`, `completion.json`.
- `adapter/`: isolated checkpoint and final adapter.
- `evaluation/`: raw three-condition responses, runtime records, scores and a readable review.
- `final-verification.json`: post-run provenance and artifact validation.

This experiment uses the installed local Unsloth MLX backend. No cloud spending,
source/model upload, model publishing, serving change or application integration
is part of it. All application versions—web/PWA, Tauri desktop, Capacitor iOS and
native macOS—remain unchanged. App builds and device tests are not applicable to
this explicitly isolated dataset/model work; no app-runtime parity claim is made.
