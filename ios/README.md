# DraftHarbour — Capacitor iOS

Reviewed 20 October 2026. This is a Capacitor 8 wrapper around the shared React application, not the independent native macOS implementation. The checked-in Xcode project declares iOS 15; verify current dependency/toolchain requirements for a release.

## Build and open

Use macOS with full Xcode, the required iOS SDK/simulator and root Node dependencies:

```bash
npm ci
npm run build:native
npm run cap:doctor
npm run cap:open:ios
```

`build:native` builds the frontend and runs Capacitor sync. `npm run cap:sync` only synchronizes existing web assets/plugins; it does not rebuild changed frontend source. After shared runtime changes, rebuild and synchronize before testing the app.

The project uses **Swift Package Manager** through `App/CapApp-SPM/Package.swift`. Do not add CocoaPods just to follow this checked-in workflow. The Capacitor CLI manages that package; leave its generated README/package files alone and keep authored guidance here.

## Simulator and device validation

From the repository root:

```bash
xcodebuild -project ios/App/App.xcodeproj -scheme App -sdk iphonesimulator -configuration Debug CODE_SIGNING_ALLOWED=NO build
```

Select an installed simulator or configured device in Xcode for interactive checks. Device/archive distribution requires the appropriate signing team/provisioning. Check icon/splash asset catalogs under `App/App/Assets.xcassets/`; metadata alone is not a complete release asset set.

Check editing, autosave/recovery, import/export/document pickers, safe areas, keyboard behavior and optional providers on the target runtime. A web build or simulator compile alone is not a physical-device test. The [PR workflow](../.github/workflows/pr-check.yml) defines a simulator compile job; inspect current run results rather than treating its definition as a pass.

## AI and network access

The wrapper uses shared provider settings and frontend request parsing. Local LLM → Custom Endpoint takes a base URL and appends `/v1/chat/completions`. Provider credentials/configuration and native/browser transport rules still apply; this wrapper is not documented as having a native Keychain implementation equivalent to the separate macOS app.

**`127.0.0.1` on an iPhone refers to the phone.** The Mac's Unsloth Studio at `127.0.0.1:8888` is not directly reachable through that phone URL. Use an intentionally configured reachable service, preferably authenticated HTTPS, and verify transport/CORS/private-network policy without weakening production defaults.

The [Narratryx pilot](../llm/Narratryx/docs/craft-source-pilot-2026-10-20.md) remains experimental and is not bundled or enabled here. Follow the [integration test plan](../docs/narratryx-integration-readiness-2026-10-20.md). Ordinary users must not need local model training; hosted optional inference remains separate from offline drafting.

## Data compatibility

Project data follows the shared frontend's IndexedDB/auxiliary storage paths and the [portable `.dhproj` contract](../docs/contracts/dhproj-v1.md). Preserve manuscript/recovery behavior and imported credential exclusion. Keep external backups; application storage is not protection against device loss.
