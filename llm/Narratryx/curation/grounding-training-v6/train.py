"""One bounded, fresh-base local Unsloth MLX experiment. No serving/default change."""
import os
os.environ.update(HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', UNSLOTH_MLX_PROMPT_CACHE_BYTES='0')
from pathlib import Path
import dataclasses, hashlib, json, math, sys, time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from foundation.validation import validate_dataset
RUN=ROOT/'artifacts/grounding-training-v6'

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()
def save(name,value):
    with (RUN/name).open('x') as f:json.dump(value,f,indent=2,default=str)

def main():
    protocol=json.loads((RUN/'protocol.frozen.json').read_text());cfg=json.loads((RUN/'request.json').read_text())
    for name,value in protocol['input_hashes'].items():assert sha(ROOT/name)==value,name
    for name,value in protocol['protected_artifacts'].items():assert sha(ROOT/name)==value,name
    for side in ['base','current-craft']:
        completed=json.loads((RUN/f'{side}.complete.json').read_text())
        assert completed['completed'] and completed['cases']==64
        assert sha(RUN/f'{side}.responses.jsonl')==completed['response_sha256']
    data=validate_dataset(ROOT/'artifacts/grounding-balanced-v1/records.jsonl',ROOT/'rights/grounding-balanced-v1.scoped.jsonl',['GB','US'])
    assert all(r['teacher'] is None and r['origin']=='derived' for r in data)
    assert not (RUN/'adapter').exists()
    assert sha(Path(cfg['model_snapshot_path'])/'model.safetensors')==protocol['base_weights_sha256']
    save('launch-audit.json',dict(started_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),protocol_sha256=sha(RUN/'protocol.frozen.json'),training_script_sha256=sha(Path(__file__)),scope='One fresh-base20-update local learning-rate ablation; no generated literary teaching targets, corpus uploads, cloud spending, app changes or promotion.'))
    from unsloth_cli.commands.train import _create_cli_trainer
    trainer=_create_cli_trainer(cfg['model_snapshot_path'],None)
    from datasets import Dataset
    from utils.datasets.pretokenized import has_custom_labels
    for token_path in cfg['local_datasets']+cfg['local_eval_datasets']:
        token_rows=[json.loads(line) for line in Path(token_path).read_text().splitlines()]
        assert has_custom_labels(Dataset.from_list(token_rows)), 'Installed worker must preserve explicit prompt/answer labels'
    assert trainer.load_model(model_name=cfg['model_name'],max_seq_length=2048,load_in_4bit=False,trust_remote_code=False,use_gradient_checkpointing='mlx')
    assert trainer.prepare_model_for_training(use_lora=True,target_modules=cfg['target_modules'],lora_r=8,lora_alpha=16,lora_dropout=0,use_gradient_checkpointing='mlx',random_state=42)
    ds,ev=trainer.load_and_format_dataset(dataset_source='',format_type='auto',local_datasets=cfg['local_datasets'],local_eval_datasets=cfg['local_eval_datasets'],eval_steps=cfg['eval_steps'],is_cpt=False)
    args=dict(cfg,output_dir=str(RUN/'adapter'),enable_wandb=False,enable_tensorboard=False,allow_ambient=False)
    save('worker-config.json',trainer._build_worker_config(args))
    gate_failures=[]
    from guards import resource_violation
    def progress(value):
        d=dataclasses.asdict(value) if dataclasses.is_dataclass(value) else vars(value)
        with (RUN/'progress.jsonl').open('a') as f:f.write(json.dumps(d,default=str)+'\n')
        print(json.dumps({key:d.get(key) for key in ['step','total_steps','loss','eval_loss','warnings','error','is_completed','status_message']}),flush=True)
        violation=resource_violation(d)
        if violation:
            gate_failures.append(violation);trainer.stop_training()
    trainer.add_progress_callback(progress)
    assert trainer.start_training(dataset=ds,eval_dataset=ev,**args)
    trainer.training_thread.join(timeout=1200)
    if trainer.training_thread.is_alive():
        trainer.stop_training();trainer.training_thread.join(timeout=30);raise RuntimeError('Twenty-minute local training deadline')
    if trainer._pump_thread:trainer._pump_thread.join(timeout=15)
    final=trainer.get_training_progress();result=dataclasses.asdict(final) if dataclasses.is_dataclass(final) else vars(final);save('final-progress.json',result)
    assert not gate_failures,gate_failures
    assert not final.error and not final.warnings and final.is_completed and final.step==protocol['training_steps'],result
    assert sha(Path(cfg['model_snapshot_path'])/'model.safetensors')==protocol['base_weights_sha256']
    for name,value in protocol['protected_artifacts'].items():assert sha(ROOT/name)==value,name
    save('completion.json',dict(completed=True,steps=final.step,adapter_sha256=sha(RUN/'adapter/adapters.safetensors'),base_and_prior_adapters_unchanged=True,model_promoted=False))
if __name__=='__main__':main()
