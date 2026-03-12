from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class GuiState:
    input_path: str = ""
    output_path: str = ""
    output_format: str = "smartbp_csv"
    source: int = 0
    missing_pulse_policy: str = "empty"
    pulse_value: Optional[int] = None
    filter_start: Optional[datetime] = None
    filter_end: Optional[datetime] = None
    include_stats: bool = True
    stats_scope: str = "selected"
    selected_columns: List[str] = field(default_factory=list)


@dataclass
class ResultSummary:
    output_file: str = ""
    rows_read: int = 0
    rows_selected: int = 0
    rows_exported: int = 0
    rows_skipped: int = 0
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    swapped_sys_dia_fixed: int = 0
    pp_mismatch_count: int = 0
    pulse_missing: int = 0
    pulse_filled: int = 0
    avg_sys: Optional[float] = None
    avg_dia: Optional[float] = None
    avg_pulse: Optional[float] = None
