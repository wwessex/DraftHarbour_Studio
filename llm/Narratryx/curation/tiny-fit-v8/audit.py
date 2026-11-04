"""Audit installed collation and standard loss masks; CCE source is pinned, not dynamically proven here."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from foundation.validation import read_jsonl,file_hash
DATA=ROOT/'artifacts/tiny-fit-v8'
def main():
 p=json.loads((DATA/'protocol.proposed.frozen.json').read_text())
 from unsloth_cli.commands.train import _activate_mlx_transformers
 _activate_mlx_transformers(p['base_path'],None)
 from unsloth_cli._inference import ensure_studio_backend_path
 ensure_studio_backend_path()
 from transformers import AutoTokenizer
 from unsloth_zoo.mlx.utils import create_batches,make_baseline_loss_fn
 import mlx.core as mx
 import unsloth_zoo.mlx.utils as utils
 import unsloth_zoo.mlx.trainer as trainer
 tokenizer=AutoTokenizer.from_pretrained(p['base_path'],local_files_only=True,trust_remote_code=False)
 rows=read_jsonl(DATA/'train.tokens.jsonl');expected={tuple(r['input_ids']):r['labels'] for r in rows}
 assert len(expected)==12
 batches=create_batches(rows,tokenizer,1,2048,seed=42,append_eos=False)
 actual=0;seen=set()
 for batch,lengths,labels in batches:
  assert labels is not None
  end=int(lengths.tolist()[0][1]);ids=tuple(batch.tolist()[0][:end]);target=labels.tolist()[0]
  assert ids in expected and target[:end]==expected[ids]
  assert all(t==-100 for t in target[end:])
  actual+=sum(t!=-100 for t in target[1:]);seen.add(ids)
 assert len(seen)==12 and actual==json.loads((DATA/'preflight.json').read_text())['unique_supervised_tokens']
 # Fixed logits isolate loss masking, not causal influence of prompt inputs.
 class Fake:
  def __init__(self,change=False):self.change=change
  def __call__(self,ids):
   logits=mx.broadcast_to(mx.array([0.,0.,0.,3.]),(1,4,4))
   return mx.concatenate([mx.broadcast_to(mx.array([8.,0.,0.,0.]),(1,2,4)),logits[:,2:]],axis=1) if self.change else logits
 fn=make_baseline_loss_fn();batch=mx.array([[0,1,2,3,3]]);lengths=mx.array([[0,5]]);labels=mx.array([[-100,-100,-100,3,3]])
 loss,n=fn(Fake(),batch,lengths,labels);masked,_=fn(Fake(True),batch,lengths,labels);wrong,_=fn(Fake(),batch,lengths,mx.array([[-100,-100,-100,0,0]]));mx.eval(loss,n,masked,wrong)
 assert int(n.item())==2 and abs(loss.item()-masked.item())<1e-6 and wrong.item()>loss.item()+2
 report=dict(passed=True,real_rows_collated=12,supervised_tokens=actual,custom_labels_and_prompt_masks_preserved=True,padding_masked=True,next_token_target_shift_checked=True,standard_loss_mask_test_passed=True,standard_loss=float(loss.item()),masked_logit_change_loss=float(masked.item()),wrong_answer_loss=float(wrong.item()),cce_dynamic_gradient_test=False,limitation='The dynamic loss test covers installed standard CE. Actual training uses CCE; its labels-aware source is inspected/pinned, not claimed equivalent solely from this test.',installed_source_hashes={str(Path(m.__file__).resolve()):file_hash(Path(m.__file__)) for m in [utils,trainer]})
 with (DATA/'loss-path-audit.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in report.items() if k!='installed_source_hashes'},indent=2))
if __name__=='__main__':main()
