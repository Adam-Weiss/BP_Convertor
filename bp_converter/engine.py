from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .detectors import detect_table
from .models import ConversionResult, Measurement
from .normalize import normalize_rows
from .options import ConversionOptions
from .stats import build_stats
from .validation import validate_measurements
from .writer import ALLOWED_COLUMNS, write_normalized_xlsx, write_smartbp_csv


DEFAULT_XLSX_COLUMNS = ["datetime", "sys", "dia", "pulse", "pp", "map", "notes", "tags"]


def _default_out_path(input_path: str, output_format: str) -> str:
    base = Path(input_path).stem
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = ".csv" if output_format == "smartbp_csv" else ".xlsx"
    suffix = "smartbp" if output_format == "smartbp_csv" else "normalized"
    return f"{base}_{suffix}_{stamp}{ext}"


def _apply_filter(measurements: List[Measurement], start: Optional[datetime], end: Optional[datetime]) -> List[Measurement]:
    out = measurements
    if start is not None:
        out = [m for m in out if m.datetime >= start]
    if end is not None:
        out = [m for m in out if m.datetime <= end]
    return out


def convert_file(input_path: str, options: ConversionOptions, output_path: Optional[str] = None) -> ConversionResult:
    table = detect_table(input_path)
    normalized = normalize_rows(table.rows, table.roles, source=options.source)
    rows_read = len(table.rows)
    validated = validate_measurements(normalized, options)
    selected = _apply_filter(validated, options.filter_start, options.filter_end)

    stats_basis = selected if options.stats_scope == "selected" else validated
    stats = build_stats(rows_read=rows_read, selected=stats_basis, exported=selected, skipped=max(rows_read - len(validated), 0))

    out_file = output_path or _default_out_path(input_path, options.output_format)
    if options.output_format == "smartbp_csv":
        write_smartbp_csv(out_file, selected)
    elif options.output_format == "normalized_xlsx":
        columns = options.selected_columns or DEFAULT_XLSX_COLUMNS
        bad_cols = [c for c in columns if c not in ALLOWED_COLUMNS]
        if bad_cols:
            raise ValueError(f"Unsupported columns requested: {bad_cols}")
        write_normalized_xlsx(out_file, selected, columns, stats if options.include_stats else None)
    else:
        raise ValueError(f"Unsupported output format: {options.output_format}")

    warnings = [w for m in validated for w in m.warnings]
    return ConversionResult(
        output_file=out_file,
        stats=stats,
        warnings=warnings,
        selected_count=len(selected),
        available_columns=ALLOWED_COLUMNS,
    )
