"""Extract policy name, version, effective date, status and owner from a document."""

from __future__ import annotations

import os
import re
from datetime import date, datetime

_FIELD = {
    "policy_name": re.compile(r"^\s*(?:policy(?:\s+name)?|title)\s*:\s*(.+?)\s*$", re.I | re.M),
    "version": re.compile(r"^\s*version\s*:\s*v?([\w.\-]+)\s*$", re.I | re.M),
    "effective_date": re.compile(r"^\s*(?:effective(?:\s+date)?)\s*:\s*(.+?)\s*$", re.I | re.M),
    "status": re.compile(r"^\s*status\s*:\s*(\w+)", re.I | re.M),
    "owner": re.compile(r"^\s*owner\s*:\s*(.+?)\s*$", re.I | re.M),
}
_FILENAME = re.compile(r"^(?P<name>.+?)_v(?P<version>[\d.]+)(?:_(?P<date>\d{4}-\d{2}-\d{2}))?$")
_DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y", "%d %B %Y")


def parse_date(raw: str) -> date | None:
    raw = raw.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def extract_metadata(text: str, path: str) -> dict:
    """Read metadata from the header text; fall back to the filename, then file mtime.

    Filename pattern: ``TravelPolicy_v3.2_2026-01-01.pdf``.
    A missing status is treated as ``Approved``.
    """
    header = text[:2000]
    found = {k: (m.group(1).strip() if (m := rx.search(header)) else None) for k, rx in _FIELD.items()}

    stem = os.path.splitext(os.path.basename(path))[0]
    fm = _FILENAME.match(stem)

    name = found["policy_name"] or (fm.group("name").replace("_", " ") if fm else stem.replace("_", " "))
    version = found["version"] or (fm.group("version") if fm else "0")

    eff = parse_date(found["effective_date"]) if found["effective_date"] else None
    if eff is None and fm and fm.group("date"):
        eff = parse_date(fm.group("date"))
    if eff is None:
        eff = date.fromtimestamp(os.path.getmtime(path)) if os.path.exists(path) else date.min

    return {
        "policy_name": name,
        "version": version,
        "effective_date": eff,
        "status": (found["status"] or "Approved").capitalize(),
        "owner": found["owner"] or "Unknown",
    }
