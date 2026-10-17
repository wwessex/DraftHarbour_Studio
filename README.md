# DraftHarbour Studio (PWA) — Offline/Online Novel Word Processor

A lightweight, installable web app for writing novels:
- Markdown editor powered by CodeMirror 6, with formatting controls and live previews
- Chapter sidebar (create/rename/delete), **drag to reorder**
- **Chapter-isolated editing** (each chapter is a separate document)
- Autosave to **IndexedDB**
- Optional online sync (simple JSON REST endpoint)
- Export (project-type aware):
  - Novel/manuscript projects: **DOCX**, **PDF**, **RTF**, text-only **EPUB**
  - Screenplay projects: **screenplay PDF**, **.fountain**

## Manuscript protection and organisation

Projects → **Backups, recovery & trash** provides verified project backups, saved-versus-recovered draft comparison, and recovery of deleted chapters/projects as separate copies. Automatic backups keep ten changed versions; manual copies can be named. Download an external copy to protect against device or browser-storage loss.

Snapshots support aligned comparisons and a safety version before restoring. Chapters can be split at the cursor or merged with the next chapter; scene plans can move between chapters. Draft/Plan/Review sidebar controls, saved manuscript searches and story-bible mention links support revision without changing prose automatically.

Portable `.dhproj` files support native JSON and web ZIP containers; see the [format contract](docs/contracts/dhproj-v1.md) for contents and compatibility limits.

## Optional collaboration and cloud integrations

Collaboration and cross-device sync depend on a configured supported backend/provider and differ by runtime. Static hosting alone does not provide real-time collaboration or continuous cloud backup. Local chapter snapshots and threaded comments work on the device. AI/provider features require explicit configuration; drafting remains available offline.

## Run

The web app uses React, TypeScript and Vite. Install dependencies and start the development server:

```bash
npm ci
npm run dev
```

Use the local URL printed by Vite. To build and preview the production app:

```bash
npm run build
npm run preview
```

Deploy the generated `dist/` directory to a static host. Optional AI and integration endpoints require a separately configured backend; static hosting alone does not provide them.

## Install (PWA)
In Chrome/Edge/Safari (iOS): use "Add to Home Screen" / "Install App".


## Native macOS App

Changes are maintained across web/PWA, Tauri Windows/Linux, Capacitor iOS and the independent native macOS app. See the [platform parity report](docs/reviews/platform-parity-2026-10-17.md) for verification and remaining device/toolchain limits.

The macOS desktop app is the SwiftUI/AppKit document app in `macos/`. It opens and saves `.dhproj` v1 files directly, includes native import/export, AI workflow configuration, recovery metadata, Generic REST sync, Dropbox/Google Drive sync, and the Scrivener package bridge.

```bash
swift test --package-path macos
./script/build_and_run.sh
```

Build-only and packaging checks:

```bash
./script/build_and_run.sh --no-launch
./script/build_and_run.sh --verify
./script/package_macos.sh
```

`./script/package_macos.sh` creates `dist/release/DraftHarbour.dmg`, verifies the DMG, writes `checksums.txt`, and generates `macos-update-manifest.json`. Local dry-runs are ad-hoc signed and may be rejected by Gatekeeper. Release builds should run `./script/package_macos.sh --distribution --channel stable` with `APPLE_SIGNING_IDENTITY`, `APPLE_NOTARY_KEYCHAIN_PROFILE`, and `RELEASE_SIGNING_KEY` configured so the DMG is Developer ID signed, notarized, stapled, and accompanied by signed checksum/update metadata.

Credential-backed provider smoke checks can be run with `npm run smoke:providers`. Add `-- --require-configured` in secure release environments to fail when no provider credentials are configured.

Dropbox and Google Drive sync use native PKCE OAuth; enter a registered Dropbox app key and Google desktop OAuth client ID in the native Integrations panel.

## Non-Mac Desktop App (Tauri)

The Tauri runtime under `desktop/` is retained for Windows and Linux desktop builds. macOS desktop distribution is handled by the native Swift app above.

### Prerequisites
- Rust toolchain (`rustup`, `cargo`)
- Platform build dependencies for Tauri/WebKit2 (Linux) or Visual Studio Build Tools (Windows)

### Install dependencies
```bash
npm install
npm --prefix desktop install
```

### Development (desktop shell + Vite renderer)
```bash
npm run desktop:dev
```

This runs the Vite dev server (on `http://localhost:1420`) and launches the native shell.

### Production build
```bash
npm run desktop:build
```

Target-specific examples:
```bash
npm run desktop:build:win
npm run desktop:build:linux
```

### Desktop runtime behaviors
- Single-instance lock: second launches focus the existing window.
- Window-state restoration: previous bounds are persisted and restored automatically.
- Close-to-background behavior: closing the window hides it unless unsaved edits exist.
- Unsaved-edit quit confirmation: app-level confirmation is shown before quitting with dirty content.
- File/deep-link routing:
  - Opening `.dhproj` files routes payloads into the running app.
  - `draftharbour://...` deep links are delivered to the web layer.

### Release signing configuration
The non-Mac packaging config is in `desktop/src-tauri/tauri.conf.json` and is environment-driven:

- Windows code-signing:
  - `WINDOWS_CERT_THUMBPRINT`

Set these in your CI provider secrets before release jobs.

Suggested CI matrix:
- macOS: native Swift package via `./script/package_macos.sh --distribution --channel "$RELEASE_CHANNEL"`
- Windows: `x86_64-pc-windows-msvc`
- Linux: `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu` (optional)

## iOS Native App (Capacitor)

This project now includes Capacitor configuration so the web app can run as a native iOS app.

### Prerequisites
- macOS with Xcode installed
- CocoaPods (`sudo gem install cocoapods` if needed)

### Build and sync web assets to native projects
```bash
npm run build:native
```

### Open in Xcode
```bash
npm run cap:open:ios
```

From Xcode, select a simulator/device and run the app.

### Daily workflow
After web code changes, re-run:
```bash
npm run build:native
```

### Capacitor health check
If native tooling seems out of sync, run:
```bash
npm run cap:doctor
```

### About iOS icon/splash image files in git
To keep PR tooling compatible in environments that reject binary files, the repo tracks only the asset catalog metadata (`Contents.json`) for iOS app icons/splash.

After opening in Xcode, add your final icon/splash images in:
- `ios/App/App/Assets.xcassets/AppIcon.appiconset/`
- `ios/App/App/Assets.xcassets/Splash.imageset/`

### If GitHub mobile shows “Error creating pull request (400)”
That error is usually a GitHub client/API issue (not a Capacitor project issue). Workarounds:
- Refresh and retry after pushing the branch again.
- Create the PR from github.com in a desktop/mobile browser instead of the GitHub mobile app.
- Use GitHub CLI: `gh pr create --fill`.

## Data
Saved locally in your browser (IndexedDB). Use **Settings → Export Backup** for a JSON backup.

## Security Appendix

### Storage boundaries by runtime

- **Web/PWA runtime:**
  - Project content is stored in IndexedDB (`DraftHarbourDB`).
  - User settings and safe integration metadata are stored in `localStorage`.
  - Sensitive provider/session credentials are best-effort and browser-bound (no OS vault APIs are available in standard web runtimes).
- **Desktop (Tauri) runtime:**
  - Project content remains in IndexedDB for renderer compatibility.
  - Sensitive credentials (AI session token, sync authorization header) are moved to the OS credential vault through native keyring APIs (Keychain/Credential Manager/libsecret).
  - The renderer persists only non-sensitive config metadata.

### Config layering and policy precedence

Runtime configuration resolves with this precedence:

1. **App defaults**
2. **User settings**
3. **Managed policy overrides** (highest precedence, read-only)

Managed policy can enforce controls such as:

- disable telemetry,
- disable AI providers,
- force local-only mode (clears remote sync URL/auth and blocks cloud AI paths),
- provider-specific AI disable lists.

### Backup/export inclusion semantics

- `.dhproj` export now tracks explicit export options in the manifest:
  - `includeSnapshots`
  - `includeIntegrationArtifacts`
- Integration artifacts are excluded by default from project-file export and require explicit inclusion.
- A secure wipe path exists for clearing stored integration artifacts before export or deprovisioning.

### Threat assumptions

- This app primarily protects against **accidental disclosure** (e.g., exported files, diagnostics, shared devices).
- It does **not** claim protection against a fully compromised OS/user session.
- On desktop, OS vault integration improves credential-at-rest posture compared with browser storage, but does not replace endpoint hardening.


## Diagnostics & Privacy Redaction
- Use **About → Create Diagnostics Report** to export a local JSON diagnostics bundle.
- Reports include runtime metadata (app version, platform, feature flags, storage estimate), recent structured error events, and a high-level app-state summary.
- Reports intentionally exclude chapter/editor content.
- Sensitive values (API keys, auth headers, tokens, secrets, password-like fields) are automatically replaced with `[REDACTED]` before export.
- Diagnostics are stored locally unless you explicitly configure a remote crash-reporting endpoint in app code.

## Optional Online Sync
Settings → Online Sync:
- Set a `Sync URL` pointing to a simple REST service:
  - `GET  {syncUrl}/novels/{novelId}`  → returns the novel JSON
  - `PUT  {syncUrl}/novels/{novelId}`  with body novel JSON → stores it
- Add an `Authorization` header value (optional).

If no server is configured, the app works fully offline.

## AI Setup (Server Proxy + Local Broker)

The AI features can run through either:
- `api/` (PHP server proxy for production-style deployments), or
- the local dev broker in `src/server/integrationBroker.ts`.

### Required security config checklist (production/staging)

- Set `APP_ENV` to a non-dev value (for example: `production` or `staging`).
- Set `APP_ALLOWED_ORIGINS` to explicit origin(s), comma-separated (for example: `https://app.example.com`).
- Confirm `allow_byok` is disabled by default in non-dev environments (enable only when intentionally required).
- Review PHP logs on startup for `[api-security]` warnings and resolve any insecure configuration warnings before go-live.

### 1) Configure `api/_config.php` provider keys

Edit `api/_config.php` and set the provider keys you plan to use:

- `groq.api_key`
- `openrouter.api_key`
- `gemini.api_key`

Each provider also has an `enabled` flag. If `enabled` is `false`, requests for that provider are rejected.

### 2) Understand `allow_byok`

`allow_byok` controls whether the client can submit `userApiKey` in the `/api/chat` request body:

- `true`: request-level key override is allowed (Bring Your Own Key)
- `false`: only server-side keys from `api/_config.php` are accepted

For shared/public deployments, `false` is generally safer.

### 3) Deploy `api/` behind PHP for `/api/chat`

`/api/chat` is a server endpoint, not a static file route. To use the PHP proxy path, deploy the `api/` directory behind a PHP-enabled web server (Apache, Nginx+PHP-FPM, etc.) so requests to `/api/chat` are executed server-side.

If you only serve static frontend files, `/api/chat` will not work.

### 4) Local dev broker env vars (`src/server/integrationBroker.ts`)

For local/server runtime (Node), set these environment variables as needed:

- `BROKER_GROQ_API_KEY`
- `BROKER_OPENROUTER_API_KEY`
- `BROKER_GEMINI_API_KEY`
- `BROKER_OPENAI_API_KEY`

`BROKER_OPENAI_API_KEY` is used by `/api/ai/generate` in the broker implementation.

See `.env.example` for a complete list of frontend and broker/server environment variables.

## AI runtime modes

The app supports two backend runtime paths for AI, depending on how you host and configure it.

### 1) Dev mode: Vite middleware + Node broker

In local dev, Vite can hand off AI requests to the broker handler in `src/server/integrationBroker.ts`:

- `POST /api/ai/generate` → handled by `generateAI(...)` (OpenAI-compatible path using `BROKER_OPENAI_API_KEY` / `OPENAI_API_KEY`)
- `POST /api/chat` → handled by `generateServerProxy(...)` (Groq / OpenRouter / Gemini proxy path)

The route dispatch happens in `handleBrokerRequest(...)`, which matches those exact paths.

### 2) Hosted mode: PHP API

In hosted deployments, the frontend calls into `api/index.php`, which routes `POST /api/chat` to `api/_chatHandler.php`.

- `api/index.php` performs CORS + rate-limit checks, then routes `/api/chat`
- `api/_chatHandler.php` validates payload fields (`provider`, `prompt`, `model`), enforces limits, resolves API keys (server key or BYOK), and forwards to the selected provider

## Frontend → backend wiring (`VITE_BROKER_BASE_URL`)

`src/lib/featureFlags.ts` exposes:

```ts
export function getBrokerBaseUrl(): string {
  return import.meta.env.VITE_BROKER_BASE_URL || '';
}
```

Frontend providers build API URLs from this value:

- Cloud/OpenAI path: `${getBrokerBaseUrl()}/api/ai/generate`
- Server-proxy path: `${getBrokerBaseUrl()}/api/chat`

Example `.env` values:

```bash
# Local Vite+broker runtime
VITE_BROKER_BASE_URL=http://localhost:5173

# Hosted PHP API on same origin (optional; empty uses relative URLs)
VITE_BROKER_BASE_URL=

# Hosted API on another origin
VITE_BROKER_BASE_URL=https://your-domain.example
```

## What happens when no broker URL is configured

Because `getBrokerBaseUrl()` falls back to `''`, requests become relative paths:

- `/api/ai/generate`
- `/api/chat`

So behavior depends on your host:

- If your server exposes those endpoints on the same origin, calls still work.
- If not, requests return 404/network errors.
- In managed-cloud mode, the OpenAI provider explicitly throws a user-facing error when no broker URL is available, prompting users to configure a custom provider or supported on-device option.

## Verify endpoint readiness before enabling AI features

Run these checks first (replace base URL as needed):

```bash
# 1) Basic route check (expect JSON 404 on GET from PHP router, which proves routing is alive)
curl -i https://your-domain.example/api/chat

# 2) CORS/preflight check for browser POSTs
curl -i -X OPTIONS https://your-domain.example/api/chat

# 3) Functional POST check (expect 200 or a structured JSON error, not HTML)
curl -i -X POST https://your-domain.example/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"provider":"groq","model":"llama-3.3-70b-versatile","prompt":"ping"}'
```

For dev broker mode, run the same checks against your local Vite URL (for example `http://localhost:5173/api/chat` and `http://localhost:5173/api/ai/generate`). Do this before turning on AI in user-facing environments so failures surface early.

If AI settings report **"Proxy endpoint not found (404)"**, you typically need one manual step:

- Set `VITE_BROKER_BASE_URL` to the host that actually serves your AI routes (`/api/chat`, and optionally `/api/ai/generate`) and redeploy/restart the frontend.
- Or, if using the PHP proxy path, deploy the `api/` folder behind PHP so `/api/chat` is routed through `api/index.php` instead of static hosting.

## External Integrations

Integration availability is staged and may depend on your project type.

| Integration | Status | Scope |
|---|---|---|
| Scrivener | Planned | Project import/export bridge for manuscript projects |
| Dropbox | Beta | Cloud file sync for backups and shared drafts |
| Google Docs | Available | Document handoff/export for collaborative review workflows |

## Configuration and Security Expectations

### Stored locally (browser)
- Draft content, chapter metadata, and editor state in **IndexedDB**.
- Local app settings (for example export defaults and integration preferences) in browser storage.
- Any local fallback for integration toggles/config (including `IntegrationConfig`) in `localStorage`.

### Server-managed (when configured)
- Synced novel/project payloads sent to your configured sync endpoint.
- Authentication/authorization handling for external providers (tokens should be issued, refreshed, and revoked server-side).
- Access controls, audit logging, and retention policies for cloud-stored content.

### Security guidance
- Treat browser storage as user-device scoped, not a hardened secret vault.
- Do not persist long-lived provider secrets in client storage.
- Prefer short-lived access tokens and server-mediated OAuth flows.
- Always use HTTPS for sync and integration endpoints.

## Migration Note (`IntegrationConfig`)

If `IntegrationConfig` schema fields are added/renamed, existing users with older `localStorage` entries should degrade gracefully:
- Include a schema `version` in stored config.
- On load, merge persisted values over safe defaults and ignore unknown fields.
- If parsing/validation fails, fall back to defaults and keep the app usable offline.
- Apply one-way migration functions (`v1 -> v2 -> ...`) instead of hard-failing older payloads.

## Notes
- Frontend dependencies are bundled by Vite. The production Service Worker caches app assets; Google Fonts are cached separately after they are fetched.
- If you update files and caching seems stuck, open once with `?nosw=1` to unregister the Service Worker.
