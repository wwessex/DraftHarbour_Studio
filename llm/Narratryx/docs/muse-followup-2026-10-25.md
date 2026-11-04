# Muse research follow-up, diagnostic review and next experiment

25 October 2026. This work continues independent model development; it does not clone or establish parity with a proprietary model, publish weights, or change an application default.

## What the two additional sources clarify

The [Muse deep-dive article](https://sudowrite.com/blog/what-is-sudowrite-muse-a-deep-dive-into-sudowrites-custom-ai-model/) discusses fiction specialisation and writer-specific instructions. Its proposed foundation model and imagined internal story representation are speculative, not a disclosed engineering recipe. Claims about whole-manuscript understanding are not evidence that our small local model can consume a novel.

The [Saliency Engine documentation](https://docs.sudowrite.com/using-sudowrite/1ow1qkGqof9rtcyGnrWUBS/saliency-engine/4KL8gFeLZNvk8CEeXpfwB2) describes selecting relevant story information before generation and respecting author-controlled card/trait visibility, including raw-data access paths. The ranking algorithm is not disclosed. Our prototype independently tests these requirements; it is not a reproduction of Sudowrite's implementation.

Neither page's sample prose, diagrams, modern descriptions or imagined JSON structures are training targets. They are research references only. We separate three workstreams: literary task training, inference-time context selection and independent evaluation. A context selector does not replace a fiction model, and fine-tuning does not supply reliable memory of a user's current manuscript.

## AI diagnosis of the first literary mixture

The [AI diagnostic](../artifacts/literary-mix-ai-review-v1/AI-DIAGNOSTIC.md) examines the eight-case review subset. It is one Codex AI assessment informed by earlier experiment statistics and some labelled outputs; it is not a fully blinded study, an independent human reviewer or a human preference ballot. The A/B/C key was not decoded. Original ballots, protocols, scores and responses remain unchanged and hash-verified.

Concrete findings include:

- A rewrite in every condition reverses breakfast still being underway when the workers arrive into breakfast ending before their arrival.
- Some continuations invent a mother/daughter relationship for Meg and Laura that the passage does not establish.
- Analysis confuses Miss Brill with the remembered English wife, or identifies the wrong person as the intended object of shaking; some responses misquote a plural pronoun as singular.
- One compression puts Julius on the step after the chair dispute, changing the source resolution.
- Meeting a dialogue word cap does not establish compliance with a requested number of spoken turns. A post-hoc quoted-dialogue-line proxy flags likely turn-count failures. It is not an authoritative parser and must be checked manually; these new diagnostics do not replace the original frozen scores.

Newly invented actions in a requested continuation are not automatically contradictions. We distinguish permitted developments or spoken revelations from assertions that an unsupported past event was already established. Stylistic concerns such as generic aphorisms are explicitly AI interpretations, not human verdicts.

Human quality ratings remain zero. The current app model remains unchanged. The next experiment tests a better-aligned curriculum rather than promoting the earlier adapter on word-count results.

## Source-only curriculum v2

The new curriculum contains **244 training examples** and **108 separate Wray validation records**. Five training authors contribute 90 underlying source paragraphs; multiple task views do not become 244 independent literary examples. No generated literary teaching answer, user manuscript, Story Bible content or unreviewed English-PD row is admitted.

The two new sources contribute only sixteen reviewed original-prose paragraphs: Wells's *The Time Machine* and Doyle's *Adventures of Sherlock Holmes*. The [scoped dossier](../rights/dossiers/literary-expansion-2026-10-25.md) records exact digital bytes/spans, author/publication evidence, crosschecks, exclusions, GB/US limits and physical-edition uncertainty. This is an attributed AI evidence assessment under the user's permission-free-source instruction, not author consent, human approval, or legal certification. It does not clear the complete acquired files or authorise publication/upload.

The curriculum adds:

- Anchored Write examples: source prose is the answer to a prompt specifying its opening, ending, genre and upper word cap. This is conditional reconstruction, not an original author-written response to a newly invented semantic outline.
- Explicit upper word caps for continuation, dialogue and craft examples; source answers remain unchanged and fit their instructions.
- Reference-based repair exercises restoring an omitted negation, typography or duplicate from an explicit reference. These are constructed exercises, not genuine author revision pairs.

Curation/source scripts and source reviews are under `curation/literary-mix-v2/` and `artifacts/literary-mix-v2/`. Broad genres, modern writing styles, full scenes and authentic revision demonstrations remain underrepresented. More updates alone cannot resolve those gaps.

## New evaluation rather than reusing exposed tests

The former 24 cases are now exposed development evidence. They remain immutable and are not described as a fresh independent test for curriculum v2.

The new experiment freezes twenty original AI-authored diagnostic cases before baseline inference and training: four separate story worlds times minimal editing, concise voice-preserving rewrite, dialogue, grounded analysis and continuation. The contexts and expected minimal repairs are **evaluation-only**, never literary teaching targets. This is an experimental diagnostic with AI structural review, not the existing formal human-reviewed benchmark. The older pending benchmark is unchanged.

The protocol predeclares word caps, exact minimal repairs, request completion/truncation, source/prompt hashes, one-message requests, empty history, disabled prompt cache and a dialogue-block count proxy. That proxy groups quoted speech by line; multiple speakers on a line or narrative quotation can make it inaccurate. It is supplementary evidence, not a definitive turn or subtext score. All editing tasks have no minimum length. Viewpoint, facts, voice and usefulness still require qualitative review.

Three conditions are the unchanged base, the prior literary-mixture candidate and a fresh-base v2 adapter. The deployed craft model is not renamed or silently replaced by the phrase “prior mixture.” No inference-speed comparison or Muse head-to-head result is claimed. Test contexts never enter the training worker; training, Wray validation and diagnostic inputs are separate files, with lexical leakage checks before freezing.

## Offline context-selection prototype

`foundation/context_selection.py` is a CPU-only reference implementation. It accepts explicit canonical records, field visibility and supplied scene-state conditions; filters before ranking; uses simple lexical/name/alias relevance; and packs whole references under a character allowance. Hidden/foreign/draft/archived data and incompatible conditional facts do not enter its ranker or prompt output. Links cannot expose hidden or omitted entry IDs. It does not infer scene state or validate the truth of visible facts.

Seven tests cover the selection rules, field visibility, incompatible/unknown state, alias boundaries, whole-entry budget, link filtering and read-only behaviour. This remains isolated from all app runtimes. The existing apps do not yet acquire new field-visibility controls, semantic search or automatic chronology from this prototype. A future integration needs an explicit portable schema/contract, full-request tokenizer budgeting, parity fixtures and source/runtime tests in web/PWA, Tauri, iOS and independent macOS. User hidden data must be filtered before any remote inference or embedding request; this prototype itself makes none.

## Execution and promotion boundary

The v2 experiment uses the same pinned 4B eight-bit base, fresh rank-eight LoRA, answer-only labels, one pass and a maximum of 61 updates, with a ten-GB MLX allocation guard. Separate fixed Wray records monitor validation. Previous model and base hashes are protected, only one model runs at a time, and the existing developer inference configuration is restored afterwards. No paid/cloud job, corpus upload, publication, app installer change or default upgrade is included.

See the [v2 training report](literary-mix-v2-training-2026-10-25.md) for actual completion, memory and test results. This document defines the research/implementation work; it does not substitute plans for measured quality evidence. Any promotion still needs independent human review and qualification of the exact packaged runtime on supported hardware.

## Completed outcome

The v2 run completed all 61 updates and 60 comparison requests, but several brevity metrics regressed. It remains experimental. The separate controlled edit-preview pilot returned 4/4 exact repairs versus 1/4 with full-text rewriting on the same four fixtures/current craft model. That is a limited application-mechanics result, not improved model weights or broad literary quality. The current 116-test foundation suite passed. The original serving model/configuration was restored, no app variant or manuscript was changed, and no model was promoted.
