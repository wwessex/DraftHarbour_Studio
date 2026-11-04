# Austen scene paired with Woolf's criticism

The review proposal now gives the model the original visit scene before asking for Woolf's published criticism. The 715-word context runs from the visitors interrupting the dinner preparations through Emma's reply about income and Lord Osborne's change of manner. It replaces the scene-summary version, preserving the exact Woolf answer and the 42 training and 16 monitor memberships.

The source is PG63569, a transcription of the 1923 D. Appleton edition. The manuscript corroborates the scene's Austen authorship, including the interruption, the conversation about riding, and Emma's reply. The prompt notes the name differences between Woolf's account and the supplied edition. The manuscript website supplies attribution evidence. The original print transcription supplies the training context. [Edition catalogue](https://www.gutenberg.org/ebooks/63569) · [Manuscript headnote](https://janeausten.ac.uk/edition/ms/WatsonsHeadNote.html) · [Opening of the visit](https://janeausten.ac.uk/manuscripts/qmwats/b7-4.html) · [Emma's reply](https://janeausten.ac.uk/manuscripts/qmwats/b7-7.html)

The added GB/US ledger entry covers that one interval as input context. It excludes Oulton's continuation and other edition material. Source interval, author split and dataset checks passed. The cached tokenizer reproduced the exact answer and counted 1,181 tokens including the end token, within the 2,048-token budget. This is one passage-and-criticism example. The answer models reasoning from scene details, with direct quotation and calibrated uncertainty still underrepresented.

[Local validation manifest](../artifacts/watsons-v33/review.json)
