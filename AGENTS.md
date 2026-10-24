# AGENTS.md — DraftHarbour Studio

Repository guidance reviewed against source on 20 October 2026. Manifests, lockfiles and workflow files remain authoritative for executable commands and dependency versions. `CLAUDE.md` provides a source navigation guide; `README.md` documents setup and product/model status.

## Standing preference: all maintained applications

- Inspect, implement and validate every applicable version by default: **web/PWA**, **Windows/Linux Tauri**, **Capacitor iOS**, and the **independent SwiftUI/AppKit macOS app**.
- `src/` is shared by web/PWA, the Tauri renderer and Capacitor. It does not implement native macOS behavior; inspect `macos/` separately.
- Preserve portable project/data compatibility. Synchronize native web assets when shared runtime code changes, and check platform-specific networking, credentials, files and UI behavior.
- Report exactly which versions received source changes, build/test checks and actual runtime/device checks. Disclose blockers. A configured CI job or historical report is not a fresh successful run.
- Respect an explicitly narrower user scope. Model research under `llm/Narratryx/` stays independent of application functionality unless integration is requested.

## Repository map

| Path | Responsibility |
|---|---|
| `src/` | React 19 / TypeScript / Vite; CodeMirror 6; Dexie persistence |
| `src/context/` | App context, reducer, settings and workspace services |
| `src/lib/storage.ts` | Actual IndexedDB implementation/migrations; `src/lib/storage/` includes facade entry points |
| `src/lib/ai/` | Provider interfaces/factories, custom endpoints, availability, pipelines and story context |
| `src/components/Windows/SettingsWindow.tsx` | Shared settings UI, including AI configuration |
| `src/server/integrationBroker.ts` | Vite development middleware backend handlers |
| `api/` | Separately deployed PHP proxy, not a server bundled into a static site |
| `desktop/src-tauri/` | Tauri 2 Windows/Linux shell, Rust writing engine, keyring and updater |
| `ios/` | Capacitor 8 wrapper/Xcode project; shares the built web application |
| `macos/` | Swift 6 package: independent native app and core |
| `script/` / `scripts/` | Native macOS build/release scripts / JavaScript quality and smoke checks |
| `fixtures/`, `docs/contracts/` | Portable `.dhproj` fixtures and compatibility contract |
| `llm/Narratryx/` | Isolated rights, curation, evaluation and experimental models |

Do not edit another checkout under `.claude/worktrees/` as this checkout. Capacitor-generated SPM files are CLI-managed; authored iOS guidance belongs in `ios/README.md`.

## Commands and validation

Install root dependencies with `npm ci`; install the desktop CLI package with `npm --prefix desktop ci` when needed.

| Purpose | Command |
|---|---|
| Web development / production / preview | `npm run dev` / `npm run build` / `npm run preview` |
| Fast source checks | `npm run lint`, `npm run typecheck` |
| Tests / coverage | `npm run test`, `npm run test:coverage` |
| Vite config / changed coverage | `npm run verify:vite-config`, `npm run coverage:changed` |
| Bundle / assets / inventory | `npm run bundle:check`, `npm run assets:check`, `npm run test:inventory` |
| Frontend CI chain | `npm run ci` |
| Tauri development / build / debug | `npm run desktop:dev`, `npm run desktop:build`, `npm run desktop:build:debug` |
| Tauri Rust checks | `cargo test --locked --no-default-features --manifest-path desktop/src-tauri/Cargo.toml` |
| Build and synchronize Capacitor | `npm run build:native` |
| Capacitor sync / health / Xcode | `npm run cap:sync`, `npm run cap:doctor`, `npm run cap:open:ios` |
| Native macOS tests | `swift test --package-path macos` |
| Native macOS run / build | `npm run macos:run`, `npm run macos:build` |
| Provider smoke checks | `npm run smoke:providers` (contacts configured services) |

`npm run ci` runs lint → typecheck → Vite config → coverage tests → web build → bundle budgets → duplicate assets. It does **not** include `coverage:changed`, Python foundation tests, native tests or iOS compilation. The PR workflow additionally runs changed coverage, Narratryx CPU foundation tests, macOS tests/app build, Windows/Linux shell tests and iOS simulator compilation. Inspect `.github/workflows/pr-check.yml` before describing current jobs.

With full Xcode, the configured iOS simulator compile is:

```bash
xcodebuild -project ios/App/App.xcodeproj -scheme App -sdk iphonesimulator -configuration Debug CODE_SIGNING_ALLOWED=NO build
```

Use checks proportionate to the change. Documentation-only work needs source/command/link consistency checks, not regenerated native assets. Runtime changes require relevant tests and platform checks. Never count skipped checks as passes.

## Implementation and data rules

- Read existing implementations/tests first. Use strict TypeScript, `@/` imports, existing context/reducer/service boundaries and the command registry in `src/lib/commands.ts`. Shared domain types live in `src/types/`; provider-specific types also live near their implementation.
- Follow established component patterns, CSS Modules, Tailwind and theme tokens. Retain lazy loading of heavy dependencies and offline drafting when providers fail or are unavailable.
- Add meaningful regression coverage for behavior changes. Obtain test counts from current execution/inventory rather than stale prose.
- Preserve user changes/manuscripts. Avoid unrelated fixes, repository-wide formatting, generated-file churn and changes in other worktrees.
- Follow `docs/contracts/dhproj-v1.md` and shared fixtures. Web exports are ZIP with `project.json`; native macOS exports JSON; importers accept both. Preserve/remap known IDs and passive native extensions according to the contract.
- The web database currently has v5 backup/trash additions. Add migrations for new persisted schema and keep old projects readable. IndexedDB and localStorage are not one crash-atomic transaction.
- Preserve backups, trash, snapshots and recovery. Imports/restores must not silently overwrite the current manuscript or activate imported credentials.
- Browser storage is not an OS secret vault. Inspect actual persistence: Tauri keyring handling covers specific secret paths, not every possible configuration field. Native macOS uses Keychain-backed accounts. Never print credentials.
- Respect managed policy, local-only operation and explicit provider configuration. Remote AI/sync requests can transmit project context; do not activate them silently.

## Narratryx and experimental AI

- Read `llm/Narratryx/README.md` and its latest linked report before model work. Training completion, structural validation and literary improvement are different claims.
- Portable export/package tooling lives in `llm/Narratryx/runtime/packaging/`. Its development catalog has no download URL or release approval; Mac inference evidence does not establish Windows support or production installer readiness. See [the runtime report](llm/Narratryx/docs/portable-local-runtime-2026-10-24.md) and [local/online plan](docs/ai-local-and-online-setup-plan.md).
- App-owned inference is implemented separately in `desktop/src-tauri/src/local_runtime.rs`, shared `src/lib/ai/desktopLocalProvider.ts` and native `LocalModelRuntime.swift`. See [the app-managed trial](docs/managed-local-ai-trial.md). Never expose a native credential/port through renderer IPC, accept executable paths/trust hashes from projects, or add HTTP/cloud fallback to the managed-local provider. The current catalog enables only the verified Mac ARM64 development bundle; Windows/Linux installers, model downloads and hosted sign-in are not delivered.
- Verified offline package replacement/restore lives in `desktop/src-tauri/src/local_install.rs` and native `LocalModelInstaller.swift`. Native code owns selection/confirmation. Preserve unknown files and recovery directories; do not delete a prior package before verification or treat staged renames as power-loss-safe transactions. The current 8 GiB rejection floor is not hardware certification. Different model identities require reviewed catalog/engine updates.
- Experimental app setup uses existing providers (`src/lib/ai/narratryx.ts`, native `NarratryxProfile.swift`); the separate authenticated service is `llm/Narratryx/runtime/local/`. See [the integration guide](docs/narratryx-app-trial.md). Keep service token files and model artifacts out of Git.
- Current adapters remain experimental. The latest craft pilot has mixed mechanical results and no completed blinded human quality ratings. Placeholder names such as `narratryx:latest` do not prove a model is installed or released.
- Use only sources, jurisdictions, uses and spans supported by exact rights records. Dataset-wide public-domain metadata is not per-edition clearance. Attribute AI evidence reviews accurately; never invent human approval or legal certification.
- The user's current training scope excludes generated literary teaching targets. Keep unresolved teacher-output candidates and unreviewed bulk corpus rows out of training. Distinguish task instructions from source-derived answer provenance.
- Preserve held-out authors/works, benchmark hashes and independent evaluation. Editing tests must not gain a minimum length that encourages explanation. Exact canonical continuation is not a fiction-quality metric.
- Keep data preparation/training out of app startup, installers and manuscript storage. Integrate through the existing provider abstraction and a separate, replaceable inference service. Ordinary users must not need local training or an expensive GPU.
- Loopback URLs refer to the client device: a Mac Studio URL cannot serve a Windows PC or iPhone through that device's own `127.0.0.1`.
- Documentation work does not authorize paid jobs, corpus uploads, model publication/promotion or changes to app defaults. Follow the user's execution scope.

## Releases and reporting

Use `codex/` for new Codex branches. Preserve hooks and repository PR conventions. Local ad-hoc macOS signing is not a notarized distribution; follow platform/release guides for distribution signing and artifact checks. Packaging alone does not publish a release.

Completion reports state changes, actual checks, limits and parity across applicable versions. Keep historical validation dates distinct from current results.
