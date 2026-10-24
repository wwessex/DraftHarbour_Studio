# DraftHarbour Studio

An offline-first application for novels and screenplays, combining chapter/scene editing, planning, manuscript protection, export and optional AI/cloud services. Core drafting requires no model, training environment or paid AI provider, and remains usable offline after installation/caching.

Documentation reviewed against this checkout on **20 October 2026**. Manifests/workflows define current commands; historical reports are dated evidence, not a claim every platform was retested today.

## Applications

| Version | Implementation | Guide |
|---|---|---|
| Web/PWA | React 19, TypeScript, Vite, CodeMirror 6, Dexie/IndexedDB | This README |
| Windows/Linux desktop | Shared frontend in Tauri 2, with Rust services | [Desktop](desktop/README.md) |
| iOS | Shared frontend in Capacitor 8 | [iOS](ios/README.md) |
| Native macOS | Independent SwiftUI/AppKit document application, Swift 6 package | [macOS](macos/README.md) |

macOS desktop distribution uses Swift, not Tauri. Shared React changes do not update native macOS automatically. [AGENTS.md](AGENTS.md) and [CLAUDE.md](CLAUDE.md) describe contributor responsibilities across all versions.

## Writing, planning and protection

- Book chapters and Fountain screenplay scenes with project-aware editing and exports.
- Outlines, scene plans, corkboard, character/world notes, story blueprint, search, goals, review/analysis tools and optional AI workflows.
- Local autosave, snapshots, recovery, backups and deleted-item recovery. Workflows/storage differ between the shared frontend and native document app.
- Portable `.dhproj`: web exports ZIP containing `project.json`; native macOS exports JSON. Both importers accept both containers. See the [format contract](docs/contracts/dhproj-v1.md) for fields, ID remapping, migrations and limits.
- Manuscript DOCX, PDF, RTF and text-only EPUB; screenplay PDF and Fountain. Follow project-specific export choices and preflight warnings.

Automatic project backups retain ten changed versions; manual copies can be retained separately. Local backups do not protect against device loss or cleared browser storage. Retain external copies through project backup/export workflows. Native project-file deletion also involves the operating system's Trash and differs from browser project trash.

## Web setup

Use Node/npm compatible with the lockfile/dependencies. Current PR jobs use Node 20 for frontend checks and Node 22 for Tauri/iOS jobs; inspect workflow files before matching CI.

```bash
npm ci
npm run dev
```

Open Vite's printed URL. Production build and preview:

```bash
npm run build
npm run preview
```

Deploy `dist/` to a static host. Static output and `vite preview` do not include the Vite development broker, PHP server, model server, OAuth service or collaboration backend. Install the PWA through the browser's install/Add to Home Screen workflow where supported; browser AI availability is separate.

## Desktop and iOS setup

Tauri requires Rust and the platform's WebView/native build prerequisites, plus the separate CLI package:

```bash
npm --prefix desktop ci
npm run desktop:dev
```

Build with `npm run desktop:build`, `npm run desktop:build:win` or `npm run desktop:build:linux` on a suitable host. A target argument alone does not supply another OS's system toolchain. Tauri's development renderer is configured at port 1420.

Native macOS requires a suitable Swift/macOS SDK environment; full Xcode is needed for normal XCTest/IDE workflows:

```bash
swift test --package-path macos
npm run macos:build
npm run macos:run
```

`macos:build` stages without launching. `./script/build_and_run.sh --verify` launches/verifies too; it is not build-only. See [macOS guidance](macos/README.md) for SDK/scratch overrides and signing.

The checked-in iOS project uses Xcode/Swift Package Manager; adding CocoaPods is not a prerequisite for this workflow:

```bash
npm run build:native
npm run cap:doctor
npm run cap:open:ios
```

Rebuild/synchronize after shared application changes. See [iOS guidance](ios/README.md) for simulator compilation, assets and device networking.

## Optional AI and Narratryx

Existing providers support capable on-device facilities, a configured managed broker, OpenAI-compatible services, the PHP provider proxy and local/self-hosted LLMs. Availability depends on provider configuration and runtime capability; static hosting alone supplies no managed AI service.

[Narratryx](llm/Narratryx/README.md) is an **independent model-development workspace**, containing rights evidence, curation, validation, evaluation and experimental adapters. It is not imported into app startup or required to install/use DraftHarbour.

The [latest craft pilot](llm/Narratryx/docs/craft-source-pilot-2026-10-20.md) completed five local updates on twenty source-only craft answers and sixteen matched before/after tasks. Results are mixed; better literary quality is unproven. The adapter is not a promoted production model. Human quality review and substantive author-revision training pairs remain outstanding.

**An opt-in experimental integration is implemented across all maintained apps.** The main manuscript interface includes visible **Write**, **Rewrite** and **Continue** buttons with inline instructions, preview and passage-scoped acceptance. Settings only configures the connection. Use **Set up Narratryx (experimental)** in the shared Local AI settings or native macOS AI provider tools. A separate authenticated service pins the exact craft adapter; live base/candidate HTTP requests and the actual shared provider path passed locally. See the [setup and validation guide](docs/narratryx-app-trial.md) for limits, token handling, rollback and platform test boundaries. Literary improvement remains unproven.

The accepted [setup plan](docs/ai-local-and-online-setup-plan.md) offers **On this computer**, **Online AI** and **Decide later**, with offline drafting available throughout and no end-user training. The [app-managed local trial](docs/managed-local-ai-trial.md) now implements native Rust/Swift process ownership and AI setup beside the writing controls. A staged [2.71 GB Mac ARM64 development bundle](llm/Narratryx/docs/portable-local-runtime-2026-10-24.md) works in the native app without endpoint/key entry; the existing manual service remains available. Windows/Linux package availability, automatic downloads, complete onboarding and hosted online sign-in remain release work. Browser/iOS setup does not install a desktop model.

Desktop setup can also select, verify and install an already obtained local package, with resource checks, a native confirmation and restore of the previous verified copy. It does not download or publicly distribute the experimental weights, accept arbitrary models or activate AI merely by installing a package.

### Endpoint configuration

| Provider/client | Configure |
|---|---|
| Shared app: Local LLM → Custom Endpoint (`generic-openai`) | Server **base URL**, e.g. `http://127.0.0.1:8890`; app appends `/v1/chat/completions` |
| Shared app: Ollama | Ollama base URL; app appends `/api/chat` |
| Shared app: Custom Endpoint (`openai-compatible`) | **Full** completion URL, subject to endpoint/key validation |
| Native macOS: compatible/custom HTTP provider | **Full** completion URL, e.g. `http://127.0.0.1:8890/v1/chat/completions` |

Use the exact served model ID, not placeholder defaults such as `narratryx:latest`. Credentials must match the service. Browser CORS/mixed-content/private-network rules and native transport policy can affect access. On an iPhone or another computer, `127.0.0.1` refers to that device, not the Mac.

### Backend and integration configuration

`VITE_BROKER_BASE_URL` selects an optional broker host. `VITE_AI_DEVELOPER_MODE` and `VITE_INTEGRATIONS_DEVELOPER_MODE` control relevant developer paths. Vite variables are exposed to the frontend; never use them for server secrets.

During `npm run dev`, middleware from `src/server/integrationBroker.ts` handles routes including `/api/chat` and `/api/ai/generate`. Server provider credentials come from its environment. The PHP deployment routes `/api/chat` through `api/index.php`; it does not implement all Node broker routes. Managed-cloud availability checks require a configured broker URL. Verify actual routes, authentication and response format instead of assuming every provider works on the same origin with an empty URL.

Generic REST sync, Dropbox, Google Drive and Scrivener bridge implementations exist. OAuth registration, configuration, backend deployment, runtime and file support determine usable workflows. The Scrivener bridge has bounded package support, not complete feature compatibility. Static hosting alone supplies neither continuous cloud backup nor real-time collaboration.

## Data and privacy

Shared app project records use IndexedDB; settings/auxiliary data also use browser storage. Native macOS uses document-owned state and native recovery/backup services. Cross-storage writes are not one crash-atomic transaction.

Native macOS accounts use Keychain. Tauri supplies OS keyring operations for specific configured secret paths, not every possible provider field. Browser storage is not a hardened vault. Imported projects must not activate credentials or imported sync authorization.

AI, sync, grammar and integration services may receive text/project context when used. Managed policy can disable providers or enforce local-only operation. Diagnostics are designed to exclude manuscripts and redact recognized sensitive fields; inspect implementation before extending collection. Export/backup inclusion and credential-exclusion semantics follow the [format contract](docs/contracts/dhproj-v1.md).

## Validation

```bash
npm run lint
npm run typecheck
npm run test
npm run ci
```

`npm run ci` is the frontend lint/typecheck/Vite-config/coverage/build/bundle/assets chain. Additional checks include `npm run coverage:changed`, `npm run test:inventory`, Swift tests, Rust shell tests and iOS simulator compilation. [AGENTS.md](AGENTS.md) lists commands; [PR workflow](.github/workflows/pr-check.yml) defines current remote jobs. `npm run smoke:providers` contacts configured services; it does not evaluate literary quality.

The [17 October parity report](docs/reviews/platform-parity-2026-10-17.md) records historical checks/limits; model checks are in dated experiment reports. Documentation updates do not imply fresh application builds or device tests.

## Packaging and releases

Native macOS packaging uses `npm run macos:package` / `./script/package_macos.sh`. Local ad-hoc signing is not Developer ID notarization; distribution requires signing/notarization/release-signature configuration. Tauri target/signing/updater settings are in `desktop/src-tauri/tauri.conf.json` and the release workflow. iOS archives/device distribution need signing/provisioning and completed assets.

See the [release checklist](docs/releases/release-checklist.md), [rollback runbook](docs/releases/incident-rollback-runbook.md) and [desktop release workflow](.github/workflows/desktop-release.yml). Local packaging or a CI definition does not publish a release.
