"""Scoped source evidence assessment; no model training or rights-holder consent claim."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import validate_schema,clear_source,load_ledger
OUT=ROOT/'artifacts/literary-mix-v2'
RAW=ROOT/'rights/raw/literary-expansion-2026-10-25'
EVIDENCE=ROOT/'rights/evidence/literary-expansion-2026-10-25'
LEDGER=ROOT/'rights/literary-mix-v2.scoped.jsonl'

class PageText(HTMLParser):
    def __init__(self):super().__init__();self.parts=[]
    def handle_data(self,data):self.parts.append(data)

def norm(text):return ' '.join(re.findall(r'\w+',text.casefold()))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return [json.loads(line) for line in path.read_text().splitlines()]

def main():
    OUT.mkdir(exist_ok=False)
    evidence=json.loads((EVIDENCE/'manifest.json').read_text())
    for item in evidence:
        assert sha(ROOT/item['path'])==item['sha256']
    for name in ['wells-catalogue','doyle-improved-catalogue']:
        text=(EVIDENCE/(name+'.html')).read_text()
        assert 'Public domain in the USA' in text
    assert '70 years after' in (EVIDENCE/'uk-term.html').read_text()
    assert 'gutenberg.pglaf.org' in (EVIDENCE/'provider-mirrors.txt').read_text()
    comparison=[]
    for number in [1,2]:
        parser=PageText();parser.feed((EVIDENCE/f'wells-chapter-{number}.html').read_text())
        comparison.append(norm(' '.join(parser.parts)))
    doyle_comparison=norm((RAW/'doyle-adventures.txt').read_text())
    excerpts=[]
    sources=[('wells-time-machine-pg35','wells-time-machine.txt','The Time Traveller (for so',' III.\n'),('doyle-adventures-pg48320','doyle-adventures-pg48320.txt','To Sherlock Holmes she is always',None)]
    for source,filename,begin,end_marker in sources:
        raw=(RAW/filename).read_text();start=raw.index(begin);stop=raw.index(end_marker,start) if end_marker else raw.index('*** END OF THE PROJECT GUTENBERG')
        candidates=[]
        for match in re.finditer(r'[^\n]+(?:\n[^\n]+)*',raw[start:stop]):
            text=' '.join(match.group().split())
            if not 55<=len(text.split())<=150 or re.search(r'\[|\]|https?://|\*|_|Gutenberg|Illustration',text):continue
            if source.startswith('wells'):
                matched=[n+1 for n,value in enumerate(comparison) if norm(text) in value]
                if not matched:continue
                proof=f'Exact normalised word sequence in 1895 Heinemann scan-backed chapter transcription {matched}; punctuation/whitespace may differ. Not a physical-copy collation.'
            else:
                if norm(text) not in doyle_comparison:continue
                proof='Exact normalised word sequence also present in independently pinned PG1661 transcript; title matter of selected PG48320 identifies Harper & Brothers and copyright 1892. No claim to an identified physical first-edition copy.'
            candidates.append(dict(id=f'{source}-{len(candidates):03d}',source_id=source,start=start+match.start(),end=start+match.end(),raw_text=match.group(),text=text,word_count=len(text.split()),crosscheck=proof,transformation='collapse whitespace only; offsets are LF-normalised Unicode code points'))
        # Small, deliberately reviewable scope; not the whole books or every candidate.
        selected=candidates[:8]
        assert len(selected)==8,source
        excerpts.extend(selected)
    with (OUT/'new-source-spans.json').open('x') as f:json.dump(excerpts,f,indent=2,ensure_ascii=False)
    span_hash=sha(OUT/'new-source-spans.json')
    catalogue={'wells-time-machine-pg35':35,'doyle-adventures-pg48320':48320}
    ledger=read(ROOT/'rights/literary-mix-v1.scoped.jsonl')
    for ident,filename,author,dates,death,year,title,publisher,edition in [
      ('wells-time-machine-pg35','wells-time-machine.txt','H. G. Wells','1866–1946',1946,1895,'The Time Machine','William Heinemann, London (1895 underlying edition; PG digital source)','Pinned PG35 digital transcript. Only eight selected paragraph word sequences collated with scan-backed 1895 Heinemann Chapters 1–2; physical source copy of PG35 is unidentified. No full-book or modern-matter clearance.'),
      ('doyle-adventures-pg48320','doyle-adventures-pg48320.txt','Arthur Conan Doyle','1859–1930',1930,1892,'Adventures of Sherlock Holmes','Harper & Brothers, Franklin Square, New York','Pinned PG48320 improved digital transcript; title matter identifies Harper & Brothers and copyright 1892, not an independently verified date/identity of a physical printing. Eight original prose spans only; not PG1661 or a claimed 1892 first-edition facsimile.')]:
        url=f'https://www.gutenberg.org/ebooks/{catalogue[ident]}'
        record=dict(schema_version='1.0',id=ident,work_id='the-time-machine' if ident.startswith('wells') else 'adventures-of-sherlock-holmes',title=title,source_kind='public_domain_candidate',author_ids=['hg-wells' if ident.startswith('wells') else 'arthur-conan-doyle'],contributors=[dict(name=author,role='author of selected original narrative prose only',life_dates=dates)],publication=dict(original_year=year,edition=edition,publisher=publisher,evidence=[url,'https://en.wikisource.org/wiki/The_Time_Machine_(Heinemann_text)' if ident.startswith('wells') else 'https://www.gutenberg.org/cache/epub/48320/pg48320.txt']),source=dict(url=f'https://gutenberg.pglaf.org/cache/epub/{catalogue[ident]}/pg{catalogue[ident]}.txt',retrieved_on='2026-10-25',revision='sha256:'+sha(RAW/filename),raw_path=str((RAW/filename).relative_to(ROOT/'rights')),sha256=sha(RAW/filename),included_material=f'Only eight exact LF-normalised Unicode spans for {ident} in artifacts/literary-mix-v2/new-source-spans.json, SHA-256 {span_hash}. Original prose and unchanged substrings; whitespace collapse only.',excluded_material='Provider wrappers, license, trademarks, credits, catalogue descriptions, title/printer matter, headings/contents, illustrations/captions, footnotes, ads, modern notes, third-party extracts and all unselected prose. Comparison pages are evidence only, not training text.',terms_evidence=[url,'https://www.gutenberg.org/policy/permission.html','https://www.gutenberg.org/policy/license.html','https://www.gutenberg.org/policy/terms_of_use.html','https://www.gutenberg.org/MIRRORS.ALL'],terms_decision='Codex AI evidence assessment under user permission-free-source instruction supports private local GB/US use of these expired original-prose spans without a new rights-holder grant. Source notices retained unchanged; no provider endorsement, branded redistribution, cloud upload or publication is authorised. Physical-edition uncertainty disclosed; not human approval or legal certification.',notices='Exact acquired bytes, complete provider notices, source snapshots and checksums retained privately. Source original prose is separated from provider branding and modern descriptive material.'),clearances=[dict(jurisdiction='GB',basis=f'Selected original author died {death}; ordinary life-plus-70 literary term expired by end {death+70}. No later independent contributions or edition layout included.',uses=['training','evaluation'],evidence=['https://www.gov.uk/copyright/how-long-copyright-lasts',url]),dict(jurisdiction='US',basis=f'Underlying selected original prose published {year}, before 1931; provider item identifies public domain in USA. Original historical published term has elapsed; modern independent additions excluded.',uses=['training','evaluation'],evidence=[url,'https://www.copyright.gov/circs/circ15a.pdf'])],unresolved_issues=[],review=dict(status='approved',reviewer='Codex AI: scoped source evidence assessment',reviewed_on='2026-10-25',notes='AI assessment, not a human ballot, author consent or legal certification. Supports only explicitly collated and reviewed selected original-prose spans under the user’s existing instruction. Exact physical print-copy uncertainty remains disclosed; no claim that the full acquired files are cleared.'))
        validate_schema(record,'rights-record');ledger.append(record)
    with LEDGER.open('x') as f:
        for record in ledger:f.write(json.dumps(record,ensure_ascii=False)+'\n')
    index=load_ledger(LEDGER)
    for excerpt in excerpts:
        raw=clear_source(index[excerpt['source_id']],LEDGER,['GB','US'],'training')
        assert raw[excerpt['start']:excerpt['end']]==excerpt['raw_text']
        assert ' '.join(excerpt['raw_text'].split())==excerpt['text']
    with (OUT/'source-audit.json').open('x') as f:json.dump(dict(passed=True,new_scoped_sources=2,new_scoped_paragraphs=16,source_evidence_manifest_sha256=sha(EVIDENCE/'manifest.json'),scope_sha256=span_hash,human_approval_recorded=False,new_permission_requested=False,assessment='AI evidence review only; no full-book or publication permission inferred'),f,indent=2)
    print('Sixteen scoped original-prose spans passed GB/US source evidence assessment and exact raw-span checks.')
if __name__=='__main__':main()
