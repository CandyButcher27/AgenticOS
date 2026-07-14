# Token Router

An LLM router: send a prompt, get a response from the best available free/cheap
model — no need to know which model or provider to call. Built to let an
orchestrator (e.g. Claude Code) delegate subtasks without spending its own tokens.

## Quick start

```bash
uv sync
uv run pytest -v          # unit tests, no real API calls
```

Set real provider keys in `.env` (not committed — see `.env` for the expected
vars: `GROQ_API_KEY`, `OPENROUTER_API_KEY`, `GEMINI_API_KEY`, plus
`LANGSMITH_*` for tracing). Then:

```bash
.venv/Scripts/python.exe smoke_test_models.py     # verify every catalog entry is real and callable
```

## Two ways to use it

**HTTP:**
```bash
.venv/Scripts/python.exe -m uvicorn app:app --port 8000
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is the capital of France?"}'
```
(`keys` is optional — omit it and it falls back to `.env`.)

**MCP tool** (for Claude Code or any MCP client):
```bash
claude mcp add token-router -- "<path-to>/.venv/Scripts/python.exe" "<path-to>/mcp_server.py"
```
Exposes `delegate_task(prompt, keys=None, task_type=None)`.

## How routing works

1. Filter the catalog (`catalog.yaml`, gitignored/locally maintained) to models
   whose provider you have a key for (server `.env` or per-request).
2. Pre-filter out anything currently rate-limited or whose token-per-minute cap
   can't fit this prompt.
3. A small router-LLM picks the best remaining model, weighing each candidate's
   `size` tier against how demanding the prompt looks.
4. If the pick fails, fall back through: the same model on a different provider
   (if `family`-linked), then the rest of the filtered catalog.

See `CLAUDE.md` for full architecture and current implementation status.

## Not yet built

A vision-based review-and-revise loop (render output → critique → revise) is
designed but not implemented — see `CLAUDE.md`'s "Current state / where to
resume" section and the plan at
`C:\Users\sriva\.claude\plans\router-prefilter-and-review-loop.md`.
