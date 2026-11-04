"""Audit the installed Unsloth update against the frozen pilot before amending it."""
import importlib.metadata
import inspect
import json
from pathlib import Path
import runpy

from train import ROOT, build_worker, expected_worker, sha
from foundation.validation import read_jsonl, validate_dataset

PLAN = ROOT / 'artifacts/pilot-recipe-v26'
OUT = ROOT / 'artifacts/pilot-recipe-v26-install-audit'


def main():
    assert __debug__ and not OUT.exists()
    protocol_path = PLAN / 'protocol.frozen.json'
    manifest = json.loads((ROOT / 'curation/pilot-recipe-v26/manifest.json').read_text())
    assert sha(protocol_path) == manifest['protocol_sha256']
    protocol = json.loads(protocol_path.read_text())
    for name, expected in protocol['input_hashes'].items():
        assert sha(ROOT / name) == expected, name
    for name, expected in protocol['model_metadata_hashes'].items():
        assert sha(Path(name)) == expected, name
    assert sha(Path(protocol['base_path']) / 'model.safetensors') == protocol['base_weights_sha256']
    versions = {name: importlib.metadata.version(name) for name in protocol['reference_environment']}
    assert versions == protocol['reference_environment'] | {'unsloth': '2026.11.1'}
    hashes = {name: sha(Path(name)) for name in protocol['installed_source_hashes']}
    cfg = json.loads((PLAN / 'request.json').read_text())
    data = validate_dataset(ROOT / 'artifacts/curriculum-fit-v24/records.review-only.jsonl',
                            ROOT / 'rights/curriculum-fit-v24.scoped.jsonl', ['GB', 'US'])
    assert len(data) == 50 and all(r['teacher'] is None and r['origin'] == 'derived' for r in data)

    from unsloth_cli.commands.train import _activate_mlx_transformers
    from unsloth_cli._inference import ensure_studio_backend_path
    _activate_mlx_transformers(protocol['base_path'], None)
    ensure_studio_backend_path()
    from transformers import AutoTokenizer, __version__
    from datasets import Dataset
    from utils.datasets.pretokenized import prepare_pretokenized_dataset
    from unsloth_zoo.mlx.utils import create_batches

    assert __version__ == protocol['active_tokenizer_transformers']
    for fn in (_activate_mlx_transformers, prepare_pretokenized_dataset, create_batches):
        path = inspect.getsourcefile(fn)
        assert sha(Path(path)) == hashes[path]
    tokenizer = AutoTokenizer.from_pretrained(protocol['base_path'], local_files_only=True,
                                              trust_remote_code=False)
    batch_audit = runpy.run_path(str(ROOT / 'curation/trainer-audit-v25/audit.py'))['audit_batches']
    prior = json.loads((ROOT / 'artifacts/trainer-audit-v25/installed-audit.json').read_text())
    results = {}
    for split in ('train', 'validation'):
        rows = read_jsonl(PLAN / f'{split}.tokens.jsonl')
        prepared = prepare_pretokenized_dataset(Dataset.from_list(rows), max_seq_length=None,
                                                vocab_size=len(tokenizer), mlx=True)
        assert [dict(row) for row in prepared] == rows
        results[split] = [batch_audit(rows, prepared, tokenizer, create_batches, n) for n in (1, 2)]
    assert results == prior['batches']
    trainer, _, _, _, worker = build_worker(cfg)
    assert not trainer.training_thread and not trainer._pump_thread
    expected = expected_worker(cfg)
    differences = sorted(key for key in worker.keys() | expected.keys()
                         if key not in worker or key not in expected or worker[key] != expected[key])
    assert not differences, f'Worker configuration changed fields: {differences}'
    for name, digest in hashes.items():
        assert sha(Path(name)) == digest
    OUT.mkdir()
    with (OUT / 'worker-config.json').open('x') as stream:
        json.dump(worker, stream, indent=2)
    evidence = dict(protocol_sha256=sha(protocol_path), reference_environment=versions,
                    installed_source_hashes=hashes, batches=results,
                    worker_config_sha256=sha(OUT / 'worker-config.json'),
                    audit_sha256=sha(Path(__file__)),
                    training_started=False)
    with (OUT / 'amendment.json').open('x') as stream:
        json.dump(evidence, stream, indent=2)
    print('Installed batch output and worker configuration match the frozen pilot.')


if __name__ == '__main__':
    main()
