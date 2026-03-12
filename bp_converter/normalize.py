from __future__ import annotations

import re
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional

from .models import Measurement


def norm_cell_text(x: Any) -> str:
    if x is None:
        return ""
    s = str(x)
    s = s.replace("\r\n", " ").replace("\n", "").replace("\r", "")
    return re.sub(r"\s+", " ", s).strip()


def to_int(value: Any) -> Optional[int]:
    s = norm_cell_text(value)
    if s == "" or s.lower() == "nan" or s.upper() == "NA":
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def to_float(value: Any) -> Optional[float]:
    s = norm_cell_text(value)
    if s == "" or s.lower() == "nan" or s.upper() == "NA":
        return None
    try:
        return float(s)
    except ValueError:
        return None


def split_tags(tag_cell: Any) -> str:
    s = norm_cell_text(tag_cell)
    if s in ("", "0"):
        return ""
    parts = [p.strip() for p in s.split(",") if p.strip()]
    return ",".join(parts)


def build_notes(tags: str, user_notes: str, extra_note: str) -> str:
    user_notes = norm_cell_text(user_notes)
    extra_note = norm_cell_text(extra_note)
    if user_notes == "0":
        user_notes = ""
    combined = user_notes
    if extra_note:
        combined = (combined + " | " if combined else "") + extra_note
    if tags:
        if combined:
            return f"Tags: {tags}\r\n\r\nNotes: {combined}"
        return f"Tags: {tags}"
    return f"Notes: {combined}" if combined else ""


def parse_datetime_value(date_value: Any, time_value: Any = None) -> datetime:
    if isinstance(date_value, datetime):
        dt = date_value
    elif isinstance(date_value, date) and not isinstance(date_value, datetime):
        dt = datetime(date_value.year, date_value.month, date_value.day)
    else:
        s = norm_cell_text(date_value)
        if time_value not in (None, ""):
            s = f"{s} {norm_cell_text(time_value)}".strip()
        if not s:
            raise ValueError("Empty datetime")
        fmts = [
            "%m/%d/%y %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%m/%d/%y %H:%M", "%m/%d/%Y %H:%M",
            "%d-%b-%y %H:%M:%S", "%d-%b-%Y %H:%M:%S", "%d-%b-%y %H:%M", "%d-%b-%Y %H:%M",
            "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%m/%d/%y", "%m/%d/%Y", "%Y-%m-%d",
        ]
        dt = None
        for fmt in fmts:
            try:
                dt = datetime.strptime(s, fmt)
                break
            except ValueError:
                continue
        if dt is None:
            m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{2,4})(?: (\d{1,2}):(\d{2})(?::(\d{2}))?)?$", s)
            if not m:
                raise ValueError(f"Unrecognized Date format: {s!r}")
            mm, dd, yy, hh, mi, ss = m.groups()
            year = int(yy)
            if year < 100:
                year += 2000
            dt = datetime(year, int(mm), int(dd), int(hh or 0), int(mi or 0), int(ss or 0))

    if isinstance(time_value, time):
        dt = dt.replace(hour=time_value.hour, minute=time_value.minute, second=time_value.second)
    return dt.replace(second=int(dt.second or 0))


def normalize_rows(rows: List[List[Any]], roles: Dict[str, int], source: int) -> List[Measurement]:
    out: List[Measurement] = []
    for idx, row in enumerate(rows, start=1):
        date_idx = roles.get("datetime", roles.get("date"))
        time_idx = roles.get("time")
        if date_idx is None or date_idx >= len(row):
            continue
        date_raw = row[date_idx]
        time_raw = row[time_idx] if (time_idx is not None and time_idx < len(row)) else None
        dt = parse_datetime_value(date_raw, time_raw)
        sys_v = to_int(row[roles["sys"]]) if roles.get("sys") is not None and roles["sys"] < len(row) else None
        dia_v = to_int(row[roles["dia"]]) if roles.get("dia") is not None and roles["dia"] < len(row) else None
        if sys_v is None or dia_v is None:
            continue

        pulse_idx = roles.get("pulse")
        pulse = to_int(row[pulse_idx]) if pulse_idx is not None and pulse_idx < len(row) else None
        weight_idx = roles.get("weight")
        weight = to_float(row[weight_idx]) if weight_idx is not None and weight_idx < len(row) else None
        pp_idx = roles.get("pp")
        pp = to_int(row[pp_idx]) if pp_idx is not None and pp_idx < len(row) else None
        map_idx = roles.get("map")
        map_v = to_float(row[map_idx]) if map_idx is not None and map_idx < len(row) else None
        notes_idx = roles.get("notes")
        notes = norm_cell_text(row[notes_idx]) if notes_idx is not None and notes_idx < len(row) else ""
        tags_idx = roles.get("tags")
        tags = split_tags(row[tags_idx]) if tags_idx is not None and tags_idx < len(row) else ""

        out.append(
            Measurement(
                datetime=dt,
                sys=sys_v,
                dia=dia_v,
                pulse=pulse,
                weight=weight,
                pp=pp,
                map=map_v,
                notes=notes,
                tags=tags,
                source=source,
                original_date=norm_cell_text(date_raw),
                original_time=norm_cell_text(time_raw),
                original_row_index=idx,
            )
        )
    return out
