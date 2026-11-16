from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class PolicyDoc:
    path: str
    policy_name: str
    version: str
    effective_date: date
    status: str
    owner: str
    text: str

    @property
    def key(self) -> str:
        """Normalised name used to group versions of the same policy."""
        return " ".join(self.policy_name.lower().split())

    @property
    def citation(self) -> str:
        return f"{self.policy_name} v{self.version} (effective {self.effective_date.isoformat()}, {self.path})"
