import concurrent.futures,hashlib,json,urllib.request
from pathlib import Path
r=Path(__file__).resolve().parents[2];ev=r/'rights/evidence/source-expansion-2026-11-02';raw=r/'rights/raw/source-expansion-2026-11-02'
lock=json.loads((r/'curation/revision-preflight-v1/source-lock.json').read_text())
jobs=[]
for n,leaves in [('james-1881',[155,156]),('james-1908',[181,182,183])]:
 ref=next(x for x in lock['images'] if x['source']==n)
 for leaf in leaves:jobs.append((ev/f'{n}-leaf-{leaf}.jpg',ref['url'].replace(f'_{ref["leaf"]:04d}.jp2',f'_{leaf:04d}.jp2')))
jobs += [(raw/'pg688.txt','https://www.gutenberg.org/cache/epub/688/pg688.txt'),(ev/'pg688-catalog.html','https://www.gutenberg.org/ebooks/688'),(ev/'pg-permission.html','https://www.gutenberg.org/policy/permission.html'),(ev/'pg-terms.html','https://www.gutenberg.org/policy/terms_of_use.html'),(ev/'gb-copyright.html','https://www.gov.uk/copyright/how-long-copyright-lasts'),(ev/'us-circular15a.pdf','https://www.copyright.gov/circs/circ15a.pdf')]
def get(job):
 p,url=job
 assert not p.exists()
 response=urllib.request.urlopen(url,timeout=35);data=response.read(3000001)
 assert len(data)<3000000
 if p.suffix=='.jpg':assert data.startswith(b'\xff\xd8')
 if p.suffix=='.txt':assert b'START OF THE PROJECT GUTENBERG' in data or b'START OF THIS PROJECT GUTENBERG' in data
 p.write_bytes(data)
 return dict(path=str(p.relative_to(r)),url=url,resolved_url=response.geturl(),sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),retrieved_on='2026-11-02')
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 for job,res in zip(jobs,ex.map(get,jobs)):
  rows.append(res);print(res['path'],res['bytes'])
with (ev/'acquisition.json').open('x') as f:json.dump(rows,f,indent=2);f.write('\n')
