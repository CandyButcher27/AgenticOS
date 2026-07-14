import os
import sys
import time
import litellm
from catalog import load_catalog

KEY_ENV = {
    "groq": "GROQ_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "gemini": "GEMINI_API_KEY",
}

if __name__ == "__main__":
    delay = float(sys.argv[1]) if len(sys.argv) > 1 else 0
    entries = load_catalog()
    for i, entry in enumerate(entries):
        model_id = entry["id"]
        provider = entry["provider"]
        key = os.environ.get(KEY_ENV.get(provider, ""))
        if not key:
            print(f"SKIP  {model_id} (no {KEY_ENV.get(provider)} in env)", flush=True)
            continue
        try:
            response = litellm.completion(
                model=model_id,
                api_key=key,
                messages=[{"role": "user", "content": "Say OK."}],
            )
            print(f"OK    {model_id} -> {response.choices[0].message.content!r}", flush=True)
        except Exception as e:
            print(f"FAIL  {model_id} -> {e}", flush=True)
        if delay and i < len(entries) - 1:
            time.sleep(delay)
