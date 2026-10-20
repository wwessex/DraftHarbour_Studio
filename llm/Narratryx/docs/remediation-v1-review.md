# Post-training review and targeted draft examples — 19 October 2026

The completed Opie/Wray adapter remains experimental. Its extra mechanical pass
is dialogue line count, while editing accuracy, continuity and causal reasoning
remain weak. This follow-up reviews all 14 existing pairs and prepares twelve
new instruction/answer candidates. It does not launch another training run or
record human approval.

**Training-request update, 19 October:** The user subsequently instructed
“proceed with training”. The [output-use review](../rights/dossiers/remediation-output-use-2026-10-19.md)
records the official terms checked and the unresolved account-specific
permission. The dataset remains unreleased; no additional run was started.

This is **AI editorial review with model identities visible**. The same agent
has already inspected named outputs, so this cannot be presented as independent
blind preference testing. The existing blind packet and its private key remain
unchanged; no ballots, human ratings or preference results have been supplied.

## Review of all diagnostic pairs

The original prompts, 28 responses and objective scores are preserved in
`artifacts/clean-source-training-v1/fresh-context-v1/`. “Pass” below means only
the existing mechanical checks passed.

| Case | Base / adapter mechanical pass | Editorial finding and implication |
| --- | --- | --- |
| fiction-ferry | fail / fail | Both exceed the cap. Base relocates Nia inconsistently and places the missing brother on shore. Adapter adds a departure followed by an order to wait. Train local decisions with clear physical continuity. |
| editing-ferry | pass / pass | Both change “was holding” to “held” while saying “None” in the change list. Teach exact reproduction and a change list that matches the actual edit. |
| analysis-ferry | fail / fail | Both fail exact quotations; the adapter also exceeds the word cap. Both assert stakes or obstacles beyond the supplied facts. Teach quotations plus explicit boundaries between observation and inference. |
| dialogue-ferry | pass / pass | Both include action/narration despite “dialogue only”. Base calls the coat the child's brother's, changing its attribution. A line-count pass misses factual and format failures. |
| pacing-ferry | fail / fail | Both exceed the cap and add departure/loss events; the adapter explicitly turns a missing brother into a brother lost to the sea. Preserve the same moment and events in both rhythms. |
| storytelling-ferry | fail / fail | Both exceed the cap. Base proposes reuniting the child with a coat already held. Adapter puts Nia aboard, then on the dock. Check possession, location and causal links within each alternative. |
| fiction-orchard | fail / fail | Both exceed the cap. Base moves from sketching to a future first stroke; adapter announces a need to decide without making a clear immediate choice. Teach one observable decision and its local consequence. |
| editing-orchard | pass / pass | Both mostly preserve wording but normalise the supplied curly apostrophe without reporting it, while saying no changes. Accept minimal output when preservation is requested. |
| analysis-orchard | fail / fail | Both invent a verification/inspection goal and attribute knowledge or control to the father. Adapter reaches the length range but offers only one quotation. Teach uncertainty about unstated motives and two exact evidence spans. |
| dialogue-orchard | fail / pass | Adapter reaches 12 lines; base has 13. Base transfers the map to the father. Adapter still includes narrative lines and explicit fear/secrets. Teach speech-only lines with facts preserved, not line count alone. |
| pacing-orchard | fail / fail | Both exceed the cap and bring cutting into the present. Changing event timing is not a controlled pacing rewrite. |
| storytelling-orchard | fail / fail | Both exceed the cap. Base conflates pruning with saving an orchard from development; adapter treats burying a map as sufficient to save the trees. Require an explicit mechanism connecting choice, cost and payoff. |
| control-no-change | pass / pass | Both reproduce the passage exactly. Preserve this capability rather than rewarding extra explanation. |
| control-one-edit | pass / pass | Both perform the specified single substitution exactly. More complex edit reporting remains unproven. |

No model preference votes or aggregate literary score are inferred from this
table. The existing 5/14 versus 6/14 mechanical result remains unchanged.

## New candidate material

The twelve drafts use two newly invented contexts: a clock-repair shop with a
collection-label discrepancy, and a concert-programme printing shortfall. They
are **synthetic**, not public-domain literature or human-authored material. No
Austen/Opie/Wray prose, benchmark context or benchmark answer was repurposed as a
training target. They share the observed *failure types*, not the tested scenes.

| Task | Two candidate behaviours |
| --- | --- |
| Editing | Leave correct prose exactly unchanged; delete one intentional duplicated word and accurately report it. Neither editing task has a minimum word count. |
| Analysis | Quote two exact phrases; identify the goal and obstacle while marking unknown motives and proposed next actions. |
| Dialogue | Exactly eight lines of quoted speech, with conflicting aims and no narration or explicit explanation of the concealed motive. |
| Pacing | Change sentence rhythm and emphasis while retaining the same event sequence, quantities, possessions and unresolved state. |
| Storytelling | Two clearly labelled alternatives, each with a choice, cost/consequence and causally connected later payoff. |
| Fiction | A short continuation that makes one immediate decision while preserving viewpoint, tense and the original obstacle. |

Human reviewers should assess whether the targets are useful prose, whether the
subtext is effective, and whether the slow pacing examples repeat facts too
heavily. Passing objective checks does not settle those judgments. Two scenes
are a small teaching seed, not a representative literary training corpus. All
records are proposed training candidates; none is an independent evaluation set.

## Checks and release status

The build reuses the foundation's existing schema, objective-check and lexical
leakage functions without weakening or changing them:

- Twelve dataset records and one separate pending rights record pass structural
  validation; content hashes use the existing canonical message digest.
- All task-specific mechanical checks pass, including exact edit outputs, two
  exact analytical quotations, word limits, eight dialogue lines and quoted
  speech only. These are checks of the drafted targets, not model results.
- The existing leakage check passes against all 120 draft benchmark tasks, and
  neither new context equals a benchmark context. This is a lexical screen,
  not proof of semantic independence or web-wide originality.
- Source/output-use and teacher review fields remain pending. The existing
  training-release validator refuses the dataset at the first unapproved record.
  Earlier human approval of the 108 raw prose passages does not cover these
  newly generated examples or the teacher's terms.
- Recorded hashes confirm that the approved prose export, trained adapter,
  previous responses, benchmark tasks and rubric remain unchanged.

The linked terms URL is a provenance reference, not a finding that those terms
apply to this account. The exact serving-model revision was not available and
is not invented. No legal determination or synthetic-output training permission
has been recorded. An editorial “keep” alone cannot resolve that separate issue.

## Files and next stage

Open the complete review pack:

`/Users/williamwessex/Documents/Writer1/llm/Narratryx/artifacts/remediation-v1/REVIEW.md`

Each example presents its context, instruction, target, purpose, criteria and a
blank keep/revise/reject decision. Those blanks are not approval records.

- `data/remediation-v1.pending.jsonl`: twelve schema-valid pending candidates.
- `rights/remediation-v1.pending.jsonl`: separate pending original-material record.
- `artifacts/remediation-v1/validation.json`: mechanical results, release refusal
  and protected-input hashes.
- `curation/remediation-v1/build-review.py`: explicit, local one-off builder;
  refuses to overwrite existing review artifacts and launches no inference.

The next stage is editorial review and revision of these targets, plus a
separate determination of applicable output-use permissions. Only after those
checks should a concrete, bounded SFT experiment be prepared and validated. A
later evaluation must use independently reviewed material beyond these two
training scenes; these examples must never be advertised as unseen tests.

All changes are inside `llm/Narratryx`. Web/PWA, Tauri desktop, Capacitor iOS and
the separate native macOS application remain unchanged. No app builds, device
checks, additional model inference, training, paid jobs or uploads were run for
this follow-up. Existing 72-test training-run evidence remains historical; this
material-only change was checked with the data validators described above.
