'''
File where all the pre filters are applied as well as the logic is applied for the router to be called , in later stages 
we will be having a seperate file for all the filtering part and then this file will just be getting the keys checking for 
tracing and handle the logic with calling the llm. 
'''

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"), override=True)

import litellm

from catalog import load_catalog, filter_catalog
from router_llm import select_model
import rate_limiter

CATALOG = load_catalog()

if os.environ.get("LANGSMITH_TRACING"):
    litellm.success_callback = ["langsmith"]

PROVIDER_KEY_ENV = {
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "ollama": "OLLAMA_API_KEY",
    "nvidia": "NVIDIA_API_KEY",
}

SERVER_KEYS = {
    provider: os.environ[env_var]
    for provider, env_var in PROVIDER_KEY_ENV.items()
    if os.environ.get(env_var)
}


class NoSupportedProviderError(Exception):
    pass


class AllModelsRateLimitedError(Exception):
    pass


class PromptTooLargeError(Exception):
    pass


def _fits_tpm(prompt: str, entry: dict) -> bool:

    '''
    This funcition is used to estimate the number of tokens per minute that a prompt will use, we use the internal
    litellm tokken counter for this, we are assuming that we do not have the information for the same in the catalog
    then we will assume it can pass through and we accept it.
    '''

    tpm = (entry.get("rate_limits") or {}).get("tpm")
    if tpm is None:
        return True
    estimated_tokens = litellm.token_counter(
        model=entry["id"], messages=[{"role": "user", "content": prompt}]
    )
    return estimated_tokens <= tpm


def _prefilter_candidates_by_ratelimit_and_tpm(prompt: str, filtered: list[dict]) -> list[dict]:

    '''
    This function essentially pre filters the candidates that are present by a rate limiter as well as the above function 
    which checks for the number of tokens per minute
    '''

    return [e for e in filtered if rate_limiter.is_available(e) and _fits_tpm(prompt, e)]


def _narrow_by_task_type(filtered: list[dict], task_type: str | None) -> list[dict]:

    '''
    This function makes a futher filtered list having only the model with the task types, this ensures that our llm model 
    can only choose fromt he filtered set making it more accurate. A fallback is that we give the entire dictionary if
    we dont get any filtered set
    '''

    if not task_type:
        return filtered
    narrowed = [e for e in filtered if task_type in e["tags"] or e["type"] == task_type]
    return narrowed or filtered


def _ranked_candidates(prompt: str, filtered: list[dict], house_key: str) -> list[dict]:

    '''
    This function essentially chooses one model for us, but lets say for some reason this model has been rate limited, we 
    then instead try to find another model of the same family instead of dropping the model all together, also here we tend
    to choose from the same family first instead of going into a random family
    '''
    chosen_id = select_model(prompt, filtered, house_key)
    chosen = next(e for e in filtered if e["id"] == chosen_id)

    family = chosen.get("family")
    same_family = [
        e for e in filtered
        if e["id"] != chosen_id and family is not None and e.get("family") == family
    ]
    rest = [e for e in filtered if e["id"] != chosen_id and e not in same_family]
    return [chosen, *same_family, *rest]


def handle_chat(prompt: str, keys: dict[str, str] | None = None, task_type: str | None = None) -> dict:

    '''
    This is essentially unpacking of the dictionary what we are doing is that we take in client keys and we have our own 
    server keys and we unpack both the dictionaries together, one bug over here is that when unpacking if lets say the 
    clinet hasnt provided us with the groq key then we use our own server key for that. Ideally we should be omitting
    the entirety of the groq family itself and only search for the keys that have been provided by the clinet.
    '''

    keys = {**SERVER_KEYS, **(keys or {})}
    filtered = filter_catalog(CATALOG, set(keys.keys()))
    filtered = _narrow_by_task_type(filtered, task_type)
    if not filtered:
        raise NoSupportedProviderError("no supported provider keys")

    pre_filtered = _prefilter_candidates_by_ratelimit_and_tpm(prompt, filtered)
    
    if not pre_filtered:
        if any(not rate_limiter.is_available(e) for e in filtered):
            raise AllModelsRateLimitedError("all matching models are rate-limited, try again later")
        raise PromptTooLargeError("prompt too large for every available model's token-per-minute limit")

    house_key = os.environ.get("GROQ_API_KEY", "")
    candidates = _ranked_candidates(prompt, pre_filtered, house_key)

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
