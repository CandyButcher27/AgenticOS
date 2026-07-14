# Token Optimiser Inspirations — Summary

Overview of the 4 repos in `inspirations/tokens/`, each documented in full at
`inspirations/tokens/token_optimiser_N/README-explained.md`. All four are
AMD/hackathon submissions solving the same brief — answer a fixed benchmark of
tasks from a Fireworks-backed LLM API while minimizing token spend — but with
meaningfully different architectures. Useful reference material for
`Token-router`'s own routing/rate-limiting design.

## At a glance

| | token_optimiser_1 ("Zephyr-AHTIS") | token_optimiser_2 (AMD Track1 agent) | token_optimiser_3 ("Thymus") | token_optimiser_4 ("TokenForge") |
|---|---|---|---|---|
| Core strategy | 5-layer cascading fallback | Zero-token local routing decision, then heavy per-call prompt/output optimization | Local model answers first, verified, then escalated by confidence | 2-tier fail-closed: free deterministic solvers, then one real LLM call |
| Routing decision cost | Free (regex classifier) | Free (fine-tuned DistilBERT + regex fallback) | Free (local GGUF model self-reports routing_decision + confidence) | Free (regex classifier) |
| Local/offline model | Ollama (`qwen2.5-coder:3b`), HF Inference API fallback | None in the scored path (routing model is a tiny classifier, not a chat model) | `llama-cpp-python`, Qwen2.5-3B-Instruct GGUF, baked into the Docker image at build time | None — no local LLM, only deterministic solvers |
| Paid escalation | Fireworks AI, 3 hardcoded model tiers | Fireworks AI, model chosen from `ALLOWED_MODELS` (prefers a "kimi" model) | Fireworks AI, cost-aware `ModelSelector` picks cheapest model clearing a per-task capability threshold | Fireworks AI, raw `urllib` HTTP, dynamic model scoring by parsing name strings (size/capability tags) |
| Verification before accepting an answer | Per-task-type `validate()` gate + self-consistency (calls local model twice, checks agreement) | Per-category deterministic validators + local repair (never a 2nd LLM call to fix output) | Task-specific verifier classes: `CodeVerifier` (AST + generated tests), `QASummaryVerifier` (entity overlap), `SelfVerifier` (model critiques its own answer) | None beyond output sanitization (strips `<think>` tags, filler) — no correctness verification step |
| "Cheap fix" escalation tier | No — binary local vs. paid | No — binary local vs. paid, but paid calls can be bundled (multiple tasks in one call) | Yes — `SHEPHERD` (send local draft to Fireworks as a cheap review/fix) vs `RESET` (full fresh paid solve) | No — binary local (free) vs. paid |
| Semantic cache | Yes — embeddings + cosine similarity ≥0.99 (`sentence-transformers`) | No | No | No |
| Request bundling | No | Yes — same-category tasks packed into one API call, with per-item validation fallback | No | No |
| Learning/adaptive routing | Yes — persisted success-rate heuristic (`routing_stats.json`) biases local vs. paid per task type | No (routing is a trained classifier, static after training) | No (routing is per-query, not adaptive across the run) | No |
| Hardcoded benchmark answers | Yes — `qa_solver.py` hardcodes known Q&A pairs | No | No | Yes, extensively — most of `local_solvers.py`'s Tier-0 hit rate comes from literal answers to the known AMD validation prompts, not general solving |
| Deployment | Docker image (Ollama + embeddings baked in), Streamlit demo | Docker image (`track1-agent/`), separate Streamlit demo (not in scored image) | Docker multi-stage build (compiles `llama-cpp-python`, bakes GGUF weights, `HF_HUB_OFFLINE=1`) | Docker image, GitHub Actions CI (import/behavior checks + multi-arch build/push) |

## Common patterns across all 4

- **Chain-of-responsibility / cascading fallback** is the universal shape: try the
  free/local option first, escalate only on failure or low confidence.
- **Routing decisions themselves must be free** — every repo is careful that the
  classify-and-decide step never itself calls a paid model (that would defeat the
  point). They use regex, tiny local models, or a fine-tuned classifier instead.
- **Config/model list is environment-driven, not hardcoded** — all four respect an
  `ALLOWED_MODELS`/`FIREWORKS_BASE_URL`-style override so the harness can inject
  the real permitted models at judging time without code changes.
- **Local repair over re-querying** — malformed model output gets fixed with
  string/regex post-processing locally rather than paying for a second call to
  "fix itself."
- **Same container contract** — read a tasks JSON, write a results JSON, exit 0 —
  reflecting a shared hackathon harness format across all 4 submissions.
- **Benchmark overfitting is common and acknowledged** — several repos (1, 4
  especially) lean on literal hardcoded answers to the known evaluation prompts to
  hit "0-token, 100%-accuracy" numbers; this is explicitly noted in each repo's own
  doc as not generalizing to unseen prompts.

## Relevance to Token-router

Token-router already does the free-routing-decision + catalog-based model
selection pattern these repos use, plus (uniquely among the four) real
cross-provider fallback and a token-budget-aware pre-filter. None of the four
repos here implement:
- Cross-provider fallback for the same underlying model (Token-router's `family`
  field)
- A vision-based critique/revise loop
- Real-key smoke testing of every catalog entry before use

Ideas worth considering for Token-router, seen here but not yet built:
- **Semantic caching** (token_optimiser_1) — could avoid re-routing/re-calling for
  near-duplicate prompts.
- **A cheap "review/fix" escalation tier** (token_optimiser_3's `SHEPHERD`) — sits
  between "trust the small model" and "fully re-solve with a bigger one," could
  reduce cost further than the current binary router-pick-or-fallback.
- **Request bundling** (token_optimiser_2) — batching same-task-type calls into
  one request where the target model/task allows it.
- **Self-consistency check** (token_optimiser_1: call twice, compare) as a cheap
  confidence signal before accepting an answer, without a separate verifier model.
