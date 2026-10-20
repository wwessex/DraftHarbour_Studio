# Narratryx: readiness for an in-app trial

Assessment date: **20 October 2026**. This is a source/API-readiness assessment and implementation/test plan. It does not record an app integration, authenticated generation request, model promotion or current platform build/device pass.

## Decision

**There is enough infrastructure and experimental model material to begin an opt-in developer trial in the applications. There is not enough evidence to make the trained adapter the default model or advertise better literary quality.** An integration trial can establish usability, request/response behavior and operational limits while model development continues independently.

The first practical step is to establish an authenticated completion from the **exact candidate adapter** through a separate inference endpoint, then configure existing provider settings. A training checkpoint alone is not a running API. A new manuscript format, training dependency or replacement of core writing features is unnecessary.

## Evidence checked

| Component | Current evidence | Limit |
|---|---|---|
| Shared app provider | `src/lib/ai/customLlmProvider.ts` supports Ollama and OpenAI-compatible non-streaming/streaming requests, model selection and cancellation | Source inspection; no live app request to this adapter |
| Shared provider configuration | `providerManager.ts`, `types.ts` and `SettingsWindow.tsx` contain local/custom endpoint, model and credential configuration | Existing settings paths differ in authentication/validation behavior |
| Native macOS provider | `AIProvider.swift` and `AIWorkflowServices.swift` implement a separate configurable compatible HTTP client/factory and Keychain-backed credential resolution | Native payload/prompt/streaming behavior differs from the shared provider; it posts to the full configured endpoint |
| Candidate artifact | `llm/Narratryx/artifacts/craft-training-v2/adapter` completed five fresh-base LoRA updates; artifact/hash recorded in the pilot report | Local generated MLX artifact, not a portable all-platform executable or published service |
| Model comparison | Sixteen before/after cases completed without errors/truncation | Mixed mechanical results; no completed blinded human literary ratings |
| Running Studio | Read-only `GET http://127.0.0.1:8888/openapi.json` advertises `/v1/chat/completions`, `/v1/models` and authenticated inference routes | Route advertisement does not prove the candidate is registered, loaded or selected |
| Studio authentication | Unauthenticated `GET /v1/models` and `GET /api/inference/loaded-models` both returned **401** | No credentials extracted, settings changed or inference/model-load requests made during this assessment |
| Legacy cloud gateway | `llm/Narratryx/runtime/cloud/api.py` proxies compatible requests to vLLM | Not validated for this MLX adapter; its existence does not establish deployment, production security or format conversion |

The latest [pilot report](../llm/Narratryx/docs/craft-source-pilot-2026-10-20.md) records twenty source-only craft answers, about thirty seconds of local training, reported peak 6.34 GB and the limitations. Training success is sufficient for a technical trial, not a quality claim. Existing branding and defaults such as `narratryx:latest` do not identify an installed specialist model.

## Trial architecture

```text
DraftHarbour UI and current AI provider interface
                  |
      authenticated inference API
                  |
    explicit model/version selection
        base model | candidate adapter

Independent model workspace: rights -> curation -> training -> evaluation
```

Keep the API and model registry outside the application. Use explicit model/version IDs so testers can compare the unchanged base with the candidate and switch back. Keep ordinary writing, project storage and export available when inference is unavailable. Do not bundle training libraries/checkpoints in installers or silently change provider defaults.

For a local Mac-only developer trial, the existing Studio may supply the endpoint once authentication and exact-adapter serving are verified. If its API does not expose this externally created adapter correctly, use or implement a small separate serving adapter and verify its identity/protocol first. Do not assume the browser chat selection, a local directory name or a registered training-run route automatically selects this CLI-generated checkpoint.

For normal Windows/Mac users and iOS testers, use an intentionally reachable authenticated HTTPS inference service. Their devices must not need training, MLX or a powerful GPU. Hosting/provider choice, operating cost, authentication, limits and actual deployment remain separate work; this assessment launches no paid job or external service.

## Configuration contract

| Client path | Endpoint setting | Other requirements |
|---|---|---|
| Web/PWA, Tauri and Capacitor: Local LLM → Custom Endpoint (`generic-openai`) | Base URL, e.g. `http://127.0.0.1:8888` | Client appends `/v1/chat/completions`; provide exact model ID and required credential |
| Shared app: Custom Endpoint (`openai-compatible`) | Full completion URL | Settings/key validation and provider routing are distinct from the Local LLM path |
| Native macOS: compatible/custom HTTP provider | Full URL, e.g. `http://127.0.0.1:8888/v1/chat/completions` | Native client posts directly there; factory resolves Keychain credentials |

Do not append `/v1/chat/completions` to the shared Local LLM base URL or the provider will duplicate the path. Do not give native macOS only a base URL. Supply the service's actual model ID; neither an arbitrary display name nor a UI URL is a model endpoint.

The running Studio requires authentication. Establish its supported API authentication without disabling protection or embedding Studio/admin credentials in distributed applications. A production inference service should supply appropriately scoped access rather than exposing development/admin controls.

`127.0.0.1` means the client device: a Windows PC or iPhone cannot reach the Mac through its own loopback address. Verify browser CORS, HTTPS/mixed-content/private-network behavior, native transport restrictions and intended origin/authentication policy. Do not broaden production security defaults merely to make a local test pass.

## Concrete implementation and test sequence

1. **Verify serving independently.** Use supported credentials; verify model discovery or explicit model resolution, the exact base revision and candidate adapter hash, and one bounded compatible completion. Confirm the service is using the candidate rather than silently answering with its base. Check a base-model route too. Preserve version/identity evidence without logging secrets.
2. **Bound requests.** Start with short disposable passages. The experiment used an empty system prompt, 512 output tokens and short contexts within 2048 total inference tokens; actual app providers add their own prompts/context and use other generation defaults. Set/test server limits explicitly. Do not silently discard story facts to fit a window, assume app output limits match the experiment, or treat app results as directly comparable to the frozen benchmark.
3. **Use existing provider settings.** Select the experimental service/model explicitly on a test installation. No new model-specific core application dependency is needed. If existing settings prove insufficient, add the smallest equivalent behavior to both the shared frontend and independent macOS implementation. This documentation update adds no experimental toggle or automatic endpoint configuration.
4. **Test writing actions safely.** On disposable projects, try continuation, restrained editing, dialogue, pacing and analysis. Verify result review/manual application, undo/safety behavior and project compatibility. Responses must not replace a manuscript without the intended user action. Preserve the established offline workflow and current provider choice outside the trial.
5. **Test failures and version switching.** Cover bad credentials, unknown model/adapter, unavailable server, timeout, cancellation, oversized context and unsupported response/stream formats. Errors should be actionable, credentials redacted and manuscripts preserved. Verify switching between base/candidate and back to the prior provider without data migration or corruption.
6. **Complete every platform's checks below.** Record source tests, builds and real runtime/device observations separately. Use mocks/fixtures for reproducible protocol regressions and live smoke tests for the configured service; neither replaces the other.
7. **Review quality independently.** Use the existing blinded comparison and new in-app usability findings. Two independent reviewers on a representative subset, with disagreements adjudicated, are required by the evaluation plan before a quality/promotion claim. Model outputs from app trials are not automatically training data under the current source restriction.

## Cross-platform acceptance matrix

| Version | Source/build checks for an eventual integration change | Runtime checks still needed |
|---|---|---|
| Web/PWA | Provider/settings regressions; relevant frontend checks/build | Authenticated model discovery/generation, CORS/network restrictions, cancellation, reload and offline drafting |
| Windows/Linux Tauri | Shared regressions/build plus Rust checks and native target build | Reachable service from the target OS, keyring hydration, file persistence, failure handling and unchanged writing workflows |
| Capacitor iOS | Shared checks; `npm run build:native`; simulator compilation | Simulator/device endpoint reachability, transport policy, credentials, lifecycle interruption and manual insertion/undo |
| Native macOS | Provider protocol/core regressions, Swift tests and app build | Separate native settings/payload, Keychain access, URLSession transport, generation/result application and document safety |

No platform completion is claimed from this matrix. The current assessment changed documentation only. Existing shared app/provider source and independent macOS source were inspected; no native assets were regenerated, builds/devices exercised, authenticated service configured or manuscript modified.

## Go/no-go boundaries

Proceed with an **experimental technical trial** once an authenticated exact-candidate completion and appropriate runtime reachability are established. Keep the candidate opt-in and replaceable. Do not require literary superiority merely to collect integration evidence, but do not advertise superiority or promote the adapter without that evidence.

The immediate unresolved service gate is configuration/verification, not a shortage of more training steps. Better source-backed demonstrations, substantive revision pairs and human quality review remain separate model-development work. A broader release additionally needs hosting/cost decisions, security/operational validation and all-platform acceptance evidence.
