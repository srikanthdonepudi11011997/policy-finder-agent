"""Tiny dependency-free BM25 search over policy chunks.

Swap this for ChromaDB + embeddings if you want semantic search (see README).
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass

from .models import PolicyDoc

STOPWORDS = {
    "the", "a", "an", "is", "are", "of", "to", "for", "and", "or", "in", "on", "what", "whats", "who", "how",
    "do", "does", "i", "we", "my", "our", "me", "can", "about", "current", "latest", "policy", "policies",
    "show", "tell", "give", "please", "any", "there", "it", "that", "this", "with", "be", "get",
}


def tokenize(text: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9]+", text.lower()) if t not in STOPWORDS]


@dataclass
class Chunk:
    doc: PolicyDoc
    text: str


def chunk_doc(doc: PolicyDoc, max_words: int = 120) -> list[Chunk]:
    paras = [p.strip() for p in re.split(r"\n\s*\n", doc.text) if p.strip()]
    chunks, buf = [], []
    for p in paras:
        buf.append(p)
        if sum(len(x.split()) for x in buf) >= max_words:
            chunks.append(Chunk(doc, "\n\n".join(buf)))
            buf = []
    if buf:
        chunks.append(Chunk(doc, "\n\n".join(buf)))
    return chunks


class BM25Index:
    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75):
        self.chunks, self.k1, self.b = chunks, k1, b
        # policy name is added to the indexed text so name matches rank higher
        self.tokens = [tokenize(c.doc.policy_name + " " + c.text) for c in chunks]
        self.avg = (sum(map(len, self.tokens)) / len(self.tokens)) if self.tokens else 0
        df = Counter(t for toks in self.tokens for t in set(toks))
        n = len(chunks)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}

    def search(self, query: str, k: int = 3) -> list[tuple[float, Chunk]]:
        q = tokenize(query)
        scored = []
        for chunk, toks in zip(self.chunks, self.tokens):
            tf = Counter(toks)
            score = 0.0
            for t in q:
                if t in tf:
                    f = tf[t]
                    score += self.idf.get(t, 0) * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * len(toks) / self.avg))
            if score > 0:
                scored.append((score, chunk))
        return sorted(scored, key=lambda x: x[0], reverse=True)[:k]
