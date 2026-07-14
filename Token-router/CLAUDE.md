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
- **`rate_limiter.py`** — in-memory sliding-window tracker (rpm/rpd only, not
  tpm/tpd — see chat_core.py's pre-filter for tpm). OpenRouter's free-tier models
  share ONE bucket per account (`openrouter:free_shared`) — verified against
  OpenRouter's docs, not per-model. Groq models get independent buckets.
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

`.env` (gitignored) holds `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, plus
`LANGSMITH_TRACING`/`LANGSMITH_API_KEY`/`LANGSMITH_ENDPOINT` for tracing. litellm
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

This project is mid-implementation of a plan at
`C:\Users\sriva\.claude\plans\router-prefilter-and-review-loop.md` (design spec at
`docs/superpowers/specs/2026-07-14-router-prefilter-and-review-loop-design.md`).

**Done:**
- Core router (catalog, router_llm, rate_limiter, chat_core, app.py, mcp_server.py)
- `size` field added to every catalog entry, router prompt updated to weigh it
- `family` field + cross-provider fallback (verified live: gpt-oss-20b via Groq
  when OpenRouter's copy is rate-limited)
- `keys` made optional (falls back to server `.env` via `SERVER_KEYS`)
- **Task 1 of the plan (deterministic pre-filter)** — done, tested, 28/28 passing.
  `PromptTooLargeError` wired through `app.py` (413) and `mcp_server.py`.
- Frontend integration: `Frontend/scripts/regenerate_via_router.py` (one-shot
  design.md → 3 files) and `Frontend/scripts/generate_forced_model.py` (same, but
  forces a specific model instead of letting the router pick) both work, used to
  regenerate `Frontend/websites/posthog/` and produce comparison builds at
  `posthog-sonnet/` and `posthog-nemotron-ultra/`.

**Not started:**
- **Task 2** — add `playwright` as a Token-router dependency (needed for Task 3's
  screenshot rendering). Not yet in `pyproject.toml`.
- **Task 3** — vision review-and-revise loop: `--review` flag on
  `regenerate_via_router.py`, renders the generated site, sends a screenshot to a
  vision-capable catalog model for critique, feeds critique back for a revision
  pass, repeats 3x. Full code is written out in the plan file, Task 3.
- **Task 4** was "write this CLAUDE.md" — superseded by this file existing now.

Resume by reading the plan file directly and continuing from Task 2. No worktree was
used — work happened directly on `feat/token-router`. Uncommitted changes exist for
Task 1's files (`app.py`, `catalog.py`, `chat_core.py`, `mcp_server.py`,
`router_llm.py`, `smoke_test_models.py`, `tests/test_app.py`,
`tests/test_chat_core.py`, `pyproject.toml`, `uv.lock`) — nothing has been committed
since the `chore: add real-key smoke test script and catalog source notes` commit.
`conftest.py` and `new_models.md` were deleted at some point during Task 1's
implementation (tests still pass without `conftest.py` — verify why before assuming
it's safe to leave deleted, in case pytest's rootdir-discovery behavior changes).
