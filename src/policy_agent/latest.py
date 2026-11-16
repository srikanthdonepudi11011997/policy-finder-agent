"""Core logic: choose the latest in-force version of every policy."""

from __future__ import annotations

import re
from collections import defaultdict
from datetime import date
from typing import Iterable

from .models import PolicyDoc


def parse_version(v: str) -> tuple:
    """'3.10' -> (3, 10) so 3.10 sorts after 3.9. Non-numeric parts are ignored."""
    return tuple(int(p) for p in re.findall(r"\d+", v)) or (0,)


def pick_latest(docs: Iterable[PolicyDoc], as_of: date | None = None) -> dict[str, PolicyDoc]:
    """Return {policy key: latest version}.

    Only Approved documents already in effect on ``as_of`` (default today) count.
    The winner has the newest effective date, then the highest version number.
    """
    as_of = as_of or date.today()
    groups: dict[str, list[PolicyDoc]] = defaultdict(list)
    for d in docs:
        if d.status.lower() == "approved" and d.effective_date <= as_of:
            groups[d.key].append(d)
    return {k: max(v, key=lambda d: (d.effective_date, parse_version(d.version))) for k, v in groups.items()}
