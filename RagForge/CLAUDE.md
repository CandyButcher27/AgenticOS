# CLAUDE.md

This file provides guidance to Claude Code when working in this folder.

## What this is

Planning + eval-data folder for **RagForge**, an adaptive retrieval-augmented
generation framework built as a learning project via a 12-level curriculum
(one new RAG concept per level). No RAG code lives here yet — this folder
holds the curriculum, PRD, and downloaded eval datasets. The actual code repo
will live at `C:\Users\sriva\Documents\codestuff\projects\ragforge` once
Level 1 starts.

## Mentor rule (critical, overrides default helpfulness)

Do NOT generate the RAG implementation. Review, explain, debug, and critique
the user's own code only. Never replace their code with a complete
implementation unless explicitly asked. Goal is the user's understanding,
not fast completion. Mechanical tasks (downloading datasets, writing eval
harness scaffolding they didn't ask you to avoid, git operations) are fine —
the ban is specifically on writing the retrieval/RAG logic itself.

## Layout

- `RagForge_Combined.md` — the source of truth: per-level build guide (what
  to build, what's banned, final product per level), full paper reading
  list, product context. Local-only (gitignored).
- `RAG.md`, `RagForge_Level_Roadmap.md` — original source notes the combined
  file was merged from. Local-only (gitignored).
- `download_eval_datasets.py` — pulls eval datasets into `data/`. Tracked in
  git (it's code, not notes).
- `data/` — gitignored. Downloaded datasets:
  - `scifact/` — real shared corpus (5183 docs) + queries (1109) + qrels
    (339). Use for Levels 1-5, 8-9 retrieval metrics (Recall@k/MRR/NDCG).
  - `squad/eval.jsonl` — per-question context, not a shared corpus. Use for
    answer-grounding checks.
  - `hotpotqa/eval.jsonl` — multi-hop QA with per-question context_docs. Use
    for Level 6 (decomposition) and Level 10 (graph).
- `.venv/` — gitignored, holds `datasets` lib for the download script.

## Notes

- All `*.md` except this file are gitignored — they're personal planning
  notes, not meant to be versioned.
- `MEMORY.md` here is a project-local note, separate from the global
  `~/.claude` memory system.
