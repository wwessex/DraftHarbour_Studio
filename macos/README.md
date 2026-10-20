# DraftHarbour — native macOS

Reviewed 20 October 2026. The supported macOS desktop implementation is a **SwiftUI/AppKit document application**, independent of the React/Tauri renderer. The Swift 6 package declares macOS 14 as its minimum. Some optional features require a newer OS/framework and runtime capability checks.

## Structure and workflows

- `Sources/DraftHarbourNative/`: application, document lifecycle, commands and native views; AppKit `NSTextView` editing bridge.
- `Sources/DraftHarbourNativeCore/`: portable project models/codec, store, import/export, manuscript safety, analysis, AI, sync and integration services.
- `Tests/DraftHarbourNativeCoreTests/`: Swift core/provider/codec/safety regressions.
- `Resources/` and `DraftHarbourNative.entitlements`: app resources and release entitlements.

The app supports `.dhproj` documents, native writing/planning/review UI, import/export including text-only EPUB, snapshots, recoverable sections, verified backups, project context, provider-configured AI, generic REST sync, Dropbox/Google Drive sync and a bounded Scrivener package bridge. Implemented capabilities do not imply all credentials/backends are configured or that every workflow has current device/GUI validation.

[The portable contract](../docs/contracts/dhproj-v1.md) defines JSON/ZIP imports, known extension preservation, ID remapping and credential exclusion. Native exports are JSON; web exports use ZIP. Document-owned state, native recovery/backup behavior and OS Trash are not identical to browser IndexedDB/project trash.

## Build and run

From the repository root:

```bash
swift test --package-path macos
npm run macos:build
npm run macos:run
```

The npm scripts call `script/build_and_run.sh`; `macos:build` passes `--no-launch`. The script builds SwiftPM, stages a local ad-hoc signed app, and exposes it at `dist/DraftHarbour.app`; the physical bundle normally lives under `~/Library/Caches/DraftHarbour/BuildProducts/`.

```bash
./script/build_and_run.sh --no-launch
./script/build_and_run.sh --verify
```

`--verify` launches/verifies the staged app; it is **not** build-only. Open `macos/Package.swift` in full Xcode for IDE, XCTest and GUI workflows. Command Line Tools alone may lack XCTest or compatible SwiftUI macro support; report the actual installed toolchain's failure rather than marking tests passed.

For cloud-synchronized source folders, locked caches or SDK issues, the build script supports `DRAFTHARBOUR_SWIFT_SCRATCH_PATH`, `DRAFTHARBOUR_MACOS_PACKAGE_DIR` and `DRAFTHARBOUR_MACOS_SDK`. Choose installed, compatible paths rather than copying an SDK version from an old report:

```bash
DRAFTHARBOUR_SWIFT_SCRATCH_PATH=/tmp/draftharbour-swift-build ./script/build_and_run.sh --no-launch
```

## AI and integrations

Native providers/factory are in `AIProvider.swift`, `AIWorkflowServices.swift` and `AppleFoundationModelsProvider.swift`. The HTTP client expects a **full completion endpoint**, such as `http://127.0.0.1:8888/v1/chat/completions`, plus the served model ID and suitable authentication. Provider secrets use Keychain-backed accounts. The factory enforces managed policy and local-only controls.

Apple Foundation Models is conditional on framework/macro availability and macOS 26+ runtime eligibility; the app's macOS 14 minimum does not make that provider universally available. Native prompts and pipeline stage lists differ from the shared frontend; test behavior rather than assuming exact parity.

Narratryx now has an explicit **Set up Narratryx (experimental)** control through the existing provider settings (native macOS: AI tools → Provider). Follow the [app trial guide](../docs/narratryx-app-trial.md) for authenticated service configuration, exact model IDs, rollback and validation boundaries. The adapter remains experimental and is not bundled or enabled by default. Ordinary clients need service access, not local training or expensive hardware.

Dropbox needs a registered app key/redirect configuration; Google Drive needs a desktop OAuth client and uses the native loopback flow. Implementations include PKCE, Keychain-backed tokens and revision/conflict handling. Test credential-backed flows with the intended accounts; source presence is not evidence of configured production sync.

## Validation and release

Run `swift test --package-path macos`, build the app, and separately verify native GUI/editor behavior, import/export round trips, recovery, credentials and configured providers. Frontend tests do not validate this independent implementation. See the dated [parity report](../docs/reviews/platform-parity-2026-10-17.md) for historical results and limits, not today's test status.

```bash
npm run macos:package
./script/package_macos.sh --distribution --channel stable
```

The packaging script creates/verifies `dist/release/DraftHarbour.dmg`, checksums and update metadata. Local ad-hoc packages are not notarized distribution builds. Distribution requires Developer ID signing, notarization credentials and a release signing key (`APPLE_SIGNING_IDENTITY`, `APPLE_NOTARY_KEYCHAIN_PROFILE`, `RELEASE_SIGNING_KEY` or its path variant). Inspect the script and [release checklist](../docs/releases/release-checklist.md) before publishing. Packaging does not itself publish a release.
