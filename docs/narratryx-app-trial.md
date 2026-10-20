# Narratryx experimental application trial

Implemented on 20 October 2026 following the [readiness assessment](narratryx-integration-readiness-2026-10-20.md). This is an opt-in technical trial. The [craft pilot](../llm/Narratryx/docs/craft-source-pilot-2026-10-20.md) has mixed results and no completed blinded human literary ratings. Integration does not establish improved fiction quality or promote the adapter.

## Architecture and model identity

All clients use the existing custom/OpenAI-compatible provider boundary. The shared React implementation covers web/PWA, Windows/Linux Tauri and Capacitor iOS. Native macOS has its own setup control and URLSession implementation. No client imports training code, ships checkpoints, starts training or loads MLX. Offline drafting and current provider defaults remain available.

The optional [local service](../llm/Narratryx/runtime/local/) runs independently on Apple Silicon. The [serving manifest](../llm/Narratryx/configs/narratryx-craft-v1.json) pins:

- Candidate ID: `narratryx-craft-v1`.
- Comparison ID: `narratryx-base`, the same loaded model with adapter modules disabled per request.
- Base: `mlx-community/Qwen3.5-4B-MLX-8bit`, revision `5319bbbe4f1cbe6c0b3c80f4f7de4f0338c3906d`.
- Adapter: local `artifacts/craft-training-v2/adapter`, SHA-256 `09f950e0954105b4b5bf1cdd5c7a4ee882d617742aadad6ec33c1dda5af84688`.

Startup verifies hashes of weights, tokenizer, model metadata and adapter configuration before loading. A private execution copy points the loader at the exact cached snapshot; original artifacts remain unchanged. `/v1/models` and completion metadata expose version/hash identity, never credentials or local paths. Unknown model IDs fail rather than silently use the base. New model IDs/endpoints remain configurable without a manuscript format migration or a client-specific training dependency.

## Start the optional developer service

This requires the existing, separately installed Unsloth Studio MLX environment and the exact local artifacts. A fresh clone does not contain the ignored weights/adapter; foundation requirements alone cannot run inference. The environment tested here used Unsloth 2026.10.7, MLX 0.32.4, mlx-lm 0.32.2, mlx-vlm 0.7.8 and Transformers 5.5.0. The engine uses that installation's Studio backend APIs; compatibility with a different installation/version must be checked.

From `llm/Narratryx`, using the Python executable from that inference environment:

```bash
python -m runtime.local --port 8890 \
  --allow-origin http://localhost:5173 \
  --allow-origin http://127.0.0.1:5173 \
  --allow-origin http://localhost:1420 \
  --allow-origin http://127.0.0.1:1420 \
  --allow-origin tauri://localhost \
  --allow-origin http://tauri.localhost \
  --allow-origin https://tauri.localhost \
  --allow-origin capacitor://localhost
```

The default host is `127.0.0.1`. Startup creates a dedicated random access token in `artifacts/local-serving/access-token`, mode 0600, and prints its **path only**. Enter that token in the app's API Key field; do not use Studio administrator credentials. Keep the token file private and out of Git/project exports. Stop the process with Ctrl-C; restart to clear an unhealthy backend. The service has no auto-start/install hook.

Optional flags select `--base-snapshot`, `--adapter`, `--manifest`, `--token-file`, `--host` and `--port`. Changing artifacts requires an intentionally updated reviewed manifest. Offline model resolution prevents accidental downloads or resolving a mutable Hub revision during startup.

## Configure a test installation

Use a disposable project and short passages initially.

| Application | Setup |
|---|---|
| Web/PWA, Windows/Linux Tauri, Capacitor iOS | Settings → Local AI (Custom LLM) → **Set up Narratryx (experimental)**. Enter service **base URL**, e.g. `http://127.0.0.1:8890` on the serving Mac, and access token. The app appends `/v1/chat/completions`. Use **Test Connection**, then existing AI writing tools. The experiment model selector switches candidate/base; the model field also accepts future service IDs. |
| Native macOS | AI tools → Provider → **Set up Narratryx (experimental)**. Enter the **full URL**, e.g. `http://127.0.0.1:8890/v1/chat/completions`, access token and **Save Provider**. Select the saved provider in the AI tools/chat. To compare, use model `narratryx-base`. |

Setup does not carry another provider's secret into the new endpoint. Shared setup selects the experimental provider only after a click and leaves the endpoint blank until entered. Native setup prepares a new provider; an existing saved provider remains intact. To roll back, select the prior provider or the comparison base. Review responses through existing suggestion/application controls; the model cannot directly write a manuscript or run tools.

## Write, Rewrite and Continue

Open **Tools → AI Writing Tools** in web/PWA, Tauri or iOS. Native macOS exposes the same buttons in **AI Writing** and **AI Suggestions**. They use the configured provider, including the experimental Narratryx service; they require no retraining.

- **Write:** enter instructions, then generate a new passage to append. It can start an empty chapter.
- **Rewrite:** select a passage in the editor before opening the tools. With no selection, it targets the final paragraph. Optional instructions can request a change in voice, clarity or pace. It returns one replacement, without a required minimum length.
- **Continue:** generates after the final paragraph, preserving existing writing. It does not treat the published next paragraph as the expected answer.

Generation previews the result. **Append to Chapter** accepts new writing; **Replace Passage** accepts a rewrite. The target chapter and source text must still match the request snapshot; changed text requires a fresh generation. Shared clients apply passage changes through the existing editor transaction/undo path. Native macOS creates a before-change snapshot and offers **Undo AI Change**, guarded against intervening edits. The existing advanced pipeline and other suggestion tools retain their own behavior.

## Limits, reachability and errors

This service supports text-only, non-streaming chat: one generation at a time, at most 512 output tokens, 4,096 total input-plus-reserved-output tokens, 32 messages, a 64 KiB request and a 120-second cancellation deadline. The engine checks the token count itself because the underlying MLX cache does not enforce this model's requested window. It rejects oversized requests with HTTP 413; it does not truncate manuscript context. Disconnects and deadlines cancel generation. The app profile disables automatic retries of inference requests; a busy response is explicit.

Authentication failure is HTTP 401, an unlisted browser origin 403, unknown model 404, busy service 429, deadline/cancellation 504, and model failure 500. Streaming, images and tool calls are unsupported. An HTTP 200 with an empty/malformed completion does not pass the shared connection test. Use the configured token for `/v1/models`; `/health` is a lightweight public readiness route.

`127.0.0.1` on a Windows PC or iPhone refers to **that device**, not this Mac. For ordinary users on other devices, provide an intentionally reachable authenticated HTTPS service with this protocol (or another compatible implementation serving the intended model). No training, GPU or MLX install is required on their client. Hosting, TLS, per-user credentials, quotas, production operations and model-format compatibility for a non-MLX server are separate deployment work. This change launches no paid service, public tunnel or model publication. Do not expose the development server directly to the internet.

Browser HTTPS/mixed-content/private-network policy, CORS and native transport rules still apply. The explicit origin list does not override browser policy. Use the actual client origin, not a wildcard. Configuring a remote service sends the selected text/context there. A loopback developer smoke test does not establish device/LAN/public-hosted access.

## Validation evidence

Local evidence on 20 October 2026:

- Authenticated HTTP completions succeeded for the pinned base and adapter; identity metadata matched the manifest. Unauthenticated discovery failed with 401 and an unknown model failed with 404.
- The **actual shared `CustomLlmProvider`**, bundled with its normal HTTP transport, passed an authenticated connection probe and candidate completion. The separately compiled **native macOS `OpenAICompatibleProvider`** also completed an authenticated candidate request through URLSession. Local results are retained under ignored `artifacts/local-serving/` without the credential. These are provider harness checks, not GUI insertion/undo or device tests.
- CPU service tests cover authentication, artifact tampering, CORS, payload rejection, context limits, cancellation, concurrent requests and the shared version contract, without loading model libraries.
- React regressions cover explicit setup, credential separation, candidate/base selection, future model IDs and request/error behavior. Native core regressions cover the shared profile, actual URLSession request format and context-failure manuscript preservation.

Build/test results and target-specific runtime limits are recorded in the implementation PR. Unit tests and provider smoke requests are not Windows/iOS device tests or blinded literary evaluation. Complete target-device generation, credentials, lifecycle, manual insertion/undo and offline drafting checks before a broad release. Existing human quality review remains outstanding; app outputs do not become training targets automatically.
