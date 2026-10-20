# DraftHarbour — Windows/Linux desktop

Reviewed 20 October 2026. This Tauri 2 shell hosts the shared React application. macOS desktop uses the independent [SwiftUI/AppKit application](../macos/README.md). Shared frontend changes cover this renderer, not native macOS.

## Setup and development

From the repository root, install root and desktop CLI dependencies:

```bash
npm ci
npm --prefix desktop ci
npm run desktop:dev
```

Install Rust and the native Tauri/WebView prerequisites for the target host. Windows needs the appropriate MSVC/Windows build tools; Linux needs its WebKit/GTK dependencies. The shell starts Vite at `http://localhost:1420` as configured in `src-tauri/tauri.conf.json`.

```bash
npm run desktop:build
npm run desktop:build:debug
npm run desktop:build:win
npm run desktop:build:linux
```

The target-specific commands select Rust targets; they do not install another operating system's system libraries or establish cross-compilation support on a Mac. Tauri's before-build command builds the shared frontend. Equivalent package-local commands are `npm --prefix desktop run dev`, `build` and `build:debug`.

## Native responsibilities

`src-tauri/src/main.rs` supplies single-instance/window behavior, file/deep-link routing, credential keyring operations and native command integration. `writing_engine.rs` performs whole-manuscript search/analysis and backup validation. Shared TypeScript fallback paths preserve essential writing operations outside the shell.

Project records remain in the renderer's IndexedDB; the shell is not a separate native manuscript database. Specific provider/sync secrets use native vault paths; inspect current persistence rather than assuming all config fields are vaulted. `.dhproj` and `draftharbour://` routing must retain the shared [project contract](../docs/contracts/dhproj-v1.md).

## AI experiments

Existing shared provider settings can connect to an authenticated compatible inference service. Local LLM → Custom Endpoint expects the **base URL** and appends `/v1/chat/completions`; use the exact model ID advertised by the server. A Windows/Linux client's `127.0.0.1` is not the development Mac. MLX training artifacts are not a Windows inference runtime.

The [Narratryx pilot](../llm/Narratryx/docs/craft-source-pilot-2026-10-20.md) remains experimental. It has not been bundled into this app or validated through this shell. See the [integration test plan](../docs/narratryx-integration-readiness-2026-10-20.md). Normal users should be able to use optional hosted inference without training or special local hardware.

## Validation

From the root:

```bash
npm run lint
npm run typecheck
npm run test
npm run build
cargo test --locked --no-default-features --manifest-path desktop/src-tauri/Cargo.toml
```

Run native tests/builds on their appropriate hosts and verify file opening, unsaved-edit handling, keyring behavior, network requests and updater behavior separately. Host Rust tests on macOS are not Windows/Linux runtime tests. PR workflow definitions include Windows/Linux shell test jobs; that alone is not current execution evidence.

## Distribution

`src-tauri/tauri.conf.json` configures MSI/NSIS and Linux package formats, signing and updater artifacts. Windows certificate configuration uses `WINDOWS_CERT_THUMBPRINT`; updater/release signatures require the relevant CI configuration. Check [.github/workflows/desktop-release.yml](../.github/workflows/desktop-release.yml), the [release checklist](../docs/releases/release-checklist.md) and [rollback guide](../docs/releases/incident-rollback-runbook.md). Building a package does not publish it.
