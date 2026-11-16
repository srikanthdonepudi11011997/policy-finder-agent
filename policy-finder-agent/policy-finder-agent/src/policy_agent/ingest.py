"""Load policy files (.txt, .md, .pdf, .docx) from a folder."""

from __future__ import annotations

import os

from .metadata import extract_metadata
from .models import PolicyDoc

SUPPORTED = (".txt", ".md", ".pdf", ".docx")


def read_text(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in (".txt", ".md"):
        with open(path, encoding="utf-8", errors="ignore") as f:
            return f.read()
    if ext == ".pdf":
        from pypdf import PdfReader  # optional dependency

        return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)
    if ext == ".docx":
        from docx import Document  # optional dependency (python-docx)

        return "\n".join(p.text for p in Document(path).paragraphs)
    raise ValueError(f"Unsupported file type: {path}")


def load_policies(folder: str) -> list[PolicyDoc]:
    docs: list[PolicyDoc] = []
    for root, _, files in os.walk(folder):
        for name in sorted(files):
            if not name.lower().endswith(SUPPORTED):
                continue
            path = os.path.join(root, name)
            try:
                text = read_text(path)
            except Exception as exc:  # keep going if one file is unreadable
                print(f"[warn] skipped {path}: {exc}")
                continue
            docs.append(PolicyDoc(path=os.path.relpath(path, folder), text=text, **extract_metadata(text, path)))
    return docs
