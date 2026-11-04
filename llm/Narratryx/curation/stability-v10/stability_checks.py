"""Predeclared exact repetition diagnostics; no semantic or literary-quality rating."""
import re
from collections import Counter
def repeated_dialogue(text):
 bodies=[]
 for line in text.splitlines():
  line=line.strip().strip('"“”')
  line=re.sub(r'^(?:Cora|Devin|Jules|Anika)\s*:\s*','',line)
  body=' '.join(line.strip().strip('"“”').casefold().split())
  if len(body.split())>=6:bodies.append(body)
 return max(Counter(bodies).values(),default=0)
