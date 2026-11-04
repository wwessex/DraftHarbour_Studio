# Originality baseline for craft

Craft generated three drafts for each of three development briefs at temperature 0.7. The first run used the normal local engine, which resets the sampling seed to 42 for each request. All nine within-brief pairs were identical. The second run varied seeds 42, 43 and 44 through the private evaluation backend. Every within-brief pair differed, and the greatest shared four-word phrase Jaccard score was 0.00635.

The overlap check searched 22 hash-verified source files from the current rights ledger. Across both runs, it found zero contiguous matches of 12 or more normalized words. The check measures exact overlap with this local collection. It does not measure paraphrase or compare against the base model's pretraining corpus.

The varied drafts still had writing problems. The kiln drafts tried different approaches, including checking a log and sketching the interior, but introduced unestablished readings or actions around the hot kiln. Two of three bus exchanges fit the turn limit, yet shifted who wanted the seat. All three bakery drafts exceeded 150 words and largely reused the same dilemma despite different wording. The lexical results therefore provide a separate baseline from plot variation and instruction adherence.

All 18 generations completed. The evaluation uses three exposed development briefs. Future model comparisons should use the same seed set for each model on separate holdout prompts, score factual constraints and distinct scene developments alongside overlap, and keep the outputs out of training. The varied-seed experiment ran on Apple Silicon in a private process. Platform build and runtime checks were outside its scope.

[Fixed-seed overlap](../artifacts/originality-v35/overlap.json) · [Varied-seed overlap](../artifacts/originality-v35-varied-seeds/overlap.json)
