# Worker/Agent Layer — Design

## Context

This is sub-project 1 of a 3-part restructure of Token-Router:

1. **Worker/agent layer** (this spec) — give the router a way to delegate a whole
   multi-step task to a model, not just a single completion.
2. Catalog/type expansion — add embedding/rerank/other non-chat model types to
   `catalog.yaml` with their own call paths.
3. MCP surface update — expose the worker layer (and any new model types) through
   `mcp_server.py` so Claude/Codex can call in and delegate.

Only (1) is in scope here. (2) and (3) get their own specs later.

## Problem

Today, `chat_core.handle_chat()` and the `delegate_task` MCP tool are one-shot:
prompt in, single `litellm.completion()` call out. There's no way to hand off a
task that requires multiple steps — read a file, run a command, iterate based on
the result, then report back. The goal is for a frontier model (Claude/Codex) to
delegate an entire task to a "worker" and get a finished result back, without
spending its own tokens on the intermediate steps.

## Architecture

A new module, `scripts/worker.py`, sitting alongside `chat_core.py` and reusing
its catalog/routing/rate-limit machinery. One entry point:

```python
def run_worker(
    task: str,
    working_dir: str,
    keys: dict[str, str] | None = None,
    task_type: str | None = None,
    max_iterations: int = 25,
) -> dict:
    ...
```

Returns `{"result": <str>, "models_used": [<model id>, ...], "iterations": <int>}`
on success, or raises one of the exceptions below on failure.

### Loop

1. Build the initial message list: a system message describing the task, the
   working directory, and the available tools; a user message containing `task`.
2. Filter the catalog to entries with `tool_calling` in `functions` (models
   without tool-calling can't drive this loop — reuses `filter_catalog` /
   `_narrow_by_task_type` from `catalog.py`/`chat_core.py`, with an added
   tool-calling filter).
3. Pick a model via the existing ranking (`_ranked_candidates`) and call
   `litellm.completion()` with `tools=WORKER_TOOLS` and the running message list.
4. If the model returns tool calls: execute each one (see Tools below), append
   the assistant message and each tool's result (or error) as a `tool` role
   message, and loop back to step 3.
5. If the model calls `finish_task`: loop ends, return its `summary`/`result`
   args as the worker's output.
6. If `max_iterations` is reached without a `finish_task` call: loop ends,
   raises `WorkerIncompleteError` with whatever transcript/partial state exists
   — fails closed rather than guessing at a result.
7. Same rate-limit/tpm pre-filtering as `handle_chat` applies on **every** turn
   (not just the first), so if the chosen model gets rate-limited mid-task, the
   next turn picks a different available model from the same filtered set. This
   means a single task can span multiple underlying models — that's expected
   and reflected in `models_used`.

### Tools

Four fixed tools, defined once as `WORKER_TOOLS` (OpenAI tool-calling schema):

- `read_file(path: str) -> str` — reads a file relative to `working_dir`.
- `write_file(path: str, content: str) -> str` — writes a file relative to
  `working_dir` (creates parent dirs as needed), returns a confirmation string.
- `run_shell(command: str) -> str` — runs a shell command with `cwd=working_dir`,
  returns combined stdout+stderr (truncated to a fixed length — 4000 chars — to
  avoid blowing up the message list on chatty commands) and the exit code.
- `finish_task(summary: str, result: str) -> None` — terminal tool; calling it
  ends the loop. Not actually executed against anything — its arguments are
  captured and returned as the worker's output.

No sandboxing beyond `cwd=working_dir` for shell and path-joining for file
tools — same trust level the caller already has (mirrors the "caller-specified
working directory" decision from brainstorming: this is not designed to run
untrusted tasks, it's designed to run tasks a human/caller already trusts, the
same way this codebase's own subagents operate directly on the repo).

All four tools are path-restricted to stay under `working_dir` (reject `path`
values that resolve outside it via `os.path.realpath` + prefix check) — not for
sandboxing against a malicious task, but to fail loudly on an obvious mistake
(e.g. a task prompt that causes the model to try to write outside its assigned
directory) rather than silently touching the wrong part of the filesystem.

### Errors

- `NoSupportedProviderError`, `AllModelsRateLimitedError`, `PromptTooLargeError`
  — reused as-is from `chat_core.py`. Same meaning: no candidate models available
  at all, given the current keys/task_type/tool_calling filter.
- `WorkerIncompleteError` (new) — `max_iterations` reached without
  `finish_task`. Carries the partial transcript so the caller can inspect how
  far it got.
- Tool *execution* errors (file not found, non-zero shell exit, path escapes
  `working_dir`) are **not** raised — they're caught and fed back to the model
  as the tool result (e.g. `"error: <message>"`), the same pattern any coding
  agent uses, so the model can self-correct on the next turn.

## Data Flow

```
caller (MCP tool, later) -> run_worker(task, working_dir)
  -> loop:
       filter_catalog + tool_calling filter + rate-limit/tpm prefilter
       -> pick model (reuses _ranked_candidates)
       -> litellm.completion(tools=WORKER_TOOLS)
       -> model returns tool_calls or finish_task
       -> execute tool(s) against working_dir, append results
  -> finish_task called -> return {result, models_used, iterations}
     OR max_iterations hit -> raise WorkerIncompleteError
```

## Testing

New `tests/test_worker.py`, following the existing mocking pattern in
`tests/test_chat_core.py` (mock `litellm.completion`, not real API calls):

- **Happy path**: scripted 2-turn response (`write_file` then `finish_task`) —
  assert the file was actually written to the test's tmp working dir, and the
  returned `result` matches `finish_task`'s args.
- **Multi-model fallback mid-task**: first turn's chosen model reports
  rate-limited (mock `rate_limiter.is_available`) after one tool call; assert
  the second turn picks a different model and `models_used` has two entries.
- **Runaway task**: every scripted turn returns another tool call, never
  `finish_task`; assert `WorkerIncompleteError` raised once `max_iterations` is
  hit, and that iterations actually stopped at the cap (no infinite loop).
- **Tool error is non-fatal**: scripted `read_file` on a missing path; assert
  the loop continues (error fed back as tool result) rather than raising, and
  a subsequent scripted `finish_task` still completes the task.
- **Path escape rejected**: scripted `write_file` with `path="../outside.txt"`;
  assert it's rejected as a tool error (not raised, not executed outside
  `working_dir`), consistent with the "fail loudly, don't raise" tool-error
  convention above.
- **No tool-calling models available**: filtered catalog has entries but none
  with `tool_calling`; assert `NoSupportedProviderError`.

## Out of Scope (deferred to later specs)

- Embedding/rerank/other non-chat model types — sub-project 2.
- Exposing this through `mcp_server.py` as a new MCP tool — sub-project 3.
- Async/polling execution — explicitly decided against for v1 (blocking call).
- Tool registry / pluggable tools beyond the fixed four.
- Web search/fetch tool access — explicitly deferred, file+shell only for v1.
- Per-task isolation (scratch dir, git worktree) — explicitly deferred, caller's
  own working directory is used directly for v1.
