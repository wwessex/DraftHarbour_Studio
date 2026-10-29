"""Archive only allowlisted experimental adapter files; never collect a directory tree."""
import argparse,hashlib,json,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
META=ROOT/'models/experimental-2026-10-29'
OUT=ROOT/'artifacts/model-archive-v1'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--edition',choices=['experimental-2026-10-29','grounding-v6-2026-10-29'],default='experimental-2026-10-29')
    args=parser.parse_args()
    meta=ROOT/'models'/args.edition
    out=OUT if args.edition=='experimental-2026-10-29' else ROOT/'artifacts/model-archive-v6'
    manifest=json.loads((meta/'manifest.json').read_text())
    out.mkdir(exist_ok=False)
    built=[]
    for model in manifest['models']:
        source=ROOT/model['source_adapter']
        for name,expected in model['files'].items():
            if sha(source/name)!=expected:raise RuntimeError('Adapter mismatch: '+model['id']+'/'+name)
        destination=out/model['asset']
        with zipfile.ZipFile(destination,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as archive:
            for name in ['adapters.safetensors','adapter_config.json']:
                archive.write(source/name,name)
            for name in ['README.md','LICENSE','NOTICE','manifest.json']:
                archive.write(meta/name,name)
        with zipfile.ZipFile(destination) as archive:
            assert set(archive.namelist())=={'adapters.safetensors','adapter_config.json','README.md','LICENSE','NOTICE','manifest.json'}
            for name,expected in model['files'].items():
                assert hashlib.sha256(archive.read(name)).hexdigest()==expected
            assert archive.testzip() is None
        built.append(dict(asset=destination.name,sha256=sha(destination),bytes=destination.stat().st_size))
    (out/'assets.json').write_text(json.dumps(built,indent=2)+'\n')
    (out/'SHA256SUMS').write_text(''.join(r['sha256']+'  '+r['asset']+'\n' for r in built))
    print(json.dumps(built,indent=2))
if __name__=='__main__':main()
