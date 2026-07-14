"""
Send each websites/<site>/screenshot.png + index.html to an Ollama Cloud VLM
and write websites/<site>/metadata.json for semantic search / RAG retrieval.

Config:
  config.yaml      ollama.host / ollama.model (CLI --model overrides)
  .env             OLLAMA_API_KEY=...

Usage:
  python scripts/generate_metadata.py
  python scripts/generate_metadata.py --model qwen2.5vl:32b
  python scripts/generate_metadata.py stripe nike   # only these sites
"""
import argparse
import json
import os
import sys
from pathlib import Path

import ollama
import yaml
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
WEBSITES = ROOT / "websites"

load_dotenv(ROOT / ".env")
with open(ROOT / "config.yaml", encoding="utf-8") as f:
    CONFIG = yaml.safe_load(f)

SCHEMA_FIELDS = [
    "title",             # short human-readable name for the design, e.g. "Fintech Dashboard Hero"
    "industry",          # single tag from a closed-ish set: fintech, developer-tools, ai, healthcare,
                         # real-estate, travel, education, social, crypto, portfolio, agency, e-commerce...
    "description",       # 2-3 sentence semantic summary optimized for embedding-search retrieval —
                         # mention industry, visual style, layout, and overall user experience
    "design_style",      # whole-site aesthetic: minimal, glassmorphism, brutalist, corporate, editorial,
                         # luxury, apple-like, linear-inspired, retro, cyberpunk...
    "layout_style",      # whole-page structure: centered-hero, split-hero, bento-grid, dashboard,
                         # magazine, storytelling, single-page, scrolling-experience...
    "mood",              # list of tone tags: corporate, playful, luxury, technical, minimal...
    "color_style",       # list of semantic color descriptors: deep-navy, pastel-gradient, high-contrast-dark...
    "typography_style",  # list: thin-weight-sans, serif-editorial, monospace-technical...
    "theme",             # light, dark, or mixed
    "visual_density",    # airy, balanced, or dense
    "complexity",        # simple, medium, advanced, or experimental
    "uniqueness",        # conventional, modern, distinctive, or experimental
    "best_for",          # list of use cases this design suits: startup-landing, hackathon,
                         # enterprise-saas, product-launch, portfolio, agency, documentation...
    "keywords",          # free-form list of short tags, e.g. "rounded", "gradient", "dark", "cards"
]

PROMPT = f"""You are a design analyst cataloguing marketing website templates for a
semantic search system. Look at the attached full-page screenshot and the HTML
source below, then return ONLY a JSON object with exactly these fields:

{json.dumps(SCHEMA_FIELDS, indent=2)}

Rules:
- "description" must be 2-3 sentences, written as a semantic summary optimized for AI
  retrieval — mention industry, visual style, layout, and overall user experience. Example:
  "A premium fintech landing page featuring a dark theme, large rounded cards, generous
  whitespace, and a split hero showcasing a financial dashboard. The design emphasizes trust,
  enterprise credibility, and modern visual hierarchy, making it suitable for B2B SaaS and
  investment platforms."
- "title", "industry", "design_style", "layout_style" are single short lowercase kebab-case
  strings (title may use normal capitalization).
- "theme" must be exactly one of: light, dark, mixed.
- "visual_density" must be exactly one of: airy, balanced, dense.
- "complexity" must be exactly one of: simple, medium, advanced, experimental.
- "uniqueness" must be exactly one of: conventional, modern, distinctive, experimental.
- "mood", "color_style", "typography_style", "best_for", "keywords" are arrays of short
  lowercase kebab-case tags (3-8 tags each).
- Base tags on what's actually visible/present, not generic guesses.
- Do not invent component-level detail (navbar/footer/button styles) — stay at whole-page level.
- Return raw JSON only, no markdown fences, no commentary.

HTML source:
```html
{{html}}
```
"""


def build_client() -> ollama.Client:
    api_key = os.environ.get("OLLAMA_API_KEY")
    if not api_key:
        sys.exit("OLLAMA_API_KEY not set in .env")
    host = CONFIG["ollama"]["host"]
    return ollama.Client(host=host, headers={"Authorization": f"Bearer {api_key}"})


def generate_for_site(client: ollama.Client, model: str, site_dir: Path) -> dict:
    screenshot = site_dir / "screenshot.png"
    html_file = site_dir / "index.html"
    if not screenshot.exists():
        raise FileNotFoundError(f"missing {screenshot}, run scripts/screenshot_sites.py first")

    html = html_file.read_text(encoding="utf-8")
    prompt = PROMPT.format(html=html[:8000])

    resp = client.chat(
        model=model,
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [str(screenshot)],
        }],
        format="json",
    )
    data = json.loads(resp["message"]["content"])
    data["site"] = site_dir.name

    def tags(key):
        return ", ".join(data.get(key, []))

    data["embedding_text"] = " | ".join([
        data.get("title", ""),
        data.get("industry", ""),
        data.get("description", ""),
        data.get("design_style", ""),
        data.get("layout_style", ""),
        tags("mood"),
        tags("color_style"),
        tags("typography_style"),
        data.get("theme", ""),
        data.get("visual_density", ""),
        data.get("complexity", ""),
        data.get("uniqueness", ""),
        tags("best_for"),
        tags("keywords"),
    ])
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=CONFIG["ollama"]["model"], help="Ollama Cloud VLM model name")
    parser.add_argument("sites", nargs="*", help="specific site folder names (default: all)")
    args = parser.parse_args()

    client = build_client()
    sites = sorted(p for p in WEBSITES.iterdir() if p.is_dir() and (p / "index.html").exists())
    if args.sites:
        wanted = set(args.sites)
        sites = [p for p in sites if p.name in wanted]

    for site_dir in sites:
        out = site_dir / "metadata.json"
        try:
            data = generate_for_site(client, args.model, site_dir)
        except Exception as e:
            print(f"{site_dir.name}: FAILED - {e}")
            continue
        out.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"{site_dir.name}: {out.name}")


if __name__ == "__main__":
    main()
