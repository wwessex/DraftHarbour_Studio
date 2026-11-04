# Local base model comparison

The untuned Qwen3.5-4B, craft, and cached Gemma 4 E4B completed the same six prompts. They received identical user prompt bytes and hand-selected facts, fresh contexts and a 384-token output cap at temperature zero. The Qwen variants used MLX with the craft adapter disabled or enabled. Gemma used Ollama and the local Q4_K_M artifact. Tokenizers, chat templates and inference backends differ, so this compares deployable model configurations. The Gemma artefact's model layer is 9.61 GB on disk and Ollama reported offloading all layers to the M5 GPU. This stage measured neither cross-platform deployment nor fine-tuning feasibility for Gemma.

| Check | Untuned Qwen | Craft | Gemma |
|---|---|---|---|
| Word ranges | 1/4 | 3/4 | 3/4 |
| Wrench ownership | Recasts the loan as theft and returns the wrench to Leena | Same error | Preserves the wrench's absence, but refers to chapter one in prose |
| Photograph permission | Moves and photographs through glass, with the lower corner unreadable | Same action and uncertainty | Same action and uncertainty, within the requested length |
| Harbour Continue | Invents an unsupported boarding signal | Same signal | Keeps boarding open, but exceeds the cap and shifts to first person |
| Harbour Write | Lowers the lamp and exceeds the cap | Lowers the lamp but restores the traded token | Fits the range and stages a verbal request instead of applying the lamp rule |
| Rewrites | Both change the prose and preserve the main uncertainty | Both change the prose and preserve the main uncertainty | Both change the prose and preserve the main uncertainty, with a small ambiguity shift in the landing rewrite |

The first Ollama attempt timed out during the readiness probe while the server was discovering the GPU. A separate retry handled startup timeouts and completed all six Gemma responses. The private server was terminated after evaluation. Both Qwen reference runs completed, and hashes and prompt identity checks passed for all 18 responses.

Gemma is a useful challenger for ownership and permission handling. Its harbour errors and tied word-range score leave a base switch unsupported on this sample. Use more independent scenes before selecting a model to fine-tune. The comparison used three earlier development prompts and three new diagnostic prompts. The originality holdout remains reserved. This was local inference research on Apple Silicon, with application and Windows device checks outside scope.

[Comparison evidence](../artifacts/base-comparison-v41/comparison.json)
