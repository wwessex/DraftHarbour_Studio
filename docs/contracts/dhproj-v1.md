# Portable project contract: dhproj v1

Both the web importer and native macOS codec accept UTF-8 JSON or a ZIP containing `project.json`. Web exports retain the existing ZIP container, including `manifest.json`; native exports remain JSON. The shared fixtures are `fixtures/dhproj-v1.json` and its ZIP counterpart `fixtures/dhproj-v1.zip.base64`.

The envelope contains `manifest` (`format: "dhproj"`, `version: 1`), `project`, `projectType` and ordered `sections`. Section content and snapshot documents use Markdown. Legacy rich-text JSON is converted on web import. Preserve section metadata, scenes, parts, tags, goals, POV and status. Optional collections include `snapshots`, `commentThreads`, `characters`, `worldEntries` and `storyBlueprint`. Research stored in character/world descriptions and notes travels with those entries; externally linked resources are not embedded.

Importing into the web library creates a separate project. Project, section, scene, character, world, snapshot and comment IDs are regenerated, and known references are remapped. Duplicate section IDs and foreign chapter references are rejected before insertion. Character relationships, world character links and voice-profile references follow the new identities.

Native-only `exportHistory`, `aiChatThreads`, `aiRevisionLog`, `collaboration` and `deletedSections` fields survive web round trips as passive portable data. Known ID-shaped references are remapped. This does not promise lossless preservation of arbitrary unknown extensions. Import does not activate provider credentials or imported sync authentication. Existing installation sync settings are retained. Web export removes sync authentication from exported preferences and legacy integration metadata.

Complete-project JSON backups use the existing version-3 envelope with additive optional character/world/blueprint fields. Backups include project-owned manuscript, snapshots, comments and story-bible notes. Installation-wide preferences, global story-bible entries, credentials and external media are not complete-project backup content. `.dhproj` has additional optional settings/progress/integration fields for compatibility.

The web database upgrade to v5 only adds `backups` and `trash` tables. Existing manuscript IDs and records remain in place. Automatic project backups retain ten changed versions; manual backups remain until application data is cleared. SHA-256 detects accidental backup corruption before restoration, but is not an authenticity signature. Restoring backups or trash creates a separate project, keeping the original untouched.

Auxiliary data currently remains in localStorage. Imports stage those writes inside the IndexedDB operation and roll them back on reported failures. There is no crash-atomic transaction across the two storage systems or protection against every concurrent-window race. A future unified project repository should address that boundary with an explicit migration.

Web import limits input files to 100 MiB. The native ZIP reader limits extracted `project.json` to 100 MiB. These bounds do not constitute a general ZIP security certification. Shared fixtures exercise both containers in TypeScript and Swift tests; native tests require an Xcode installation with XCTest.

Native `deletedSections` is an optional additive collection containing archived section metadata/content, snapshots and comments. Older files default to an empty collection. Web imports retain it as passive project data and remap known project references; native recovery creates fresh section/scene/comment/snapshot identities.
