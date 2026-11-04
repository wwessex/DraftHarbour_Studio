"""Invoke an existing v26 phase in the separate v27 run directory."""
import importlib
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'curation/source-training-v26'))
phase = sys.argv.pop(1)
assert phase in ('train', 'evaluate', 'report')
module = importlib.import_module(phase)
module.RUN = root / 'artifacts/source-training-v29'
module.main()
