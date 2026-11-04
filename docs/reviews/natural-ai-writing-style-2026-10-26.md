# Natural writing defaults across AI tools

Implemented and checked on 26 October 2026.

All shared writing provider entry points now add the same compact natural-writing guidance: Chrome on-device APIs, managed cloud/OpenAI-compatible endpoints, server proxy, custom local/self-hosted models, and Tauri managed-local IPC. This covers Suggestions, Chat, Write, Rewrite, Continue, analysis and pipeline requests that use these providers. The independent Swift implementation applies matching guidance to OpenAI-compatible generation, managed local generation, Apple Foundation Models generation and its separate tool-assisted Chat route.

The default asks for the author's voice, viewpoint, tense and register; concrete details, precise verbs, natural dialogue and varied rhythm; direct, specific feedback; and fewer stock phrases, generic transitions and unnecessary summaries. Author instructions and the requested language, scope and output format take priority. Copyediting, grammar, translation, anchors and structured edit schemas retain their constraints. There is no output rewriter, deliberate-error insertion, automatic manuscript mutation, detector bypass, authorship claim, new network destination or model-training change. Output quality still depends on the model and source context; detector avoidance is not guaranteed or measured.

The shared request helper is immutable and idempotent so fallback/retry requests do not accumulate duplicate guidance. Chrome Summarizer receives the guidance as instructions rather than manuscript text; Writer and Rewriter receive it through their existing instruction paths. Chrome's context budget accounts for the added instruction length and retains the prior read-only Bible routing.

## Fresh validation

- `npm run ci`: passed lint, typecheck, Vite config check, 1,565 tests in 143 files, coverage, production build, bundle budgets and duplicate-asset check. Existing Tailwind sourcemap warnings did not fail the build.
- Native macOS source build passed with the installed macOS 26.5 SDK. Thirteen focused tests passed across natural writing guidance, Suggestions, Writing Actions and manuscript Chat. Tests cover original request preservation, structured-output instructions, approval/source guards and provider transport behavior; these are not literary-quality evaluations.
- An installed managed local model returned a 578-character Suggestions preview for a synthetic 36,042-character chapter with the new style policy. The source remained unchanged. The smoke also reproduced the expected error for the unbounded request. No author manuscript was used.
- `npm run cap:sync` succeeded, copying the new production web assets into Capacitor iOS.
- iOS simulator Debug compilation succeeded using the project App scheme with signing disabled. No simulator launch or physical-device inference check was performed.
- The macOS development app was rebuilt, ad-hoc signed and signature-verified at `~/Library/Caches/DraftHarbour/BuildProducts/DraftHarbour.app` (build `2026102602`). The previous bundles were preserved. No running app was stopped. `dist/DraftHarbour.app` links to the updated development app. This is not a notarized release.
- `git diff --check` passed.

## Version coverage

Web/PWA and the shared Tauri/Capacitor renderer received the provider changes and production build/test checks. Native macOS received independent Swift changes and build/tests plus managed-model execution. iOS received synced assets and a fresh simulator compilation. Windows/Linux installers and runtime/device checks were not run; their shared renderer receives the same defaults on the next desktop package build. Apple Foundation Models, Chrome's real browser AI APIs, and external providers were covered through source/transport checks rather than live model calls. No GUI screenshot was required for this instruction-only change.
