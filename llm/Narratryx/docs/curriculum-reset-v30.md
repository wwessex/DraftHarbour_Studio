# Narratryx curriculum reset

The last three pilots used the same 34 literary targets. V27 halved the learning rate and recovered several mechanical scores. V29 changed four prompt briefs and left all 3,706 supervised answer tokens intact. Neither passed the gate. All three ran on the same 44 exposed regression cases plus five fit cases. Another small recipe adjustment would give little evidence about wider writing ability.

The 34 lessons cover nine authors, with 12 from Amelia Opie. There are 12 editing, 12 fiction, seven dialogue, two pacing and one storytelling records under the current task labels. No record is labelled narrative analysis. These counts describe coverage and do not measure the quality of individual lessons. Expand the variety of examples before spending another run on optimizer tuning.

1. Baseline craft on the new 12-case development screen. It covers continuation, dialogue, rewrite, scene writing, pacing and analysis on new scenarios. The prompts and criteria are frozen before any inference. Use this screen to debug the evaluation and commission a larger, separate holdout before making a selection decision.
2. Build a balanced source-backed pilot. Start with roughly 120 distinct examples as a planning target, with meaningful coverage across the six skills and no dominant author. Prioritize scenes where a feasible action changes the situation, dialogue with an actual turn in the negotiation, revisions with observable craft choices, and authentic critical passages whose claims are supported by the quoted work. Require exact source and rights records and preserve held-out authors and works. Leave a skill short if suitable sources are unavailable.
3. Keep the base, LoRA settings and seed fixed for the first curriculum comparison. Record supervised tokens by skill and cap repeated source exposure. If training volume increases, describe the result as the effect of the new curriculum and budget together. Use a matched-token control if isolating the data mix matters.
4. Keep the old cases as a regression screen. Measure format and factual constraints deterministically. For prose and analysis, have an automated evaluator score task-specific criteria on anonymized pairs, swapping their order and recording evidence for each decision. Count inconsistent judgments as inconclusive. Report results by skill, with model choice contingent on a fresh holdout and with human review optional.
5. Stop this line of experiments if the expanded curriculum fails on the fresh cases. Then investigate whether the base model, data constraints or application context is limiting the target behavior before committing to another training sweep.

The first 12 cases are a development screen, with two scenarios per skill. They are too small for a release decision and must remain outside training. Prompt text and evaluation criteria were written for this screen. Training targets still require eligible original source material.

LIMA reported gains from improving prompt diversity and response quality in its own alignment experiments. Tülu 3 used skill-specific mixtures and separate development and unseen evaluations. These studies inform the design. They do not establish an effective dataset size or recipe for Narratryx.

[LIMA paper](https://arxiv.org/abs/2305.11206) · [Tülu 3 paper](https://arxiv.org/abs/2411.15124)
