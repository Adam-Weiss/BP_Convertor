from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class ConversionOptions:
    """Runtime options for conversion behavior and output."""

    source: int = 0
    missing_pulse_policy: str = "empty"
    fixed_pulse_value: Optional[int] = None
    correct_swapped_sys_dia: bool = True
    detect_pp_mismatch: bool = True
    allow_missing_pulse: bool = True
    output_format: str = "smartbp_csv"
    selected_columns: Optional[List[str]] = None
    filter_start: Optional[datetime] = None
    filter_end: Optional[datetime] = None
    include_stats: bool = True
    stats_scope: str = "selected"
