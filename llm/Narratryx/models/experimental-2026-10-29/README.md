# Narratryx experimental model archive

This repository's [experimental release](https://github.com/wwessex/DraftHarbour_Studio/releases/tag/narratryx-experimental-2026-10-29) archives the actual custom **MLX LoRA weights**, not merely a model name. Download an adapter ZIP and `SHA256SUMS` from that release. Both adapters require the separately obtained exact base specified in [manifest.json](manifest.json); the ZIPs are not standalone models or Windows installers.

| Asset | Identity | Status |
|---|---|---|
| `narratryx-craft-v1-mlx-adapter.zip` | Existing craft profile, five updates | Existing experimental selection |
| `narratryx-grounding-v5-mlx-adapter.zip` | Latest completed balanced trial, twenty updates | Research candidate; not promoted |

The archive includes `adapters.safetensors`, its exact `adapter_config.json`, this card, manifest, Apache-2.0 licence and modification notice. No raw books, datasets, scans, evaluation answers, manuscripts, credentials or reviewer keys are included. The adapter/config SHA-256 values are recorded in the manifest, alongside base revision and weight/metadata hashes. ZIP checksums are in `SHA256SUMS`. This is a backup/public research artifact, not an application upgrade. Installing it must not silently replace a user's chosen model.

The [base model](https://huggingface.co/mlx-community/Qwen3.5-4B-MLX-8bit) identifies [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) and Apache-2.0. Included upstream licence and [NOTICE](NOTICE) retain attribution and identify these trained modifications. Training source evidence concerns selected expired original prose and GB/US uses; there is no blanket worldwide legal certification or source-provider endorsement. Earlier local-only publication authorisations are not claimed to have covered this upload: the user explicitly requested model upload on 29 October 2026. That request authorises these model artifacts, not corpus redistribution. Existing frozen rights records are preserved.

The v5 candidate trained on 80 records (56 source-prose and 24 structural lessons) with no generated literary teaching targets. All 192 responses completed, but clock-state exact accuracy remained 6/24 in all conditions and unsupported temporal/attribution assumptions persisted. Eight exact repair checks passed in all conditions; prose format results were mixed. Human literary-quality ratings remain zero. Neither training completion nor this archive establishes a reliable quality upgrade or Muse equivalence.

For restoration, verify the ZIP checksum, then the extracted adapter/config hashes against the manifest, and use the pinned base with the existing Narratryx MLX inference service. Keep the selected craft and trial adapters in separate directories. Apple Silicon training/inference evidence does not establish cross-platform runtime or installer support. Application users do not need to train these models.

The allowlisted archive builder is `llm/Narratryx/curation/model-archive-v1/package.py`. It verifies exact source weights/configuration hashes, packages only six specified files, tests ZIP integrity and rechecks the embedded hashes. Its output stays under ignored `artifacts/model-archive-v1/`.
