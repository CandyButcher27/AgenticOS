import sys
from pathlib import Path

TOKEN_ROUTER = Path(__file__).resolve().parents[2] / "Token-router" / "scripts"
sys.path.insert(0, str(TOKEN_ROUTER))
import litellm  # noqa: E402
from chat_core import SERVER_KEYS  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from regenerate_via_router import PROMPT_TEMPLATE, FILE_MARKER, TRAILING_TOOL_CALL_GARBAGE, SITES_DIR  # noqa: E402


def generate_with_model(site: str, model_id: str, provider: str, out_dir_name: str) -> dict[str, str]:
    design_spec = (SITES_DIR / site / "design.md").read_text(encoding="utf-8")
    key = SERVER_KEYS[provider]

    response = litellm.completion(
        model=model_id,
        api_key=key,
        messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(design_spec=design_spec)}],
    )
    content = response.choices[0].message.content

    files = {}
    for name, body in FILE_MARKER.findall(content):
        body = body.strip()
        if name != "index.html":
            body = TRAILING_TOOL_CALL_GARBAGE.sub("", body).strip()
        files[name] = body
    missing = {"index.html", "style.css", "app.js"} - files.keys()
    if missing:
        raise ValueError(f"model response missing files: {missing}")

    out_dir = SITES_DIR / out_dir_name
    out_dir.mkdir(exist_ok=True)
    for name, body in files.items():
        (out_dir / name).write_text(body, encoding="utf-8")

    return files


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("usage: python generate_forced_model.py <site> <model_id> <provider> <out_dir_name>")
        sys.exit(1)

    site, model_id, provider, out_dir_name = sys.argv[1:5]
    print(f"generating {site} with {model_id}...")
    try:
        files = generate_with_model(site, model_id, provider, out_dir_name)
        print(f"  OK  wrote {', '.join(files.keys())} to websites/{out_dir_name}/")
    except Exception as e:
        print(f"  FAIL -> {e}")
