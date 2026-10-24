# Writing selection and submission fixes — 24 October 2026

Two reported problems affected the main writing workspace: Rewrite could lose its highlighted target when focus moved into the assistant, and Write offered instructions without a clear submission control. The live model test also showed a separate inference-input problem: sending the surrounding chapter encouraged it to return paragraphs beyond a tiny rewrite target.

## Resulting behavior

- Shared web/PWA, Tauri and Capacitor controls capture the manuscript source/range before pointer focus changes and lazy composer mounting. The independent native macOS view creates its writing plan synchronously before expanding controls or scheduling generation. Native editor selection updates from focus-loss/field-editor activity no longer replace the manuscript highlight.
- Rewrite retains that target while instructions are edited, displays the original selected passage, rejects invalid/stale selections and replaces only the frozen span after explicit acceptance. With no selection, the final-paragraph fallback remains available and is labelled. Closing/reopening or changing chapters clears old scope; explicit new selections replace it.
- Rewrite sends only its target/task and author instructions to inference. It no longer sends the full chapter/story-bible continuity context as another passage to rewrite. Custom endpoint inference uses an editing-specific system instruction. Write and Continue retain continuity context.
- Both interfaces now have an explicit **Generate draft** button and active-action label, outside the scrolling instruction/preview region. Write opens/focuses instructions; Generate enables once nonblank directions are supplied. Loading disables generation and retains Stop. Suggestions remain previews until Append/Replace is chosen.

The implementation preserves UTF-16 offsets, source/chapter freshness checks, surrounding whitespace, snapshots/revision behavior, and offline drafting. No model training, credentials, dataset/benchmark hashes, persisted document schema or default provider changes are involved. A bounded target does not prove the model follows all stylistic instructions; the original target and replacement remain visible for review.

## Validation

Shared regression coverage includes a pointer-down selection followed by a collapsed editor caret, instruction edits followed by regeneration, exact replacement of a few words within a paragraph, partial multi-paragraph selection, emoji offsets, stale/invalid highlights, reopening without selection and Write→instructions→Generate→preview. The same fixture cases are used by native Swift tests. Native source builds successfully; local command-line tools lack XCTest, so current full-Xcode CI must be checked separately.

The local frontend CI chain passed **1,485 tests in 133 files**, lint, TypeScript, Vite configuration, production build, bundle budgets and asset checks. The native source build and separately staged app's ad-hoc signature check passed. These dated checks do not substitute for current Windows/Linux shell, full-Xcode Swift/iOS CI or device checks.

In the actual browser, selecting `a gull called` first exposed a model response containing surrounding paragraphs. After the input-context fix, the same displayed target produced `A gull called.` only. Write then generated a two-sentence lantern-at-dawn preview through the explicit Generate button. Neither preview was appended/replaced, and the chapter word count remained 939 throughout. These are scoped UI/inference checks, not literary-quality ratings.

Capacitor receives rebuilt/synchronized web assets; this is separate from iOS simulator compilation or a physical-device test. Tauri shares the corrected renderer; native macOS has separate source changes and compilation. Windows/Linux application runtime/device tests and current CI results must be reported distinctly.

A new native app bundle is staged in a separate local build-cache directory and its ad-hoc signature verified. The running Mac application was not stopped or overwritten because it contains the user's current draft. Save and quit that application before opening the separately staged build; the already-running process cannot acquire source changes through browser HMR. This is a local test build, not a notarized distribution.
