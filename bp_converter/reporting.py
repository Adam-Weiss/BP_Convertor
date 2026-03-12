from __future__ import annotations

from .models import ConversionStats


def stats_to_lines(stats: ConversionStats) -> list[str]:
    """Render conversion stats to simple key:value text lines."""
    return [f"{k}: {v}" for k, v in stats.__dict__.items()]
