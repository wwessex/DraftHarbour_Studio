# Balanced grounding/prose local trial — 29 October 2026

This report covers one authorised fresh-base experiment, independent of the application. It follows the [reviewed and frozen proposal](grounding-balanced-proposal-2026-10-29.md). Training completion, structural accuracy and literary improvement are separate conclusions; the candidate is not promoted.

## Data and execution

The frozen mixture contains 80 training records: 56 retained source-prose lessons and 24 structural grounding/editing lessons. Sixteen previously exposed Wray records remain a development monitor. Exact per-split source-span and GB/US rights checks pass against the [scoped ledger](../rights/grounding-balanced-v1.scoped.jsonl); this is not new book clearance or legal certification. No bulk corpus, new book acquisition, external upload or paid job was involved.

The mixture has 9,085 supervised tokens: 8,686 prose and 399 structural. Its 70/30 row ratio is approximately 95.6/4.4 by supervised tokens. That distinction matters when interpreting weak transfer; it does not by itself prove why a particular answer failed. The prose answers remain source-derived, with no generated literary teaching targets. Structural labels/time states are deterministic or AI-reviewed annotations, not human gold. The earlier review retained 23 evidence annotations and clarified one quotation without changing source prose.

Training used the cached Qwen3.5-4B MLX 8-bit base, fresh LoRA rank 8/alpha 16, dropout 0, learning rate 5e-6, seed 42, batch 1/accumulation 4, one epoch, 20 updates, context 2,048 and no packing. Explicit pretokenised labels mask prompts and supervise answers/EOS. Token preflight preserves every answer without truncation; maximum input length is 1,882 tokens. The installed loader recognises custom labels before loading the model.

The development machine reports Apple M5 and 16 GiB RAM. Installed environment metadata records Python 3.13.14, Unsloth 2026.10.8, MLX 0.32.4, mlx-lm 0.32.2 and mlx-vlm 0.7.9. The CLI log selects its Transformers 5.3.0 compatibility tier; installed default metadata reports 5.5.0. These are different observations, not an independently captured worker import-version assertion.

The [new execution wrapper](../curation/grounding-training-v5/run.py) freezes input, engine and execution-source hashes and refuses to overwrite runs. Both 64-case baselines must complete before training. Conditions run serially with one user message, no prior assistant messages, zero reported cached prompt tokens, temperature 0, seed 42 and at most 384 output tokens. Errors or truncation stop the experiment. Training stops on warning/error, nonfinite metrics, reported MLX peak above 10 GB, more than 20 updates or the 20-minute external deadline. The supervisor also checks its subprocess tree's resident memory against a 10 GB cap. The older eight-update runner and historical artifacts are untouched.

## Evaluation boundaries

Each condition receives the same 64 cases: 24 new clock-state tuples, 16 new prose-transfer tasks in four fictional situations, and 24 **exposed retention regressions** from the prior trial. The 24 clock tests check same-day arithmetic and arrived/unknown/absent distinctions. The prose cases test exact selection repair, grounded analysis, chronology-preserving rewrite and continuation. Clock tuples are disjoint from training, but the task family is familiar. Retention tests are not a fresh independent benchmark.

The frozen strict clock scorer accepts JSON key order and whitespace differences, but rejects duplicate or extra keys, wrong types, fenced prose and wrong values. Exact edit checks ignore only surrounding response whitespace. Word counts use whitespace splitting; dialogue quote-block counts are formatting proxies. None measures literary quality. Editing has no minimum length, and a canonical continuation is not a gold answer.

Training completed all **20 updates** with no warnings or errors. The worker reported **210.1 seconds**; the supervised whole training phase, including setup/save, took **229.49 seconds**. Reported peak MLX memory was **7.167 GB**. The final progress record carries a development loss of **1.147302**; this is the exposed Wray monitor, not independent literary evaluation. The CLI emits evaluation at updates 10 and 20, both 1.1473 to four decimals. Differing worker/progress/wall timers should not be conflated.

All **192 responses** completed: 64 for each condition, with no errors or output truncation, one-message fresh contexts, zero reported cached tokens and no context overflow. Base/current/candidate phases took 194.88/189.99/213.60 seconds respectively.

| Mechanical diagnostic | Base | Current craft | Candidate |
|---|---:|---:|---:|
| New clock JSON, exact (24) | 6/24 | 6/24 | 6/24 |
| New selected edit, exact (4) | 4/4 | 4/4 | 4/4 |
| New analysis ≤70 words (4) | 4/4 | 3/4 | 3/4 |
| New rewrite ≤90 words (4) | 4/4 | 4/4 | 4/4 |
| New continuation 60–90 words (4) | 2/4 | 3/4 | 2/4 |
| Exposed minimal repair, exact (4) | 4/4 | 4/4 | 4/4 |
| Exposed dialogue ≤100 words (4) | 3/4 | 1/4 | 1/4 |
| Exposed dialogue 4–6 quote blocks (4) | 4/4 | 4/4 | 4/4 |
| Exposed pacing ≤85 words (4) | 4/4 | 4/4 | 4/4 |
| Exposed continuation 60–90 words (4) | 3/4 | 4/4 | 4/4 |

Exposed chronology-rewrite and grounded-analysis word limits pass 4/4 in every condition. Thirty-eight of the 64 answers are identical across all three conditions; this includes many short structural/repair answers, so it is not a general similarity or quality measure. There is **no clock-state gain**, no exact-edit gain and mixed length compliance. Full per-case mechanical data is in [scores.json](../artifacts/grounding-training-v5/scores.json).

## Informed AI observations

This is an informed, named-condition Codex inspection, with prior exposure to the tasks and baselines. It is not independent, blinded or human assessment.

All three conditions incorrectly call the expected visitor late in all four new prose analyses, although the supplied current time precedes the arrival time. The candidate explicitly calls Ivo late at 10:35 despite an 11:20 expectation, and repeats the error for Anton, Ewan and Nora. Its planetarium continuation says Mei knows Anton will be late and treats the unexplained lens cap as a deliberate statement; the puppet-workshop continuation also asserts future lateness as known. New imaginative action/detail is allowed in continuation, but unsupported certainty about these unresolved facts is a defect under the actual task.

The exposed saffron and kiln analyses are also identical across conditions: saffron attributes the label to Lin while incorrectly calling her late, and kiln invents that Niko was the last person present. These unsupported premises survive the new training. The new planetarium rewrite also drops the exact 15:05 action time, and the new bookbinding rewrite drops 11:05 despite being asked to preserve times. Passing a word limit does not resolve these failures.

No reliable literary-quality upgrade is established. These results do not justify promoting the candidate or promising Muse-equivalent performance. Repeated short runs are not a substitute for reviewed task supervision and independent quality assessment.

## Review and preservation

The [blinded full packet](../artifacts/grounding-training-v5/BLIND-REVIEW.md) contains the 40 prose cases, with A/B/C randomised independently per case. The [eight-case starting packet](../artifacts/grounding-training-v5/QUICK-REVIEW.md) uses the same labels. Eighty blank ballots support two reviewers; no human ratings have been recorded. The condition key is stored separately with mode 0600. This report names conditions, so prospective reviewers should use the packet before reading these observations or the private key.

The selected craft manifest, cached base and all 16 protected prior adapter/configuration files verify unchanged. The legacy development service was initially stopped on port 8890 and remains stopped; no service was started merely for this experiment. Application defaults and model selection remain unchanged. Data preparation and training are not added to application startup, installation or manuscript storage.

The [final evidence verification](../artifacts/grounding-training-v5/final-verification.json) passed: 192 matched responses, 20 completed updates, 80 training/16 monitor records, saved candidate hash, enforced resource limits, frozen inputs/base/protected artifacts unchanged, preserved initial service state and 80 blank human ballots. **166 CPU foundation tests passed in 55.890 seconds**, including six new resource-boundary and strict JSON scoring regressions. All new execution/review/verification Python modules compile. Source hashes in the frozen execution protocol bind the actual run scripts and predeclared scorer; postprocessing/review scripts were added during execution and are not represented as preregistered literary judgement.

Recheck the completed evidence without inference or training, from `llm/Narratryx`:

```bash
.venv-foundation/bin/python -c "import runpy; m=runpy.run_path('curation/grounding-training-v5/verify.py'); print(m['verify']())"
```

The next useful step is the blinded prose review, followed by a narrowly designed curriculum revision addressing the observed temporal/attribution failures and measured retention. Keep prose craft supervision substantial, inspect actual loss-token balance, and freeze genuinely new diagnostic situations before any further run. Do not automatically lengthen training or promote on JSON/length scores alone.

All work is confined to Narratryx. Web/PWA, Windows/Linux Tauri, Capacitor iOS and independent native macOS received no source, default, configuration or generated-asset changes. No application builds or device/runtime acceptance tests were needed or run for this isolated research change. Successful training on this Mac does not establish Windows inference, installer readiness or performance on ordinary users' devices.
