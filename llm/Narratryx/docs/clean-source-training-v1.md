# Opie/Wray local training and paired diagnostics

The user requested **“Time to train?”** after approving the exact 108-passage
selection. One fresh-base local adapter run completed successfully. This is a
small raw-prose adaptation experiment; successful execution does not establish
better fiction, editing or analysis.

## Training evidence

| Item | Observed result |
| --- | --- |
| Base | `mlx-community/Qwen3.5-4B-MLX-8bit` |
| Base revision | `5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d` |
| Initialization | Fresh LoRA adapters; no previous adapter or checkpoint resumed |
| Data | 108 approved original prose paragraphs, 54 Opie and 54 Wray |
| Data size | 9,871 words; 12,487 text tokens |
| Scope | Existing recorded GB/US training/evaluation approval; no new works |
| Backend | Installed Unsloth MLX trainer adapter used by its CLI |
| Precision | Cached 8-bit base preserved; no forced 4-bit conversion |
| Objective | Raw-text next-token prediction, EOS handling, no chat template |
| Schedule | One epoch, 27 optimizer updates, batch 1, accumulation 4 |
| Context | 512 tokens, no packing; preflight maximum paragraph 313 text tokens |
| LoRA | Rank 8, alpha 16, dropout 0; worker's resolved module mapping saved |
| Optimizer | AdamW, LR `1e-5`, linear decay, 3 warmup steps, seed 42 |
| Internal evaluation | Disabled; no random same-work split claimed as independent |
| Training duration | 78.3 seconds reported by progress; excludes setup and comparison |
| Peak MLX allocation | 6.50 GB; this is not total system RAM usage |
| Worker aggregate training loss | 3.2508; not an independent evaluation score |
| Final optimizer-step loss | 3.6967; batches differ, so first/last losses are not a learning curve |
| Adapter | 47,616,418 bytes; checkpoint at step 27 and final adapter saved |
| Adapter SHA-256 | `77bbf1e343b87e880dd53d7c1c2b9ca64df4c1ac4ba7885eefa0bd686ab17f87` |

All 27 emitted step losses and gradient norms were finite. The worker reported
one epoch and no training warnings. Source approvals, exact raw spans, approved
export and protected input hashes were checked before launch. The base weight
hash and training export hash were unchanged after training. Tokenizer file
hashes also match the preparation pins. The installed MLX worker's supported
LoRA/raw route was used because its separate Continued Pretraining mode is
unsupported on this host.

The run used the backend directly through the installed CLI trainer adapter,
with the exact prepared parameters, rather than submitting a Studio browser
training request. The browser's old pilot form does not represent this run.
No paid jobs, model uploads, external inference/judging services, model merges,
serving changes or application integration were performed.

## Paired comparison protocol

A separate inference process loads the final adapter and pinned base. It
alternates base/candidate order over the existing 14 cases, for 28 responses.
Each request gets one new user message, no earlier responses, no system prompt,
no tools and no prompt cache. Base responses disable adapters on the same loaded
base weights; candidate responses enable them. Generation uses temperature 0,
seed 42, maximum 512 output tokens and disabled thinking. Raw responses are
saved before objective scoring.

These cases have already been used in the previous pilot. They are exploratory
regression diagnostics, not unseen generalization evidence or a frozen broad
literary benchmark. The two scenario contexts and exact-output controls do not
support a general literary-quality claim. No uncleared Murray text or synthetic
teacher answers are included.

The inference backend warns that the configured 2,048-token context limit is
not enforced by every cache layer of this model. These short prompts and the
512-token generation cap are well below that size; the warning is retained in
the inference log.

## Comparison results and decision

All **28 requests completed**, with no inference errors, empty responses or
output truncations. Each used one message, no prior assistant turns and zero
cached tokens. The adapter hash was unchanged and the inference backend was
unloaded after the comparison. All 14 fresh base responses exactly match the
previous pilot's base responses, providing an additional reproducibility check.

| Mechanical checks | Base | New adapter |
| --- | --- | --- |
| All cases | 5/14 | 6/14 |
| Editing, including two exact-output controls | 4/4 | 4/4 |
| Dialogue | 1/2 | 2/2 |
| Fiction continuation | 0/2 | 0/2 |
| Analysis | 0/2 | 0/2 |
| Pacing | 0/2 | 0/2 |
| Storytelling plans | 0/2 | 0/2 |

The only additional whole-case pass is `dialogue-orchard`: the base produced
13 nonblank lines and the adapter 12, inside the requested 8–12 range. This is
the same total format score as the older 19-paragraph adapter; it is not a new
demonstration of literary improvement. Most remaining failures involve length
limits, and both models still fail the exact-quotation analysis check.

AI editorial inspection, with model identities visible, found material problems
that the format score does not capture:

- **Editing:** Both ferry answers change “was holding” to “held”, yet state
  “None” in their change lists. Passing a length check does not validate editing.
- **Analysis:** The adapter's orchard answer invents a plan to inspect trees
  before harvest and treats the father's awareness/decision as established.
  The passage establishes neither. It also supplies only one quoted fragment.
- **Pacing:** The adapter's ferry versions add a missed departure and a brother
  lost to the sea. Its orchard fast version brings cutting forward to the
  present. The task required preservation of the supplied events and facts.
- **Dialogue:** The orchard answer meets the line bound but includes narrative
  action and explicit “unspoken fear”/“secrets”; the task asked for dialogue only
  and a concealed motive. The extra mechanical pass is therefore limited.
- **Storytelling:** The ferry proposal places Nia aboard and then stranded on
  the dock. The orchard proposal claims burying a map saves the trees without
  establishing a causal mechanism. Both adapter plans exceed the word cap.

**Decision: retain this adapter as an experimental artifact. Literary
improvement has not been demonstrated; do not promote it or extend training
automatically.** The small raw-prose run establishes that this local workflow
executes successfully. It does not teach the instruction-following and editorial
judgment needed by the application by itself.

The next useful stage is to review the paired responses, then construct a small
set of reviewed instruction/answer examples targeting factual preservation,
accurate change lists, dialogue-only output and causal scene plans. Broader
independent evaluation and rights/quality approval of additional examples remain
necessary before another experiment. Repeating epochs on these paragraphs
without resolving those gaps is not supported by these results.

`fresh-context-v1/BLIND-REVIEW.md` contains all 14 pairs with identities concealed
and task criteria attached. Its assignment key is separate and mode 0600. No
human votes or blind preference results have been invented. The evaluator who
has already seen these named outputs cannot claim a subsequent blind judgment.

## Validation and application isolation

All **72 foundation tests passed**. No application source, runtime, model
selection, bundled assets or project-data format was changed. The web/PWA,
Tauri desktop, Capacitor iOS and native macOS applications were outside this
explicitly isolated model experiment; no application builds or device tests
were run. No cross-platform runtime parity claim is made for this adapter.

## Artifacts

Training artifacts:

`/Users/williamwessex/Documents/Writer1/llm/Narratryx/artifacts/clean-source-training-v1/`

- `launch-audit.json`: current launch request and approval/input evidence.
- `worker-config.json`: resolved actual worker settings.
- `training.log`, `progress.jsonl`, `final-progress.json`, `training-summary.json`.
- `completion.json`: completed step count and unchanged base/export checks.
- `tokenizer-pin-check.json`: tokenizer configuration hashes.
- `foundation-tests.log`: 72-test validation result.
- `adapter/`: final adapter, metadata and step-27 checkpoint.
- `fresh-context-v1/`: separate paired inference protocol, outputs and reviews.

The original preparation artifacts retain `prepared_not_started` and
`launch_authorized: false` as historical facts about that earlier step. The new
launch audit records the subsequent user instruction; source approval was not
silently treated as training-launch permission.
