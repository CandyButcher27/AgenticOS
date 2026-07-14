import litellm

ROUTER_MODEL = "groq/llama-3.1-8b-instant"


def _catalog_prompt(filtered_catalog: list[dict]) -> str:
    lines = [f"- {e['id']}: {e['description']} (tags: {', '.join(e['tags'])})" for e in filtered_catalog]
    return "\n".join(lines)


def select_model(prompt: str, filtered_catalog: list[dict], house_key: str) -> str:
    if not filtered_catalog:
        raise ValueError("filtered_catalog must not be empty")
    fallback = filtered_catalog[0]["id"]

    try:
        response = litellm.completion(
            model=ROUTER_MODEL,
            api_key=house_key,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Pick the single best model id for this user prompt. "
                        "Reply with ONLY the model id, nothing else.\n\n"
                        f"Available models:\n{_catalog_prompt(filtered_catalog)}\n\n"
                        f"User prompt: {prompt}"
                    ),
                }
            ],
        )
        chosen = response.choices[0].message.content.strip()
    except Exception:
        return fallback

    valid_ids = {e["id"] for e in filtered_catalog}
    return chosen if chosen in valid_ids else fallback
