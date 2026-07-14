# RagForge

Notes/planning folder for the RagForge adaptive-retrieval project (code repo not yet created, see RAG.md for planned local path).

## Contents
- `RAG.md` — PRD (architecture, modules, API, benchmarks)
- `RagForge_Level_Roadmap.md` — original 12-level learning curriculum (source)
- `RagForge_Combined.md` — merged, per-level guide: what to build / not allowed / final product per level, plus papers + product context
- `download_eval_datasets.py` — pulls eval datasets into `data/` (gitignored)
- `data/` — gitignored, holds downloaded datasets:
  - `scifact/` — corpus.jsonl (5183 docs) + queries.jsonl (1109) + qrels.jsonl (339): real shared corpus, use for Levels 1-5, 8-9 retrieval metrics (Recall@k/MRR/NDCG)
  - `squad/eval.jsonl` — 237 rows, per-question context (not shared corpus), for answer-grounding checks
  - `hotpotqa/eval.jsonl` — 300 rows, multi-hop QA with per-question context_docs, for Level 6 (decomposition) and Level 10 (graph)
- `.gitignore` — ignores `.venv/`, `data/`, `*.md` (all markdown notes stay local-only)

## Status
As of 2026-07-15: no RAG code written yet. Eval datasets in place. Next: start Level 1 (basic RAG from scratch) per `RagForge_Combined.md`.
