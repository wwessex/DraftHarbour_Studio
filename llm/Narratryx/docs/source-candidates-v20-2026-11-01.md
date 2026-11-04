# Source-only teaching candidates — 1 November 2026

Prepared **nine traceable candidates**, with eight selected in a **28-example review proposal**. This follows the [fiction prompt comparison](fiction-questions-v19-2026-11-01.md): clearer questions alone did not reliably fix scene progression or constraint fidelity. This work improves the available task demonstrations; it does not establish model improvement. **No training or inference occurs.** The selected craft model and all applications remain unchanged.

## Candidates and sampling decisions

| Candidate | Published demonstration | Proposal decision |
|---|---|---|
| Wilson resistance continuation | After Frado resists, Mrs. B. lowers her weapon and carries the wood; Frado recognises the effect | Replace the full-scene resistance lesson |
| Harper market departure | A servant responds to the coded exchange and leaves at a quicker pace | Replace the full-scene market lesson |
| Hopkins invitation departure | Sappho accepts, then Dora says goodbye and leaves | Reserve: overlaps the retained event-time repair |
| Opie conditional escort | A refused payment leads to a limited escort agreement and fallback arrangement | Add |
| Opie unfulfilled wait | Clifford waits, boards the coach and eventually gives up expecting Agnes; she does not appear | Add |
| Opie garden action | Agnes actually ties the flowers while Fitzhenry follows attentively | Add |
| Opie contrasting aims | Agnes's reluctance to intrude meets Fanny's affection, then Agnes explains her need for support | Add as narrated dialogue |
| Opie reported money | Clifford performs alarm and makes a claim that Agnes believes; narration distinguishes performance from belief | Add |
| James dog-description revision | Documented edition variant changes “contemplated” to “took in”, preserving the surrounding sentence | Add as a limited lexical revision |

The pool contains three complete-paragraph continuations, four directed prose scenes, one narrated dialogue scene and one genuine author-edition revision. The historical answers are not modernised or rewritten by AI. Briefs are AI-authored after reading the sources; they are not historically commissioned prompts or independent tests of invention.

Agreements and actual outcomes are explicitly permitted where the source contains them. The escort and invitation examples must not be mislabelled as demonstrations of preserving missing consent. The Opie exchange has three spoken turns **with narration**, not dialogue-only output. No new dialogue-only demonstration is claimed.

The James variant is genuine but small: the later text is 45 whitespace-delimited words, and “took in” is not a shorter-word-count replacement for “contemplated”. It does **not** fill the gap in substantive concise paragraph revisions, and no general preference for the later edition is implied. The two existing broader James revision lessons remain in the proposal. No suitable new substantive revision pair was established within the inspected scope.

## Proposal composition and exposure

The proposal grows from 22 to **28 training records**: 20 broader prose/revision lessons, the same five semantic repairs and the same three structural controls. Two full-scene parents are replaced rather than sampled alongside their continuation variants. Six lesson records are additions relative to the latest mixture: five Opie paragraphs and the James edition pair. Those six additions use seven edition-specific source intervals because the revision pair has two editions.

The eight selected candidates are source-disjoint from the retained lessons, comparing canonical source hashes and intervals even when rights-record IDs differ. The invitation continuation is excluded because its parent span overlaps `sr14-event-times`. It remains a review alternative, not a second presentation of the same material in the proposal. No training recipe or automatic sampling schedule is created.

There are **no new authors or works**. Source prose appeared in earlier preparation or source/task corpora; these candidates are not asserted to be unseen training material. The useful change is task presentation and coverage, not fresh-author diversity. Seven training authors remain separate from Wray's 16 previously exposed validation monitors. Monitor content, roles and messages are preserved; only the proposal's dataset-version label changes. Wray monitors are not fresh literary-quality tests.

The previous 44 primary development prompts remain outside the training prompts. Five explicitly labelled seen-training-fit cases intentionally match retained repair lessons and are checked separately, not misrepresented as independent evaluation. No v17–v19 generated response, guiding-question example, AI review note or held-out literary passage enters training.

## Rights and exact provenance

Preparation uses the existing `grounding-balanced-v1.scoped.jsonl` ledger and its exact GB/US training limits. No ledger, approval or rights scope is enlarged. Existing source decisions retain their original human/AI attribution; this work records an **AI source/task preparation review**, not new human quality approval or legal certification.

The continuation contexts and answers are exact contiguous substrings of their existing parent spans, separated only by source paragraph whitespace. The additional Opie paragraphs must be present in the pinned screened scope manifest and its approved export. Original raw offsets and span hashes are checked with CRLF preserved, then mapped explicitly into the universal-newline coordinates used by foundation validation. Only newline normalisation is applied to those answer targets; line wrapping, spelling and historical phrasing remain intact. No prose is fetched outside the recorded spans. The James pair retains both edition records and unchanged source texts.

Dataset schema, exact-source checks, approved-scope membership, source hash checks, author/work splits, within-proposal overlaps, proposal membership and unchanged prior evidence all pass. These are structural and provenance checks against existing decisions, not a new legal opinion or proof of literary quality.

The full CPU foundation suite passes **235 tests in 70.671 seconds**, including three new raw-offset, tamper-rejection and complete-paragraph derivation tests. The final evidence verifier and Python compilation pass. No application test run is represented by this CPU result.

## Tokenizer checks and artifacts

The offline cached tokenizer preflight passes for all **44 records**: 28 proposed training records plus 16 exposed monitors. Maximum length is **499 tokens**, below the 2,048-token context limit. The training records contain **3,033 supervised tokens**. Answers round-trip exactly through tokenization, proposed labels mask the prompts, and no target is truncated. **No model weights are loaded.** This checks proposed label construction; an installed collator/trainer audit is still required before execution.

Scripts are in `curation/source-candidates-v20/`, with derivation helper `foundation/source_candidates.py`. Local artifacts in `artifacts/source-candidates-v20/` include:

- `REVIEW.md`: all nine briefs and exact published answers.
- `candidates.jsonl` and `derivations.jsonl`: source-bound candidates, original/canonical coordinates and derivations.
- `records.proposed.jsonl`: 28 training records and 16 unchanged exposed monitors.
- `verification.json`, `tokenizer-preflight.json` and `final-verification.json`: checks and input/output hashes. The final verifier distinguishes six added lesson records from seven edition-specific intervals.

A tracked preparation lock records source/artifact hashes and results without including weights, literary responses, private state or executable training data in Git.

Read-only verification:

```bash
cd llm/Narratryx
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/source-candidates-v20/verify.py'); print(m['verify']())"
```

## Next step and limits

Next, audit the installed training collation and freeze a bounded recipe before executing another pilot. The source/task preparation review is complete; the packet remains available for sampling review. Preserve the selected model and original evaluations. A 28-example historical curriculum remains very small and does not supply broad modern fiction, sustained dialogue, genre diversity or Muse-equivalent capability. Substantive author-revision pairs and independent human literary ratings remain evidence gaps.

Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS have no source, configuration, default or generated-asset changes. No app builds or device/runtime checks are run for this isolated preparation. There are no training jobs, inference requests, corpus downloads, paid jobs, uploads, model publication or promotion.
