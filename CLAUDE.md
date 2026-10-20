# CLAUDE.md — DraftHarbour Studio

Source guide reviewed 20 October 2026. Read [AGENTS.md](AGENTS.md) first: its standing all-version scope, data-protection, validation and model-development rules also apply to Claude. [README.md](README.md) is the setup/product entry point. Manifests and lockfiles take precedence over dependency versions mentioned in prose.

## Architecture

DraftHarbour is an offline-first novel/screenplay application with four maintained runtime families:

| Runtime | Implementation |
|---|---|
| Web/PWA | React/TypeScript in `src/`; CodeMirror 6; Dexie/IndexedDB and auxiliary browser storage |
| Windows/Linux | Shared frontend in Tauri 2 under `desktop/`; Rust native services and credential-vault integration |
| iOS | Shared built frontend in Capacitor 8 under `ios/`; Xcode/Swift Package Manager project |
| macOS | Independent SwiftUI/AppKit document app under `macos/`; `.dhproj` documents, native services and Keychain |

Shared React edits do not update native macOS editor/settings/provider/import/export behavior. Inspect corresponding Swift implementations and tests. The runtimes do not necessarily use identical prompts, configuration, networking or UI.

The root package declares React 19, TypeScript 5.6, Vite 6, CodeMirror 6, Dexie 4, Tailwind 4, Vitest 4 and ESLint 9. Native macOS uses Swift tools 6.0 with a macOS 14 package minimum. Capacitor's generated SPM package declares iOS 15; check the Xcode project and dependencies for the effective deployment target.

## Source navigation

| Concern | Start here |
|---|---|
| App composition | `src/App.tsx`, `src/context/AppContext.tsx` |
| Reducer/settings/services | `src/context/state/appReducer.ts`, `src/context/appSettings.ts`, `src/context/services/` |
| Commands | `src/lib/commands.ts` |
| Editor/Markdown | `src/components/Editor/`, `src/lib/editor/` |
| Shared settings | `src/components/Windows/SettingsWindow.tsx` |
| Domain types | `src/types/index.ts`; local types also exist in domain modules |
| IndexedDB/migrations | `src/lib/storage.ts`; `src/lib/storage/` contains facade modules |
| Persistence keys | `src/lib/storageKeys.ts` |
| Recovery/backups | `src/lib/recoveryJournal.ts`, `src/lib/recoverDraft.ts`, `src/hooks/useAutomaticBackups.ts`, storage safety functions |
| AI | `src/lib/ai/types.ts`, `providerManager.ts`, `customLlmProvider.ts`, `openaiProvider.ts`, `pipelines.ts`, `storyBible.ts` |
| AI configuration | `src/lib/ai/configUi.ts`, `src/lib/validation/settingsValidation.ts` |
| Integrations | `src/lib/integrations/` — generic sync, Dropbox, Google Drive and Scrivener |
| Backend | `src/server/integrationBroker.ts` for Vite dev; `api/index.php` for separate PHP deployment |
| Export | `src/lib/export/` — manuscript/screenplay formats including text-only EPUB |
| Tauri | `desktop/src-tauri/src/main.rs`, `writing_engine.rs`, `tauri.conf.json` |
| Native macOS UI | `macos/Sources/DraftHarbourNative/` — app, document, views |
| Native macOS logic | `macos/Sources/DraftHarbourNativeCore/` — models, providers, codecs, safety, sync, analysis |
| Native tests | `macos/Tests/DraftHarbourNativeCoreTests/` |
| Model research | `llm/Narratryx/` — independent of application runtime |

## Change workflows

For a command/panel, inspect command registration, current window/modal state and app composition. Equivalent native behavior may require `DraftHarbourCommands.swift`, native views and core services. Use established CSS Modules/Tailwind/theme conventions; native appearance is separate.

For a persisted field, inspect TypeScript and Swift Codable models, IndexedDB migrations, settings defaults, backups/exports/imports and shared fixtures. Follow [the portable project contract](docs/contracts/dhproj-v1.md) for known extensions, ID remapping and JSON/ZIP compatibility. An interface edit alone is not a migration. Do not assert all domain types must live in a single file or that facade modules are the actual database implementation.

For AI, trace provider configuration through the factory and request/result UI. The shared frontend supports Chrome on-device AI, managed cloud, OpenAI-compatible endpoints, server proxy and custom LLM backends. Native macOS has its own HTTP provider/factory plus a conditional Apple Foundation Models implementation. On-device availability depends on installed framework/OS/browser/device capability.

Shared **Local LLM** configuration accepts a server base URL, appending `/v1/chat/completions` for generic-openai/vLLM/llama.cpp or `/api/chat` for Ollama. Native macOS HTTP configuration expects the **full endpoint URL**. Shared **Custom Endpoint** uses another code path with endpoint/key validation; keyless local service behavior is not identical across these options.

For networking, inspect managed policy, client transport, timeouts, cancellation, response parsing and browser/native restrictions. Vite middleware is a development backend. Static hosting and `vite preview` do not run it. PHP has separate route/authentication coverage and is not an identical Node broker deployment.

## Narratryx status

Narratryx is model development, not an established released specialist model. The [latest craft pilot](llm/Narratryx/docs/craft-source-pilot-2026-10-20.md) trained twenty source-only answers for five updates and completed sixteen matched before/after tasks. Results are mixed and blinded human quality ratings remain absent.

The opt-in integration is implemented in `src/lib/ai/narratryx.ts`, shared `AIConfigPanel`, native `NarratryxProfile.swift` and native AI tools. The separate `llm/Narratryx/runtime/local/` service pins the craft adapter and cached base, authenticates inference, bounds context/output and exposes base/candidate IDs. Live HTTP and the actual shared provider path passed locally; this does not establish target-device or literary-quality acceptance. Read [the current integration guide](docs/narratryx-app-trial.md); the earlier [readiness assessment](docs/narratryx-integration-readiness-2026-10-20.md) is historical.

Keep model versions replaceable and model serving/training outside the application. Do not enable experimental adapters by default, embed Studio credentials, require ordinary users to train locally, or silently alter manuscripts. Existing Narratryx branding/default model strings are not evidence those models are installed.

## Checks and reporting

Use [AGENTS.md](AGENTS.md) and platform guides for commands. `npm run ci` is a frontend chain, not all native or changed-coverage jobs. Co-located Vitest tests and native core tests validate different implementations.

For docs-only edits, check paths, commands, links and factual consistency. For runtime work, run meaningful regressions and required platform checks; synchronize Capacitor assets when shared runtime changes warrant it. Report Windows/Linux builds, iOS simulator/device checks and native GUI checks separately.

Historical `docs/reviews/` results retain their dates and limitations. Avoid stale test counts, universal parity claims and treating configured CI jobs as completed runs. Preserve unrelated local changes and other `.claude/worktrees/` checkouts.
