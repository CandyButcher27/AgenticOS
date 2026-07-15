# Token-router

Project's `CLAUDE.md` has the always-load essentials (what this repo is, the
catalog-verification rule, build/test commands). This file has the full
architecture breakdown, environment details, and session-by-session history —
read it when you need the detail, not by default.

## Architecture

- **`config/catalog.yaml`** (gitignored — locally maintained, not versioned) —
  the model catalog. Each entry: `id` (litellm model string), `provider`,
  `tags`, `description`, `type` (chat/guardrail), `input_types`/`output_types`,
  `functions` (tool_calling/vision/reasoning/etc.), `rate_limits`
  (`rpm`/`tpm`/`rpd`/`tpd`, `null` when unconfirmed), `expires` (free-tier
  expiration date if known), `size` (small/medium/large/unknown —
  parameter-count tier, used by the router to avoid picking underpowered
  models for demanding tasks), `family` (links the same underlying model
  served by multiple providers, e.g. `gpt-oss-20b` on both Groq and
  OpenRouter, for cross-provider fallback).
- **`scripts/catalog.py`** — loads and filters the catalog by which provider
  keys are present. `load_catalog()`'s default path is resolved relative to
  this file (`__file__`, up one level into `config/`), not the caller's cwd —
  important because this module gets imported from other projects' scripts
  (e.g. `Frontend/scripts/regenerate_via_router.py`, which points `sys.path`
  at `Token-router/scripts`).
- **`scripts/router_llm.py`** — a small fixed model
  (`groq/llama-3.1-8b-instant`) picks the best catalog entry for a prompt from
  the filtered list. The prompt tells it each candidate's `size` tier and
  instructs it to prefer medium/large models for demanding tasks. Falls back
  to the first candidate if the call fails or it hallucinates an id not in the
  catalog.
- **`scripts/rate_limiter.py`** — sliding-window tracker (rpm/rpd only, not
  tpm/tpd — see chat_core.py's pre-filter for tpm), persisted to
  `rate_limiter_state.json` (gitignored, next to `.env`) so usage survives a
  process restart instead of re-learning each provider's limits via a fresh
  429. Loads + prunes stale entries on import, saves on every `record_call`;
  skipped entirely under pytest (`PYTEST_CURRENT_TEST` env check) so the test
  suite stays pure in-memory. OpenRouter's free-tier models share ONE bucket
  per account (`openrouter:free_shared`) — verified against OpenRouter's docs,
  not per-model. Groq/Gemini/Ollama/NVIDIA models get independent buckets.
- **`scripts/chat_core.py`** — `handle_chat()`, the shared core: merges
  caller-supplied keys over server `.env` defaults, filters the catalog by
  provider/task_type, **pre-filters by rate-limit availability AND
  token-budget fit** (`_prefilter_candidates_by_ratelimit_and_tpm`/
  `_fits_tpm`, using `litellm.token_counter()` to estimate the prompt's size
  against each candidate's `tpm` before the router-LLM ever sees it — added
  after `groq/openai/gpt-oss-120b` rejected a ~10,758-token prompt with its
  8000 tpm cap), ranks the survivors (router's pick, then same-`family`
  entries on other providers, then the rest), tries each until one succeeds or
  all are exhausted. Raises `PromptTooLargeError` when every candidate fails
  specifically on the tpm check, `AllModelsRateLimitedError` when rpm/rpd
  exhaustion is involved instead.
- **`scripts/app.py`** / **`scripts/mcp_server.py`** — thin wrappers mapping
  `chat_core`'s exceptions to HTTP status codes (400/413/429/502) / MCP error
  responses respectively.
- **Repo layout**: all Python modules live in `scripts/`, all YAML config
  lives in `config/`. A root `conftest.py` puts `scripts/` on `sys.path` for
  pytest; running a script directly (`python scripts/whatever.py`) needs no
  such shim since Python already adds a script's own directory to
  `sys.path[0]`.

## Environment

`.env` (gitignored) holds `GROQ_API_KEY`, `OPENROUTER_API_KEY`,
`GEMINI_API_KEY`, `OLLAMA_API_KEY`, `NVIDIA_API_KEY`, plus
`LANGSMITH_TRACING`/`LANGSMITH_API_KEY`/`LANGSMITH_ENDPOINT` for tracing.

- **Ollama Cloud**: `ollama_chat/<name>` litellm prefix, needs an explicit
  `api_base="https://ollama.com"` (passed in `smoke_test_models.py`; **not
  yet wired into `chat_core.py`'s actual call path** — only
  `PROVIDER_KEY_ENV` knows about the `ollama` provider so far, the api_base
  override still needs adding to `chat_core.py` itself before real `/chat`
  requests can reach Ollama Cloud).
- **NVIDIA**: `nvidia_nim/<org>/<model>` litellm prefix, api_base auto-resolves
  to `https://integrate.api.nvidia.com/v1` — no override needed, confirmed via
  `litellm.get_llm_provider()`. Fully wired, works out of the box.
- litellm auto-loads `.env` on import, but `chat_core.py` also loads it
  explicitly by absolute path (`load_dotenv(..., override=True)`) — needed
  because litellm's automatic dotenv discovery is call-stack/cwd-dependent and
  can pick up a *different* `.env` (e.g. `Frontend/.env`) when this code is
  imported from another project's script.

Setup: `uv sync` inside `Token-router/` (uses `pyproject.toml`/`uv.lock` — the
`requirements.txt` here is stale/unused, predates the `uv` migration, kept
only because pyproject.toml's `readme` field points at it... actually points
at README.md; requirements.txt is just leftover cruft, safe to ignore).

## Known gaps (not yet worked on)

- **Router-LLM prompt bloat**: `router_llm.py` stuffs the *entire* filtered
  catalog into the prompt every time. The catalog grew from 39 to 77 entries
  this reporting period (38 of them NVIDIA), so this is materially worse than
  when it was first flagged — at 39 entries it was already ~2,120 tokens,
  eating over a third of `groq/llama-3.1-8b-instant`'s own 6,000 tpm cap
  before the user's actual prompt is even added. `chat_core.py`'s tpm
  pre-filter never checks the router call itself, only the candidate models
  it might pick. No accuracy/success-rate tracking either — a bad routing
  pick just silently falls back to `filtered_catalog[0]`.
  Idea (not implemented): replace "send the whole catalog to an LLM" with a
  free regex/category classifier first (pattern used by 2 of the 4
  inspiration repos — see git history for `INSPIRATIONS.md`, sections 2 and
  5, before it was deleted from the repo root), demoting `router_llm.py` to a
  fallback for ambiguous cases only; optionally add persisted per-category
  success-rate tracking (`learning_router.py`-style) so bad picks
  self-correct. This has gone from a "could" to a "should."
- **Ollama Cloud api_base**: see Environment section above — real `/chat`
  requests to `ollama_chat/*` models will fail in production until
  `chat_core.py` passes `api_base` for that provider.
- **NVIDIA candidates worth re-testing**: a dozen chat-capable NVIDIA models
  timed out repeatedly during smoke-testing (even at 45-60s) despite
  appearing on the free-tier list — not necessarily permanently broken, see
  the exclusion list in `config/catalog.yaml`'s NVIDIA section header comment.
- **Tooling gotcha**: `litellm.completion()`'s own `timeout` kwarg is not
  trustworthy for the `nvidia_nim` provider — several models hung
  indefinitely through litellm's client regardless of the timeout passed, and
  even `subprocess.run(..., timeout=N)` didn't reliably bound total
  wall-clock time. Raw `requests.post()` against
  `.../v1/chat/completions` with an explicit `(connect, read)` timeout tuple
  was the only method that actually enforced a bound. If extending
  `smoke_test_models.py` to cover NVIDIA, don't route those calls through
  `litellm.completion()` without independently re-verifying the timeout is
  honored.

## Planned restructure (in progress, 2026-07-16)

Three-part plan to turn this from "route one prompt to one model" into "delegate
a whole task to a worker, plus support non-chat model types." Spec docs live in
`docs/superpowers/specs/`.

1. **Worker/agent layer** — spec written and committed
   (`docs/superpowers/specs/2026-07-16-worker-agent-layer-design.md`), not yet
   implemented. New `scripts/worker.py`: a `run_worker(task, working_dir, ...)`
   loop that reuses the existing catalog/router/rate-limit machinery but gives
   the model 4 tools (`read_file`, `write_file`, `run_shell`, `finish_task`)
   and iterates until `finish_task` is called or `max_iterations` is hit.
   Blocking call, caller-supplied working directory (no sandboxing beyond
   path-restriction to that directory), file+shell tools only (no web access
   in v1). See the spec for full design/error-handling/testing plan.
2. **Catalog/type expansion** (not yet spec'd) — add embedding/rerank/other
   non-chat model types to `catalog.yaml` with their own litellm call paths
   (`litellm.embedding()`, `litellm.rerank()`, etc.), distinct from the
   `chat`/`guardrail` types the catalog currently supports.
3. **MCP surface update** (not yet spec'd) — expose the worker layer (and any
   new model types from #2) through `scripts/mcp_server.py` so Claude/Codex
   can delegate whole tasks, not just single completions, through one MCP
   connector.

## Session history

### 2026-07-14/15
- Core router + deterministic pre-filter + Frontend integration
  (`regenerate_via_router.py`, `generate_forced_model.py`) done and committed.
  The original plan's vision review-and-revise loop task is still not started;
  full code for it is written out in
  `C:\Users\sriva\.claude\plans\router-prefilter-and-review-loop.md`, if
  resuming that thread — needs `playwright` added as a dependency first.
- `catalog.yaml` rebuilt from 60 speculative entries (scraped from
  `ollama.com/search?c=cloud` and a user-pasted Gemini rate-limit table) down
  to 39 **smoke-tested-working** ones. See the header comments above the
  Ollama and Gemini sections in `config/catalog.yaml` for exactly what was
  removed and why (paid-tier gating, deprecated ids, wrong size tags).
- `ollama` added to `chat_core.py`'s `PROVIDER_KEY_ENV` — was previously
  entirely unwired, meaning no Ollama model could ever have been called even
  though it was in the catalog. Still incomplete (see Known gaps above).
- `rate_limiter.py` gained disk persistence.

### 2026-07-16
- `nvidia` added to `chat_core.py`'s `PROVIDER_KEY_ENV` (`NVIDIA_API_KEY`).
- 38 models added to `catalog.yaml` from build.nvidia.com's free preview
  endpoint. Real `org/model` ids were pulled from `GET
  https://integrate.api.nvidia.com/v1/models` (matched against the site's
  slugs) rather than scraped per-page. Full exclusion list and reasons in the
  header comment above the NVIDIA section in `config/catalog.yaml`.
- Repo reorganized: Python modules moved into `scripts/`, YAML config into
  `config/`, root `conftest.py` added for pytest's `sys.path` shim, stray
  root-level docs (`INSPIRATIONS.md`, `inspirations-token-optimisers.md`,
  `problems+solutions.md`) removed.
- Worker/agent layer designed (see Planned restructure above) — spec written,
  not yet implemented.
- This file (`MEMORY.md`) and `CLAUDE.md` restructured: `CLAUDE.md` now holds
  only the always-need essentials (what this repo is, catalog-verification
  rule, build/test commands); this file holds the full architecture,
  environment, and history detail. Reason: `CLAUDE.md` loads into every
  session's context automatically, `MEMORY.md` doesn't — keeping the
  always-loaded file thin saves tokens every session.
