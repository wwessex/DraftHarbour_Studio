# AI Suggestions sidebar and local request repair

Validated on 26 October 2026.

## Changes

Native macOS Suggestions now lives in a resizable document sidebar beside the manuscript. The document buttons, AI Panel command, and legacy Tools selections route Suggestions and Chat into the document; the two AI sidebars are mutually exclusive. The old floating Suggestions implementation is replaced.

The previous workflow sent an entire chapter plus project references to the managed model's 4,096-token context window. Some pipeline stages also discarded the custom instruction. The new native service passes explicit action instructions: advice uses the final 2,000 chapter characters and filtered Bible references bounded to 800 characters; revision actions use the selected passage or last paragraph, split into parts of at most 2,000 characters without dropping source characters. Custom instructions are limited to 2,000 characters. These bounds reduce request size; they are character limits, not guarantees for every possible tokenizer/input.

Generated text remains a preview. Explicit approval is required to append advice or replace the reviewed passage. Approval checks the entire original chapter snapshot, saves a recovery snapshot, preserves surrounding text, and records an AI revision. Discard and cancellation leave the manuscript unchanged. Existing provider configuration and managed-local policy apply; no cloud fallback was introduced.

Native Swift and Tauri Rust now distinguish context-limit, busy, authentication and other HTTP failures without reflecting private server response details into UI errors.

## Fresh checks

- Native app source build passed using SwiftPM's native build system and the installed macOS 26.5 SDK.
- Native `AISuggestionServiceTests`: 5 passed. Covers bounded long-chapter advice, direct custom instructions, selection-only replacement, stale-source rejection, lossless partitioning and safe context error classification.
- Standalone linked Swift smoke passed equivalent core checks. Using the installed managed local model, an unbounded 36,042-character synthetic chapter reproduced the context-limit failure. Suggestions then generated a 792-character preview for that same chapter, with the source unchanged. Only synthetic manuscript text was used. The smoke stopped its own model process afterward.
- Shared `AISuggestionsPanel.test.tsx`: 9 passed.
- Tauri core tests on this Mac: 18 passed, 2 ignored. This is a host test run, not a Windows/Linux package or device check.
- `git diff --check` passed.
- A separate development app bundle was built, ad-hoc signed, signature-verified and launched. Its verified binary was copied into `~/Library/Caches/DraftHarbour/BuildProducts/DraftHarbour.app`, preserving the previous bundle. `dist/DraftHarbour.app` points there. Build number: `2026102601`. This is not a notarized release.

## Platform scope and limits

Native macOS received the sidebar/service changes and local-model runtime checks. Tauri Windows/Linux received the safer HTTP error classifier and host Rust test coverage. The shared web/PWA, Tauri renderer and Capacitor iOS Suggestions implementation was inspected: it already uses a sidebar and bounded chapter-ending context. No shared runtime source was changed by this repair, so native web assets did not require synchronization.

GUI verification was attempted twice after launch, but computer use failed with ScreenCaptureKit error -3811 (audio/video capture failure). Therefore no fresh visual sidebar or GUI approval check is claimed. Windows/Linux installers, browser runtime and iOS simulator/device behavior were not executed for this repair. No author manuscript was edited.
