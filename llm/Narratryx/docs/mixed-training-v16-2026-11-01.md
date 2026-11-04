# Mixed prose/semantic-repair pilot — 1 November 2026

The user authorised execution of the [corrected v15b mixed proposal](mixed-curriculum-v15-2026-11-01.md). This run starts fresh from the pinned cached Qwen3.5-4B MLX 8-bit base, with **22 training examples presented once each**: 14 broader prose tasks, five source-exact semantic repairs and three structural editing controls. Sixteen previously exposed Wray records monitor loss, outside training. Source intervals do not overlap between selected training records. No generated literary teaching answers or new source clearances are added.

## Frozen execution

The local Unsloth MLX request retains the proposed 22-update cap, one epoch, batch 1/accumulation 1, learning rate 5e-5, two warmup updates, linear schedule, LoRA rank 8/alpha 16/dropout 0, seed 42 and 2,048-token context. There is no checkpoint resume, oversampling, paid job or publication. Changes in dataset and update count relative to v13 prevent a single-factor causal claim.

Tokenizer/installed-collation checks preserve all intended input/label pairs, prompt masking and EOS: **2,449 supervised tokens**, comprising 1,711 broader-prose, 695 semantic-repair and 43 structural-edit tokens. Maximum record length is 499 tokens. Rights/span/author-work separation is checked against the existing scoped GB/US ledger; this is not a new legal certification or human approval. The withdrawn first v15 preparation draft is not used.

The plan makes **147 fresh-context requests**, 49 each for base, current craft and candidate. Each condition receives 44 primary cases (eight newly unrun clearer-constraint cases and 36 exposed v13 regressions), followed by five deliberately **seen training-fit** repair prompts. Seen fit is reported separately, never counted as transfer or literary quality. The eight new tasks become exposed after execution. They are correlated, cue-rich development cases, not an independent human benchmark.

Controls run before training. Every request uses one user message, no assistant history, temperature 0, seed 42, repetition penalty 1.0, zero reported cached tokens and a 384-token output cap. All responses are generated in this run; none are reused. Models unload between conditions. Warnings, errors, nonfinite progress, output truncation, the 22-update cap, 10 GB MLX/process-tree RSS gates and 20-minute phase deadlines stop execution without automatic retry. These resource gates are not hardware certification. The initially captured legacy service state is preserved.

## Results

**All 22 updates and all 147 fresh-context responses completed without errors or truncation.** Training phase elapsed was 64.29 seconds including setup/save; the worker reported 38.84 seconds and peak MLX memory 6.92 GB. All 2,449 supervised-token exposures were recorded, with no warnings/errors. Exposed monitor loss was 1.0748, not independent quality evidence.

| Primary diagnostic | Base | Current craft | Candidate |
|---|---:|---:|---:|
| Primary responses complete | 44/44 | 44/44 | 44/44 |
| New closed-task exact answers | 3/4 | 3/4 | 3/4 |
| Exposed clock exact answers | 3/6 | 3/6 | 3/6 |
| Exposed composite claims | 2/6 | 2/6 | 2/6 |
| Selected-word edit references | 7/7 | 7/7 | 7/7 |
| Long repeated-dialogue flags | 0/6 | 0/6 | 0/6 |
| New dialogue word limit | 1/1 | 1/1 | 1/1 |
| New continuation word limits | 2/2 | 2/2 | 2/2 |
| New rewrite word limit | 1/1 | 1/1 | 1/1 |
| Exposed dialogue word limits | 2/5 | 3/5 | 4/5 |
| Exposed continuation word limits | 5/7 | 5/7 | 3/7 |
| Exposed rewrite word limits | 3/3 | 3/3 | 3/3 |
| Exposed scene-writing word limits | 1/2 | 0/2 | 1/2 |

Word-limit passes are not turn-count, paragraph-count or semantic passes. Selected-word references compare output after trimming surrounding whitespace; the seen-source repairs below use strict character matching. Every model misidentifies the unknown object in the new binding JSON case; it is the uninspected duplicate, not the readable original. The new time, permission and evidence-state cases pass in all three conditions. Stronger prompt cues therefore do not establish a training gain.

### Seen training-fit only

| Seen repair diagnostic | Base | Current craft | Candidate |
|---|---:|---:|---:|
| Exact full source answer | 1/5 | 1/5 | 2/5 |
| Characters outside correction preserved | 1/5 | 1/5 | 4/5 |
| Exact correction at a preserved slot | 1/1 assessable | 1/1 assessable | 2/4 assessable |
| Lexical-anchor proxy | 3/5 | 3/5 | 3/5 |

The slot denominator is only answers with intact outside boundaries, so these fractions are not comparable five-case success rates. Full-answer improvements are partly preservation/formatting, not proof of better semantic reasoning. These five training prompts never contribute to primary or generalisation scores.

- The candidate exactly restores the lever passage; controls already restore its future direction but do not preserve every source character. The conditional-agreement answer is exact for all three models.
- All restore bed denim, but the candidate drops other source wording. The strict repair therefore fails despite correcting the intended property.
- All restore refreshments to nine but omit the source's final timing qualifier, so the source-exact metric fails. This is not evidence that the model still thinks refreshments are at half past seven.
- The announced-visit candidate retains past-night wording in an unnatural opening. Both controls use a future announcement with changed typography/wording. The candidate's improved surrounding-text preservation does not rescue that semantic regression.

No reliable general or literary-quality improvement is established. The adapter remains local and unpromoted.

## Writing observations and review

An informed AI inspection with model conditions already visible finds mixed writing behaviour:

- Archive dialogue explicitly calls a future supervisor late. Seed dialogue instead gets the 45-minute future interval right; the improvement in that setting does not generalise to the archive setting.
- Music dialogue asserts that an unchecked photocopy is blurry. Several continuations still hover, defer or leave a call unmade rather than take an informative practical step.
- Reel dialogue introduces a claimed personal backup reel beyond the stated untested spare, and has eight turns despite four–six requested. Its 89 words pass the length metric while the practical resource question and turn count remain weak.
- New arrival dialogue has seven turns despite four–six requested. It computes the 45-minute interval numerically but attaches it ambiguously to hypothetical lateness. Do not label that conditional statement an unqualified assertion that the courier is already late.
- Reel scene writing confuses which reel is untested, exceeds its word range at 136 and leans on abstract stakes. Coat writing fits its range but still conflates a separate scrap/button with destroying original fabric.
- Coat continuation again has two paragraphs instead of one. The introduced pocket iron remains a questionable convenience under the older brief, whose tool policy is less explicit than the new closed-list tasks; the paragraph violation is clear.
- Conservatory, rope and reel continuations are short. The rope answer adds an unestablished missing-object mystery, an editorial concern rather than proof of an identified culprit. Ordinary permitted detail is not automatically a factual error.
- The new spare/size tasks preserve important explicit constraints but still deserve human review for practical next-action quality. A plan for a future heat test is not proof one occurred; size measurement does not establish heat resistance. Approval is not automatically needed for explicitly allowed inspection of a spare.

These observations are not independent, blinded human ratings or a full pass/fail semantic rubric. Both controls also have substantial errors. Before increasing training, review the paired outputs and the failed seen announced-visit repair; do not mistake exact formatting gains for successful correction or broader storytelling ability.

The [randomised writing packet](../artifacts/mixed-training-v16/REVIEW.md) compares current craft and candidate only for completed writing pairs. At most 21 pairs support 42 blank ballots for two reviewers. The private condition key is mode 0600; no human ratings are fabricated. Paired review must respect each prompt's scope: allowed spare inspection does not require permission to alter the original, ordinary permitted scene actions are allowed, and a closed resource list should be enforced only where specified.

Closed JSON tasks are scored strictly, rejecting duplicate/unknown keys and wrong value types such as integer1 for Booleantrue. Selected-word edits use their minimal references. Seen-source repairs retain exact character matching, with separate outside-correction preservation, correction-at-slot when boundaries remain intact and a lexical-anchor proxy. An answer can contain the desired word while failing to preserve its surrounding text. Conversely, a corruption phrase may legitimately remain elsewhere in the source; the corrected v15b metric accounts for its original count. These proxies are not literary scores.

## Verification and application scope

The full CPU foundation suite passed **217 tests in 43.934 seconds**, including four new execution-plan/resource guards and four strict JSON scoring checks. The post-run verifier passed frozen recipe/data/code hashes, GB/US rights/split checks, actual training completion/token count, all 147 response prompt/protocol/adapter hashes, zero reported cached tokens, fresh single-message contexts and context limits. It independently checks 44 primary plus five seen-fit attempts per condition and their separate score counts. Base/prior/selected model hashes are unchanged.

The randomised packet has **21 writing pairs and 42 blank human ballots**; its private key is mode 0600. All models unloaded and the initially stopped legacy service remains stopped. Python compilation and report links/whitespace checks pass. Local evidence includes `verification.json`, `scores.json`, per-condition completion markers and training/resource logs. The tracked `curation/mixed-training-v16/execution.lock.json` preserves code/artifact hashes and dated test results without literary responses, private keys or weights. Human quality ratings remain zero and no model is promoted.

Frozen source data/tokens/proposed recipe remain in `artifacts/mixed-curriculum-v15b/`. Runtime protocol, combined cases, responses, resource logs and the candidate adapter are in `artifacts/mixed-training-v16/`, excluded from ordinary Git. Scripts are in `curation/mixed-training-v16/`. After execution/reporting, read-only evidence verification is available with:

```bash
cd llm/Narratryx
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/mixed-training-v16/verify.py'); print(m['verify']())"
```

No selected profile, existing adapter, app-owned runtime, manuscript store, installer or release asset changes. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/default/configuration/generated-asset changes and no app build or device/runtime check. Mac MLX execution does not establish Windows inference support, Muse equivalence or production readiness. No cloud job, corpus upload, remote inference, publication or promotion occurs.
