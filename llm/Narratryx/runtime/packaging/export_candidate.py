"""Export the exact experimental adapter locally, without training or publication."""
from pathlib import Path
import argparse
import json
import os
import time

from runtime.local.engine import MLXEngine, file_hash

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--llama-source', type=Path, required=True)
    args = parser.parse_args()
    source = args.llama_source.resolve()
    for name in ('convert_hf_to_gguf.py', 'llama-quantize'):
        if not (source / name).is_file():
            raise ValueError(f'Missing installed conversion tool: {name}')
    args.output.mkdir(parents=True, exist_ok=False)
    output = args.output.resolve()
    pin = json.loads((ROOT / 'configs/narratryx-craft-v1.json').read_text())
    base = Path.home() / '.cache/huggingface/hub' / ('models--' + pin['base_repo'].replace('/', '--')) / 'snapshots' / pin['base_revision']
    os.environ['UNSLOTH_LLAMA_CPP_SCRIPTS_DIR'] = str(source)
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['TRANSFORMERS_OFFLINE'] = '1'
    report = dict(schema_version=1, model_id=pin['model_id'], experimental=True,
                  base_revision=pin['base_revision'], source_adapter_sha256=pin['adapter_sha256'],
                  converter_sha256=file_hash(source / 'convert_hf_to_gguf.py'),
                  quantizer_sha256=file_hash(source / 'llama-quantize'),
                  quantization='Q4_K_M', distribution_approved=False, status='started')
    started = time.monotonic()
    engine = None
    try:
        engine = MLXEngine(pin, base, ROOT / pin['adapter_path'])
        def export():
            model = engine.backend._model
            save = getattr(model, 'save_pretrained_gguf', None)
            if save is None:
                raise RuntimeError('Installed MLX model has no GGUF exporter')
            processor = engine.backend._processor or engine.tokenizer
            save(str(output), processor, quantization_method='q4_k_m')
        engine.executor.submit(export).result()
        models = [p for p in output.rglob('*.gguf') if 'q4_k_m' in p.name.lower() and 'mmproj' not in p.name.lower()]
        if len(models) != 1:
            raise RuntimeError(f'Expected one text Q4_K_M model, found {len(models)}')
        model = models[0]
        report.update(status='exported', artifact=model.relative_to(output).as_posix(),
                      bytes=model.stat().st_size, sha256=file_hash(model))
        print(json.dumps({k: report[k] for k in ('status', 'artifact', 'bytes', 'sha256')}), flush=True)
    except BaseException as error:
        report.update(status='failed', error_type=type(error).__name__, error=str(error))
        raise
    finally:
        report['elapsed_seconds'] = round(time.monotonic() - started, 2)
        (output / 'export-report.json').write_text(json.dumps(report, indent=2) + '\n')
        if engine is not None:
            engine.close()


if __name__ == '__main__':
    main()
