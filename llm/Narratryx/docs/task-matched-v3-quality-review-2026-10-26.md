# Task-matched v3: eight-case AI quality review — 26 October 2026

**The candidate has not demonstrated a reliable literary-quality upgrade. Keep the current craft model selected.** This completes an informed AI diagnostic of the eight-case packet; it does not complete the independent human-review gate.

## Method and limitations

One Codex AI reviewer assessed the eight-case packet's 24 responses with the A/B/C key withheld during judgement. The reviewer had already seen model scores and some labelled outputs in the development conversation and could recognise some text. Therefore this is **not independent, human or fully blind**. The subset is purposive, with one case per story situation, not a random sample or a population-level fiction-quality benchmark.

The ordinal task-fit scale runs from1 (major correction needed or explicit constraint/chronology failure) through3 (useful elements but substantive revision needed) to5 (satisfies the observed task). Relative preferences can select a weak answer and are not a release endorsement. New events, dialogue revelations and invented details allowed by creative prompts were distinguished from hard contradictions and prohibited invented prior history. Names in administrative notes were not demanded where the model prompt left a narrator unnamed.

Label-level judgements, evidence, response hashes and word counts were fixed before decoding the private condition key. A word-count check caught an initial judgement that incorrectly implied an aquarium answer met its100-word cap: it had103 words. The corrected judgement and lower rating were frozen before decoding; both draft versions and locks remain preserved. No model response, test prompt, mechanical score or human ballot was changed.

## Findings

| Descriptive outcome | Cases |
|---|---:|
| Strict AI preference for base | 2 |
| Strict AI preference for current craft | 1 |
| Strict AI preference for candidate | 1 |
| Identical three-way answers/ties | 3 |
| Uncertain two-way preference/tie | 1 |

These eight outcomes are not statistically meaningful win rates. No aggregate prose-quality score, independent preference claim or Muse-equivalence claim is made. The decoded case-to-condition mapping stays private to avoid further unblinding future reviewers.

- **Directed writing:** the seed-bank responses are byte-identical across all three conditions. They offer a deadline and choice, but the key-related question is awkward given the key's stated location. New dialogue and deadlines are allowed by this creative task; they are not automatically labelled factual errors.
- **Exact editing:** all three bakery repairs are identical and correctly remove only the duplicate. This is a successful narrow repair, not evidence of stronger fiction.
- **Pacing:** all three map-room rewrites are identical. They change the donor's future arrival at noon into an arrival that has happened before the clock strikes eleven. This directly violates the requested chronology. Short sentences and length compliance do not repair that semantic failure.
- **Grounded analysis:** all three costume-room responses assign the alteration to Ada without marking that as inference and move the ledger into Leon's hands. Two also describe the explicitly stated lack of authorisation as inferred. The relatively preferred answer still needs major correction; none is a satisfactory grounded analysis.
- **Continuation:** one tram continuation invents memorised archives and an unexplained earlier constraint, despite a prohibition on presenting unknown history as fact. The alternatives have useful scene elements but lean on generic trembling, fogging breath and nervous looks. A tram's arrival is not automatically equated with its departure; that ambiguity was not counted as a definite ten-minute timing error.
- **Dialogue:** the observatory answers tend toward overt bickering rather than distinctive subtext. Spoken revelations and changing weather can be valid new developments; staging, motivation and prior-history implications require judgement. In the aquarium case all three answers exceed100 words (125,107,103); the shortest still fails. New administrative procedures and concern for future fish safety are not automatically contradictions, but the motivation and signature/budget logic remain weak.
- **Laundry writing:** two responses have plausible practical choices but no decisive literary preference emerged. Another has unclear staging and an ambiguous reference to an unseen name. The ambiguity was not converted into a proven claim that an unopened envelope had been read. Familiar ghosts, shadows, flickering lamps and emotional paralysis remain style weaknesses.

## Decision and next data work

The [training experiment](task-matched-v3-training-2026-10-26.md) showed modest dialogue-format gains. This informed review supplies no reliable evidence that those gains translate into overall literary usefulness. The fifty training spans were reused from earlier pilots; reframing them is not a broader independent corpus. More epochs on the same material are not justified by this review.

Before a further pilot, prioritise independently sourced scenes with clear goals, varied character voices and complete exchanges; genuine revisions with explicitly classified changes to meaning; and source-grounded analysis/extractive evidence tasks that separate quotation, inference and unknowns. Preserve the user's exclusion of generated literary teaching answers. Structured source-derived labels may aid precision, but must not be misrepresented as expert-authored literary explanations. The Dickens structural alternative ending is not a minimal-copyedit target; the Hopkins lead is still a sourcing candidate rather than cleared training text.

The exposed v3 outputs and their diagnostic corrections are **evaluation material only**. Do not feed them back as teaching answers or select a new checkpoint on these cases. Freeze fresh, separate final-evaluation situations for a future candidate. Independent human review still requires actual reviewers and concrete evidence; no outreach, paid review or invented ballot has occurred. Future human reviewers should receive only the original packet and blank ballot, without this AI judgement report, scores or condition key until their ballots are complete.

## Artifacts and checks

Local evidence: `artifacts/task-matched-quality-review-2026-10-26/` contains initial and corrected immutable label-level reviews, SHA-256 locks, a separate private decoded mapping and verification output. [Decoder](../curation/task-matched-quality-review-v1/decode.py) checks the judgement lock, packet, exact response bytes/counts, model pin and unchanged human ballots before decoding. It records **zero human ratings** and **no promotion**.

The original eight-case packet, model responses, protocol, all frozen protocol inputs, mechanical scores and48 blank human ballots were checked unchanged. No training or inference job ran for this review. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS application source, model settings, packages and manuscripts were not changed by this model-review work. No new application build, device test or rerun of the previously passing120-test foundation suite is claimed; this step used direct artifact-integrity checks and Python syntax validation.
