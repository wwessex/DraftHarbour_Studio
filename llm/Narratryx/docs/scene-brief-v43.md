# Grouped scene facts diagnostic

Craft generated 12 fresh responses on six new briefs. The fact sentences, model and generation settings were held constant. One condition used a single block of prose. The other added possessions, permissions and unknowns labels and line breaks. Presentation order alternated between pairs. A preparation script initially stopped on a field name mismatch before inference. The corrected run completed all 12 requests without errors or truncation.

All 12 responses used one paragraph. Prose met the word range in 6/6 and grouped facts met it in 5/6. The qualitative findings below are an informed AI review.

| Scene | Finding |
|---|---|
| Gauge | Both use chalk and leave the valve alone. Prose treats a reading as proof that the system is ready. Grouped facts introduce ink and connect pressure to the returned wrench. |
| Curtain | Prose closes the curtain. Grouped facts leave it half drawn, add a visible stranger and exceed the word cap. |
| Chart copy | Both copy visible marks while keeping the cover closed. Grouped facts describe only the first three marks but then call the copy a duplicate of the original data. Prose likewise makes an overly broad claim about completeness. |
| Rain | Both wipe the bench, but both treat a dry exterior as evidence that the pouch contents are safe. |
| Bell | Prose infers that the porter heard the call. Grouped facts invent an immediate rescue and take Mina through the gate. The brief establishes a request for help. |
| Shelf | Both use the wedge on the empty section. Prose overclaims that danger has passed. Grouped facts give a more local consequence. |

Grouping by itself produced no consistent improvement in this six-case diagnostic. The repeated pattern is an available action followed by a consequence the evidence cannot support. The useful source additions are scenes in which an action yields a limited observation and the narration leaves uncertainty intact, as well as passages where an unavailable object stays unavailable. These evaluation prompts and responses remain outside training.

This comparison used standalone Apple Silicon MLX. It exercised model inputs only, with application builds and device checks outside scope.

[Mechanical scores](../artifacts/scene-brief-v43/mechanical-scores.json)
