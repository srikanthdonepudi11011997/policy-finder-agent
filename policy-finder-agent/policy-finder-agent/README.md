# Policy Finder Agent

An open-source agent that reads a folder of company policy documents, works out the **latest approved version** of each policy, and answers questions from that version only, with a citation.

## How it works
1. **Ingest**: reads `.txt`, `.md`, `.pdf`, `.docx` files.
2. **Metadata**: pulls policy name, version, effective date, status, owner from the header (falls back to the filename, e.g. `TravelPolicy_v3.2_2026-01-01.pdf`).
3. **Latest**: keeps only `Approved` versions already in effect, then picks the newest effective date, then the highest version (`1.10` > `1.9`).
4. **Search**: BM25 over chunks of the latest versions only.
5. **Answer**: returns the relevant text (or an LLM answer via Ollama) with file, version and date.

Drafts, retired and future-dated versions are never treated as current policy.

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export PYTHONPATH=src                                # Windows: set PYTHONPATH=src

python -m policy_agent.cli data/sample_policies list
python -m policy_agent.cli data/sample_policies versions "Travel Policy"
python -m policy_agent.cli data/sample_policies ask "What is the hotel limit for travel?"

streamlit run app.py        # web UI
pytest                      # run tests
```

## Optional: local LLM answers (Ollama)
```bash
ollama pull llama3
export OLLAMA_MODEL=llama3
```

## Policy file header format
```
Policy: Travel Policy
Version: 3.0
Effective Date: 2026-01-01
Status: Approved        # Approved | Draft | Retired (missing = Approved)
Owner: Finance
```

## Roadmap
- Semantic search with ChromaDB + sentence-transformers
- Version-to-version change summaries
- Alerts when a new version is published
- SharePoint / Google Drive / Object Storage connectors

## Oracle AI Agent Studio version
The same design maps to an agent with a document (RAG) tool and instructions to ignore Drafts, pick the newest effective date, and cite version and date. See the build guide.

## License
MIT. Use only sample or public policies in this repo, never real company documents.
