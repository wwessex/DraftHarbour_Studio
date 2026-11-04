# Informed AI review of 17 writing pairs — 1 November 2026

All 17 current-craft/candidate writing pairs from the [25-example pilot](task-matched-pilot-v13-2026-11-01.md) have been reviewed against their full prompts and actual responses. **There is no reliable literary-quality upgrade to promote.** Some rewrites improve local factual fidelity and some dialogue becomes shorter, but chronology, object identity and practical scene development remain weak.

This is an **informed AI editorial review**. Model conditions and earlier failure analyses were already known. It is neither independent nor blinded, and it adds no human ratings. The original randomised packet, private key and 34 blank human ballots remain unchanged. The [full annotated review](../artifacts/task-matched-v13-ai-review/REVIEW.md) and its machine-readable companion record evidence and limitations for every pair. These annotations and generated evaluation responses are explicitly **ineligible training targets**; they are not synthetic teaching examples.

## Findings by case

Preferences below are limited relative judgements, not successful-task counts. A preferred answer can still fail a clear requirement.

| Pair | Local preference | Main finding |
|---|---|---|
| Archive dialogue | Candidate, limited | Six turns rather than seven. Both give the wrong interval until 11:00 at 10:20. |
| Archive continuation | Candidate, limited | Meets length and avoids the invented noon deadline. Both stall rather than take the requested practical next step. |
| Archive rewrite | Candidate | Less added fragility/deadline pressure; movement remains largely a paraphrase. |
| Music dialogue | Neither | Current craft invents a blurry photocopy; candidate exceeds length and muddles permission/equipment. |
| Music continuation | Candidate, slight | Names an intended note-writing action; neither produces a useful check of the copy. |
| Music rewrite | Candidate | Correctly keeps unknown suitability attached to the photocopy rather than the original. |
| Seed dialogue | Neither | Both call a future supervisor late; additional workshop deadlines or notes are unestablished. |
| Seed continuation | Neither | Both invent supervisor authority over assessing the spare and stop the action. |
| Seed rewrite | Current craft, limited | Avoids newly asserting fragility, though both exaggerate the practical dilemma. |
| Coat dialogue | Current craft, format only | Meets turn/word constraints. Both invent material facts; candidate treats untested strength as a definite defect. |
| Reel dialogue | Candidate, limited | Six concise turns instead of thirteen; which reel is used and how it is protected remain unclear. |
| Reel continuation | Neither | Current craft introduces another recorder and two paragraphs; candidate is short and resolves the choice through withholding. |
| Reel scene writing | Current craft, limited | Retains the unknown spare more clearly. Both are overlong/static; candidate invents Anika's need to recover her own voice. |
| Conservatory continuation | Current craft, limited | Meets length and explicitly retains the expected arrival. Neither materially advances the scene. |
| Rope continuation | Tie | Near-identical 50-word outputs: only the third-sentence noun changes from paper to pattern. Both miss length. |
| Coat continuation | Current craft, format only | One paragraph rather than two. Both tests and their claimed conclusions deserve scrutiny. |
| Coat scene writing | Candidate, limited | Meets the word range; both confuse a separate scrap/button with destruction of original fabric. |

This gives **seven candidate preferences, five current-craft preferences, one tie and four neither**. The reviewer is one informed AI, cases share settings, and both conditions often fail. The counts are not independent votes, statistical evidence, a win rate against Muse or a model-promotion threshold.

## Corrections to overly strict interpretations

The earlier pilot report's observations remain preserved as historical evidence. This closer review qualifies several interpretations rather than converting them into unquestionable labels:

- Missing agreement to **mark, cut or damage the original** does not necessarily prohibit harmless inspection of a spare. Characters agreeing to test a blank are not automatically inventing permission to alter an original. Conversely, an absent supervisor is not automatically the sole decision-maker. This distinction is essential to avoiding stalled, overcautious scenes.
- A recorder may be tested through playback without erasing a recording. The word master may refer to the existing choir recording; it does not prove a second copy was invented. Ambiguous reel handling should receive a human judgement, not an automatic false-resource label.
- A continuation can add ordinary fictional observations or atmosphere. An engraving, a character perception or an omitted repetition of an earlier time is not automatically a contradiction. A rewrite expressly forbidding added knowledge is more restrictive. Qualifiers such as seemed and hinting are not unqualified factual assertions.
- A convenient pocket iron/tool kit is questionable scene construction under the constrained brief, but the prompt does not explicitly list every allowed ordinary tool. The candidate's two paragraphs are a clear violation; the equipment criticism is interpretive. Future resource tests should state whether the resource list is closed.
- Agreement to safe work is not itself a failure when only damaging alterations lack permission. Ambiguous consent should not be treated as proven consent to cutting. Preserve the exact scope of the author constraint.

These distinctions prevent a future curriculum or automatic evaluator from teaching the model that all new detail or all practical action is forbidden. None excuses the explicit wrong-time arithmetic, premature-lateness statements, wrong-object uncertainty or paragraph/length violations.

## Next work before more updates

| Priority | Target | Existing source coverage and limit |
|---|---|---|
| 1 | Object/property binding | Preserve which object is original, spare, tested or unknown. The music rewrite is a useful diagnostic; its generated output must not become a teaching target. Existing Hopkins descriptions provide objects/properties but do not cover the full original/spare negotiation. |
| 2 | Time in applied prose | Existing announced schedules and invitation scenes support future-event distinction; they do not supply a complete literary example for every constructed clock state. Keep deterministic clock labels separate from prose quality, and avoid assuming that oversampling them repairs dialogue reasoning. |
| 3 | Action and evidence | Source dialogues ending with an actual chair offer, deferred answer or stated condition can demonstrate specific movement. Select briefs that describe what the source actually does; a quick fitting cannot establish every material property. |
| 4 | Permission scope | The source-derived James deferred proposal, Hopkins unanswered question and Opie explicit marriage condition illustrate different states. Do not relabel an explicit agreement as unresolved consent, or an unanswered factual question as a permission refusal. |
| 5 | Evaluation clarity | In any **new** cases, state whether ordinary tools may be introduced and which actions require whose permission. Preserve these now-exposed cases and scores unchanged. Add genuine paraphrase/scene diversity rather than treating three settings with the same scaffold as independent literary coverage. |

There is no prepared replacement literary target or new training job in this review. Keep the current selected model. The next development step is a small, source-backed curriculum proposal aimed at these particular gaps, with exact spans and a frozen task-matched evaluation before another bounded pilot. If no suitable source span exists, retain the gap instead of manufacturing an answer or increasing epochs on unrelated prose. Human review of the paired outputs remains outstanding.

## Verification and application scope

The annotation builder verifies all 17 case IDs, each quoted evidence anchor against its actual condition's response, word counts, prior execution code/artifact hashes and the unchanged 34 blank human ballots. A fresh run of the existing pilot evidence verifier also passes, including base/prior/selected-model hashes and all 108 response/protocol hashes. The earlier **200-test suite** result belongs to the pilot; it was not rerun for this editorial review. This review adds no training or serving code. Python compilation, report links and whitespace checks pass.

Review data and notes remain under ignored `artifacts/`; a tracked review lock retains code/artifact hashes without response/reviewer prose or weights. Source scripts are in `curation/task-matched-v13-ai-review/`. Read-only review verification:

```bash
cd llm/Narratryx
.venv-foundation/bin/python curation/task-matched-v13-ai-review/verify.py
```

No new model requests, training, dataset alteration, source acquisition, paid job, publication or promotion occurred. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/default/configuration/generated-asset changes, builds or device/runtime checks. All app features and the selected craft profile remain unchanged.
