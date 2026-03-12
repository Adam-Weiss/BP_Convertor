from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Measurement:
    datetime: datetime
    sys: int
    dia: int
    pulse: Optional[int] = None
    weight: Optional[float] = None
    pp: Optional[int] = None
    map: Optional[float] = None
    notes: str = ""
    tags: str = ""
    source: int = 0
    original_date: str = ""
    original_time: str = ""
    original_row_index: Optional[int] = None
    warnings: List[str] = field(default_factory=list)
    corrections_applied: List[str] = field(default_factory=list)


@dataclass
class ConversionStats:
    rows_read: int = 0
    rows_selected: int = 0
    rows_exported: int = 0
    rows_skipped: int = 0
    swapped_sys_dia_fixed: int = 0
    pp_mismatch_count: int = 0
    pulse_missing: int = 0
    pulse_filled: int = 0
    first_timestamp: Optional[datetime] = None
    last_timestamp: Optional[datetime] = None
    avg_sys: Optional[float] = None
    avg_dia: Optional[float] = None
    avg_pulse: Optional[float] = None
    min_sys: Optional[int] = None
    max_sys: Optional[int] = None
    min_dia: Optional[int] = None
    max_dia: Optional[int] = None
    min_pulse: Optional[int] = None
    max_pulse: Optional[int] = None


@dataclass
class ConversionResult:
    output_file: str
    stats: ConversionStats
    warnings: List[str]
    selected_count: int
    available_columns: List[str]
