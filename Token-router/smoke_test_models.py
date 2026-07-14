import sys
import time
import litellm
from catalog import load_catalog
from chat_core import SERVER_KEYS, PROVIDER_KEY_ENV

if __name__ == "__main__":
    delay = float(sys.argv[1]) if len(sys.argv) > 1 else 0
    entries = load_catalog()
    for i, entry in enumerate(entries):
        model_id = entry["id"]
        provider = entry["provider"]
        key = SERVER_KEYS.get(provider)
        if not key:
            print(f"SKIP  {model_id} (no {PROVIDER_KEY_ENV.get(provider)} in env)", flush=True)
            continue
        try:
            kwargs = {}
            if provider == "ollama":
                kwargs["api_base"] = "https://ollama.com"
            response = litellm.completion(
                model=model_id,
                api_key=key,
                messages=[{"role": "user", "content": "Say OK."}],
                **kwargs,
            )
            print(f"OK    {model_id} -> {response.choices[0].message.content!r}", flush=True)
        except Exception as e:
            print(f"FAIL  {model_id} -> {e}", flush=True)
        if delay and i < len(entries) - 1:
            time.sleep(delay)
