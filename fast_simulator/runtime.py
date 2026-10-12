"""Respect CPU quotas when choosing a default pool size."""
import math
import os
from pathlib import Path

def available_cpus():
    count = len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else (os.cpu_count() or 1)
    try:
        quota, period = Path('/sys/fs/cgroup/cpu.max').read_text().split()
        if quota != 'max':
            count = min(count, max(1, math.ceil(int(quota)/int(period))))
    except (OSError, ValueError):
        pass
    return max(1, count)
