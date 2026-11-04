# Narratryx target against Sudowrite Muse

The product target is comparable results on fiction writing tasks, with a local option on ordinary Windows and Mac computers. The model target is competitive fiction prose when given equivalent instructions and story context. Track the model and the editor workflow separately so a failure can be attributed to the writing model, the context supplied, or the product interaction.

Sudowrite describes Muse as a proprietary model for fiction. Its documentation separately describes the Saliency Engine selecting relevant Story Bible information for prose generation. These public descriptions inform the workflow comparison. They leave the base model, dataset and training recipe unknown. [Muse](https://sudowrite.com/muse) · [Model overview](https://sudowrite.com/blog/what-is-sudowrite-muse-a-deep-dive-into-sudowrites-custom-ai-model/) · [Saliency Engine](https://docs.sudowrite.com/using-sudowrite/1ow1qkGqof9rtcyGnrWUBS/saliency-engine/4KL8gFeLZNvk8CEeXpfwB2)

| Capability | Comparable result |
|---|---|
| Write and Continue | Produces usable scene-length prose from a brief or prior passage. Characters act for distinct reasons and those actions change the scene. Maintains viewpoint, voice, tense and requested pacing. |
| Rewrite | Makes the requested stylistic change, preserves facts and ambiguity, and respects the selected text boundary in the editor. |
| Dialogue and alternatives | Delivers distinct voices and subtext. Regeneration offers different credible actions or turns in the conversation while preserving story constraints. Check overlap with known sources separately. |
| Multi-scene continuity | Uses the right character, timeline and world facts across chapters. Ignores irrelevant facts and respects writer-controlled visibility. |
| Local delivery | Measures time to first text, generation speed, peak memory, and completion on representative Mac and Windows systems. Authors use an existing model through the provider interface. |

The current 50-example pilot provides a working training path and short-form regression evidence. It regressed on three checks, so craft remains the selected model. Neither has a matched Muse result or a demonstrated multi-scene quality advantage. The frozen 24-case originality holdout is useful for a local comparison across six skills. Add separate longer scenarios to measure chapter continuity and prose endurance. [Latest pilot](source-training-v38.md) · [Originality holdout](holdout-v36.md)

## Comparison and training decisions

1. Build original test projects with recurring characters, facts introduced in earlier scenes, deliberate distractors, and explicit author-only facts. Use briefs, scenes and permissions created for evaluation. Keep them out of the training corpus.
2. Compare base and craft with fixed inputs. For local runs, compare a model receiving the correct hand-selected facts with the same model receiving the app's selected facts. If the correct facts improve the result, investigate context selection. If the model still fails, prioritize the writing model or training targets.
3. When legitimate Muse output is available, run the same creative intent with the same supplied story material. Record the product workflow and settings and disclose any unavoidable differences in context or sampling. Judge anonymized prose pairs with evidence and reversed order. Separate format, continuity, prose preference, and run-to-run variation. Human review is optional.
4. Train for demonstrated gaps using a broader mix of exact, rights-verified targets, especially complete scenes and longer continuations. Keep model comparisons controlled. Use a stronger replaceable model as a benchmark if the current base plateaus on the longer tasks. Reserve any paid or hosted run for its separately authorized scope.
5. Claim comparable performance only for workflows and hardware that have passed the matched comparison. Treat inconclusive scores as inconclusive and keep craft selected until a candidate clears the automatic gates.

Muse responses are evaluation references. They stay outside training. This stage defines the comparison. It does not report a Muse score or execute the longer workflow tests.
