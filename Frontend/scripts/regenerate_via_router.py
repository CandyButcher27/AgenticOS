import re
import sys
from pathlib import Path

TOKEN_ROUTER = Path(__file__).resolve().parents[2] / "Token-router"
sys.path.insert(0, str(TOKEN_ROUTER))
from chat_core import handle_chat  # noqa: E402
from playwright.sync_api import sync_playwright
from chat_core import CATALOG, SERVER_KEYS
import litellm

SITES_DIR = Path(__file__).resolve().parents[1] / "websites"

FILE_MARKER = re.compile(r"=== FILE: (index\.html|style\.css|app\.js) ===\s*\n(.*?)(?==== FILE:|\Z)", re.DOTALL)
TRAILING_TOOL_CALL_GARBAGE = re.compile(r"(</[\w:]+>\s*)+\Z")

REVIEW_ITERATIONS = 3

VISION_MODEL_TAGS = {"vision"}

PROMPT_TEMPLATE = """You are generating a static single-page website homage based on the design spec below.
Output exactly three files, and nothing else (no explanations, no markdown code fences).

Wrap each file's content in a marker line exactly like this, then the raw file content:
=== FILE: index.html ===
<full index.html content here, links to "style.css" and "app.js">
=== FILE: style.css ===
<full style.css content here>
=== FILE: app.js ===
<full app.js content here, use vanilla JS only>

Design spec:
---
{design_spec}
---
"""


def regenerate_site(site: str) -> dict[str, str]:
    site_dir = SITES_DIR / site
    design_spec = (site_dir / "design.md").read_text(encoding="utf-8")

    result = handle_chat(PROMPT_TEMPLATE.format(design_spec=design_spec), task_type="code")
    content = result["content"]

    files = {}
    for name, body in FILE_MARKER.findall(content):
        body = body.strip()
        if name != "index.html":
            body = TRAILING_TOOL_CALL_GARBAGE.sub("", body).strip()
        files[name] = body
    missing = {"index.html", "style.css", "app.js"} - files.keys()
    if missing:
        raise ValueError(f"model response missing files: {missing} (model_used={result['model_used']})")

    return files


def _pick_vision_model() -> dict:
    candidates = [
        e for e in CATALOG
        if "vision" in e.get("functions", []) and e["provider"] in SERVER_KEYS
    ]
    if not candidates:
        raise ValueError("no vision-capable model available with a configured server key")
    return candidates[0]


def _render_screenshot(site_dir: Path, files: dict[str, str]) -> Path:
    for name, content in files.items():
        (site_dir / f"_review_{name}").write_text(content, encoding="utf-8")
    html_path = site_dir / "_review_index.html"
    # rewrite links so the temp html references the temp css/js, not the live files
    html_content = files["index.html"].replace('href="style.css"', 'href="_review_style.css"').replace('src="app.js"', 'src="_review_app.js"')
    html_path.write_text(html_content, encoding="utf-8")

    screenshot_path = site_dir / "_review_screenshot.png"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 900})
                page.goto(html_path.resolve().as_uri(), wait_until="networkidle")
                page.screenshot(path=str(screenshot_path), full_page=True)
            finally:
                browser.close()
    finally:
        for name in files:
            (site_dir / f"_review_{name}").unlink(missing_ok=True)
        html_path.unlink(missing_ok=True)
    return screenshot_path


def _critique(screenshot_path: Path, design_spec: str) -> str:
    import base64
    vision_entry = _pick_vision_model()
    key = SERVER_KEYS[vision_entry["provider"]]
    image_b64 = base64.b64encode(screenshot_path.read_bytes()).decode()

    response = litellm.completion(
        model=vision_entry["id"],
        api_key=key,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Here is a screenshot of a generated website, and the design spec "
                            "it should match. Give a concrete, actionable critique: what's "
                            "visually wrong or missing compared to the spec (spacing, color "
                            "usage, missing sections, layout mismatches). Be specific.\n\n"
                            f"Design spec:\n---\n{design_spec}\n---"
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                ],
            }
        ],
    )
    print(f"    (critique by {vision_entry['id']})")
    return response.choices[0].message.content


def _revise(design_spec: str, critique: str, files: dict[str, str]) -> dict[str, str]:
    revise_prompt = PROMPT_TEMPLATE.format(design_spec=design_spec) + (
        f"\n\nHere is the current version of the three files:\n"
        f"=== FILE: index.html ===\n{files['index.html']}\n"
        f"=== FILE: style.css ===\n{files['style.css']}\n"
        f"=== FILE: app.js ===\n{files['app.js']}\n\n"
        f"A visual reviewer gave this critique against the design spec:\n{critique}\n\n"
        f"Revise all three files to address the critique. Output them in the same "
        f"=== FILE: ... === format as before, all three files, complete content."
    )
    result = handle_chat(revise_prompt, task_type="code")
    content = result["content"]

    revised = {}
    for name, body in FILE_MARKER.findall(content):
        body = body.strip()
        if name != "index.html":
            body = TRAILING_TOOL_CALL_GARBAGE.sub("", body).strip()
        revised[name] = body
    missing = {"index.html", "style.css", "app.js"} - revised.keys()
    if missing:
        raise ValueError(f"revision response missing files: {missing} (model_used={result['model_used']})")
    return revised


def review_and_revise(site: str, files: dict[str, str], design_spec: str) -> dict[str, str]:
    site_dir = SITES_DIR / site
    for i in range(REVIEW_ITERATIONS):
        print(f"  review pass {i + 1}/{REVIEW_ITERATIONS}...")
        screenshot_path = _render_screenshot(site_dir, files)
        critique = _critique(screenshot_path, design_spec)
        screenshot_path.unlink(missing_ok=True)
        print(f"    critique: {critique[:200]}...")
        files = _revise(design_spec, critique, files)
    return files


def write_site_files(site: str, files: dict[str, str]) -> None:
    site_dir = SITES_DIR / site
    for name, content in files.items():
        target = site_dir / name
        backup = site_dir / f"{name}.bak"
        if target.exists() and not backup.exists():
            backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
        target.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    args = sys.argv[1:]
    review = "--review" in args
    sites = [a for a in args if a != "--review"]

    if not sites:
        print("usage: python regenerate_via_router.py [--review] <site> [<site> ...]")
        sys.exit(1)

    for site in sites:
        print(f"regenerating {site}...")
        try:
            files = regenerate_site(site)
            if review:
                design_spec = (SITES_DIR / site / "design.md").read_text(encoding="utf-8")
                files = review_and_revise(site, files, design_spec)
            write_site_files(site, files)
            print(f"  OK  wrote {', '.join(files.keys())} for {site}")
        except Exception as e:
            print(f"  FAIL {site} -> {e}")
