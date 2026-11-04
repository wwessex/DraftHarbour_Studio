"""Four original editing fixtures; compare raw rewriting with validated patches.

Evaluation only. Uses the existing authenticated loopback developer service and
never trains, changes an app setting, or applies output to a manuscript.
"""
from pathlib import Path
import hashlib,json,sys,urllib.request
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.anchored_edits import AnchorEdit,apply_anchor_edits
OUT=ROOT/'artifacts/anchored-edit-inference-v1'
FIXTURES=[
 ('latch','“The door is closed,” Rosa said. The latch was still still warm.','“The door is closed,” Rosa said. The latch was still warm.'),
 ('case','Leon’s violin case rested on the old old bench.','Leon’s violin case rested on the old bench.'),
 ('letter','“Keep the seal intact.” Ada put the letter beside beside the lamp.','“Keep the seal intact.” Ada put the letter beside the lamp.'),
 ('tape','Noa’s gloves were sealed; Sera left the unused unused tape on the shelf.','Noa’s gloves were sealed; Sera left the unused tape on the shelf.'),
]

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    OUT.mkdir(exist_ok=False)
    manifest=json.loads((ROOT/'configs/narratryx-craft-v1.json').read_text())
    protocol=dict(kind='Controlled inference/application workflow pilot; not a model-training or literary-quality result',model_id=manifest['model_id'],adapter_sha256=manifest['adapter_sha256'],script_sha256=sha(Path(__file__)),application_helper_sha256=sha(ROOT/'foundation/anchored_edits.py'),temperature=0,max_tokens=256,fixtures=FIXTURES,provenance='Original Codex AI-authored evaluation fixtures; never training or teacher targets',order='Alternate arm order by fixture; no latency comparison',application='Preview strings only. Exact unique nonoverlapping anchors and captured-target equality required. No JSON repair or fallback to expected answers.')
    with (OUT/'protocol.frozen.json').open('x') as stream:json.dump(protocol,stream,indent=2,ensure_ascii=False)
    token=(ROOT/'artifacts/local-serving/access-token').read_text().strip()
    outputs=[]
    with (OUT/'responses.jsonl').open('x') as stream:
        for index,(ident,source,expected) in enumerate(FIXTURES):
            order=['rewrite','patch'] if index%2==0 else ['patch','rewrite']
            for arm in order:
                instruction='Remove only the consecutive duplicated word. Preserve all other characters, quotes, apostrophes, punctuation and wording.'
                if arm=='rewrite':prompt=instruction+' Return only the corrected passage.\n\nTARGET:\n'+source
                else:prompt=instruction+' Return ONLY JSON with this exact structure: {"edits":[{"before":"exact unique substring containing the duplicate","after":"corrected substring"}]}. Use the smallest edit. Each before value must occur exactly once in the target. Do not return unchanged text or Markdown.\n\nTARGET:\n'+source
                payload=dict(model=manifest['model_id'],messages=[dict(role='user',content=prompt)],temperature=0,max_tokens=256,stream=False)
                request=urllib.request.Request('http://127.0.0.1:8890/v1/chat/completions',data=json.dumps(payload).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+token})
                error=None;text='';result=None;usage={};finish=None
                try:
                    with urllib.request.urlopen(request,timeout=90) as response:data=json.load(response)
                    text=data['choices'][0]['message']['content'];finish=data['choices'][0]['finish_reason'];usage=data.get('usage',{})
                    if arm=='rewrite':result=text.strip()
                    else:
                        obj=json.loads(text)
                        assert isinstance(obj,dict) and set(obj)=={'edits'} and isinstance(obj['edits'],list)
                        assert all(isinstance(edit,dict) and set(edit)=={'before','after'} for edit in obj['edits'])
                        edits=[AnchorEdit(edit['before'],edit['after']) for edit in obj['edits']]
                        result=apply_anchor_edits(source,source,edits)
                except Exception as exc:error=type(exc).__name__+': '+str(exc)
                row=dict(case_id=ident,arm=arm,raw_response=text,result=result,exact=result==expected,error=error,finish_reason=finish,usage=usage,protocol_sha256=sha(OUT/'protocol.frozen.json'))
                stream.write(json.dumps(row,ensure_ascii=False)+'\n');stream.flush();outputs.append(row)
                print(ident,arm,'exact=',row['exact'],'error=',error,flush=True)
    summary={arm:dict(exact=sum(row['exact'] for row in outputs if row['arm']==arm),cases=4,rejections=sum(bool(row['error']) for row in outputs if row['arm']==arm),truncated=sum(row['finish_reason']=='length' for row in outputs if row['arm']==arm)) for arm in ['rewrite','patch']}
    with (OUT/'summary.json').open('x') as stream:json.dump(dict(results=summary,interpretation='Four synthetic copyediting fixtures only. Workflow/application effect on the existing craft model, not improved weights or evidence of general rewriting skill.',app_manuscripts_modified=False),stream,indent=2)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
