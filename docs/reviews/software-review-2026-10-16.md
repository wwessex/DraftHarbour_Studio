# DraftHarbour Studio development review — 16 October 2026

The app has enough functionality to support serious drafting. Its next investment should be confidence in saving, restoring and moving complete projects between runtimes. This session fixed focused persistence problems without changing the database schema, adding dependencies, removing features or touching existing manuscript databases through terminal commands.

## A. Overall assessment

These are provisional engineering judgements after the fixes, based on source review, automated checks and the browser workflow below. They are not scores from a long-term author study or a complete native release certification.

| Area | Score / 10 | Assessment |
| --- | ---: | --- |
| Functionality | 7.5 | Broad drafting, planning, screenplay, export, analysis and integration capabilities. Completeness varies by runtime and configured backend. |
| UX/UI | 6.5 | Comfortable writing surface and coherent warm palette. Planning controls, heuristic scores and AI setup compete with the first writing task. |
| Performance | 6.5 | CodeMirror, lazy modals and virtual chapter navigation are useful foundations. The PDF bundle is large; long-project and sync workloads need benchmarks. |
| Stability | 6.5 | Strong test inventory, but important persistence defects were present. A recovery warning still does not recover an unsaved manuscript delta. |
| Code quality | 7 | Typed models and service boundaries help. Duplicate frontend/native implementations, mixed storage and broad context updates increase maintenance costs. |
| Suitability for novelists | 7 | Chapters, scenes, goals, snapshots, character/world tools and focus mode cover substantial ground. Recovery, complete backups and revision workflows need more confidence. |

### Architecture and feature interactions

- The web/PWA application uses React 19, TypeScript, Vite, CodeMirror 6, CSS modules/Tailwind and Dexie. Manuscript and snapshot content is Markdown, with a migration from older Tiptap JSON.
- AppContext coordinates project selection, settings, chapter metadata, scenes and editing. Editor changes update React state immediately; persistence is delayed. Backup/export operations must therefore await pending writes.
- IndexedDB holds novels, chapters and snapshots. localStorage holds settings, comments, story blueprints, characters, world entries, progress and integration metadata. These stores cannot participate in one atomic transaction.
- Tauri supplies the Windows/Linux shell; Capacitor wraps the web application for iOS. macOS also has a separate SwiftUI/AppKit document application and Swift core, including atomic recovery-file writes.
- AI and integration providers use optional local/remote brokers or platform adapters. Their real credential-backed operation was not exercised. Static hosting does not provide those backend services.

## B. Problems discovered

| Severity | Finding | Outcome |
| --- | --- | --- |
| High | A single debounced callback discarded earlier chapter edits and earlier fields when another update arrived. | Fixed: merge pending patches by chapter and serialize writes. Failed patches remain pending for retry. |
| High | Backup and project-file export could read IndexedDB before the latest typing reached it. | Fixed: await pending chapter writes; abort export when saving fails. Imports and project changes also flush pending writes first. |
| High | Older rich-text backup/project imports bypassed the existing IndexedDB migration. | Fixed: convert imported chapter content, sync baselines and snapshot content to Markdown before insertion. |
| High | Imported comments or snapshots could retain a foreign chapter ID; a colliding comment ID could overwrite a local comment. Duplicate source chapter IDs also made remapping ambiguous. | Fixed: reject duplicate IDs and unknown chapter references before imported data is written. |
| Medium | The unsaved warning used a timer instead of persistence completion; the header could report Saved after a failed write. | Fixed: derive pending status from the save queue and retain Unsaved changes until successful persistence. |
| Medium | pagehide marked a session clean even with unsaved edits. Changing callback identity could also mistake the current session marker for an earlier crash. | Fixed, including legacy beforeunload compatibility. |
| Medium | StrictMode mount-effect replay could overwrite stored settings with defaults, repeating onboarding and losing preferences in development. | Fixed: do not persist defaults before stored settings finish loading. |
| Medium | Test discovery entered a nested checkout; Vite dependency scanning entered generated native HTML. | Fixed: scope test discovery and web entry scanning; exclude generated/native build trees from lint. |
| Medium | A search-test context fixture created fresh chapter arrays every render, causing an infinite effect loop. A dashboard test depended on a now-expired calendar date. | Fixed: stable fixture and explicit test date. |
| Documentation | README described Tiptap, direct static serving of source and CDN-loaded dependencies. | Corrected editor and Vite run/build instructions and dependency description. Other backend availability claims still merit a documentation pass. |

### Outstanding risks

1. **High, release priority: dependencies.** `npm audit --json` reported 32 affected dependency entries: 4 critical, 20 high, 7 moderate and 1 low. Counts include transitive chains; they do not establish 32 exploitable application paths. The installed iOS runtime is covered by the [Capacitor origin/proxy advisory](https://github.com/advisories/GHSA-rvm3-566m-v7fv). The [Vitest UI-server advisory](https://github.com/advisories/GHSA-5xrq-8626-4rwp) and [Vite development-server advisory](https://github.com/advisories/GHSA-p9ff-h696-f583) concern development exposure. Schedule compatible updates and native rebuild validation before release. Dependencies were not upgraded in this session.
2. **High: backup completeness and transaction boundaries.** JSON backup contains manuscript sections, snapshots and comments, but not the character/world collections or story blueprint. The richer `.dhproj` exporter includes characters/world entries but still omits the story blueprint. Auxiliary localStorage writes happen after the IndexedDB import transaction, so quota failures can leave a partially restored project. A format/transaction redesign needs approval and migration planning.
3. **High: sudden termination.** Pending failed writes survive in memory during the current session. They do not survive process death. pagehide flushing is best effort, and browsers may terminate without firing it. A durable recovery journal remains necessary.
4. **Medium: import identity and navigation.** Character/world IDs are not regenerated alongside chapter IDs when importing a copied project. Imported projects are followed by reload, but workspace selection can still point at the old project. Follow up with focused entity-isolation and project-selection tests.
5. **Medium: long-project cost.** The sync merge uses a quadratic line-comparison matrix, and content hashing memoizes whole manuscript strings without eviction. Chapter-switch snapshots are unbounded. These are code-level scalability risks; no large-novel stress benchmark was run.
6. **Medium: deletion recovery.** Chapter deletion removes both manuscript and snapshots. A recoverable trash and a safety snapshot before restoration would make destructive actions easier to trust.

## C. Changes implemented and verification

### Files affected

| Purpose | Files, relative to repository root |
| --- | --- |
| Autosave queue and persistence integration | `src/lib/chapterSaveQueue.ts`, `src/context/AppContext.tsx`, `src/App.tsx` |
| Save feedback and reduced-motion support | `src/components/Header/Header.tsx`, `SaveStatus.tsx`, `SaveStatus.module.css` |
| Backup/import ordering and recovery markers | `src/hooks/useProjectFileActions.ts`, `src/hooks/useCrashRecovery.ts` |
| Import conversion and reference validation | `src/lib/storage.ts` |
| Tooling and instructions | `vite.config.ts`, `eslint.config.js`, `README.md` |
| New regression suites | `src/lib/chapterSaveQueue.test.ts`, `src/lib/storage.importSafety.test.ts`, `src/context/AppContext.persistence.test.tsx`, `src/hooks/useCrashRecovery.test.tsx`, `src/hooks/useProjectFileActions.test.tsx` |
| Updated existing tests | AppContext actions, SaveStatus, DashboardModal and SidebarSearch suites |

### Verification performed

- **Passed:** final coverage run, **119 test files / 1,402 tests**. Overall line coverage: **63.90%**. Save queue, crash-recovery hook and SaveStatus each have 100% line coverage; project-file actions have 71.87%. Coverage percentage is not a guarantee of correct behavior.
- **Passed:** TypeScript typecheck; ESLint over `src`, `vite.config.ts` and `eslint.config.js`; whitespace/diff check.
- **Passed:** changed tracked source coverage gate, using `COVERAGE_DIFF_RANGE=HEAD` to include this session's uncommitted tracked changes. New save-queue source was also checked directly in the coverage summary.
- **Passed:** Vite config loading with serve/test conditions; production Vite build and PWA generation with current source and temporary copies of tracked public assets recovered from Git.
- **Passed:** the repository's bundle budget script against a clean temporary production build: main 435.0 KiB / 800; export 225.5 / 240; AI 89.5 / 220; integrations 53.7 / 220; total JavaScript 3,173.7 / 3,500. Values are uncompressed.
- **Passed:** duplicate-asset check against temporary copies of tracked assets. No duplicate filenames with mismatched hashes.
- **Browser verified:** enter writing workspace, type in chapter one, create/type chapter two, switch back, reload and confirm both chapters' text. After the settings fix, dismissed onboarding remains dismissed after reload.

**Environment limits:** the initial installed dependencies and several workspace files timed out during filesystem reads. `npm ci` restored dependencies but its Husky prepare hook hit an unavailable placeholder file. The ordinary `npm run build` could not write the cloud-placeholder `tsconfig.tsbuildinfo`; public assets and an unrelated untracked TypeScript copy also blocked ordinary build/root lint. Verification used `tsc --noEmit`, scoped lint and temporary recovered assets rather than replacing those user files. The exact full `npm run ci` command was not passed. Native builds, device behavior, screen readers, actual crash recovery, service-worker updates and credential-backed integrations were not certified.

### Captured UX flow

1. **Onboarding.** Clear dialog title, visible focus ring and Skip affordance. The opening message makes AI setup the main rationale; offer Start Writing as the primary author task, with blueprint setup optional. The screenshot establishes presentation, not full keyboard or screen-reader compliance.

![Step 1: onboarding](/Users/williamwessex/.codex/visualizations/2026/10/16/01a146bd-5fa4-77c1-851f-24a617837a08/review/01-onboarding.png)

2. **Empty writing workspace.** Warm neutrals, clear selected chapter and a generous writing surface provide a sound design direction. Expanded planning panels consume sidebar space before there is content. DOM inspection also exposed heuristic criticism on an empty chapter. Default those suggestions to quiet/optional and retain a clear route to planning.

![Step 2: writing workspace](/Users/williamwessex/.codex/visualizations/2026/10/16/01a146bd-5fa4-77c1-851f-24a617837a08/review/02-writing-workspace.png)

3. **Reloaded draft at a narrower viewport.** Chapter two's prose survived reload, and Write/Outline/Inspector navigation is visible. Several toolbar actions use icons alone and save text collapses at narrower widths. Inspect accessible names, keyboard order, contrast and zoom with dedicated accessibility testing before assigning compliance claims.

![Step 3: reloaded second chapter](/Users/williamwessex/.codex/visualizations/2026/10/16/01a146bd-5fa4-77c1-851f-24a617837a08/review/03-reloaded-second-chapter.png)

## D. Ten future improvements, ranked

Effort is relative engineering scope, not a delivery estimate. P0 is reliability/release work; P1 is the next author-workflow investment; P2 follows that foundation. Some proposals extend existing functionality.

| Rank | Improvement | Author benefit | Effort | Priority |
| --- | --- | --- | --- | --- |
| 1 | Verified rotating complete-project backups, with restore checks and an explicit contents list | Very high: confidence that the whole novel project can be recovered | Medium–large | P0 |
| 2 | Durable crash journal and recovery screen showing saved versus recovered text | Very high: recover typing after termination or storage errors | Medium | P0 |
| 3 | Recoverable chapter/project trash and automatic safety versions before restoration | Very high: safer editing and fewer irreversible mistakes | Medium | P1 |
| 4 | Portable project round trips covering blueprint, story bible, research, links and stable identity | High: consistent projects across web, desktop and backups | Medium–large | P1 |
| 5 | Revision comparison with readable diffs, named milestones and side-by-side review | High: easier structural and prose revision | Medium | P1 |
| 6 | Extend the binder with parts, movable scenes, split/merge and preserved metadata | High: manage full-length novels comfortably | Large | P1 |
| 7 | Extend manuscript search with keyboard result navigation, saved searches and entity cross-links | High: find and fix references across long drafts | Medium | P1 |
| 8 | Character/location occurrence views with linked evidence and optional continuity warnings | High: keep a long novel consistent without noisy judgement | Medium | P2 |
| 9 | Simplify Draft/Plan/Review entry points and remember sidebar/focus preferences | High: lower cognitive load during sustained writing | Medium | P2 |
| 10 | Export presets, preview/preflight and tested editorial handoff; assess EPUB demand | Medium–high: fewer surprises outside the app | Medium | P2 |

Comparator grounding: [Scrivener](https://www.literatureandlatte.com/scrivener/overview) connects its binder/corkboard workflow and snapshots; [Ulysses backups](https://help.ulysses.app/backups) and [goals](https://help.ulysses.app/goals) emphasise protection and sustained writing; [Novelcrafter's Codex](https://www.novelcrafter.com/features/codex) connects story-bible entries to manuscript mentions. The proposed ranking is an inference about DraftHarbour's current gaps, not a claim that every comparator workflow was tested here.

## E. Architectural advice

Keep React, TypeScript, Vite and CodeMirror for the web application. No reviewed evidence justifies a language or framework migration. Rust remains appropriate for Tauri-specific native boundaries, and Swift fits the existing native macOS document application. Rewriting working features would cost more than tightening persistence and cross-runtime contracts.

Establish one documented `.dhproj` contract with shared example files and round-trip tests for TypeScript and Swift. Explicitly define optional fields, legacy content conversion, entity IDs, relationships and backup inclusion rules. Decide whether maintaining two independent desktop UI implementations is worth the ongoing parity cost before expanding both.

With approval, consolidate project-owned auxiliary data into a transactional project repository, with explicit migrations and recovery copies. Retain small non-project preferences separately. Preserve explicit AI/provider opt-in; new AI work should offer source-linked suggestions, previews and reversible application rather than automatically altering prose.

## F. Practical roadmap

1. **Release preparation:** update vulnerable dependencies in a focused compatibility change; rebuild/retest iOS; make the workspace fully available locally and rerun the exact repository CI chain. Resolve remaining README/backend-availability claims.
2. **Reliability milestone:** approve and design complete backup coverage, durable recovery, entity remapping and recoverable deletion. Add failure-injection tests for quota errors, concurrent windows and interrupted imports before migrations ship.
3. **Author workflow milestone:** improve revision comparison, manuscript search and scene movement. Make empty-state advice quiet; test the first five minutes with authors before changing the wider design.
4. **Scale and accessibility milestone:** benchmark representative large novels, cap caches/snapshot retention, move expensive analysis off the typing path, and test keyboard, screen-reader, contrast, reduced-motion and zoom behavior.
5. **Selective differentiation:** expand linked story-bible/continuity features and export polish after the reliability foundation passes. Avoid adding more providers or dashboards without evidence that they help authors finish and revise novels.
