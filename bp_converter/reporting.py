from __future__ import annotations

from .models import ConversionStats


def stats_to_lines(stats: ConversionStats) -> list[str]:
    return [f"{k}: {v}" for k, v in stats.__dict__.items()]
