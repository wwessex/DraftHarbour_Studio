# Craft baseline on the fresh development screen

The current craft adapter completed all 12 frozen cases in fresh contexts with zero request errors or truncations. Response order and hashes verified. This is a development baseline with two cases per skill. The observations below combine mechanical checks with an informed AI reading of the responses.

| Skill | Observed baseline |
|---|---|
| Continuation | One of two met the 70–110-word range and both used a single paragraph. The ferry scene makes the bell rope appear to stop the boat mechanically. The kiln scene adds a measured temperature spike that the prompt never establishes. |
| Dialogue | Both met the word cap. The bus exchange had nine turns and the rehearsal exchange seven, against a limit of six. The rehearsal response substitutes hallway access for the offered lobby. |
| Rewrite | Both change the prose. The window version keeps the original sequence and uncertainty, with resentment suggested by the narrator's treatment of the cup. The stair version adds urgency but repeats “frozen” and “freezing” in its first sentence. |
| Scene writing | Both exceed 150 words. The bakery creates a concrete choice but also introduces a competing promise. The audition adds a tuning fork and conductor, making the proposed action harder to follow. |
| Pacing | Both use two paragraphs under 130 words. The station response accelerates through movement but jumps from the footprint to an unexplained sprint. The orchard response slows through perception and then freezes the action. |
| Analysis | Both meet the word cap. The ribbon response quotes two details but asserts a motive and invents an observed reaction. The desk response supplies only one direct quotation and treats an honored guest as established. |

MLX logged that it could not enforce the configured 2,048-token cache limit on one layer. The recorded requests stayed within that budget. The screen and responses remain evaluation-only.

The existing source ledger also identifies 20 previously scoped craft-analysis answers from Wharton and Hamilton. Those were used in the current craft adapter's earlier pilot, so they are candidates for curriculum continuity. They teach craft commentary and need a separate fit check against the new passage-analysis task, which asks the model to cite evidence and qualify interpretation. The baseline supports prioritizing practical scene progression, turn count, and evidence-bound analysis in the expanded curriculum.

[Baseline evidence](../artifacts/curriculum-reset-v30-baseline/baseline.json)
