"""Resource gates for this twenty-update experiment; no inference/training imports."""
import math


def resource_violation(progress):
    if progress.get('error'):
        return 'training error'
    if progress.get('warnings'):
        return 'training warning'
    for field in ('loss', 'eval_loss', 'peak_memory_gb'):
        value = progress.get(field)
        if value is not None and (not isinstance(value, (int, float)) or not math.isfinite(value)):
            return 'invalid ' + field
    if (progress.get('peak_memory_gb') or 0) > 10:
        return 'MLX peak exceeds10GB'
    if (progress.get('step') or 0) > 20:
        return 'twenty-update limit exceeded'
    return None
