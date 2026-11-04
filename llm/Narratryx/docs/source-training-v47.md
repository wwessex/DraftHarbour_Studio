# Dialogue and editing reinforcement pilot

This pilot adds two exact Saki dialogue passages and four existing source-grounded anchored copyedit exercises to the 55-example curriculum. The copyedit exercises address a related editing skill. They provide limited direct supervision for stylistic rewriting. GB/US rights, exact source intervals, overlap, split and installed one-record batching checks passed. The existing 16 monitor rows were preserved.

The fresh adapter completed 61 updates at 2.5e-5 in 102.41 seconds. It processed 7,149 supervised tokens with a reported 8.39 GB MLX peak and no training warnings. All 49 new responses completed without errors or truncation. The comparison reused 98 pinned reference responses.

The automatic gate kept craft. Compared with v45, dialogue turn compliance improved from 1/6 to 2/6, still below craft's 3/6. The candidate repeated dialogue more often than craft and changed only one of four rewrite passages, versus four for craft. Legacy continuation word limits scored 2/7 against craft's 5/7. Clock-state checks improved on exposed prompts. The holdout remains reserved.

This was an Apple Silicon model experiment. App builds and device checks were outside scope.

[Automatic decision](../artifacts/source-training-v47/automatic-decision.json)
