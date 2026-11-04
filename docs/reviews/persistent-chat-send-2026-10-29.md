# Chat Send visibility and request lifetime

Implemented and validated on 29 October 2026.

## Changes

The previous native layout gave the flexible transcript higher layout priority than the composer. Chat now gives the composer its intrinsic height and priority, letting the transcript use the remaining scrollable area. Send is enabled for a nonempty message while idle. Availability text is informational; the live provider performs the final availability/policy check and reports an actionable error, allowing a newly ready Apple model to be used without a stale UI gate.

`AIChatSession` now owns the request, selected thread/provider, input and progress at document scope. Sidebar view disappearance no longer cancels or loses the request. Moving between Write, Corkboard and Review, hiding Chat, or temporarily replacing its presenter retains the same session. A window-scoped AppKit bridge cancels on actual document-window closure, rather than visibility changes. Explicit Stop and project replacement also cancel. Late replies are rejected after cancellation or a project-ID change. Duplicate submissions are blocked synchronously; provider, edit permission and question are captured for the request. Existing thread history, local-only checks and edit approval/source guards remain.

Shared web/PWA, Tauri renderer and Capacitor Chat no longer abort when their sidebar is hidden. Explicit Stop, project changes and component disposal retain cancellation. Pending results and progress remain available on reopening Chat.

## Fresh checks

- Native app build passed using Xcode's selected toolchain and the local non-iCloud Swift build cache.
- Native tests: 15 passed (AIChatSessionTests and AIChatTests). New coverage includes presenter replacement during a pending request, duplicate sends, explicit cancellation with a late result, subsequent requests, and rejection of a reply after project replacement.
- Live synthetic Apple Foundation Models check: a message submitted through the document-owned session completed and stored an assistant reply. No author manuscript was used.
- Shared lint and typecheck passed. All five Chat sidebar tests passed, including hiding/reopening Chat during a deferred manuscript review without starting another provider or losing the result.
- Production web build and Capacitor asset sync passed.
- iOS simulator Debug compilation passed with signing disabled. No simulator/device launch is claimed.
- Changed tracked sources passed `git diff --check`.
- Development macOS build `2026102902` was staged, ad-hoc signed, signature-verified and installed at `~/Library/Caches/DraftHarbour/BuildProducts/DraftHarbour.app` while that bundle was not running. A separate signed copy is in `BuildProducts/PersistentChat-20261029/DraftHarbour.app`; previous app bundles were preserved. No process or author manuscript was modified to stage it. This is not a notarized release.

## Limits and parity

Native macOS received independent session ownership, composer and window-lifetime changes. The shared web/PWA, Windows/Linux Tauri and Capacitor renderer received the sidebar cancellation fix, tests/build and refreshed iOS web assets. Windows/Linux installers were not built or run. The live Apple test verifies the send/service path, not button geometry. Fresh visual/hover checks remain unavailable because this session's computer-use tool fails with ScreenCaptureKit capture error -3811, as recorded in the preceding repair report. No new successful visual check is claimed.
