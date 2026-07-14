# Router Pre-Filter & Vision Review Loop — Design Spec

Date: 2026-07-14

## Goal

Two follow-on problems surfaced while using the Token-router to regenerate
Frontend site stubs:

1. The router-LLM can pick a model that structurally cannot serve the
   request — e.g. `groq/openai/gpt-oss-120b` failed with a real Groq 429
   because the prompt (~10,758 tokens) exceeded its 8000 TPM free-tier cap.
   The router had no way to know this before picking.
2. Free-model output quality varies a lot by model size (confirmed:
   `poolside/laguna-xs-2.1` (small) produced noticeably weaker output than
   `nemotron-3-ultra-550b-a55b` (medium/large) from the same design spec,
   and even the good free-model output still lacked the polish of a
   Claude Sonnet subagent doing the same task). A visual critique-and-revise
   loop should close some of that gap without spending Claude tokens.

This spec covers both: a deterministic pre-filter step in the router
(`Token-router`), and an opt-in vision review loop in the Frontend
regeneration script (`Frontend/scripts/regenerate_via_router.py`).

## Part 1: Deterministic Pre-Filter (Token-router)

### Where it fits

In `chat_core.handle_chat`, between `_narrow_by_task_type` and
`_ranked_candidates`/`select_model`. Today the router-LLM sees every
catalog entry matching the caller's keys and task_type, with no awareness
of whether a given model can actually take the request right now. The
pre-filter narrows that list first.

### What it checks

For each candidate entry:
1. **rpm/rpd availability** — `rate_limiter.is_available(entry)`, the same
   check already used post-pick for fallback. Moving it earlier means the
   router never recommends something already rate-limited.
2. **tpm fit (new)** — estimate the prompt's token count via
   `litellm.token_counter(model=entry["id"], messages=[...])` and compare
   against `entry["rate_limits"]["tpm"]`. If `tpm` is `null` (unconfirmed,
   e.g. `groq/compound-beta`), treat as always-fitting — consistent with
   the existing permissive-default pattern for unconfirmed limits
   elsewhere in the catalog.

An entry survives the pre-filter only if it passes both checks.

### Empty result handling

If the pre-filter empties the candidate list, determine why before
raising:
- If every excluded entry failed specifically on the tpm check (regardless
  of rpm/rpd state) → raise `PromptTooLargeError` (new exception in
  `chat_core.py`), message includes which models were tried and their tpm
  caps.
- Otherwise (at least one exclusion was due to rpm/rpd) → raise the
  existing `AllModelsRateLimitedError`, unchanged.

### What stays the same

- The existing post-pick fallback (`rate_limiter.is_available` check
  inside `_ranked_candidates`/`handle_chat`) is **not removed** — it stays
  as a cheap safety net for the race between pre-filter time and actual
  call time (another caller could exhaust a shared bucket in between).
- `_ranked_candidates`'s family-fallback logic (same underlying model via a
  different provider) is unchanged and still runs after the pre-filter has
  already narrowed the pool.

## Part 2: Vision Review Loop (Frontend)

### Where it fits

Opt-in via a new `--review` flag on
`Frontend/scripts/regenerate_via_router.py`. Without the flag, behavior is
unchanged (today's one-shot generate-and-write). With the flag, each site
goes through an additional render → critique → revise cycle before the
final files are written.

### Reviewer model

The generator (whatever `handle_chat`/router picks, or a forced model —
unchanged from today) is text-only for the strong free models
(`nemotron-3-ultra-550b-a55b`, `groq/openai/gpt-oss-120b`, etc.). The
critique step needs an actual vision-capable catalog entry — e.g.
`openrouter/nvidia/nemotron-nano-12b-v2-vl:free` or
`openrouter/google/gemma-4-26b-a4b-it:free` (both have `image` in
`input_types`). The router (via `task_type="vision-review"` or direct
catalog filter on `functions: [vision]`) picks among these for the
critique call specifically; the generator model handles the revision call.

### Loop mechanics

Per site, with `--review`:
1. Generate as today (prompt → 3 files via `FILE_MARKER` parsing).
2. Render `index.html` via Playwright (reusing the pattern already in
   `Frontend/scripts/screenshot_sites.py`: headless Chromium,
   `file://` URL, full-page screenshot) to a temp PNG — not committed,
   not written into the site folder.
3. Send the screenshot + the original design spec to the vision model,
   asking for a concrete, actionable critique against the spec (what's
   visually wrong: spacing, color usage, missing sections, layout
   mismatches).
4. Feed the critique + design spec + current 3 files back to the
   generator model, asking for a revised version of all 3 files.
5. Repeat steps 2-4 up to a fixed cap of **3 iterations** (hardcoded
   constant, not configurable via CLI for this first version).
6. Write the final iteration's files to the site folder (same `.bak`
   backup behavior as today).

No early-exit-on-"good enough" logic in this version — always runs the
full fixed number of iterations when `--review` is passed. (A future
version could add a vision-model verdict field to stop early; out of
scope here.)

### Cost/rate-limit awareness

Each `--review` run costs 1 (generate) + up to 3×2 (render+critique,
revise) = up to 7 model calls per site instead of 1. Given OpenRouter's
free tier is a shared 20 RPM / 50 RPD bucket across all `:free` models,
`--review` should be used deliberately on a handful of sites, not batched
across all 8 remaining stubs at once.

## Files Touched

- `Token-router/chat_core.py` — pre-filter step, `PromptTooLargeError`
- `Token-router/rate_limiter.py` — no change (existing `is_available` reused)
- `Frontend/scripts/regenerate_via_router.py` — `--review` flag, loop logic
- New: Playwright screenshot helper reused/imported from
  `Frontend/scripts/screenshot_sites.py` (or factored into a small shared
  function if the existing script isn't easily importable as-is)

## Testing

- `Token-router/tests/test_chat_core.py` — new tests: tpm-exceeding model
  excluded from candidates; `PromptTooLargeError` raised when all
  candidates fail tpm; `AllModelsRateLimitedError` still raised when
  exclusion is due to rpm/rpd instead; pre-filter doesn't affect models
  with `tpm: null`.
- Frontend review loop: no unit test framework exists in `Frontend/` today
  (Python scripts, no pytest present) — verify manually via a single real
  `--review` run on one site, same smoke-test-before-scaling approach used
  earlier this session for the base regeneration script.

## Out of Scope

- Configurable iteration cap (hardcoded at 3 for now).
- Early-exit on vision-model "good enough" verdict.
- Applying `--review` retroactively to `posthog` (already regenerated this
  session) unless explicitly requested.
- TPM/TPD tracking persistence across process restarts (still in-memory
  only, same as existing rpm/rpd tracking).
