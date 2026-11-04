# Local pilot recipe — 3 November 2026

The frozen recipe presents each of the 34 audited training examples once, with 16 exposed monitors and a 34-update cap. It starts a fresh LoRA adapter from the pinned Qwen base. It retains the previous pilot's batch size of one, 2,048-token context, seed 42, rank 8, alpha 16, and learning rate of 5e-5. Packing is disabled and the checkpoint starts empty. The recipe pins the token rows, installed source, cached model metadata, base weights and craft comparator.

The comparison uses base, current craft and the new candidate on the same 44 previously exposed regression prompts. Five prompts that overlap the training set are scored separately as fit checks. Each condition gets a fresh conversation for each prompt, for 147 proposed requests total. This comparison measures regression and fit. An independent literary assessment would require fresh material and human review.

The execution wrapper must enforce a 20-minute phase deadline, a process-tree RSS cap of 10 billion bytes and a reported MLX peak cap of 10 GB. Warnings, errors, nonfinite metrics, cap breaches and truncated evaluation responses stop the run. The existing 28-update runner needs to be bound to this recipe with the new step limit before launch.

The freezer reproduced all 44 retained token rows exactly and matched the audited counts for all 50 records. The settings and frozen file hashes verified, and four targeted trainer-recipe tests passed. This stage prepared the recipe and loaded the cached tokenizer. Training and comparison results are pending.

[Local frozen protocol](../artifacts/pilot-recipe-v26/protocol.frozen.json)
