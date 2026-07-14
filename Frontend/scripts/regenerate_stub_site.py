"""
Walk the un-regenerated stub sites listed in REGENERATE.md one at a time,
ask an OpenRouter LLM to rewrite websites/<site>/index.html with real,
brand-distinct content (grounded in that site's own design.md + style.css),
show a preview, and let you accept/skip/retry before moving to the next site.

Config:
  config.yaml      openrouter.model
  .env             OPENROUTER_API_KEY=...

Usage:
  python scripts/regenerate_stub_site.py
"""
import json
import re
import urllib.request
from pathlib import Path

import yaml
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parent.parent
WEBSITES = ROOT / "websites"
REGENERATE_MD = ROOT / "REGENERATE.md"

load_dotenv(ROOT / ".env")
with open(ROOT / "config.yaml", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

PROMPT_TEMPLATE = """You are rewriting the marketing homepage for "{site}" from a generic
placeholder template into real, brand-distinct content.

Below is this site's design brief (design.md) and its actual style.css (already
brand-specific). The current index.html still has generic boilerplate copy
("Feature 1/2/3", shared filler sentences) that must be replaced.

Rewrite index.html completely:
- Reuse the class names already defined in style.css wherever they fit (nav, hero,
  cards, footer, etc). Only introduce a new class name if the design brief clearly
  calls for a section style.css doesn't cover.
- Replace ALL placeholder copy with real, specific copy that matches the brand voice,
  product, and visual language described in design.md.
- Keep the same <link rel="stylesheet" href="style.css"> and <script src="app.js"></script>
  references.
- Return ONLY the complete raw HTML document, no markdown fences, no commentary.

design.md:
```
{design_md}
```

style.css:
```css
{style_css}
```

current index.html (to replace):
```html
{index_html}
```
"""


def build_headers() -> dict:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise SystemExit("OPENROUTER_API_KEY not set in .env")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def call_openrouter(prompt: str) -> str:
    body = json.dumps({
        "model": CONFIG["openrouter"]["model"],
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers=build_headers(),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"].strip()


def strip_fences(text: str) -> str:
    text = re.sub(r"^```(?:html)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def pending_sites() -> list[str]:
    lines = REGENERATE_MD.read_text(encoding="utf-8").splitlines()
    sites = []
    for line in lines:
        m = re.match(r"^- (\S+)(?! \(regenerated\))$", line.strip())
        if m and "(regenerated)" not in line:
            sites.append(m.group(1))
    return sites


def mark_regenerated(site: str):
    text = REGENERATE_MD.read_text(encoding="utf-8")
    text = text.replace(f"- {site}\n", f"- {site} (regenerated)\n")
    REGENERATE_MD.write_text(text, encoding="utf-8")


def process_site(site: str) -> bool:
    site_dir = WEBSITES / site
    design_md = (site_dir / "design.md").read_text(encoding="utf-8")
    style_css = (site_dir / "style.css").read_text(encoding="utf-8")
    index_html = (site_dir / "index.html").read_text(encoding="utf-8")

    prompt = PROMPT_TEMPLATE.format(
        site=site, design_md=design_md, style_css=style_css, index_html=index_html,
    )

    print(f"\n{'=' * 60}\n{site}\n{'=' * 60}")
    new_html = strip_fences(call_openrouter(prompt))
    print(new_html)
    print(f"{'-' * 60}")

    while True:
        choice = input(f"[{site}] accept / skip / retry? (a/s/r): ").strip().lower()
        if choice == "a":
            (site_dir / "index.html").write_text(new_html, encoding="utf-8")
            mark_regenerated(site)
            print(f"{site}: written + marked regenerated")
            return True
        if choice == "s":
            print(f"{site}: skipped")
            return True
        if choice == "r":
            new_html = strip_fences(call_openrouter(prompt))
            print(new_html)
            print(f"{'-' * 60}")
            continue
        print("please answer a, s, or r")


def main():
    sites = pending_sites()
    if not sites:
        print("No pending sites in REGENERATE.md")
        return
    print(f"{len(sites)} site(s) pending: {', '.join(sites)}")
    for site in sites:
        process_site(site)


if __name__ == "__main__":
    main()
