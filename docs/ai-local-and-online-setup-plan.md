# AI setup: local and online choices

Decision recorded 24 October 2026. The owner has a website/domain, no app user-account system, and wants locally installed desktop applications with a choice of local or online AI during setup.

**Status: accepted direction and implementation plan, not a completed runtime or hosted deployment.** Existing Write/Rewrite/Continue tools and the manually configured experimental service remain the current technical trial. No paid hosting, accounts, model distribution or automatic model downloads are created by this document.

Artifact milestone, 24 October: a [verified macOS ARM64 development package](../llm/Narratryx/docs/portable-local-runtime-2026-10-24.md) now exports and runs the craft adapter as a 2.71 GB text-only GGUF, with private runtime authentication managed by the developer harness. Native application lifecycle/setup, downloads and Windows/other-device runtime checks remain outstanding. This evidence advances step 1 without claiming that steps 2–5 are delivered.

Native integration milestone, 24 October: [the app-managed trial](managed-local-ai-trial.md) adds Rust and Swift process managers and main-interface setup controls. Actual Mac native and Rust manager generation passed with internal credentials; the native app generated a preview without key entry. Automatic installation/downloads, target Windows/Linux runtime testing, complete first-run onboarding and hosted accounts remain unfinished. The artifact milestone above describes its earlier scope.

## User experience

Setup offers **On this computer**, **Online AI** and **Decide later**. Ordinary drafting, files, backups and exports work locally without signing in, downloading a model or enabling AI. The choice remains editable beside the main writing controls.

Local mode needs no account, API-key entry, terminal, Unsloth installation or training. Show the actual download size, disk/RAM check and model identity before an explicit download. The app verifies the download, starts/stops its inference runtime, manages private local authentication internally and reports readiness. Do not show Local AI as ready merely because an endpoint/model name is configured. If the device cannot run the model, leave writing available and explain the available choices.

Online mode uses ordinary app sign-in and automatically managed sessions. Users never copy the operator's model-service key. Identify the selected online service and explain that requested passage/context leaves the device. Do not switch from local to online automatically when local inference fails. Advanced user-owned endpoints remain optional.

## Implementation sequence

1. **Validate a distributable local artifact.** The present experimental adapter is MLX, not a verified Windows runtime artifact. Establish a pinned export/conversion path, tokenizer/chat-template identity and equivalent before/after inference checks. Review model/base redistribution terms and retain provenance. Package/download eligibility is separate from literary-quality promotion. No new training or public model upload is required or authorized by this plan.
2. **Build the desktop runtime manager.** Use a replaceable inference interface; evaluate llama.cpp/GGUF for Windows/Linux and macOS portability, retaining optional MLX support. Bundle a signed, versioned runtime or download verified runtime artifacts. Include resumable model acquisition, hash verification, bounded resource checks, process ownership, local-only IPC/loopback, automatically managed credentials, health checks, cancellation, updates and rollback. Never run training from startup/installers. Benchmark the chosen small model on ordinary CPU-only Windows hardware and the 16 GB development Mac before publishing hardware claims.
3. **Wire the setup and main writing UI.** Store mode/model selection separately from manuscript credentials; use existing provider boundaries and managed/local-only policy. Preserve selection-scoped preview, acceptance, undo/snapshots and offline operation. Report downloading, starting, ready, unavailable and recoverable error states rather than a generic key prompt.
4. **Implement optional online access.** Confirm the existing website host's capabilities before choosing the gateway and inference host. Add account/session validation, server-held inference credentials, allowed model IDs, user-level quotas, bounded requests, cancellation and operating-cost limits. The website can distribute apps/models and support accounts; a domain alone does not establish an inference service. Keep the model host replaceable. Select hosting and approve costs separately before any paid deployment.
5. **Validate all maintained clients.** Test first-run choice, restart, missing model, interrupted download, offline startup, changed context, cancellation, key/session expiry, model replacement and rollback. Test real platforms separately from shared-source or CI passes. Follow independent literary evaluation before claiming better writing quality.

## Platform contract

| Client | Local AI path | Online AI path |
|---|---|---|
| Windows/Linux Tauri | App-managed native runtime, device capability checks and OS-private credentials; no local training | Managed account session through a reachable HTTPS gateway |
| Native macOS | Independent Swift runtime/process integration and Keychain handling; shared React changes do not supply it | Independent session/provider integration through the same gateway contract |
| Web/PWA | Offer on-device browser capabilities or a deliberately connected local companion only where supported; do not claim the desktop model is installed in the browser | Hosted session and gateway, without service keys in browser storage/build variables |
| Capacitor iOS | Separate device/runtime validation; do not assume a desktop GGUF is suitable or that another computer is reachable via the phone's loopback | Hosted session and gateway with appropriate native credential storage |

Different local engines/models must be identified accurately. Existing Chrome or Apple on-device AI is not automatically the trained Narratryx adapter. Downloading/running a model is inference, not training.

## Current code boundaries and gaps

- `src/components/AI/WritingWorkspace.tsx` and native `Views/WritingAssistantView.swift` provide the visible actions and preview workflow.
- Shared providers can address compatible endpoints; the independent native factory resolves saved endpoint configurations and Keychain credentials. Neither currently installs or supervises a distributable local model runtime.
- `llm/Narratryx/runtime/local/` is a separately installed, hash-pinned MLX developer service. It is not a packaged cross-platform runtime.
- `src/server/integrationBroker.ts` is Vite development middleware. Its managed generation route currently targets an environment-configured provider, not an authenticated production Narratryx account service.
- `api/` is a separately deployed PHP proxy with server-key authorization/IP limits; a shared client token is not individual app account/session management.
- Existing OAuth helpers are for external file-service integrations, not DraftHarbour user accounts.

## Primary implementation references

[llama.cpp](https://github.com/ggml-org/llama.cpp) documents CPU, Apple Silicon and quantized inference backends. [Unsloth export troubleshooting](https://docs.unsloth.ai/basics/saving-and-using-models/troubleshooting) explains why the training chat template and token formatting must be retained across inference engines. These support an engineering candidate and validation requirement, not a claim the current adapter is already converted, packaged or quality-equivalent.
