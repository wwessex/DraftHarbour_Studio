# Chat layout, Apple model availability and toolbar repair

Changes and fresh checks on 29 October 2026.

## Repairs

- Native Chat has a dedicated scroll area for the transcript and proposed edits. Provider/thread controls and the bounded message composer sit outside that area. Long messages wrap to their full height; new messages and thread changes scroll to the bottom. The surrounding document no longer wraps the whole Chat panel in a second ScrollView.
- Apple Foundation Models is gated by its public SDK module and OS availability. The previous `canImport(FoundationModelsMacros)` condition was always false here because macro implementations are compiler plugins, not importable modules. This incorrectly bypassed the system availability API and disabled both generation and tool-assisted Chat even though the system model was available. All five guards in the independent native implementation are corrected. A regression test compares the provider's status with the real public system API.
- The custom left-sidebar toolbar button is removed, retaining NavigationSplitView's standard toggle and the existing menu/keyboard command.
- Formatting controls have descriptive hover help and accessibility labels. Split, Merge, status, workspace selection, writing actions, AI setup and preview controls have additional hover help. Existing toolbar help remains.
- Shared web/PWA, Tauri renderer and Capacitor Chat already separated transcript scrolling from the composer. Its resizable input is now capped at 150px and the sidebar clips overflow; the chapter list is bounded to 20vh so it cannot crowd out the conversation. Shared toolbar IconButtons already expose hover titles.

## Validation

- Full native app build passed using Xcode 27.1's selected Swift toolchain and public Foundation Models SDK. A signed development bundle (build `2026102901`) was staged separately, signature-verified, then installed at `~/Library/Caches/DraftHarbour/BuildProducts/DraftHarbour.app` while that bundle was not running. Previous bundles were preserved. No app was stopped and no author manuscript was edited. Local ad-hoc signing is not notarization.
- A linked synthetic smoke reports the app provider as `available`, generates 148 characters through Apple Foundation Models, and receives a 52-character tool-assisted Chat reply. Both ran on device using synthetic text.
- Shared lint and typecheck passed. Eight focused Chat/Header/AppShell tests passed. Production build and Capacitor asset sync passed.
- iOS simulator Debug compilation passed with signing disabled. This is compilation, not a launched simulator/device check.
- Native XCTest: 16 tests passed across AIChatTests, ManuscriptChatTests and NaturalWritingStyleTests, including the real public-SDK availability regression. The repository-local build cache hit iCloud file-change errors, so the successful test run used a separate local cache at `~/Library/Caches/DraftHarbour/SwiftChatRepair-20261029`. Offloaded source files were hydrated; no source content was replaced to bypass synchronization.
- Changed native files passed `git diff --check`.
- GUI verification was attempted after the previous app had exited. The updated app process launched, but computer use failed with ScreenCaptureKit error -3811 (audio/video capture failure). Therefore long-reply scrolling, hover rendering and the single toggle have source/build validation but no fresh visual pass or screenshot.

## Version coverage and limits

Independent native macOS received the availability, scrolling and toolbar fixes plus the live Apple-model check. Web/PWA and the shared Windows/Linux Tauri and Capacitor renderer received the CSS bounds, tests/build and synchronized assets. Native Apple Foundation Models is a macOS feature; no browser/iOS provider support was invented. Windows/Linux installers and runtime/device checks were not executed. The existing project, provider, approval, snapshot and manuscript formats are preserved.
