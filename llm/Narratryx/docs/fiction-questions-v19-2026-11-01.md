# Fiction task-question comparison — 1 November 2026

**Clearer questions do not reliably improve fiction across these six scenarios.** All 36 fresh-context requests complete, but repetitions, unsupported conclusions, permission problems and excessive dialogue turns remain. Keep the selected craft model and existing application prompts. No further training or model promotion is justified by this comparison alone.

This follows the [matched entity-selection diagnostic](question-ablation-v18-2026-11-01.md). That toy test's 5/16 → 16/16 result does not transfer into a comparable fiction-quality gain.

## Frozen comparison

Two Rewrite, two Continue and two dialogue scenarios are selected from the existing mixed-v16 evaluation. They cover object/property identity, permission, closed workshop resources, future arrival, unresolved object origin and the only unchecked spare reel. All are **exposed development cases**, selected with knowledge of earlier failures, not a fresh independent benchmark or a representative sample of fiction genres.

Each original prompt is reproduced byte-for-byte. Its clarified counterpart appends guiding questions and a reminder to return only requested fiction without planning notes. Facts, original constraints and word limits remain intact; no literary answer is supplied. This tests a guidance package, not interrogative grammar alone. Two scenarios per task type are too few for broad conclusions.

Each of the existing base, current craft and mixed-v16 models receives all 12 prompts, with no earlier response reused. Pair order alternates original-first/clarified-first by scenario; model order remains fixed. Every request has one user message, no assistant history and zero reported cached tokens. These are standalone fiction tasks, not a deployed app-flow or full Story Bible integration test.

## Mechanical results

| Metric per model | Base original / clarified | Craft original / clarified | Mixed-v16 original / clarified |
|---|---:|---:|---:|
| Rewrite word limits | 2/2 · 2/2 | 2/2 · 2/2 | 2/2 · 2/2 |
| Continue word limits | 2/2 · 1/2 | 2/2 · 1/2 | 1/2 · 1/2 |
| Dialogue word limits | 1/2 · 1/2 | 1/2 · 1/2 | 2/2 · 2/2 |
| Rewrite/Continue single paragraph | 4/4 · 4/4 | 4/4 · 4/4 | 4/4 · 4/4 |
| Dialogue four-to-six speaking turns | 0/2 · 1/2 | 0/2 · 1/2 | 0/2 · 1/2 |

Word counts use whitespace splitting, including speaker labels. Paragraph counts are mechanical proxies. Dialogue turns are checked manually against the actual outputs, which have one speaking turn per nonempty line; quoted dialogue with action tags is not thereby counted as satisfying “dialogue only”. All clarified reel dialogues still contain narration. Rewrite has no minimum length. There is no canonical-continuation matching or automated literary-quality score.

## Informed AI prose review

All 18 within-model original/clarified pairs are reviewed with model conditions visible. This is **informed Codex AI judgement**, not blinded, independent or human evaluation. Evidence quotes and output hashes accompany each note. Existing human ballots remain untouched; human literary ratings remain zero.

- **Inventory Rewrite:** base and craft remain repetitive with either prompt. Mixed-v16's clarified answer is a useful local improvement: 22 words rather than 40, keeping readability, the uninspected duplicate and missing agreement without repeating each fact.
- **Archive Rewrite:** base/craft clarified answers have modest concision or tonal advantages, but both versions remain static. Mixed-v16 versions are both 54 words; its original avoids the added unsupported “fragile” description. These are small local preferences, not reliable style gains.
- **Spare Continue:** base/craft clarification invents an earlier pencil line and ends ready to mark the unapproved original. This is a proposed violation, not completed marking. Their original versions perform allowed spare measurement but make an unsupported “safe to test” assurance. Mixed-v16 clarification avoids that original-marking plan, yet turns a dimensional check into confirmed suitability and no heat risk. It has not performed a heat test. Both mixed versions remain flawed.
- **Conservatory Continue:** base/craft clarified outputs fall to 48 words, below the 60-word minimum, and still largely pick up/replace the ring and watch. Mixed-v16 gives 46/54 words, both too short; its clarified version adds “growing delay” and claims Nabil is already on his way without evidence. It gives no contradictory explicit clock time, but the framing is poorly supported. Neither identifies who left the ring.
- **Courier dialogue:** base/craft clarification explicitly states the correct 45 minutes remaining. Mixed-v16 clarification instead omits the optional interval and removes its original's confusing conditional lateness wording; it does not demonstrate a new calculation. All six outputs have seven turns, over the requested maximum. They repeatedly promise to inspect instead of progressing through inspection. Base original's hypothetical “If he's late by ten minutes” is not an assertion that the courier is already late. Allowing copy inspection does not invent approval to alter the original, since inspection is already permitted.
- **Reel dialogue:** base/craft clarified answers shorten the negotiation to six turns but still exceed 100 words, include narration and invent another reel. Mixed-v16's clarified version is the stronger local answer: six turns, 97 words, no extra reel, and a concrete visual inspection while suitability remains unknown. It still includes narration. Its original has eight turns and proposes a personal backup reel. Ordinary box details are not automatically tool violations in this non-closed resource list; playback does not itself erase a recording, and permission to test is not authority to erase.

Local preferences per model are base **2 original / 2 clarified / 2 neither**, craft **2 / 2 / 2**, and mixed-v16 **2 / 3 / 1**. These are comparisons of particular flaws, not acceptable-answer counts, independent votes or a model leaderboard. Some preferred answers still fail a requirement. No overall literary upgrade or Muse equivalence is established.

## Execution and verification

Generation uses the cached pinned base/adapters and existing local engine: thinking disabled, temperature 0, seed 42, repetition penalty 1.0, maximum 384 output tokens and 2,048-token context. Tokenizer preflight passes. Each condition unloads before the next. Existing 10 GB process-tree RSS and 20-minute phase limits, per-request cancellation and error/truncation stops remain in place. All requests finish normally; no automatic retries occur. The initially stopped legacy service remains stopped.

Mechanical and review verifiers check exact original/clarified construction, response/prompt/protocol/adapter hashes, one-message contexts, zero cached tokens, output/context limits, recomputed word/paragraph totals, review evidence quotes, actual dialogue turns, unchanged prior models/evidence and service state. Training data, rights scopes and human ballots are unchanged. All generated fiction and review notes are evaluation-only and ineligible for training.

The full CPU foundation suite passes **232 tests in 71.732 seconds**, including three new pair-construction, task-balance and mechanical-scoring tests. It runs after inference stops. Both evidence verifiers and Python compilation pass. These checks validate the experiment tooling; they do not turn the informed AI review into independent literary evidence.

Source scripts are in `curation/fiction-questions-v19/`, with helper `foundation/fiction_questions.py`. Frozen cases/protocol are in `artifacts/fiction-questions-v19-plan/`; responses, mechanical scores, `COMPARISON.md`, `AI-REVIEW.md` and verification records are in `artifacts/fiction-questions-v19/`. The tracked diagnostic lock contains hashes and results, not weights, response prose or private state.

Read-only audit, without inference:

```bash
cd llm/Narratryx
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/fiction-questions-v19/verify_review.py'); print(m['verify']())"
```

## Next work and scope

Do not apply the appended question checklist globally or run another tiny fine-tune on this evidence. Prepare additional task-matched training candidates from exact cleared source spans, prioritising complete practical scene progression, concise genuine revision and distinct dialogue aims. Keep this evaluation set out of training; generated answers and these review notes must not become teaching targets. Check source/task fit and author/work separation before proposing a bounded run. Literary promotion still needs independent human review on broader, representative cases.

Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source, configuration, default or generated-asset changes. No app builds or device/runtime checks are run for this isolated research task. No training, corpus acquisition, rights grant, paid job, external inference, upload, publication or model promotion occurs.
