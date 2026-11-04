# Published revision and dialogue pilot

The 58-example curriculum returns to the v45 mixture and uses two genuine author revision targets in place of relying on extra anchored copyedits. The longer James comparison teaches diction, rhythm and interiority. Dickens's alternative ending teaches a change in scene structure. Two additional exact Saki exchanges model subtext, deflection and comic timing. GB/US validation, source overlap, split and installed batching checks passed.

The fresh adapter completed 58 updates at 2.5e-5 in 111 seconds, processing 8,863 supervised tokens. The reported MLX peak was 9.71 GB. Training recorded zero warnings or errors.

The legacy candidate screen stopped at case 13 of 49 when the music-score dialogue hit the 384-token cap. A separate six-case development screen compared fresh rewrite and dialogue responses with craft. Craft completed all six. The candidate changed one of three rewrites, returning two passages unchanged, and repeated the same two exchanges until the first dialogue hit the output cap. Its remaining two dialogue cases were unattempted. Craft changed all three rewrites but also showed fidelity and dialogue problems. The screen's changed-text check measures whether revision occurred. It does not score style quality.

The automatic decision keeps craft on the two truncated dialogues. The 24-case holdout remains reserved. The experiment changed the source mixture and supervised token budget together. The most useful follow-up is to test a different training design or base for the two skills separately before adding more examples to this same mixture.

This was a standalone Apple Silicon model experiment. Platform builds and device tests were outside scope.

[Automatic decision](../artifacts/source-training-v48/automatic-decision.json)
