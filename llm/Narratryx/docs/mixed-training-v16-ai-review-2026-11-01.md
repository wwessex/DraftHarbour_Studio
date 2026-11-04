# Informed review of 21 mixed-pilot writing pairs — 1 November 2026

All 21 current-craft/candidate writing pairs from the [mixed pilot](mixed-training-v16-2026-11-01.md) have been reviewed against their complete prompts and actual responses. **The review does not establish an overall literary-quality upgrade.** Keep the selected craft model. Local preferences split seven each, with two ties and five neither; these are editorial judgements, not pass rates or independent votes.

This is an **informed AI review**. Conditions, some outputs and earlier failure analyses were already known. It is not blinded, independent or human. The original randomised packet and all **42 blank human ballots** remain unchanged; human literary ratings remain zero. The [full annotated review](../artifacts/mixed-training-v16-ai-review/REVIEW.md) records exact evidence anchors, word counts, judgements and limitations for every pair. All annotations and generated evaluation outputs are ineligible training targets.

## Pair findings

Every preference below is relative and often limited to one improvement; it does not approve the answer as fully satisfying its task.

| Case | Local preference | Main finding |
|---|---|---|
| New inventory rewrite | Tie | Byte-identical text, repeated properties and an added no-change assertion. No candidate distinction. |
| New spare continuation | Current craft, limited | Both measure with allowed items. Candidate overextends a size check toward safe modification and an unequipped future heat-test plan. |
| New arrival dialogue | Tie | Near-identical seven-turn answers, exceeding the six-turn maximum. The correct interval is misleadingly attached to hypothetical lateness. |
| New size continuation | Current craft, slight | Performs an observable inspection; candidate prepares to ask for approval without making the request happen. |
| Archive dialogue | Neither | Current craft invents a five-minute interval; candidate explicitly calls a future supervisor late. |
| Archive continuation | Candidate, limited | Meets length and avoids the invented noon condition, but still stalls. |
| Archive rewrite | Candidate, modest | Better object/property fidelity; little improvement beyond paraphrase. |
| Music dialogue | Neither | Both assert an unchecked copy is blurry; candidate proceeds with the assumed defect instead of checking. |
| Music continuation | Neither | Hovering versus an unmade call; no useful completed next step. |
| Music rewrite | Candidate | Keeps unknown suitability on the photocopy rather than moving it to the original. |
| Seed dialogue | Candidate, local | Correct 45-minute future interval instead of lateness, within word/turn limits; still invents consequences and vague confirmation. |
| Seed continuation | Neither | Both wait through overbroad permission assumptions; candidate also misses length. |
| Seed rewrite | Candidate, limited | More economical and less dominated by a false preservation-versus-spare dilemma. |
| Coat dialogue | Current craft, format only | Meets 100 words; candidate has 102. Both have material/provenance weaknesses. |
| Reel dialogue | Neither | Thirteen versus eight turns; candidate's shorter exchange claims a convenient personal backup reel. |
| Reel continuation | Candidate, limited | One paragraph and a real handover without another recorder, but only 53 words. |
| Reel scene writing | Current craft, limited | Keeps the untested spare clearer. Both exceed length and remain static. |
| Conservatory continuation | Current craft, limited | Meets length; candidate mostly abridges the same holding pattern. |
| Rope continuation | Current craft, slight | Better continuity with the expected person; candidate introduces an unexplained missing-object subplot. Both are short. |
| Coat continuation | Current craft, format only | One paragraph instead of two; neither quick material test supports every conclusion claimed. |
| Coat scene writing | Candidate, limited | Fits length with less inflated prose; material/choice logic remains weak. |

The apparent balance of seven versus seven cannot be treated as statistical evidence of equal ability: cases share scenarios, the reviewer is one informed AI, and many preferred answers still fail. Neither repetition-free output nor a word-count pass makes a good scene.

## What changed, and what did not

The strongest candidate improvement is local preservation of which object has an unknown property in some rewrites. Seed dialogue also improves time reasoning in that one setting. The same candidate calls a future supervisor late in archive dialogue. This is not consistent grounding transfer.

The four new clearer-constraint tasks show little advantage. Inventory output is exactly identical. Arrival dialogue differs only in a phrase while sharing the turn-count problem. Both spare continuations make a measurement, an improvement over the older generic hesitation scaffold, but that may reflect the clearer prompt rather than training: the control does it too. Size-only evidence still does not establish safety for modification or heat resistance.

For the new binding JSON case, all models choose the original as the unknown object even though the uninspected duplicate is intended. In contrast, the inventory prose rewrite correctly retains the readable original and uninspected duplicate. These are related tasks rather than an exact matched-format experiment. The contrast suggests testing question/label/output-format sensitivity; it does not prove the cause of the error or excuse the JSON failure.

The five seen-source repairs are **outside these 21 writing pairs** and remain outside primary transfer scores. Their earlier inspection also cautions against a gain claim: one extra exact answer is largely preservation/formatting, while the announced-visit candidate retains past-time wording and the controls recover a future announcement. The refreshment answer gives nine correctly but omits a source qualifier; an exact-source failure is not automatically wrong conceptual time reasoning. Preserve these distinctions when choosing future lessons.

## Calibrating the criticism

- Follow the exact permission scope. Allowing inspection of a separate spare does not permit damaging the original, and lacking original-alteration consent does not require freezing all spare inspection. A character's reassurance is not an independently verified material property.
- Enforce closed resource lists where stated. The old coat prompt does not explicitly exclude every ordinary tool, so a pocket iron is questionable realism rather than an automatically proved resource violation. Its two paragraphs are a clear instruction failure. The reel's convenient personal backup is a stronger problem under its stated spare constraint.
- A handover is not erasure or authorisation to erase. Playback need not erase a recording. Judge the actual proposed action rather than infer forbidden damage from handling alone.
- The arrival dialogue's conditional lateness phrase is confusing, not an unqualified assertion of present lateness. The archive dialogue's explicit lateness statement is a direct conflict with its current/scheduled times.
- Ordinary scene detail is not automatically forbidden. Added facts matter more under an explicitly faithful rewrite than an open continuation. The new size prompt closes items, not expressly the cast, and already mentions an owner; turning to that owner is an added staging assumption, not a conclusively forbidden person.
- Do not reward filler to meet length. A shorter continuation can still be inadequate, and an overlong answer can still contain a useful local move. Keep length, structure, semantic fidelity and literary judgement separate.

These are interpretive qualifications, not a replacement human gold standard. Original responses, cases and mechanical scores remain frozen.

## Next useful work

Do not increase epochs on the same tiny mixture as the next default action. First freeze a small **evaluation-only format diagnostic**: counterbalance which object is original/spare and known/unknown, vary the question and response format while keeping the underlying facts fixed, and compare fresh contexts across the existing models. Separate exact field/type compliance from whether the answer identifies the right entity. Keep this narrow diagnostic outside training and outside literary-quality claims. No such model requests are launched in this review.

For broader fiction improvement, the remaining need is substantially better task coverage: varied full exchanges with distinct aims, meaningful next actions, stable object identities and an unresolved but credible choice. The present few thousand supervised tokens and repeated scenario scaffolds do not establish that capability. Expand only where exact scoped source prose supports the task; a generated review comment or a model's preferred draft is not an authorised literary teaching target. Human review of the paired writing remains outstanding.

## Verification and scope

The review builder verifies all 21 writing case IDs, every evidence quotation against its actual condition's response, word counts, original execution code/artifact hashes and the unchanged 42 blank human ballots. Read-only review verification and a fresh run of the pilot evidence verifier pass, including base/prior/selected model hashes and all 147 response/protocol hashes. The pilot's **217-test** result is historical evidence for that execution; the suite was not rerun for this editorial review. New review scripts compile and link/whitespace checks pass.

Review prose, notes and structured annotations remain in ignored `artifacts/`. The tracked `curation/mixed-training-v16-ai-review/review.lock.json` retains code/artifact hashes without response/reviewer prose, private keys or weights. Source scripts are in that directory. Read-only review verification:

```bash
cd llm/Narratryx
.venv-foundation/bin/python curation/mixed-training-v16-ai-review/verify.py
```

No new training, model inference, dataset alteration, source acquisition, paid job, publication or promotion occurred. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/default/configuration/generated-asset changes, app builds or device/runtime checks. All application features and the selected craft profile remain unchanged.
