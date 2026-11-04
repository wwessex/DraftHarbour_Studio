# Unsloth installation audit for v26

Unsloth 2026.11.1 preserved every token and label across 34 training records and 16 exposed monitors. The installed preprocessing and batching reproduced the earlier audit at batch sizes one and two. All 3,706 training tokens and 1,709 monitor tokens retained their supervision, with 153 and 242 padding positions ignored in the two-record batches.

The installed worker produced the expected configuration for the frozen 34-update recipe. The runner now verifies a separate installation amendment with the new package version and source hashes, alongside the original protocol and worker configuration hashes. Its default preflight passed. Torch emitted a macOS diagnostic about multiprocessing output redirection during configuration. Training and inference remain pending.

Four targeted trainer-recipe tests passed. This was a model tooling audit on Apple Silicon. App build and device checks were outside the scope.

[Installation audit evidence](../artifacts/pilot-recipe-v26-install-audit/amendment.json)
