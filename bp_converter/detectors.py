from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .role_inference import infer_roles


@dataclass
class DetectedTable:
    headers: List[Any]
    rows: List[List[Any]]
    roles: Dict[str, int]
    score: int


def _is_number(value: Any) -> bool:
    if value is None:
        return False
    text = str(value).strip()
    if text == "":
        return False
    try:
        float(text)
        return True
    except ValueError:
        return False


def _score_candidate(headers: List[Any], rows: List[List[Any]], roles: Dict[str, int]) -> int:
    score = 0
    if {"sys", "dia"}.issubset(roles):
        score += 30
    if "datetime" in roles or "date" in roles:
        score += 30
    if "time" in roles:
        score += 5
    if "pulse" in roles:
        score += 5

    sample = rows[: min(5, len(rows))]
    for row in sample:
        if "sys" in roles and roles["sys"] < len(row) and _is_number(row[roles["sys"]]):
            score += 3
        if "dia" in roles and roles["dia"] < len(row) and _is_number(row[roles["dia"]]):
            score += 3
        if "pulse" in roles and roles["pulse"] < len(row) and _is_number(row[roles["pulse"]]):
            score += 1
        if "sys" in roles and "dia" in roles and roles["sys"] < len(row) and roles["dia"] < len(row):
            try:
                if float(row[roles["sys"]]) > float(row[roles["dia"]]):
                    score += 2
            except Exception:
                pass
    return score


def _extract_contiguous_rows(source_rows: List[List[Any]], start_idx: int, date_col: Optional[int]) -> List[List[Any]]:
    out: List[List[Any]] = []
    for row in source_rows[start_idx:]:
        if date_col is not None:
            if date_col >= len(row) or str(row[date_col]).strip() == "":
                break
        if all((str(cell).strip() == "" for cell in row)):
            break
        out.append(row)
    return out


def detect_xlsx_table(input_path: str) -> DetectedTable:
    from openpyxl import load_workbook

    wb = load_workbook(input_path, data_only=True)
    best: Optional[DetectedTable] = None
    for sheet in wb.worksheets:
        all_rows = [list(row) for row in sheet.iter_rows(values_only=True)]
        scan_rows = min(len(all_rows), 120)
        for idx in range(scan_rows):
            headers = all_rows[idx]
            roles = infer_roles(headers)
            if not ({"sys", "dia"}.issubset(roles) and ("date" in roles or "datetime" in roles)):
                continue
            date_col = roles.get("datetime", roles.get("date"))
            block = _extract_contiguous_rows(all_rows, idx + 1, date_col)
            if not block:
                continue
            score = _score_candidate(headers, block, roles)
            cand = DetectedTable(headers=headers, rows=block, roles=roles, score=score)
            if best is None or cand.score > best.score:
                best = cand
    if best is None:
        raise ValueError("Could not detect a BP-like table in XLSX file")
    return best


def _sniff_delimiter(sample: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=[",", "\t", ";"])
        return dialect.delimiter
    except csv.Error:
        if "\t" in sample:
            return "\t"
        if ";" in sample:
            return ";"
        return ","


def detect_delimited_table(input_path: str) -> Tuple[DetectedTable, str]:
    text = Path(input_path).read_text(encoding="utf-8", errors="replace")
    delimiter = _sniff_delimiter(text[:4000])
    rows = list(csv.reader(text.splitlines(), delimiter=delimiter))

    best: Optional[DetectedTable] = None
    scan_rows = min(len(rows), 200)
    for idx in range(scan_rows):
        headers = rows[idx]
        roles = infer_roles(headers)
        if not ({"sys", "dia"}.issubset(roles) and ("date" in roles or "datetime" in roles)):
            continue
        date_col = roles.get("datetime", roles.get("date"))
        block = _extract_contiguous_rows(rows, idx + 1, date_col)
        if not block:
            continue
        score = _score_candidate(headers, block, roles)
        cand = DetectedTable(headers=headers, rows=block, roles=roles, score=score)
        if best is None or cand.score > best.score:
            best = cand

    if best is None:
        raise ValueError("Could not detect a BP-like block in delimited text")
    return best, delimiter


def detect_table(input_path: str) -> DetectedTable:
    suffix = Path(input_path).suffix.lower()
    if suffix == ".xlsx":
        return detect_xlsx_table(input_path)
    if suffix in {".csv", ".tsv"}:
        table, _ = detect_delimited_table(input_path)
        return table
    raise ValueError(f"Unsupported input extension: {suffix}")
