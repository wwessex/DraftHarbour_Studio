# Guarded runner for the v26 pilot

The runner binds the frozen 34-update request to the existing process guards and the base, craft and candidate comparison. Its default entry point checks the frozen inputs, environment and worker configuration. The explicit execution flag starts the phases in order and stores their logs in a dedicated run directory. The runner rejects an existing run directory or an occupied legacy service port.

Preflight stopped because Unsloth 2026.11.1 is installed and the recipe pins 2026.10.11. The CLI training module, worker and MLX batching source also differ from the frozen hashes. The new installation needs a fresh preprocessing, batching and worker configuration audit before the recipe can be amended. The four existing trainer-recipe tests passed and all runner modules compiled. Preflight reached the source hash check before any worker or evaluation launched.

Application work was outside the scope of this model experiment. Platform build and runtime checks were skipped.
