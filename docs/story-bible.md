# Story Bible

Open **Tools → Story Bible** (native macOS: the Story Bible tool). **Story entries** is the structured editor; **Characters & World** retains existing records and their established AI context behavior.

Create an entry with **New entry**. Choose a category and canon status, then record notes, aliases, tags, custom fields (`Name: value` per line), provenance and optional story-time bounds. Filtering the entry type before creation selects that category's starter fields. Save explicitly; save or discard pending edits before selecting another entry. Existing manuscript mentions are alias-aware and jump to their chapter. Links are project-local; backlinks show entries linking to the current one.

New entries start as drafts (research and source templates start as research). Only live entries explicitly marked **canon** enter the existing AI context pipeline. AI does not create or promote structured entries automatically. Valid-from/until fields are free-text notes; the app does not determine which facts are valid at a scene automatically.

Every saved change to an existing entry records its previous state. **Restore this version** creates another revision, preserving subsequent history. **Archive entry** keeps the entry and all revisions; use **Archived** to find it and unarchive it.

JSON exports retain archived entries and history; Markdown is a readable export of live entries. **Import JSON** accepts the exported `bibleEntries` collection (up to 20 MiB), creates new IDs and remaps internal links. Full `.dhproj` projects and project backups also include the collection. Imports do not replace manuscripts or activate credentials.

The implementation is local and works without AI or networking. Web/PWA, Tauri and Capacitor use the shared React editor; native macOS has an independent SwiftUI editor and the same portable data shape. Deep Research, automated contradiction checks, temporal querying and graph views remain future work.

## AI references

Write, Rewrite, Copyedit, Continue, the writing pipeline, suggestions and translation receive a bounded subset of the current project's Story Bible references. Native macOS writing, selection/review actions and chat also read project references. Matching names and aliases prioritise entries for writing requests; this is simple relevance matching, not a complete semantic search or automatic timeline resolver. Existing Characters & World notes remain available. Explicit structured canon takes priority over legacy records with the same name in the writing reference block.

Structured draft, disputed, research, superseded, deprecated, AI-suggestion and archived entries are excluded. References are labelled read-only and kept separate from the requested text; a highlighted Rewrite still targets only that span. Entry titles/IDs, fields, aliases and validity notes help the model identify facts. Large entries may be skipped whole; an omission notice tells the model that the supplied subset is incomplete. The 3,200-character reference allowance is not a tokenizer guarantee or a complete project-context budget. Models can still make mistakes; review suggestions before accepting them. Chrome's built-in provider uses its general Prompt API when references are present so its specialised Rewriter cannot accidentally rewrite the Bible itself.

References go only to the provider you explicitly configured when you request an AI action. An online provider receives the included project facts as well as the writing context. Local mode retains its existing local-only enforcement; this feature does not enable another provider or upload anything for training. Reading the Bible for inference never authorises training on it, and the model does not edit or promote entries through these writing actions.

For the independent model-development roadmap, see the [local model improvement plan](../llm/Narratryx/docs/local-model-improvement-plan-2026-10-25.md).

## AI field access and scene facts

Expand **AI reference access** in an entry to hide the whole entry or individual notes, aliases, validity notes and custom fields from structured AI references. Titles stay visible unless you hide the entry. New or renamed custom fields start hidden until you allow them; existing fields retain their prior behaviour. Save the entry explicitly.

**Only use when** accepts conditions such as `form=human, timeline=before`. Supply matching **Scene facts** in the writing assistant. Conditions compare exact values; missing, mismatched or invalid facts exclude that field. Other tools without scene facts omit conditional fields. Scene facts stay in the current composer, clear on chapter/section changes or close, and are not saved in the project. Validity notes remain prose, without automatic timeline interpretation.

Access metadata follows JSON/project exports, backups and version history. Author exports retain hidden facts; these controls affect AI reference selection. Facts repeated in manuscript prose, summaries or other cards can remain visible through those sources. Structured canon shadows matching legacy cards even when hidden or archived, preventing that fallback from reintroducing its facts. Native chat/search also use sanitised reference copies.

**Copyedit** requests small, exact anchored corrections to selected text or the final paragraph. The app rejects ambiguous or invalid edits and shows a corrected preview; **Replace Passage** explicitly accepts it. Unchanged results explicitly say **No corrections proposed. The text is unchanged**, and replacement is disabled. When corrections are proposed, the review lists each original and corrected phrase with deletion/insertion markings and shows the corrected passage. Rewrite remains available for style, pacing and creative changes. See the [integration report](reviews/copyedit-context-integration-2026-10-25.md) for validation and platform limits.
