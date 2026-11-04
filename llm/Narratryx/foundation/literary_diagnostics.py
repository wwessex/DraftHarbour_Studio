"""Transparent diagnostic proxies, never human literary-quality ratings."""
import re


def quoted_dialogue_blocks(text: str) -> int:
    """Count nonempty lines containing paired speech quotes.

    This is a proxy: two speakers on one line can be undercounted, and quoted
    fragments inside narration can be overcounted. Verify examples manually.
    """
    return sum(bool(re.search(r'(?:“[^”\n]+”|"[^"\n]+")', line))
               for line in text.splitlines() if line.strip())
