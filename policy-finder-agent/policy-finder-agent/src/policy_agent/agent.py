"""The agent: answers questions using only the latest approved policy versions."""

from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass, field
from datetime import date

from .ingest import load_policies
from .latest import parse_version, pick_latest
from .models import PolicyDoc
from .search import BM25Index, chunk_doc, tokenize


@dataclass
class Answer:
    text: str
    sources: list[str] = field(default_factory=list)


class PolicyAgent:
    def __init__(self, folder: str, as_of: date | None = None):
        self.as_of = as_of or date.today()
        self.docs = load_policies(folder)
        self.latest = pick_latest(self.docs, self.as_of)
        chunks = [c for d in self.latest.values() for c in chunk_doc(d)]
        self.index = BM25Index(chunks)

    # ---- browsing ---------------------------------------------------
    def latest_policies(self) -> list[PolicyDoc]:
        return sorted(self.latest.values(), key=lambda d: d.policy_name.lower())

    def versions(self, name: str) -> list[PolicyDoc]:
        key = " ".join(name.lower().split())
        return sorted(
            (d for d in self.docs if d.key == key),
            key=lambda d: (d.effective_date, parse_version(d.version)),
            reverse=True,
        )

    # ---- question answering ----------------------------------------
    def _named_policy(self, question: str) -> str | None:
        """Policy whose name best overlaps the question (any status)."""
        q = set(tokenize(question))
        best, best_n = None, 0
        for d in self.docs:
            n = len(q & set(tokenize(d.policy_name)))
            if n > best_n:
                best, best_n = d.key, n
        return best

    def ask(self, question: str) -> Answer:
        named = self._named_policy(question)
        if named and named not in self.latest:
            vs = self.versions(named)
            states = ", ".join(sorted({f"{v.status} v{v.version}" for v in vs}))
            return Answer(
                f"There is no approved, in-force version of '{vs[0].policy_name}' ({states}). "
                "Drafts, retired and future-dated versions are not current policy.",
                [v.citation for v in vs],
            )

        hits = self.index.search(question, k=3)
        if named:  # restrict to the named policy
            hits = [h for h in hits if h[1].doc.key == named] or hits
        if not hits:
            return Answer("No matching policy was found.")

        top = hits[0][1].doc
        context = "\n\n".join(h[1].text for h in hits if h[1].doc.key == top.key)
        answer = self._generate(question, top, context)
        return Answer(answer, [top.citation])

    def _generate(self, question: str, doc: PolicyDoc, context: str) -> str:
        header = f"{doc.policy_name} v{doc.version}, effective {doc.effective_date.isoformat()}"
        model = os.getenv("OLLAMA_MODEL")
        if not model:  # no LLM configured: return the relevant policy text
            return f"{header}\n\n{context}"
        prompt = (
            "Answer the question using ONLY the policy text below. If it is not covered, say so.\n\n"
            f"POLICY: {header}\n{context}\n\nQUESTION: {question}\nANSWER:"
        )
        req = urllib.request.Request(
            os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate"),
            data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode(),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return f"{header}\n\n{json.loads(r.read())['response'].strip()}"
        except Exception as exc:
            return f"{header}\n\n{context}\n\n(LLM unavailable: {exc})"
