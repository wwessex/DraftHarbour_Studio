# Second local base model diagnostic

Untuned Qwen, craft and cached Gemma 4 E4B completed all 18 requests on six new, identical briefs. The mechanical scorer verified response order, prompt hashes and stop reasons. All three configurations passed four of six cases on the explicit format, length and quotation checks. Gemma used Ollama and Qwen used MLX, so this compares the local configurations available for deployment.

| Case | What the prose comparison found |
|---|---|
| Lantern | All three preserve the absent lantern and show a visible marker, but each adds an unestablished resource. Qwen and craft add a nail and tear clothing. Gemma adds crimson thread. |
| Sealed case | All keep it closed and use the shelf. Gemma fits the length and leaves the instrument unexamined, but makes the mechanics of moving the case and the drop unclear. Craft makes the dripping cease when the case touches the shelf. |
| Corridor rewrite | All revise the supplied paragraph, preserve first person and retain the unknown voice. Gemma adds tension through sensory detail. |
| Parcel dialogue | All fit the turn count. Gemma proposes relaying the message by photo while retaining the receipt, though its first statement of the rule conflicts with the later one and it assumes access to a camera. Craft reverses who must keep the receipt. Untuned Qwen preserves the receipt rule but drops the message objective. |
| Stitch pacing | All establish a quieter opening and take action at the hinge. Gemma leaves the thread outcome open but exceeds the cap. The two Qwen variants both say the thread is pulled free before questioning whether it broke. |
| Letter analysis | Gemma separates observations and inference more clearly. All three fail the requirement to quote two details. Both Qwen variants invent hesitation about opening the window. |

The prose review is an informed AI reading. It records specific failure modes without assigning a release-quality score. Across this and v41, Gemma has useful gains on some ownership, permission and analysis cases. It has yet to show a consistent advantage in resource grounding, format or continuity. Craft remains the selected model. The 24-case originality holdout stays reserved.

A useful next intervention is to test a compact scene brief that explicitly separates possessions, permitted actions and unresolved facts, using the same model and fresh scenes. That would measure whether the failures respond to better representation before another adapter run. If those failures persist under the clearer input, use them to select authentic training scenes and consider a larger model separately from the local hardware target.

This comparison used standalone inference on Apple Silicon. Application builds and Windows or iOS device checks were outside scope.

[Mechanical results](../artifacts/base-comparison-v42/mechanical-scores.json)
