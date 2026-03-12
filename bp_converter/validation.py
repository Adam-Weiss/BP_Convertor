from __future__ import annotations

from typing import List

from .models import Measurement
from .normalize import build_notes
from .options import ConversionOptions


def _apply_pulse_policy(m: Measurement, options: ConversionOptions) -> None:
    if m.pulse is not None:
        return
    if options.missing_pulse_policy == "empty":
        return
    if options.missing_pulse_policy in {"fixed", "user"} and options.fixed_pulse_value is not None:
        m.pulse = options.fixed_pulse_value
        m.corrections_applied.append(f"pulse_filled:{options.fixed_pulse_value}")
        m.warnings.append(f"missing pulse filled with {options.fixed_pulse_value}")


def validate_measurements(measurements: List[Measurement], options: ConversionOptions) -> List[Measurement]:
    """Apply validation/corrections and attach warnings/notes."""
    for m in measurements:
        extra_notes = []
        if options.correct_swapped_sys_dia and m.sys < m.dia:
            old_sys, old_dia = m.sys, m.dia
            m.sys, m.dia = m.dia, m.sys
            m.corrections_applied.append("swapped_sys_dia_fixed")
            warn = f"corrected swapped Sys/Dia (was Sys={old_sys}, Dia={old_dia})"
            m.warnings.append(warn)
            extra_notes.append(warn)

        calc_pp = m.sys - m.dia
        if m.pp is not None and m.pp < 0:
            msg = f"input PP was negative ({m.pp})"
            m.warnings.append(msg)
            extra_notes.append(msg)
        if options.detect_pp_mismatch and m.pp is not None and abs(m.pp - calc_pp) >= 2:
            msg = f"input PP={m.pp} differs from calc PP={calc_pp}"
            m.warnings.append(msg)
            extra_notes.append(msg)
        m.pp = calc_pp

        _apply_pulse_policy(m, options)

        extra_note = " | ".join(extra_notes)
        m.notes = build_notes(m.tags, m.notes, extra_note)
    return measurements
