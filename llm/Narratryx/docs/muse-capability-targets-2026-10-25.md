# Literary-model development toward a Muse-like writing experience

25 October 2026. Product capabilities are the target; this is not a claim that Narratryx reproduces or matches Sudowrite's proprietary model.

## What the reference establishes

[Sudowrite's Muse page](https://sudowrite.com/muse) advertises distinctive prose, believable dialogue, voice matching, specific descriptions, consistent viewpoint/tense, pacing, compelling openings/endings, longer scenes and Story Bible adherence. It also describes a multi-step refinement workflow. These are vendor claims, not measurements of Narratryx. The [Muse documentation](https://docs.sudowrite.com/using-sudowrite/1ow1qkGqof9rtcyGnrWUBS/sudowrite-muse/4k9bFDMSyic6mFPkYFHrkZ) describes fiction-specific training and attention to clichés. Neither referenced page supplies a reproducible training corpus, recipe, weights or enough information to reconstruct the proprietary system.

Our task is an independently developed writing assistant with comparable useful capabilities. Do not copy its sample prose into training, scrape user stories, distil protected outputs without suitable permission, or infer a licence to proprietary materials from a public marketing page. No Muse account, paid subscription, live competitor generations or head-to-head benchmark was used in this experiment.

## Capability map

| Capability | Next local experiment | Evidence still needed |
|---|---|---|
| Continue and directed prose | Source-derived continuation targets conditioned on an opening fragment | Blinded ratings of new fiction across varied genres; original direction-to-scene demonstrations are still absent |
| Rewrite and editing | Explicit duplicate repair with assistant-only loss; preserve exact punctuation and voice | Genuine author revision pairs and substantive, restrained edits; a repair proxy does not teach all editing |
| Dialogue | Fourteen next-line targets from scoped Opie prose | Longer exchanges with distinct wants, character voices and subtext; modern registers remain underrepresented |
| Narrative analysis and craft | Twenty attributed Wharton/Hamilton answers | Grounded interpretation of new passages rather than merely repeating historical advice |
| Pacing, scene shape and storytelling | Historical craft instruction plus compression/voice diagnostics | Suitable source-derived demonstrations of scene revision, escalation, openings and endings; no invented teaching answers admitted |
| Style and originality | Evaluate voice retention and unwanted repetition | More authors/genres, controlled style comparisons and human review; reduced phrase counts alone are not proof of better prose |
| Longer scenes | Not established by a 512-token response allowance | Larger-context and longer-generation tests on the exact deployment runtime, scene continuity and complete ending checks |
| Story Bible consistency | Separate read-only inference references already implemented in the app | Broader retrieval/contradiction and omission tests; never memorise user project facts through training |
| Multi-step refinement | Separate future inference workflow through provider interfaces | Compare single-pass versus draft/review/revise with the same model; measure quality, latency and factual regression |

The trial trains 142 examples, using a fresh adapter rather than repeatedly extending the current craft adapter. Wray's 108 derived examples are reserved for this candidate's validation; Wray appeared in older exploratory adapters and is not a pristine project-wide holdout. Sixteen evenly spaced records monitor validation before any result is seen. Mansfield and Chesnutt remain evaluation-only. Their contexts were already used in previous diagnostics; the new protocol does not pretend they are previously unseen research material.

## What will make the next stage materially better

1. Complete the blinded comparison of base, current craft adapter and new mixture. Keep mechanical scores, AI inspection and human ballots distinct. Do not call word-limit adherence literary quality.
2. Expand exact-edition clearance and source diversity within the permission-free-source constraint. Prioritise genuine revisions, narrative/dialogue examples and independently authored craft commentary. English-PD remains a discovery source until individual editions/spans pass the rights process.
3. Improve task alignment before expanding epochs. For directed Write examples, construct and audit task instructions from explicit facts in a cleared passage, retaining that unchanged passage as the answer target. Generated task instructions are distinct from generated literary teaching answers. Preserve the fact-to-span mapping and reject prompts that require unsupported events. Source-only training cannot be described as supervised original scene generation or author-quality revision when its targets do not demonstrate those skills. Leave unsupported categories empty rather than fabricate targets or human approval.
4. Develop a new, frozen independent task set spanning genre, voice, viewpoint, dialogue, pacing and longer scenes. Include several decoding seeds for creative tasks in a later study; today's deterministic comparison is a controlled diagnostic, not the full creative distribution. Use blind preferences with evidence and uncertainty, then compare against Muse only if an appropriately authorised comparison is available.
5. Reassess the base model only after data/evaluation improve. The existing 4B quantised base fits bounded development on the 16 GB Mac; model size alone is not literary quality. Prepare larger-model/cloud experiments only with measured requirements, a concrete spending cap and upload approval. No paid job is launched here.
6. Qualify the exact exported, quantised model/runtime on supported Windows and Mac hardware before release. Keep a versioned model catalogue and rollback; ordinary users run inference and never train locally.

The current user's exclusion of generated literary teaching targets remains in force. User manuscripts and Story Bibles are not training inputs. App runtime/defaults, installers and existing model packages stay separate from this experiment. A promising experimental adapter still requires independent quality review, packaging validation and an explicit promotion decision.

## Follow-up evidence

The [additional Muse/Saliency research and implementation report](muse-followup-2026-10-25.md), [v2 training comparison](literary-mix-v2-training-2026-10-25.md) and [precision-editing workflow pilot](anchored-edit-inference-2026-10-25.md) record the next executed phase. Neither the new adapter nor the offline prototypes were automatically promoted to applications.
