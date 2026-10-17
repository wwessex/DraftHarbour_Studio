# All-version parity follow-up — 17 October 2026

The earlier work updated the shared web frontend used by the PWA, Windows/Linux Tauri shell and Capacitor iOS wrapper. It did **not** implement every equivalent workflow in the independent native macOS application. This follow-up addresses that omission.

## Changes applied

- Added complete, SHA-256-verified native project backups with atomic file writes, ten changed automatic copies, retained named manual copies, and restoration into a new project file. The native sidebar opens Backups & Trash. Backups contain the complete native envelope, including research/story-bible data, blueprint, snapshots and comments. These are local copies; external backups remain necessary.
- Native chapter deletion now retains the section, snapshots and comments in portable trash. Restoration creates a new chapter with fresh identities. Native projects are document files, so project-file deletion/recovery remains the operating system's Trash workflow.
- Native recovery now compares saved and recovered writing, saves a safety copy before an older recovery file can be replaced, restores into a separate project, reports write failures accurately and preserves unreadable recovery files. The Save command no longer clears recovery before save completion. Recovery paths cannot escape their directory through an imported project identifier.
- Added native split at UTF-16 cursor, merge-next and scene movement. Comment anchors and metadata are preserved; crossing comments block splitting. Split/merge create safety versions and merged sections remain recoverable.
- Native snapshots now retain 30 deduplicated automatic versions while preserving manual milestones, take a safety version before restoring, offer a comparison selector and use bounded aligned line comparison with side-by-side rows.
- Added project-scoped saved native searches; Enter selects a result and the native list supplies keyboard navigation. Added bounded Unicode name/alias evidence with chapter links for native characters and world entries. Existing native Write/Corkboard/Review workspaces retain their preferences; fresh native documents start with a quiet inspector and optional blueprint setup.
- Added native export contents/text preview and text-only EPUB 3 with navigation, escaped XHTML, basic emphasis and explicit omitted-image markers. EPUB is available in presets, format selection and settings. Existing native export preflight remains active.
- Native project decoding validates manuscript references and duplicate section IDs, converts legacy rich content and accepts web ZIP/native JSON. Restore/import copies remap IDs and do not activate imported sync/provider credentials. Web round trips now retain native `deletedSections` alongside native history extensions.
- Fixed a native replacement loop that did not terminate when the replacement contained the search query. Project replacement clears reorder history.

## Verification actually performed

| Version / component | Result | Limits |
| --- | --- | --- |
| Web/PWA shared frontend | Full CI chain passed in the verified local source copy: 127 files / 1,437 tests, lint, typecheck, Vite config, coverage, production/PWA build, bundle budgets and assets check. Portable native-trash round-trip regression included. | Cloud-placeholder failures still affect direct reads in the original folder. |
| Native macOS core | Builds; nine executable safety checks passed against the compiled core, covering recovery paths, trash/comments/snapshots, split/merge/scenes, safety restore, retention, backup rotation/corruption, aligned diff/mentions, replacement termination, legacy import and EPUB structure. The same cases are checked into `ProjectSafetyTests.swift` for XCTest. | Executable checks used assertion equivalents because XCTest is unavailable; this is not a full XCTest-suite pass. |
| Native macOS application | Full SwiftUI/AppKit app build and local ad-hoc signed bundle completed with installed macOS 26.5 SDK. Normal bundle metadata restored; artifact is linked at `dist/DraftHarbour.app` and stored under `~/Library/Caches/DraftHarbour/BuildProducts/`. | Default SDK 27 fails because this Command Line Tools installation lacks SwiftUIMacros. `swift test`, including with SDK 26.5, fails on missing XCTest. GUI launch/inspection could not be verified because Computer Use permissions are not granted. |
| Tauri native shell | Eight Rust tests passed on the Mac host, using the same verified source copy and lockfile. Tauri configuration points at the shared frontend build. | Windows and Linux binaries were not executed on this Mac. |
| Capacitor iOS | Final production assets/plugins synchronized into the real iOS project; Capacitor Doctor passed. | Simulator compilation and device behavior require full Xcode; no device test claimed. |
| Future PR checks | Added Windows/Linux Tauri Rust test jobs and an iOS simulator build job; retained native macOS tests/app build and web checks. Workflow YAML parsed successfully. | New remote jobs are configured, not yet run or claimed passing. |

The native build script accepts `DRAFTHARBOUR_MACOS_SDK` to select a compatible installed SDK. Validation used `DRAFTHARBOUR_MACOS_SDK=/Library/Developer/CommandLineTools/SDKs/MacOSX26.5.sdk` and a temporary scratch directory. This is a local development build, not a notarized release or App Store submission.

## Standing instruction

The user's preference is saved in both `/Users/williamwessex/.codex/AGENTS.md` and the repository `AGENTS.md`: inspect, implement and validate **every applicable maintained version** by default, including independent native implementations; disclose platform/toolchain limits. The global instruction was subsequently supplied back into this chat, confirming that it is being loaded.

Changes remain uncommitted. Existing manuscripts were not opened or modified through terminal scripts. No release was published.
