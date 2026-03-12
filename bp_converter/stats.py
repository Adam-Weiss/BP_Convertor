from __future__ import annotations

from statistics import mean
from typing import Iterable, List

from .models import ConversionStats, Measurement


def build_stats(rows_read: int, selected: List[Measurement], exported: List[Measurement], skipped: int) -> ConversionStats:
    stats = ConversionStats()
    stats.rows_read = rows_read
    stats.rows_selected = len(selected)
    stats.rows_exported = len(exported)
    stats.rows_skipped = skipped

    stats.swapped_sys_dia_fixed = sum("swapped_sys_dia_fixed" in m.corrections_applied for m in selected)
    stats.pp_mismatch_count = sum(any("differs from calc PP" in w for w in m.warnings) for m in selected)
    stats.pulse_missing = sum(m.pulse is None for m in selected)
    stats.pulse_filled = sum(any(c.startswith("pulse_filled:") for c in m.corrections_applied) for m in selected)

    if selected:
        stats.first_timestamp = min(m.datetime for m in selected)
        stats.last_timestamp = max(m.datetime for m in selected)
        stats.avg_sys = mean(m.sys for m in selected)
        stats.avg_dia = mean(m.dia for m in selected)
        stats.min_sys = min(m.sys for m in selected)
        stats.max_sys = max(m.sys for m in selected)
        stats.min_dia = min(m.dia for m in selected)
        stats.max_dia = max(m.dia for m in selected)

    pulses = [m.pulse for m in selected if m.pulse is not None]
    if pulses:
        stats.avg_pulse = mean(pulses)
        stats.min_pulse = min(pulses)
        stats.max_pulse = max(pulses)

    return stats
