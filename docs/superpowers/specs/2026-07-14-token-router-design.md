# Token Router — Design Spec

Date: 2026-07-14

## Goal

An HTTP endpoint that abstracts away "which LLM to call" from the caller. The
caller sends a prompt plus whichever provider API keys they have; the service
picks the best available model for that prompt, calls it via litellm, and
returns the response. Every call is traced in LangSmith (per-model token
usage, full call trace) without any extra work from the caller.

## Architecture

FastAPI app, single `POST /chat` endpoint.

Request:
```json
{
  "prompt": "string",
  "keys": { "groq": "...", "openrouter": "...", "gemini": "..." }
}
```

Response (200):
```json
{ "model_used": "groq/compound-beta", "content": "..." }
```

Flow:
1. Filter the model catalog down to entries whose provider has a key present
   in the request. No matching provider → `400`.
2. Build a compact description of the filtered catalog (id, tags,
   description) and send it + the user prompt to a fixed router-LLM for
   classification.
3. Router-LLM returns a chosen model id. If the call fails, or the id isn't
   in the filtered catalog, fall back to the first catalog entry matching a
   user-sent key (no smart routing, but still works).
4. Call `litellm.completion(model=chosen, api_key=<matching user key>,
   messages=[...])`. Provider/API errors are passed through as `502` with
   the litellm error message.
5. Return `{"model_used", "content"}`.

LangSmith tracing is always on, wired at the infra level (server env), not
per-request — the user never has to know it exists.

## Components

- **`catalog.yaml`** — replaces `config.yaml`. Per model entry: litellm model
  id (e.g. `groq/compound-beta`), provider key name (`groq`), tags (`fast`,
  `code`, `reasoning`, `cheap`, ...), one-line description. Maintained by
  hand as new models are added.
- **`catalog.py`** — loads the yaml; given a set of provider names present in
  a request, returns the filtered subset of catalog entries. Empty input →
  empty output.
- **`router_llm.py`** — takes the user prompt + filtered catalog, calls one
  fixed cheap router model (e.g. `groq/llama-3.1-8b-instant`) using a
  server-side house API key (from server `.env`, not the user's keys) to
  classify which catalog model best fits the prompt. Parses the response
  into a model id. On any failure (call error, hallucinated id not in
  catalog) falls back to the first filtered catalog entry.
- **`app.py`** — FastAPI app.
  - Sets LangSmith env vars and enables `litellm.success_callback =
    ["langsmith"]` once at startup.
  - `POST /chat`: validates request has at least one usable provider key
    (`400` if not) → catalog.py filter → router_llm.py selection →
    `litellm.completion` with the winning model and its matching user key →
    catches litellm exceptions and returns `502` with the provider error
    message → returns `{"model_used", "content"}` on success.
- **`router.py`** (existing file) — superseded by `app.py`. Either deleted or
  kept as a standalone manual smoke-test script once the FastAPI app exists.

## Error Handling

| Condition | Response |
|---|---|
| No keys sent, or none match any catalog provider | `400 {"error": "no supported provider keys"}` |
| Router-LLM call fails (house key missing, rate-limited, network) | Fallback: first catalog entry matching a user-sent key |
| Router-LLM returns a model id not in the filtered catalog | Same fallback as above |
| Chosen model's completion call fails (bad user key, provider error) | `502` with the litellm provider error message passed through |

## Testing

- `test_catalog.py` — filter logic: correct subset for a given provider set;
  empty set → empty list.
- `test_router_llm.py` — mock `litellm.completion`: valid id parsed
  correctly; hallucinated/invalid id triggers fallback; router call
  exception triggers fallback.
- `test_app.py` — FastAPI `TestClient`: no keys → `400`; valid key + mocked
  completion → `200` with expected shape; completion raises → `502`.
- Manual smoke test: real `curl` against the running server with one real
  key, confirm an actual response and that a trace appears in LangSmith.

## Out of Scope (for this spec)

- Persisting user keys server-side (keys are per-request only).
- Multi-turn conversation / chat history.
- Streaming responses.
- Auth/rate-limiting on the endpoint itself.
