from __future__ import annotations

import re
from typing import Any, Dict, Iterable, Optional


ROLE_SYNONYMS = {
    "date": ["date", "measurement date"],
    "time": ["time", "measurement time"],
    "datetime": ["datetime", "date time", "timestamp", "measured at"],
    "sys": ["sys", "sys (mmhg)", "systolic", "systolic(mmhg)", "sbp", "sys mmhg"],
    "dia": ["dia", "dia (mmhg)", "diastolic", "diastolic(mmhg)", "dbp", "dia mmhg"],
    "pulse": ["pulse", "pulse (bpm)", "pulse(bpm)", "hr", "heart rate", "bpm"],
    "weight": ["weight", "weight(kgs)", "weight (kgs)", "weight kg", "weight(kg)"],
    "pp": ["pp", "pp (mmhg)", "pulse pressure", "pulse pressure(mmhg)"],
    "map": ["map", "map (mmhg)", "map( mmhg)"],
    "notes": ["notes", "note"],
    "tags": ["tags", "tag"],
}


def _compact_header(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def normalize_header(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
    return re.sub(r"\s+", " ", text).strip().lower()


def infer_roles(headers: Iterable[Any]) -> Dict[str, int]:
    """Infer semantic column roles from a header row.

    Matching is intentionally tolerant to capitalization, spacing, and
    punctuation so exports from different health apps can still be mapped.
    """
    roles: Dict[str, int] = {}
    normalized = [normalize_header(h) for h in headers]
    compact = [_compact_header(h) for h in normalized]
    compact_synonyms = {
        role: {_compact_header(s) for s in synonyms}
        for role, synonyms in ROLE_SYNONYMS.items()
    }

    for idx, hdr in enumerate(normalized):
        if not hdr:
            continue
        for role, synonyms in ROLE_SYNONYMS.items():
            if role in roles:
                continue
            if hdr in synonyms or compact[idx] in compact_synonyms[role]:
                roles[role] = idx
                break

    for idx, hdr in enumerate(normalized):
        if idx in roles.values() or not hdr:
            continue
        if "systolic" in hdr and "sys" not in roles:
            roles["sys"] = idx
        elif "diastolic" in hdr and "dia" not in roles:
            roles["dia"] = idx
        elif "pulse" in hdr and "pulse" not in roles:
            roles["pulse"] = idx
        elif "time" in hdr and "datetime" not in roles and "date" not in roles:
            roles["time"] = idx
        elif "date" in hdr and "datetime" not in roles and "date" not in roles:
            roles["date"] = idx

    return roles


def role_index(roles: Dict[str, int], role: str) -> Optional[int]:
    return roles.get(role)
