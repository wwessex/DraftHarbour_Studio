# Portable local runtime: development evidence, 24 October 2026

The existing experimental craft adapter was exported and exercised in a separate **macOS ARM64 development package**. This completes the first artifact feasibility gate in the [local/online setup plan](../../../docs/ai-local-and-online-setup-plan.md). It does not complete app-managed installation, setup, Windows execution, hosted accounts or model-quality acceptance.

## Artifact and provenance

The original adapter/base were verified against `configs/narratryx-craft-v1.json` before export. The installed Unsloth MLX exporter merged the adapter into the cached base, converted the text weights and quantized them with llama.cpp. No training, bulk corpus download, paid job, corpus upload or public model publication occurred. Original source artifacts and the frozen craft experiment were preserved.

| Item | Identity |
|---|---|
| Base revision | `5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d` |
| Source adapter SHA-256 | `09f950e0954105b4b5bf1cdd5c7a4ee882d617742aadad6ec33c1dda5af84688` |
| Portable model ID | `narratryx-craft-v1-q4-k-m` |
| Format | GGUF, Q4_K_M, text only |
| Text model size | **2,708,804,224 bytes**, about 2.71 GB / 2.52 GiB |
| Text model SHA-256 | `080c17b208b52a8823121824a27cfb9b03c34fa322faaf78b089e8273a15c71d` |
| Development bundle manifest SHA-256 | `bec8fcc53a370b0a19de9cef4a8f4234add5a31feb54dcad56a8b34b260eb4e3` |
| Installed converter/runtime source | `unslothai/llama.cpp`, tag `b11798-mix-f8a7950`, commit `ec0da70e9753093a66c34b9e2b04909d9b03f0ba` |

Export took 379.32 seconds on this development Mac. The exporter retried text conversion without an MTP head because that head was absent from the source. A separate vision projector was also generated and is excluded from the writing package. Model size is not installer size, download size, total disk requirement or peak RAM.

Weights and runtime binaries remain ignored local artifacts. The checked-in [development catalog](../configs/portable-craft-v1.dev-catalog.json) contains identities/hashes, **no download URL and no public-release approval**. Model and runtime license files and modification notices accompany the local bundle. The base model declares [Apache 2.0](https://huggingface.co/Qwen/Qwen3.5-4B/blob/main/LICENSE); the runtime source includes its MIT license. Complete notices, artifact licenses, redistribution eligibility, signing and notarization still need release review before distribution. This report grants no new rights clearance for source literature.

## Runtime contract exercised

`runtime/packaging/bundle.py` is a standard-library developer harness. It verifies a manifest against a separately trusted catalog hash, checks platform/file hashes and sizes, rejects unsafe paths, symlinks and unlisted files, and launches only the pinned executable with fixed arguments. It owns the child process, binds IPv4 loopback, chooses a temporary port and generates an internal credential in a private temporary directory. The credential is passed as a file, never a command-line secret or user-entered key. HTTP requests bypass configured proxies and do not follow redirects. Shutdown terminates the owned process and removes private credentials/logs.

The copied runtime and shared libraries ran from the package directory. The inference child uses native llama.cpp; it does not need the training environment. **The current harness still needs Python and is not the end-user app runtime manager.** Installed native app managers, resumable downloads, update/rollback, cancellation, crash recovery and device resource checks remain to implement. The harness verifies local developer-owned files; a future installer must also provide private installation ownership and safe extraction/atomic replacement.

Actual Mac smoke checks covered Write, Rewrite and Continue, authenticated discovery, unauthenticated discovery returning 401, nonempty drafts, child exit and credential cleanup. A repeated warm-cache startup measured 2.95 seconds including selection and launch verification (1.79 seconds for launch verification/startup). The first smoke measured 8.62 seconds; these are observations, not a startup guarantee or hardware recommendation. See local `artifacts/portable-runtime-smoke.json`.

## Export comparison

The original frozen sixteen craft prompts were replayed as separate single-message requests, no prior assistant history, thinking disabled, deterministic sampling settings and no reused prompt cache. Every rendered chat prompt matched the cached source tokenizer exactly. The repeatable CLI is `python -m runtime.packaging.evaluate`; it checks frozen input and tokenizer metadata hashes, refuses output overwrite and stops on template mismatch. It does not rewrite or replace the original experiment. Responses and diagnostics remain local under `artifacts/portable-evaluation-v1/` and `artifacts/portable-evaluation-v2/`.

Both the initial pass and the committed CLI repeat completed all sixteen responses with **zero errors, zero truncations and zero reused prompt tokens**, with the same narrow mechanical scores:

| Diagnostic | Original MLX craft candidate | Portable GGUF candidate |
|---|---:|---:|
| Exact minimal duplication repair | 2/4 | 2/4 |
| Continuation word limits | 1/4 | 3/4 |
| Editing word limits (no minimum) | 4/4 | 4/4 |
| Dialogue word limits | 2/4 | 3/4 |
| Compression word limits | 4/4 | 4/4 |

These outputs can differ because merging, conversion, reduced precision and inference engines differ. Matching chat formatting and mechanical constraints **do not prove equivalent literary quality or improvement**. There are no completed blinded human quality ratings. No promotion, new training or app default change follows from these results. The [original pilot report](craft-source-pilot-2026-10-20.md) remains the training evidence.

## Reproduction and boundaries

From `llm/Narratryx`, CPU safeguards run with:

```bash
.venv-foundation/bin/python -m unittest discover -s tests -v
```

On 24 October this completed **93 tests in 103.792 seconds**, including nine new package/diagnostic tests. Those tests use a fake executable/HTTP process and exercise trust/hash/path rejection, changed-package rejection before launch, platform/output limits, private credentials, redirect rejection, fresh requests, process shutdown and failed-start cleanup. No model or GPU is needed by the tests. This run is separate from the real-model smoke/comparison above.

Export requires the already installed compatible Unsloth/MLX environment and exact cached base/adapter; it is an explicit developer operation:

```bash
python -m runtime.packaging.export_candidate --output artifacts/new-export --llama-source /absolute/path/to/installed/llama.cpp
python -m runtime.packaging.bundle build --export artifacts/new-export --runtime-bin /absolute/path/to/installed/llama.cpp/build/bin --output artifacts/new-bundle --model-id narratryx-craft-v1-q4-k-m --model-license /absolute/path/to/reviewed/base/LICENSE
python -m runtime.packaging.bundle verify --bundle artifacts/new-bundle --manifest-sha256 TRUSTED_HASH_FROM_BUILD
python -m runtime.packaging.evaluate --bundle artifacts/new-bundle --manifest-sha256 TRUSTED_HASH_FROM_BUILD --tokenizer /absolute/path/to/pinned/cached/base --output artifacts/new-comparison
```

Do not replace a trusted catalog hash with one calculated from an untrusted downloaded manifest. Re-exported bytes may differ across tools; a new export must receive its own reviewed identity and comparison.

This milestone changes **model tooling only**. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS application sources/assets are unchanged. No new platform app build or device run is claimed for this milestone. Actual native inference was tested on the development Mac; Windows/Linux CPU execution, x86 artifacts, iOS runtime and browser companion integration are untested. The separate existing MLX developer service remains the app trial path.

The next implementation gate is native process ownership and readiness in both Tauri and the independent macOS app, followed by setup/main-interface choices. Online AI remains separate work: account/session support and a hosted gateway do not yet exist. Drafting must continue without AI or sign-in; local failure must never silently transmit text online.
