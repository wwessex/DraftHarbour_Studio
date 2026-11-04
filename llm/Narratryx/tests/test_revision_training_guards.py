"""Training must stop on resource, numeric, warning and update-limit failures."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'curation/revision-training-v4/guards.py'
SPEC = importlib.util.spec_from_file_location('revision_guards', PATH)
GUARDS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(GUARDS)


class RevisionTrainingGuardsTests(unittest.TestCase):
    def test_valid_bounded_progress_can_continue(self):
        self.assertIsNone(GUARDS.resource_violation(dict(step=8, loss=1.2, eval_loss=None,
                                                        peak_memory_gb=10, warnings=[], error=None)))

    def test_over_memory_or_update_budget_stops(self):
        for progress in [dict(peak_memory_gb=10.01), dict(step=9)]:
            with self.subTest(progress=progress):
                self.assertIsNotNone(GUARDS.resource_violation(progress))

    def test_nonfinite_or_unparseable_metrics_stop(self):
        for value in [float('nan'), float('inf'), 'unknown']:
            for field in ['loss', 'eval_loss', 'peak_memory_gb']:
                with self.subTest(field=field, value=value):
                    self.assertIsNotNone(GUARDS.resource_violation({field:value}))

    def test_runtime_errors_and_warnings_stop(self):
        for progress in [dict(error='out of memory'), dict(warnings=['unsupported option'])]:
            self.assertIsNotNone(GUARDS.resource_violation(progress))
