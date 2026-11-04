"""Acquire two individual source candidates and rights evidence, never bulk data."""
from pathlib import Path
import datetime,hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parents[2]
RAW=ROOT/'rights/raw/literary-expansion-2026-10-25'
EVIDENCE=ROOT/'rights/evidence/literary-expansion-2026-10-25'

def main():
    RAW.mkdir(exist_ok=False);EVIDENCE.mkdir(exist_ok=False)
    sources=[('wells-time-machine','https://gutenberg.pglaf.org/cache/epub/35/pg35.txt',RAW/'wells-time-machine.txt'),('doyle-adventures','https://gutenberg.pglaf.org/cache/epub/1661/pg1661.txt',RAW/'doyle-adventures.txt'),('wells-catalogue','https://www.gutenberg.org/ebooks/35',EVIDENCE/'wells-catalogue.html'),('doyle-catalogue','https://www.gutenberg.org/ebooks/1661',EVIDENCE/'doyle-catalogue.html'),('uk-term','https://www.gov.uk/copyright/how-long-copyright-lasts',EVIDENCE/'uk-term.html'),('provider-permission','https://www.gutenberg.org/policy/permission.html',EVIDENCE/'provider-permission.html'),('provider-license','https://www.gutenberg.org/policy/license.html',EVIDENCE/'provider-license.html'),('provider-terms','https://www.gutenberg.org/policy/terms_of_use.html',EVIDENCE/'provider-terms.html'),('provider-mirrors','https://www.gutenberg.org/MIRRORS.ALL',EVIDENCE/'provider-mirrors.txt')]
    evidence=[]
    for ident,url,path in sources:
        request=urllib.request.Request(url,headers={'User-Agent':'Narratryx-private-source-review/1.0'})
        with urllib.request.urlopen(request,timeout=30) as response:
            data=response.read(3_000_001)
            assert len(data)<=3_000_000
            metadata=dict(status=response.status,content_type=response.headers.get('Content-Type'),last_modified=response.headers.get('Last-Modified'),final_url=response.url)
        with path.open('xb') as stream:stream.write(data)
        evidence.append(dict(id=ident,url=url,path=str(path.relative_to(ROOT)),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),retrieved_on='2026-10-25',http=metadata))
        print(ident,len(data),'bytes',flush=True)
    with (EVIDENCE/'manifest.json').open('x') as stream:json.dump(evidence,stream,indent=2)
if __name__=='__main__':main()
