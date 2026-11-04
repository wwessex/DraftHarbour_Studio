# Source-exact semantic repair preparation — 1 November 2026

Following the [17-pair informed review](task-matched-v13-ai-review-2026-11-01.md), nine narrow editing candidates target object/property assignments, future events, promises, deferred decisions, explicit conditions and concrete action. **Only inputs are deliberately corrupted. Every literary answer is an unchanged contiguous substring of previously scoped published prose.** No generated evaluation answer or review annotation is converted into a teaching target.

This is preparation, not a training run or a claim that storytelling has improved. The candidates are a potential supplement to the source-prose curriculum, not a replacement with nine repair drills. Earlier experiments, their blank human ballots, source scopes and the app-selected craft model remain unchanged.

## Prepared candidates

| Candidate | Source | Controlled input error and intended repair |
|---|---|---|
| `sr14-materials` | Hopkins, lodging description | Bed drapery is assigned the window material; restore dark-blue denim while keeping window muslin separate. |
| `sr14-lever` | Wells, fictional machine explanation | The first lever's stated direction is changed from future to past; restore the source's fictional explanation. |
| `sr14-announced-visit` | Doyle, announced evening visit | A future visit is changed into a completed visit last night; restore the announcement. |
| `sr14-event-times` | Hopkins, reception invitation | Refreshments acquire the reception's time; restore refreshments at nine without changing the half-past-seven reception. |
| `sr14-deferred-answer` | James, 1908 proposal passage | Isabel's request to stop discussing the proposal is replaced by an engagement announcement; restore her deferred answer. |
| `sr14-explicit-condition` | Opie, marriage condition | The suitor's consent becomes refusal; restore the actual explicit agreement rather than treating it as unresolved. |
| `sr14-unanswered-question` | Hopkins, embroidery exchange | The undisclosed place of learning is falsely said to have been disclosed; preserve the unanswered question and the separate offer to teach. |
| `sr14-promise` | Wilson, Jim's offer of support | Future promised help becomes help already delivered; restore the promise without inventing payment. |
| `sr14-concrete-action` | Hopkins, work discussion | Offering a chair becomes wondering about permission; restore the physical action supported by the source. |

The [review packet](../artifacts/semantic-restoration-v14/REVIEW.md) shows facts, deliberately damaged input and exact original answer for each candidate. Instructions specify only the declared correction and preservation of all other characters, line breaks and historical speech. Editing has no minimum length. The facts and damaged inputs are constructed task material; assistant answers remain published source prose. Historical statements are attributed to the source narrator/characters, not asserted as modern factual guidance.

Each of the nine lessons has a distinct parent record and distinct answer; no parent is repeated within this candidate set. All nine parents' material was already exposed in earlier training. This adds task variants, not new authors, independent source diversity or an unseen literary corpus. Full previous spans remain attached as provenance, with the selected answer's relative and absolute Unicode offsets recorded separately.

The corruption helper requires exactly one original anchor, a distinct replacement and an otherwise unchanged input. Rebuilding the corruption must reproduce the entire derivation record exactly. Verification separately checks the answer against the exact scoped source slice; a plausible new sentence cannot silently replace it. Existing GB/US source-use and author/work leakage validation passes against `rights/grounding-balanced-v1.scoped.jsonl`. No source span is expanded, no new book/edition is acquired and no new human/legal approval is claimed.

## Eight new evaluation cases

Four deterministic JSON tasks separately test object/property binding, a future same-day arrival interval, permission scope and what a size-only check establishes. Their references are task labels, not literary teaching prose.

Four prose tasks test a constrained rewrite, a spare-inspection continuation, future-arrival dialogue and a continuation after a size-only check. They explicitly state when a resource list is closed, which original alteration needs approval and which spare inspection is allowed without it. A size check does not establish durability or heat resistance. Ordinary action with listed objects is permitted; the model is not asked to invent an approval hierarchy or freeze all activity.

All eight prompts are frozen, outside training and **unrun**. They are AI-authored development cases, not an independent human benchmark. The prose cases have no canonical literary reference answer and need informed judgement. Future evaluation should retain the now-exposed v13 regressions rather than silently editing their wording or scores. New cases provide clearer constraints but also stronger cues; comparisons across old/new prompts cannot isolate model improvement.

## Token preflight and limitations

The offline cached-tokenizer check passes nine candidates, with maximum **501 tokens** against 2,048 and **1,042 supervised tokens** for one presentation of each answer including EOS. Answers round-trip exactly; proposed labels mask the prompts; no answer truncates. The eight evaluation prompts have a maximum 151 tokens, leaving room for the existing 384-token output cap. Only tokenizer files are loaded; no model weights, inference or training are run. Executable token files, installed collation and a training recipe are not supplied.

These are intentionally small, cue-rich repair exercises. Several can be solved partly from wording, grammar or internal consistency; successful repair would not prove applied narrative reasoning. Most supervised tokens reproduce unchanged source prose, so aggregate loss could look good without learning the corrected semantic span. A later pilot must measure correction accuracy and preservation outside the correction separately, then test transfer to free-form writing. Source-exact matching is appropriate for these expressly minimal repairs, not for judging creative continuations.

The set also does not teach every desired action. It includes positive consent, an unanswered factual question and a deferred proposal as different source states; none should be mislabelled as another. It does not contain a fully source-backed modern negotiation over an original and an untested spare with all of the new test's constraints. It cannot justify more epochs, a wholesale curriculum replacement or model promotion by itself.

## Next bounded step

Review the candidate briefs/answers before fixing a mixture. Prefer one selected variant per source lesson rather than appending several versions of the same answer. Retain genuine scene/dialogue/revision examples and independent monitors; keep deterministic JSON diagnostics separate from literary quality. Freeze the recipe and installed collation audit before training, and compare fresh base/current craft/candidate responses on the new cases plus exposed regressions. Human quality review is still outstanding. No job or selected-model change is launched by this preparation.

## Verification and application scope

The full CPU foundation suite passed **204 tests in 39.319 seconds**, including four new corruption-boundary/immutability checks. The final verifier passes nine exact source/answer derivations, uniquely anchored input changes, GB/US rights/split checks, distinct parent/answer checks, the eight evaluation-only cases and tokenizer-preflight input hashes. Earlier experiment/review artifacts, blank human ballots, base weights and selected/prior models retain their pinned hashes. Python compilation and report-link/whitespace checks pass. Human literary-quality ratings remain zero.

Source scripts are in `curation/semantic-restoration-v14/`; exact input corruption guards are in `foundation/source_restoration.py`. Candidate prose, damaged inputs, derivations, cases and the review packet remain local under ignored `artifacts/semantic-restoration-v14/`. A tracked preparation lock retains hashes and results without literary text or weights. The builder and tokenizer preflight refuse overwrite. Read-only verification:

```bash
cd llm/Narratryx
.venv-foundation/bin/python curation/semantic-restoration-v14/verify.py
```

Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS receive no source/default/configuration/generated-asset changes, app builds or device/runtime checks. Manuscripts, app startup and ordinary users' machines are uninvolved. No paid job, remote inference, corpus upload, publication, generated literary teaching answer or model promotion occurred.
