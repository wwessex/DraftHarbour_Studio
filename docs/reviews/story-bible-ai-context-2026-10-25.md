# Story Bible AI references — 25 October 2026

## Result

Shared Write, Rewrite, Continue, pipeline, inline suggestions and translation now receive read-only Story Bible references. The independent macOS writing assistant, selection actions, review generation and workflow tools use the native reference builder. Native chat's existing Bible access now labels reference data and filters author records to the current project.

The reference builders prioritise matching names/aliases, include live structured canon plus legacy character/world facts and notes, give structured canon precedence over same-name legacy records, and skip oversized entries rather than cutting their facts mid-entry. References fit a 3,200-character allowance; an omission notice discloses incomplete context. This is neither a whole-project semantic index nor a tokenizer guarantee. Temporal notes remain notes, not automatically resolved scene truth.

Selected Rewrite receives Bible references without unrelated chapter prose; its captured editable range and acceptance safeguards remain intact. Chrome's built-in provider uses the general Prompt API when canon references are present, avoiding specialised APIs that would treat the reference block as editable source. The managed-local provider and policy boundaries are unchanged. An online request includes the supplied project facts only when the user invokes an action with that configured provider. No training data is collected by this feature.

The existing uncommitted structured Story Bible implementation was preserved. The current work builds on its schema and UI; it does not claim that pre-existing work was newly authored during this task. No changes were made to another worktree or user manuscript.

## Fresh validation

| Version or check | Actual result |
|---|---|
| Web/PWA and shared Tauri/Capacitor renderer | Full `npm run ci` passed: lint, TypeScript, Vite configuration, **1,501 tests in 136 files**, production build, bundle and duplicate-asset checks |
| Working-tree changed coverage | Passed using `COVERAGE_DIFF_RANGE=HEAD`; 12 tracked source files at the existing 50% threshold. New reference builder separately measured at 93.54% line coverage; translation component at 82.85% |
| Windows/Linux Tauri core | Locked no-default-features Rust suite: **17 passed, 2 intentionally ignored real-model tests**. No Windows/Linux device or installer test |
| Capacitor iOS | `npm run build:native` passed and web assets/plugins synchronised. Simulator compile attempted; blocked because only Command Line Tools are selected, not full Xcode |
| Independent native macOS app | `swift build` passed against the macOS 26.5 SDK. Separate development bundle staged and ad-hoc signature verified without stopping the running app |
| Native core behaviour | Standalone executable linked against the freshly built core object passed assertions for canon filtering, alias ranking, project isolation, no mutation, omissions and character limits |
| Native XCTest | Attempted; blocked by missing XCTest in the installed Command Line Tools. The standalone smoke is not a substitute claim that the XCTest suite passed |
| Real local inference | Two independent no-history developer-service requests completed: alias lookup returned “No, Captain Venn cannot swim.” and passage rewrite returned “Mara could not swim.” These are nonblind functional smoke checks, not literary-quality ratings or packaged-runtime qualification |

Regression tests cover accepted canon versus draft/archive/other-project data, fields/aliases/links/validity notes, context budgets and omitted entries, read-only storage, highlighted Rewrite requests, pipeline requests, inline suggestions, translation preview/errors and browser-provider routing. No generated output was applied to the user's manuscript.

The browser session still held older loaded code. Its Write panel was inspected, but no reload was forced because no explicit saved-state indicator was exposed. Save, then refresh to load the new web code. No new native GUI run or Windows/Linux/iOS device acceptance test is claimed. Development web and the existing authenticated local inference service were restarted with their existing configuration; credentials were not changed or printed.

Mac development build (not notarised or published):
`/Users/williamwessex/Library/Caches/DraftHarbour/BuildProducts/StoryBibleAI-20261025/DraftHarbour.app`

## Model-development follow-up

The [local model improvement plan](../../llm/Narratryx/docs/local-model-improvement-plan-2026-10-25.md) separates project retrieval from training, identifies the latest pilot's evidence gaps, proposes source-traceable task examples and independent evaluation, and gates bounded MLX or approved cloud experiments on reviewed data. Generated literary teaching targets remain excluded. No training, paid cloud job, corpus upload, model promotion or publication ran under this task.
