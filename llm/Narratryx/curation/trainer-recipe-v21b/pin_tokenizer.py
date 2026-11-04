"""Pin cached tokenizer/config metadata after reproducing all frozen token rows."""
import os
os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1')
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import file_hash,read_jsonl
OUT=ROOT/'artifacts/trainer-recipe-v21b'


def main():
    target=OUT/'model-metadata.pins.json'
    assert not target.exists()
    p=json.loads((OUT/'protocol.proposed.frozen.json').read_text());base=Path(p['base_path'])
    names=['chat_template.jinja','config.json','model.safetensors.index.json','preprocessor_config.json','processor_config.json','tokenizer.json','tokenizer_config.json','video_preprocessor_config.json','vocab.json']
    pins={str(base/n):file_hash(base/n) for n in names}
    from unsloth_cli.commands.train import _activate_mlx_transformers
    _activate_mlx_transformers(str(base),None)
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(base,local_files_only=True,trust_remote_code=False)
    records=read_jsonl(ROOT/'artifacts/source-candidates-v20/records.proposed.jsonl');checked=0
    for split in ['train','validation']:
        token_rows=read_jsonl(OUT/(split+'.tokens.jsonl'))
        source=[r for r in records if r['split']==split]
        assert len(source)==len(token_rows)
        for r,row in zip(source,token_rows):
            prompt=tokenizer.apply_chat_template(r['messages'][:-1],tokenize=False,add_generation_prompt=True,enable_thinking=False)
            a=tokenizer.encode(prompt,add_special_tokens=False);b=tokenizer.encode(r['messages'][-1]['content'],add_special_tokens=False)
            ids=a+b+[tokenizer.eos_token_id]
            assert row==dict(input_ids=ids,labels=[-100]*len(a)+b+[tokenizer.eos_token_id],attention_mask=[1]*len(ids))
            checked+=1
    for n,h in pins.items():assert file_hash(Path(n))==h,n
    assert checked==44
    with target.open('x') as f:json.dump(dict(records_reproduced=44,all_frozen_token_rows_identical=True,model_metadata_hashes=pins,training=False,weights_loaded=False,input_hashes={str(Path(__file__).relative_to(ROOT)):file_hash(Path(__file__))}),f,indent=2);f.write('\n')
    print('Pinned cached tokenizer/config metadata; all44 frozen token rows reproduced. No weights loaded.')


if __name__=='__main__':main()
