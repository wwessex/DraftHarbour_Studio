# Review implementation — 17 October 2026

This implements the reliability and author-workflow recommendations in the [16 October review](software-review-2026-10-16.md). Existing manuscript tables and IDs are preserved; database v5 adds backup and trash tables. No framework migration, paid service or new runtime dependency was introduced.

## Recommendations delivered

| Recommendation | Implementation and practical limits |
| --- | --- |
| Complete rotating backups | Project-owned manuscript, snapshots, comments, characters, world/research notes and blueprint. SHA-256 verified restoration as a new project; ten changed automatic versions plus retained named manual copies. Projects → Backups, recovery & trash includes contents and download. Copies on the same device do not protect against device loss. |
| Durable recovery | Each page lifetime journals merged pending chapter patches synchronously before the save delay. Recovery compares saved and recovered prose and creates a new chapter. Journal quota failure triggers immediate primary save and reports failure; no browser can guarantee recovery after all storage has failed. |
| Trash and safety versions | Chapter/project deletion archives content first. Trash restoration creates a separate project. Revision restoration takes a safety snapshot before changing the draft. Automatic chapter snapshots are deduplicated and capped at 30; named/safety versions are retained. |
| Portable projects | Web accepts ZIP and native JSON; native codec accepts web ZIP. Blueprint and story-bible collections travel with projects, identities and links are remapped, native history extensions are retained passively, and import opens the copied project. Shared fixtures and [contract](../contracts/dhproj-v1.md) document the boundary. |
| Revision comparison | Bounded aligned line comparison, current-versus-snapshot or snapshot-versus-snapshot review; existing editable snapshot names and named complete-project milestones. |
| Binder operations | Existing parts retained. Split at cursor preserves exact text and moves right-side comment anchors; a crossing comment blocks splitting. Scene plans remain in the first half because scenes have no prose offsets. Merge combines metadata, shifts comments and archives the merged section. Scenes move between chapters without losing metadata. |
| Search | Arrow/Enter navigation, accessible selected result, project-scoped saved searches and story-bible occurrence links. |
| Entity occurrences | Character/location names and aliases show bounded whole-name manuscript evidence with chapter links. No speculative continuity warnings or automatic prose changes. |
| Draft/Plan/Review | Three sidebar presets reuse persisted panel preferences. Fresh projects start with quiet planning panels. Empty chapters receive no heuristic criticism; insights are collapsed. Onboarding makes Start Writing primary. |
| Export handoff | Existing presets gain manuscript text/contents preview and empty-section/media warnings. Text-only EPUB 3 export adds navigation, metadata and chapter XHTML. Image embedding and certification across ebook readers remain outside this increment. |

## Additional fixes

Compatible dependency updates remove the audit findings reported in the original review. Sync comparison limits its matrix to one million changed-line cells and falls back to conservative conflict resolution; manuscript hash memoization is capped at 32 entries and excludes very large strings. Imports roll back auxiliary writes on reported failures, retain current installation sync configuration, and remap character/world references. Same-chapter content replacements now reach the editor after merges/restores.

The save queue, truthful save status, export flushes, legacy conversion, import validation and settings-load fixes from the original review remain included. Regression coverage exercises recovery failures, quota rollback, schema upgrade, trash, checksum corruption, chapter operations, EPUB structure and portable fixtures.

## Final verification

- **Passed:** `npm run ci` in `/tmp/writer1-validation`, a byte-count-verified copy of all 424 required source/config/fixture/assets files, with dependencies installed from the same lockfile. Cloud-placeholder reads in the original folder returned cancelled or empty file contents, so that folder's exact CI attempt was unsuccessful. No test scope or coverage threshold was reduced.
- **Passed:** **127 test files / 1,437 tests**, including quota rollback, recovery, v4→v5 migration, trash, checksum corruption, split/merge/comment anchors, scene movement, search, story-bible project isolation, optional onboarding, EPUB and native/web fixtures. Overall line coverage **66.39%**. New recovery journal and automatic-backup hook have 100% line coverage; chapter operations 95.12%, recovery UI 84.84%, recoverDraft 83.33%, EPUB 73.52%.
- **Passed:** changed tracked source coverage gate: **21 source modules**, minimum 50%, using `COVERAGE_DIFF_RANGE=HEAD` and the original Git working tree with the verified copy's coverage results.
- **Passed:** lint, typecheck, Vite config check, production build/PWA generation, bundle budgets and duplicate-asset check. Uncompressed budgets: main 441.8/800 KiB; export 239.1/240; AI 89.5/220; integrations 54.2/220; all JavaScript 3,197.3/3,500. The export chunk has little remaining headroom.
- **Passed:** locked install and dependency audit, **zero vulnerabilities** at validation time; iOS Capacitor asset/plugin sync using the validated production build and the real iOS project.
- **Passed:** `swift build --target DraftHarbourNativeCore`, including ZIP decoding. `swift test` could not compile XCTest because this machine has Command Line Tools rather than full Xcode. No native XCTest pass or native device certification is claimed.
- **Browser verified:** named verified backup creation and restore as a separate project; trash restoration with expected prose; recovered project selection/content after reload; export contents/text preview; EPUB preset download. The downloaded EPUB was checked for stored first-entry mimetype, parseable XML/OPF/XHTML, and expected manuscript text. Earlier split/merge and chapter-switch/reload checks remain documented in the original review.
- **Passed:** final whitespace/diff check. Changes remain uncommitted; unrelated files are retained.

The local server on port 5174 uses the verified temporary source copy because the original folder and its dependencies have intermittent cloud-placeholder failures. Ordinary builds in the original folder need it kept available offline. Existing generated `dist/` could not be replaced reliably; the passing production build is in the validation copy and its assets were successfully synced into iOS.

The native app still needs Xcode/XCTest and device validation before release. Real sudden process termination, concurrent-window races, screen readers and credential-backed integrations were not certified. Auxiliary data remains in localStorage; rollback handles reported failures but is not a crash-atomic transaction across localStorage and IndexedDB. Global story-bible entries, external media and installation credentials are outside project backup scope. A unified project repository remains a future architectural migration.

![Verified export preview and EPUB preset](/Users/williamwessex/.codex/visualizations/2026/10/16/01a146bd-5fa4-77c1-851f-24a617837a08/implementation/export-preview.png)
