# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

An LLM router: a caller sends a prompt (plus optional per-provider API keys and an
optional `task_type` hint), and the router picks the best available model from a
hand-curated, real-key-verified catalog, calls it via litellm, and returns the
response. Exposed two ways: a FastAPI `POST /chat` endpoint (`app.py`) and an MCP
tool `delegate_task` (`mcp_server.py`), both backed by the same core logic in
`chat_core.py`.

The point: let an orchestrator (Claude Code, or any caller) delegate subtasks to
free/cheap models instead of spending its own tokens, without the caller needing to
know which model to call.

## Architecture

- **`catalog.yaml`** (gitignored — locally maintained, not versioned) — the model
  catalog. Each entry: `id` (litellm model string), `provider`, `tags`,
  `description`, `type` (chat/guardrail), `input_types`/`output_types`, `functions`
  (tool_calling/vision/reasoning/etc.), `rate_limits` (`rpm`/`tpm`/`rpd`/`tpd`, `null`
  when unconfirmed), `expires` (free-tier expiration date if known), `size`
  (small/medium/large/unknown — parameter-count tier, used by the router to avoid
  picking underpowered models for demanding tasks), `family` (links the same
  underlying model served by multiple providers, e.g. `gpt-oss-20b` on both Groq and
  OpenRouter, for cross-provider fallback).
- **`catalog.py`** — loads and filters the catalog by which provider keys are present.
  `load_catalog()`'s default path is resolved relative to this file (`__file__`), not
  the caller's cwd — important because this module gets imported from other
  projects' scripts (e.g. `Frontend/scripts/regenerate_via_router.py`).
- **`router_llm.py`** — a small fixed model (`groq/llama-3.1-8b-instant`) picks the
  best catalog entry for a prompt from the filtered list. The prompt tells it each
  candidate's `size` tier and instructs it to prefer medium/large models for
  demanding tasks. Falls back to the first candidate if the call fails or it
  hallucinates an id not in the catalog.
- **`rate_limiter.py`** — sliding-window tracker (rpm/rpd only, not tpm/tpd — see
  chat_core.py's pre-filter for tpm), persisted to `rate_limiter_state.json`
  (gitignored, next to `.env`) so usage survives a process restart instead of
  re-learning each provider's limits via a fresh 429. Loads + prunes stale entries
  on import, saves on every `record_call`; skipped entirely under pytest
  (`PYTEST_CURRENT_TEST` env check) so the test suite stays pure in-memory.
  OpenRouter's free-tier models share ONE bucket per account
  (`openrouter:free_shared`) — verified against OpenRouter's docs, not per-model.
  Groq/Gemini/Ollama models get independent buckets.
- **`chat_core.py`** — `handle_chat()`, the shared core: merges caller-supplied keys
  over server `.env` defaults, filters the catalog by provider/task_type, **pre-filters
  by rate-limit availability AND token-budget fit** (`_prefilter_candidates`/
  `_fits_tpm`, using `litellm.token_counter()` to estimate the prompt's size against
  each candidate's `tpm` before the router-LLM ever sees it — added after
  `groq/openai/gpt-oss-120b` rejected a ~10,758-token prompt with its 8000 tpm cap),
  ranks the survivors (router's pick, then same-`family` entries on other providers,
  then the rest), tries each until one succeeds or all are exhausted. Raises
  `PromptTooLargeError` when every candidate fails specifically on the tpm check,
  `AllModelsRateLimitedError` when rpm/rpd exhaustion is involved instead.
- **`app.py`** / **`mcp_server.py`** — thin wrappers mapping `chat_core`'s exceptions
  to HTTP status codes (400/413/429/502) / MCP error responses respectively.

## Verifying catalog changes

Every model id in `catalog.yaml` MUST be confirmed against the real API before being
added — model ids get renamed/deprecated and a hallucinated or stale id silently
breaks routing. Use `smoke_test_models.py` (real keys from `.env`, hits every catalog
entry with a trivial prompt) after any catalog edit:

```
.venv/Scripts/python.exe smoke_test_models.py [delay_seconds]
```

Rate limit numbers must come from the provider's own published docs (Groq's
`console.groq.com/docs/rate-limits`, OpenRouter's `openrouter.ai/docs/api-reference/limits`)
— never guessed. Leave `rpm`/`tpm`/`rpd`/`tpd` as `null` when unconfirmed rather than
estimating; the rate limiter and the tpm pre-filter both treat `null` as
"always available/fits".

## Environment

`.env` (gitignored) holds `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `GEMINI_API_KEY`,
`OLLAMA_API_KEY`, plus `LANGSMITH_TRACING`/`LANGSMITH_API_KEY`/`LANGSMITH_ENDPOINT`
for tracing. Ollama Cloud models use the `ollama_chat/<name>` litellm prefix with
`api_base="https://ollama.com"` (passed explicitly in `smoke_test_models.py`; not
yet wired into `chat_core.py`'s actual call path — only `PROVIDER_KEY_ENV` knows
about the `ollama` provider so far, the api_base override still needs adding to
`chat_core.py` itself before real `/chat` requests can reach Ollama Cloud). litellm
auto-loads `.env` on import, but `chat_core.py` also loads it explicitly by absolute
path (`load_dotenv(..., override=True)`) — needed because litellm's automatic
dotenv discovery is call-stack/cwd-dependent and can pick up a *different* `.env`
(e.g. `Frontend/.env`) when this code is imported from another project's script.

Setup: `uv sync` inside `Token-router/` (uses `pyproject.toml`/`uv.lock` — the
`requirements.txt` here is stale/unused, predates the `uv` migration, kept only
because pyproject.toml's `readme` field points at it... actually points at README.md;
requirements.txt is just leftover cruft, safe to ignore).

## Testing

```
.venv/Scripts/python.exe -m pytest -v
```

All tests mock `litellm.completion`/`select_model`/`rate_limiter.is_available` —
no real API calls in the test suite. Real-key verification is a separate, explicit
step (`smoke_test_models.py`), never folded into `pytest`.

## Current state / where to resume

Core router + Task 1 (deterministic pre-filter) + Frontend integration
(`regenerate_via_router.py`, `generate_forced_model.py`) are done and committed
(see git log). The original plan's Task 3 (vision review-and-revise loop) is still
not started; full code for it is written out in
`C:\Users\sriva\.claude\plans\router-prefilter-and-review-loop.md`, Task 3, if
resuming that thread — needs `playwright` added as a dependency first (Task 2).

**This session (2026-07-14/15) added, on top of that:**
- `catalog.yaml` rebuilt from 60 speculative entries (scraped from
  `ollama.com/search?c=cloud` and a user-pasted Gemini rate-limit table) down to 39
  **smoke-tested-working** ones. See the header comments above the Ollama and
  Gemini sections in `catalog.yaml` for exactly what was removed and why (paid-tier
  gating, deprecated ids, wrong size tags). `Token-router/INSPIRATIONS.md` documents
  routing/optimization ideas pulled from the 4 hackathon repos under
  `inspirations/tokens/`, each tagged with its source repo.
- `ollama` added to `chat_core.py`'s `PROVIDER_KEY_ENV` — was previously entirely
  unwired, meaning no Ollama model could ever have been called even though it was
  in the catalog. **Still incomplete**: `chat_core.py`'s actual `litellm.completion()`
  call (line ~98) doesn't pass `api_base="https://ollama.com"` for the `ollama`
  provider, so real `/chat` requests to any `ollama_chat/*` model will still fail
  (only `smoke_test_models.py` has the api_base fix so far). Fix this before trusting
  Ollama routing in production.
- `rate_limiter.py` gained disk persistence (see Architecture section above).

**Known gap, not yet worked on (flagged in conversation, not started):** the
router's own LLM call (`router_llm.py`) stuffs the *entire* filtered catalog into
the prompt every time — at 39 entries that's ~2,120 tokens, eating over a third of
`groq/llama-3.1-8b-instant`'s own 6,000 tpm cap before the user's actual prompt is
even added, and `chat_core.py`'s tpm pre-filter never checks the router call itself,
only the candidate models it might pick. Also no accuracy/success-rate tracking —
a bad routing pick just silently falls back to `filtered_catalog[0]`. Idea (not yet
implemented): replace the "send the whole catalog to an LLM" step with a free
regex/category classifier first (pattern used by 2 of the 4 inspiration repos, see
`INSPIRATIONS.md` sections 2 and 5), demoting `router_llm.py` to a fallback for
ambiguous cases only; optionally add persisted per-category success-rate tracking
(`INSPIRATIONS.md` section 2, `learning_router.py`-style) so bad picks self-correct.
