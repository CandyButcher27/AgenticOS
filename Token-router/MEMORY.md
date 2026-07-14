# Token-router

Project has its own `CLAUDE.md` — read that first, it has the up-to-date architecture and current-state notes. Python app: `app.py`, `chat_core.py`, `catalog.py`/`catalog.yaml`, `router_llm.py`, `rate_limiter.py`, `mcp_server.py`. `catalog.yaml` and `rate_limiter_state.json` are gitignored, locally maintained. `INSPIRATIONS.md` documents routing ideas pulled from the 4 hackathon repos under `inspirations/tokens/`, each tagged with source repo.

## Status as of 2026-07-15
- Catalog rebuilt to 39 smoke-tested-working models across Groq/OpenRouter/Gemini/Ollama (was 60 speculative entries before smoke testing removed the broken ones).
- `ollama` provider wired into `chat_core.py`'s key lookup, but the actual completion call still doesn't pass `api_base` for Ollama Cloud — real `/chat` requests to Ollama models will fail until that's fixed (only the smoke test script has the fix).
- `rate_limiter.py` now persists to disk (`rate_limiter_state.json`) so it survives process restarts instead of re-learning provider limits via a fresh 429 each time.
- Known open gap: `router_llm.py` sends the whole catalog to a small Groq model on every call (~2,120 tokens at 39 entries, against that model's own 6,000 tpm cap) with no accuracy tracking — see CLAUDE.md's "Known gap" section for the fix idea (free classifier first, LLM router as fallback only).
