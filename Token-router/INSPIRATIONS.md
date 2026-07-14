# Token-Router — Ideas From Inspiration Repos

Combined notes from four hackathon "token-efficient LLM routing" submissions under
`inspirations/tokens/`. Each solved the same problem (AMD Track 1 style: answer a batch
of prompts via `/input/tasks.json` → `/output/results.json`, minimize paid LLM tokens,
keep accuracy high) with different tradeoffs. Every idea below is tagged with its
source repo so credit/context isn't lost.

## 1. Cascading / tiered fallback as the core shape

All four repos independently converge on the same top-level architecture: a chain of
increasingly expensive layers, stopping at the first one that produces a validated
answer. Never call a paid API if a cheaper method already solved it.

- **Zephyr-AHTIS** (`token_optimiser_1`): 5 layers — task classifier → semantic cache →
  deterministic solvers → local Ollama model → tiered Fireworks API (3 model tiers).
- **track1-agent** (`token_optimiser_2`): router (free, local classifier) picks cheap vs
  expensive model up front, rather than a multi-hop cascade — routing itself costs 0
  tokens because it avoids even a "which model should I use" LLM call.
- **Thymus** (`token_optimiser_3`): local GGUF model answers first; escalates to cloud
  only as SHEPHERD (cheap review/fix of the local draft) or RESET (full re-solve) based
  on the model's own self-reported confidence + verification result.
- **TokenForge** (`token_optimiser_4`): explicit two-tier "fail-closed" router — Tier 0
  (regex/SymPy/hardcoded, 0 tokens) always tried first; Tier 1 (real LLM call) only on
  a miss.

**Takeaway for Token-router:** keep this as the top-level control flow — classify →
try free/local → escalate to paid, only as far as needed, with every layer required to
pass a validation gate before its answer is accepted.

## 2. Zero-token routing decision (don't pay an LLM to pick a model)

*Source: track1-agent (`token_optimiser_2`), Thymus (`token_optimiser_3`)*

The naive approach is to ask an LLM "is this task easy or hard" before answering it —
but that costs tokens itself. Both repos solve this for free:

- track1-agent trains a small **fine-tuned DistilBERT** classifier offline
  (`router/train_router.py`), with a deterministic regex/heuristic router
  (`src/optimizer/router.py`) as a fallback when the ML checkpoint/deps aren't present
  — so the container still runs without the private model artifact.
- Thymus's classifier (`router/classifier/classifier.py`) uses a regex fast-path for
  clear categories, only falling back to prompting the *local* (already-loaded, free)
  model for ambiguous cases — never the paid cloud model.
- track1-agent also benchmarks this against a prompt-based LLM router
  (`src/baseline_router.py`) purely to prove the free router is worth it — good pattern
  for justifying a routing design in an eval report.

**Takeaway:** a hand-tuned regex/weighted-signal classifier is a legitimate zero-cost
router on its own; an optional fine-tuned model is a nice-to-have that should degrade
gracefully to the regex version if unavailable.

## 3. Deterministic solvers before any LLM call

*Source: Zephyr-AHTIS (`1`), TokenForge (`4`)*

Whole categories of tasks (math, JSON validation, code syntax checking, string ops)
don't need an LLM at all:

- Zephyr-AHTIS: per-task-type solver modules (`math_solver.py` using `re` + whitelisted
  `eval()`, `code_solver.py`/`json_solver.py` using `ast`/`json` stdlib to validate
  syntax rather than asking a model).
- TokenForge: `local_solvers.py` — SymPy for arithmetic/algebra
  (`sympy.sympify`, `sympy.solve`), regex for string ops, a static country→capital
  dict, all tried **before** falling through to Tier 1. Returns `None` (fail-closed) if
  nothing matches — never guesses.

**Takeaway:** for any task category with a deterministic ground truth (math, syntax
validity, known lookups), write a pure-Python/stdlib solver and gate the LLM call
behind "solver returned None."

**Caveat worth flagging:** both repos also lean on **hardcoded answer dicts keyed to
the exact benchmark prompts** (Zephyr's `qa_solver.py`, TokenForge's
`solve_known_prompt`/`solve_sentiment_benchmark`/etc.) — this is explicitly
benchmark-gaming, not general capability. Fine for a hackathon leaderboard, not a
pattern to copy for a real router meant to generalize to unseen prompts.

## 4. Semantic caching

*Source: Zephyr-AHTIS (`token_optimiser_1`)*

`src/cache/semantic_cache.py`: embed each query (`sentence-transformers`,
`all-MiniLM-L6-v2`), brute-force cosine similarity against every past
`(embedding, answer)` pair, return the cached answer above a similarity threshold
(0.99). Deliberately skipped for task types needing exact/structural answers
(code/json/date/math), where a "close enough" semantic match is wrong by definition.

**Takeaway:** semantic cache is a cheap win for open-ended categories (QA, general
chat) but must be excluded for tasks with a single correct structural answer.

## 5. Per-category prompt/token budgeting instead of one-size-fits-all

*Source: track1-agent (`2`), TokenForge (`4`)*

Both repos build a **small config table keyed by task category** holding a terse
system prompt + a `max_tokens` ceiling, rather than branching logic:

- track1-agent: `policies.py` (system-prompt builder) + `token_budget.py` (per-category
  `max_tokens`, e.g. math scales with "show steps" vs "final only"; summarization
  scales with source length ratio; low-confidence router output widens the budget
  defensively).
- TokenForge: `TASK_CONFIG` dict — category → `{system_prompt, max_tokens, tier}`, so
  adding a new category is a data change, not new control flow.

**Takeaway:** config-table dispatch (dict keyed by category) beats a chain of
`if category == X` branches — directly reusable pattern for Token-router's
`catalog.py`/`catalog.yaml`.

## 6. Deterministic output repair instead of a second LLM call

*Source: track1-agent (`2`), Zephyr-AHTIS (`1`), TokenForge (`4`)*

When a raw LLM answer is malformed (chatty preamble, unfenced JSON, extra commentary),
all three repos fix it locally rather than re-prompting:

- track1-agent `postprocessors.py`: strip preamble, extract/dedupe first valid JSON
  object, pull last fenced code block, extract bare sentiment label from prose.
- Zephyr-AHTIS `answer_repair.py`: close a truncated JSON brace, strip commas from
  numbers, collapse sentiment answer to one word.
- TokenForge `router.sanitize_output()`: strip `<think>...</think>` CoT tags and
  conversational filler ("Sure, here is...", "Hope this helps!").

**Takeaway:** always try a cheap string-repair pass before paying for a retry call —
directly saves tokens on the most common failure mode (model wraps the answer in
prose).

## 7. Request bundling — answer multiple tasks in one API call

*Source: track1-agent (`token_optimiser_2`)*

`bundling.py`: groups same-category, "safe"-tier-eligible tasks into a single
index-keyed JSON envelope, sent as one Fireworks call; each sub-answer is validated
independently, and any item that fails validation is peeled off and re-run
individually — so batching never lowers correctness, only sometimes saves tokens
(fail-soft).

**Takeaway:** worth adding once per-task routing/solving is solid — biggest token win
of all four repos' ideas, since it amortizes the fixed prompt overhead across N tasks.
Requires per-item validation + fallback to be safe.

## 8. Central metering / single call-site for the paid API

*Source: track1-agent (`2`), Thymus (`3`)*

Both repos funnel **every** paid-model call through exactly one function
(`src/fireworks_client.py`'s `chat()` in track1-agent; `Gateway.call()` in Thymus),
specifically so token accounting has one source of truth that matches how the eval
harness itself meters usage. Also the natural place to strip reasoning tags
(`<think>...</think>`) once, instead of at every call site.

**Takeaway:** Token-router should have exactly one function that talks to a paid
provider — useful both for token accounting and for provider swapping.

## 9. Self-reported confidence + verification, not a single static threshold

*Source: Thymus (`token_optimiser_3`)*

Rather than one global confidence cutoff, Thymus combines three signals before
deciding LOCAL vs SHEPHERD (cheap fix) vs RESET (full re-solve): the local model's own
self-reported `routing_decision`, a logit-derived confidence score (avg token
probability), and a task-specific verifier result (AST-parse + generated test
execution for code; entity-overlap heuristic for QA/summary; self-critique prompt for
math/reasoning). A hard verification-FAIL always overrides a confident-sounding answer.

**Takeaway:** a single confidence float is a weak signal alone; combining
self-reported confidence with an independent, task-specific verifier catches
confidently-wrong answers that a threshold alone would miss.

## 10. Fail-closed / fail-soft as a design discipline

*Source: all four*

Common thread across every repo: prefer returning nothing (and falling through to the
next layer) over guessing.

- TokenForge's local solvers return `None` rather than a bad guess.
- track1-agent's bundling falls back to individual per-item calls rather than losing
  the whole batch to one bad response.
- Thymus's harness loop wraps every task so one timeout/failure can't block results
  for the rest — always writes `/output/results.json`, even partial.

**Takeaway:** every layer in Token-router's pipeline should have an explicit "I don't
know, pass it on" exit rather than ever emitting a low-confidence guess as final.

## Source repos

| Idea | Repo |
|---|---|
| Cascading fallback, semantic cache, deterministic solvers, answer repair | `inspirations/tokens/token_optimiser_1` (Zephyr-AHTIS) |
| Zero-token DistilBERT/regex router, config-table prompt/budget dispatch, request bundling, central metering, backward-compat adapter shims | `inspirations/tokens/token_optimiser_2` (track1-agent) |
| Local-first GGUF model, self-reported confidence + task verifiers, two-tier escalation (SHEPHERD/RESET), fault-tolerant harness loop | `inspirations/tokens/token_optimiser_3` (Thymus) |
| Fail-closed Tier 0/Tier 1 split, SymPy solvers, heuristic model-name scoring, output sanitization | `inspirations/tokens/token_optimiser_4` (TokenForge) |
