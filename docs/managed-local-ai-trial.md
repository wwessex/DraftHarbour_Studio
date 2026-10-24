# App-managed local AI trial — 24 October 2026

Native inference ownership is now implemented in both desktop codebases. The independent macOS app can use the verified development package without entering an endpoint or key. The Tauri Rust manager uses the same package contract; Windows/Linux model packages are **not yet approved or available**, so those builds report unavailable instead of starting an unverified binary. This is an experimental developer trial, not a completed public installer or online service.

## What changed

- **Main interface:** AI setup sits beside the existing writing controls in the shared web/Tauri/iOS UI and the independent macOS UI. It offers On this computer, Online AI (coming soon) and Decide later. Existing manual connections remain available. Setup does not change a manuscript or download/train anything.
- **Local execution:** the native manager verifies the catalog-pinned manifest, platform, hashes, sizes, file inventory and paths. It starts only the verified executable, bound to IPv4 loopback with a random port and internally generated private credential. It checks authenticated model identity before generation. The renderer/project never receives a runtime URL or key. No remote fallback occurs.
- **Lifecycle:** generation is serialized, startup/generation have deadlines, Stop/cancellation kills the owned child, and normal app termination cleans up the process/private temporary files. A failed request can restart cleanly on the next action. Merely opening the app or editor does not load a model. Native macOS hashes on a worker; Tauri hashes/runs inference off its UI thread. Rust SHA-256 dependencies are optimized in debug/test builds to avoid slow multi-gigabyte verification.
- **Provider compatibility:** the shared provider retains `custom-llm` with an optional `managedRuntime` marker; the factory handles it before any HTTP/fallback path. Native uses a reserved internal endpoint marker resolved by its provider factory. Setup mode is device preference data, outside manuscript data; shared windows receive mode-change notifications, and native views use AppStorage. Existing project formats and endpoint providers stay compatible. Managed/local-only policy is checked; Decide later blocks AI provider creation until an explicit setup/configuration choice.
- **Readiness:** a saved profile is never labelled as proof a local runtime is ready. Selection checks the package; requests verify/start when necessary. Missing/unsupported packages and changed files fail explicitly. Switching modes closes/cancels the shared composer. Preview, passage acceptance and manuscript safeguards remain in the existing writing workflow.

The default context allowance remains 4,096 tokens and the output ceiling 512. Inputs above 64 KiB are rejected before generation; token overflow is rejected by the runtime with context shifting disabled. No manuscript text is silently truncated to fit. The model remains experimental; this work does not claim better literary quality.

## Development Mac trial

The verified macOS ARM64 bundle from the [artifact report](../llm/Narratryx/docs/portable-local-runtime-2026-10-24.md) was copied locally to:

```text
~/Library/Application Support/DraftHarbour/LocalAI/bundle
```

It remains outside Git. The locally built `dist/DraftHarbour.app` can select **AI setup → On this computer**, close setup, then use Write/Rewrite/Continue. No Unsloth installation, local training or key entry is needed by this path. The existing MLX developer service on port 8890 and browser connection were preserved.

Tauri's corresponding location is its OS app-data directory for `com.draftharbour.studio`, followed by `LocalAI/bundle`. Copying a Mac runtime there on Windows/Linux is not supported. The catalog intentionally accepts only the reviewed ARM64 Mac package until other platforms receive real binaries, verification and device testing. There is no UI for arbitrary executable paths or user-supplied trust hashes.

Two explicit development smokes exercise the managers without modifying manuscripts:

```bash
swift run --package-path macos LocalRuntimeSmoke /absolute/path/to/verified/bundle
DRAFTHARBOUR_TEST_BUNDLE=/absolute/path/to/verified/bundle cargo test --locked --no-default-features --manifest-path desktop/src-tauri/Cargo.toml real_package_smoke -- --ignored --nocapture
```

The Rust real-model smoke is deliberately excluded from ordinary CPU CI. Regular shell tests use tiny synthetic packages; no weights are downloaded by tests. Full Xcode is needed for Swift XCTest and iOS compilation.

## Current validation evidence

| Version/check | Actual result on 24 October |
|---|---|
| Shared web/PWA | Frontend CI chain passed: lint, TypeScript, Vite config, **1,471 tests across 133 files**, production build, bundle budgets and asset checks. Actual browser UI verified setup choices and unsupported-local messaging; existing connection/manuscript preserved. |
| Windows/Linux Tauri source | **12 Rust tests passed**, with one real-model test explicitly excluded. Real Rust manager smoke then passed separately on ARM64 Mac, including authenticated draft generation and owned shutdown. This is not a Windows/Linux executable or CPU hardware test. |
| Capacitor iOS | Shared setup/provider changes included and built web assets synchronized with Capacitor. Actual iPhone/device inference is untested. Local Xcode simulator compilation is unavailable with this machine's command-line tools. |
| Independent native macOS | Application build passed. Native manager CLI generated a real draft and rejected a cancelled generation. Actual app UI verified the installed package, generated a two-sentence preview without endpoint/key entry, and left the chapter at zero words (no append). Normal UI Quit stopped the exact owned process and removed its private credential directory. Five new XCTest cases were added; local XCTest execution is blocked because the installed command-line toolchain lacks XCTest. Remote full-Xcode results must be checked separately. |

Local package verification, native smoke tools and actual UI are separate evidence from literary evaluation. Prior PR results do not establish checks on this revision. The app is locally signed for development; it is not a notarized distribution.

## Verified local installation follow-up

AI setup now includes **Install local package…** and **Restore previous package…** in the shared interface and independent native macOS app. Desktop native code owns the folder picker, verification, resource check and final confirmation. The shared renderer cannot supply executable paths, manifests or trust hashes. Browser/iOS clicks explain that desktop packages require a supported desktop app; Windows/Linux remain unavailable while the catalog has no approved artifacts for them.

The picker accepts an already obtained, exact verified package directory. Before confirmation, setup checks the complete package identity and reports copy size, free disk space and physical RAM. Installation requires space for a staged copy plus a 256 MiB reserve. An **8 GiB physical-RAM floor is a conservative rejection guard, not an 8 GiB hardware qualification**; real model inference remains tested on this 16 GB Mac only. Native Windows capacity calls use Microsoft's [GlobalMemoryStatusEx](https://learn.microsoft.com/en-us/windows/win32/api/sysinfoapi/nf-sysinfoapi-globalmemorystatusex) and [GetDiskFreeSpaceExW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getdiskfreespaceexw); Unix uses system memory/filesystem statistics.

After confirmation, the manager refuses replacement during an active generation, stops its idle child, copies into a private staging directory and verifies the copied files before activation. It keeps the prior verified copy in `previous-bundle`. Ordinary activation failures restore the working package; rollback can recover a missing active directory from the verified previous copy. Unrecognized or tampered existing/previous directories are refused and preserved, rather than deleted as cache. Source folders inside/containing the app's model storage are rejected. Successful installation/restore does **not** enable AI or switch providers: choose **On this computer** separately.

The catalog currently approves one identity, so restore covers a prior copy of that exact package. Supporting a different model version requires a reviewed catalog/engine-contract update; arbitrary weight upgrades remain blocked. There is no remote acquisition, ZIP extraction, resumable download, public model hosting or automatic promotion. Multi-step rename recovery on abrupt process/power failure remains a release gap; this is staged replacement with tested ordinary-error recovery, not a crash-atomic transaction. Preserved recovery directories must not be indiscriminately removed.

Follow-up local checks: **1,476 frontend tests** and the frontend CI chain passed; **17 Rust tests** passed, with two real-model tests excluded from ordinary CI. The native real-package smoke installed, replaced, restored, generated and cancelled successfully, preserving the source package. A separate real-package Rust install/replace/restore/generate smoke also passed on this ARM64 Mac (69.40 seconds in the debug test build). Duplicate generated smoke packages were verified and removed after testing to recover disk space. Six new Swift installer tests cover resource rejection, verified replacement/restore, injected activation failure, tampering, unknown-data preservation and recovery when the active directory is missing. Their full-Xcode CI results must be checked separately from the earlier 99-test runtime milestone.

## Remaining release work

1. Build and validate pinned Windows/Linux runtimes and ordinary CPU hardware behavior. Review platform-specific private storage/ACLs, runtime libraries and license notices. Intel Mac and iOS support require their own artifacts/testing.
2. Add approved hosted acquisition/resumable downloads, signing/notarization, reviewed multi-version catalogs and target-device capability qualification. Verified offline package installation, resource rejection and ordinary-error restore are implemented, but are not a public model distribution service. Nothing is downloaded merely by choosing a mode today.
3. Add crash/orphan recovery and stronger parent-death supervision. Normal exit/cancellation is implemented; abrupt process death and power loss are not claimed as tested recovery. Keep account/key material out of logs, exports and backups.
4. Implement hosted account/session and gateway support after confirming website-host capabilities and approving any hosting costs. Online AI remains disabled until that exists; no client-side operator key is introduced.
5. Finish first-run onboarding and multi-window lifecycle checks, then validate on target Windows/Linux/iOS devices. Existing on-device Chrome/Apple providers are not relabelled as the Narratryx adapter. Desktop loopback never means a model on a different computer.

These release gaps do not prevent offline drafting. They must be resolved before advertising a plug-and-play service to ordinary users.
