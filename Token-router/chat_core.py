import os
import litellm

from catalog import load_catalog, filter_catalog
from router_llm import select_model
import rate_limiter

CATALOG = load_catalog()

if os.environ.get("LANGSMITH_TRACING"):
    litellm.success_callback = ["langsmith"]


class NoSupportedProviderError(Exception):
    pass


class AllModelsRateLimitedError(Exception):
    pass


def _narrow_by_task_type(filtered: list[dict], task_type: str | None) -> list[dict]:
    if not task_type:
        return filtered
    narrowed = [e for e in filtered if task_type in e["tags"] or e["type"] == task_type]
    return narrowed or filtered


def _ranked_candidates(prompt: str, filtered: list[dict], house_key: str) -> list[dict]:
    chosen_id = select_model(prompt, filtered, house_key)
    chosen = next(e for e in filtered if e["id"] == chosen_id)

    family = chosen.get("family")
    same_family = [
        e for e in filtered
        if e["id"] != chosen_id and family is not None and e.get("family") == family
    ]
    rest = [e for e in filtered if e["id"] != chosen_id and e not in same_family]
    return [chosen, *same_family, *rest]


def handle_chat(prompt: str, keys: dict[str, str], task_type: str | None = None) -> dict:
    filtered = filter_catalog(CATALOG, set(keys.keys()))
    filtered = _narrow_by_task_type(filtered, task_type)
    if not filtered:
        raise NoSupportedProviderError("no supported provider keys")

    house_key = os.environ.get("GROQ_API_KEY", "")
    candidates = _ranked_candidates(prompt, filtered, house_key)

    entry = next((e for e in candidates if rate_limiter.is_available(e)), None)
    if entry is None:
        raise AllModelsRateLimitedError("all matching models are rate-limited, try again later")

    user_key = keys[entry["provider"]]
    response = litellm.completion(
        model=entry["id"],
        api_key=user_key,
        messages=[{"role": "user", "content": prompt}],
    )

    rate_limiter.record_call(entry)
    return {"model_used": entry["id"], "content": response.choices[0].message.content}
