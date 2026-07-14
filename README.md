# AgenticOS

Monorepo for a collection of independent projects, most still early-stage or planning-only.

## Projects

- **`Token-router/`** — an LLM router. A caller (e.g. Claude Code) sends a prompt, the
  router picks the best available free/cheap model from a hand-curated, real-key-verified
  catalog (Groq, OpenRouter, Gemini, Ollama Cloud), calls it via litellm, and returns the
  response. Exposed as a FastAPI endpoint and an MCP tool. See `Token-router/CLAUDE.md` for
  architecture and current state.
- **`Frontend/`** — website/design generation project, driven through Token-router. See
  `Frontend/README.md` and `Frontend/CLAUDE.md`.
- **`RagForge/`** — planning-only so far (no code yet): a 12-level adaptive-retrieval RAG
  curriculum project. See `RagForge/RAG.md` for the PRD.
- **`CyberSecrity/`**, **`Scraper/`** — empty, placeholders for future work.
- **`inspirations/`** — reference repos pulled in for study, not part of this codebase's
  own logic. `inspirations/tokens/` (4 hackathon token-efficient-routing submissions,
  summarized in `Token-router/INSPIRATIONS.md`), `inspirations/cybersec/`,
  `inspirations/trading/`.
- **`docs/`** — design specs and planning docs (`docs/superpowers/specs/`), plus
  superpowers-skill working state (`docs/.superpowers/`).
- **`graphify-out/`** — generated knowledge-graph output from the `graphify` skill
  (`graph.json`, `GRAPH_REPORT.md`), gitignored.
- **`output/`** — stray test artifact from an early AgenticOS orchestrator run
  (`output/00cd8e45/`), stub content generated with no API key set. Not meaningful,
  safe to delete.

Each project folder that has code keeps its own `CLAUDE.md` with real architecture detail —
read that before working inside it. This file is just the map.
