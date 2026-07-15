# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**For full architecture (module-by-module breakdown), environment/provider
details, known gaps, and session history, see `MEMORY.md`.** This file only
holds what's needed every session.

## What this repo is

An LLM router: a caller sends a prompt (plus optional per-provider API keys and an
optional `task_type` hint), and the router picks the best available model from a
hand-curated, real-key-verified catalog, calls it via litellm, and returns the
response. Exposed two ways: a FastAPI `POST /chat` endpoint (`scripts/app.py`) and an
MCP tool `delegate_task` (`scripts/mcp_server.py`), both backed by the same core logic
in `scripts/chat_core.py`.

The point: let an orchestrator (Claude Code, or any caller) delegate subtasks to
free/cheap models instead of spending its own tokens, without the caller needing to
know which model to call.

All Python modules live in `scripts/`, all YAML config lives in `config/`. A root
`conftest.py` puts `scripts/` on `sys.path` for pytest; running a script directly
(`python scripts/whatever.py`) needs no such shim since Python already adds a
script's own directory to `sys.path[0]`.

## Verifying catalog changes (always follow this)

Every model id in `config/catalog.yaml` MUST be confirmed against the real API before
being added — model ids get renamed/deprecated and a hallucinated or stale id silently
breaks routing. Use `smoke_test_models.py` (real keys from `.env`, hits every catalog
entry with a trivial prompt) after any catalog edit:

```
.venv/Scripts/python.exe scripts/smoke_test_models.py [delay_seconds]
```

Rate limit numbers must come from the provider's own published docs (Groq's
`console.groq.com/docs/rate-limits`, OpenRouter's `openrouter.ai/docs/api-reference/limits`)
— never guessed. Leave `rpm`/`tpm`/`rpd`/`tpd` as `null` when unconfirmed rather than
estimating; the rate limiter and the tpm pre-filter both treat `null` as
"always available/fits".

Note: `litellm.completion()`'s `timeout` kwarg is not trustworthy for every
provider (confirmed unreliable for `nvidia_nim` — see `MEMORY.md`). If a smoke
test hangs, don't assume the model is broken before checking whether it's a
tooling issue.

## Environment

`.env` (gitignored) holds `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `GEMINI_API_KEY`,
`OLLAMA_API_KEY`, `NVIDIA_API_KEY`, plus `LANGSMITH_TRACING`/`LANGSMITH_API_KEY`/`LANGSMITH_ENDPOINT`
for tracing. See `MEMORY.md` for per-provider `api_base`/prefix quirks (Ollama
Cloud, NVIDIA).

Setup: `uv sync` inside `Token-router/` (uses `pyproject.toml`/`uv.lock` —
`requirements.txt` is stale/unused cruft, safe to ignore).

## Testing

```
.venv/Scripts/python.exe -m pytest -v
```

All tests mock `litellm.completion`/`select_model`/`rate_limiter.is_available` —
no real API calls in the test suite. Real-key verification is a separate, explicit
step (`smoke_test_models.py`), never folded into `pytest`.
