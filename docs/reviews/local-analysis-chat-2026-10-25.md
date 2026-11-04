# Local manuscript Analysis and AI Chat

Current whole-manuscript Chat and approval behavior is documented in [the later implementation report](whole-manuscript-chat-2026-10-25.md). The excerpt-only description below records the earlier implementation.

Analysis now offers an explicit **Review all chapters/scenes** action in the shared application and independent native macOS application. It snapshots manuscript text, reviews every non-empty section in bounded parts, preserves per-part feedback, and reduces all findings into overall feedback and revision priorities. Cancellation and errors retain completed feedback. Feedback never applies manuscript changes. Reports are held in the current view, not saved into portable project data; rerun after editing.

AI Chat has its own right sidebar. In web/PWA, Tauri and Capacitor, open **Tools → AI Chat** (or the quick switcher). It uses the configured local provider, six recent conversation turns and the first 4,000 characters of the active chapter/scene. The excerpt limit is displayed; it is not a claim of full manuscript awareness. Chat is held for the current project session and cleared on project change. Native macOS retains its existing project-backed threads, context tools and explicit edit proposals; its AI Chat command now toggles a sidebar beside the workspace rather than opening a tool window.

Both workflows require on-device AI or an explicitly configured exact loopback endpoint. Cloud providers and cloud fallback chains are excluded. Managed policy and the AI-off preference still apply. Tokenless local OpenAI-compatible endpoints are called directly without passing through the cloud broker. Native macOS offers configured local providers and Apple Foundation Models; availability depends on device setup. Analysis does not inject Story Bible fields, so hidden or conditional facts cannot leak through that path.

The shared frontend covers web/PWA, Windows/Linux Tauri renderers and Capacitor iOS. A desktop managed model package is not installed by browser or iOS builds. Loopback endpoints always refer to the device running the client. Windows/Linux managed package availability remains subject to the existing verified catalog.

## Fresh validation on 25 October 2026

| Application | Source and build checks | Runtime checks and limits |
| --- | --- | --- |
| Web/PWA | Shared implementation; lint, production TypeScript/Vite build, bundle budgets and duplicate-asset checks passed. Full Vitest run: 141 files / 1,539 tests passed; final focused run: 37 tests passed. | Isolated Chromium desktop and 390×844 mobile browser checks covered Analysis entry/action, independent Chat sidebar, mobile tab/layout and local-model setup errors. No local HTTP model was running, so live model responses were not evaluated. PWA installation/offline launch was not exercised. |
| Windows/Linux Tauri | Shared renderer updated and built. Host Rust test run using the cached target directory: 17 passed, 2 ignored. No Rust source changes. | Rust checks ran on macOS; no Windows/Linux shell build or device/runtime check was performed. Existing catalog limits still apply. |
| Capacitor iOS | Shared renderer updated; final `npm run build:native` built and synchronized generated web assets successfully. No authored wrapper changes. | Simulator compilation was attempted and blocked because full Xcode is absent; active developer directory is Command Line Tools. No iPhone/simulator runtime check. |
| Independent native macOS | Native Analysis service/view, local-only Chat selection/guard and document sidebar updated. Fresh source build of `DraftHarbourNative` succeeded with `--build-system native --sdk /Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk`. | Fresh standalone service smoke linked against the newly compiled core and passed all-part coverage, later/empty sections, overview generation, exact-loopback classification and remote-chat rejection using an injected local test provider. No GUI launch or live model inference check. XCTest was attempted but blocked by the missing XCTest module in Command Line Tools; the default SDK additionally lacks the SwiftUI macro plugin. Added XCTest regressions remain unexecuted. |

The initial bundle-budget attempt counted stale duplicate files in generated `dist/assets`; the final rebuild removed them. The final bundle check passed at 3,244.9 KiB of JavaScript against the 3,500 KiB limit. Existing manuscripts and unrelated working-tree edits were preserved.

## Connection recovery follow-up — 25 October 2026

The configured experimental service at `http://127.0.0.1:8890` had stopped. Restarted the existing authenticated local MLX service using its existing environment, pinned artifacts, private token file and explicit app-origin allowlist. No token was changed or printed; no cloud fallback, download or training was introduced. This developer service must remain running for the browser connection to work; browser code does not start a desktop model process.

Shared HTTP providers now replace browser transport errors with local-service/endpoint recovery guidance, while preserving cancellation. Suggestions reloads configuration when settings change, reads the current provider before generation and hydrates desktop Keychain secrets. Saving a provider notifies already-open panels even when the setup mode remains unchanged. Native macOS maps unreachable-service errors to equivalent recovery guidance.

Fresh results for this follow-up:

- Actual user browser: connection test succeeded; Suggestions returned a real local model generation; Chat returned a real local model answer about pacing. Neither response was applied to the manuscript. The local service remained healthy at completion.
- Full web suite: **1,544 tests passed in 141 files**. A subsequent additional stale-provider regression was verified in a fresh **9-test Suggestions panel run**. Lint, production build, bundle budgets and asset checks passed. Identical duplicate generated files were archived outside the checkout before the final asset check/sync; original assets were preserved.
- Shared renderer changes cover web/PWA, Windows/Linux Tauri and Capacitor iOS; final generated assets were synchronized with Capacitor. No Windows/Linux executable or iOS device checks were performed for this follow-up. No Rust or wrapper source changed.
- Independent native macOS source build passed with SDK 26.5 and the native Swift build system. A fresh linked native transport smoke verified both stopped-service guidance (injected URLProtocol failure) and a real authenticated local Narratryx completion. Added native XCTest coverage remains unexecuted because XCTest/full Xcode is unavailable. No native GUI relaunch was performed.
