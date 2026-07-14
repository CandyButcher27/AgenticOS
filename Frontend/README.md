# Frontend

Design-reference catalogue and pipeline for a semantic search + generation system: given a query like "make me a website for a SaaS page", retrieve real design patterns/components from a large catalogue of static site clones and use them to compose new frontend sites.

## Contents

- **`websites/`** — ~75 static single-page site homages (`<site>/index.html`, `styles.css`/`style.css`, `script.js`/`app.js`, `DESIGN-<site>.md`). Each `DESIGN-<site>.md` is a structured design-token spec (colors, typography, spacing, component tokens) plus prose on the brand's visual language. Primary catalogue the retrieval pipeline indexes. See `REGENERATE.md` for stub-site tracking.
- **`portfolio-concepts/`** — original (non-brand-derived) design concepts (`blueprint`, `mixdown`, `physics`, `starchart`, `terminal`, `woven`), each with `index.html`, a design spec, and `unique.md` explaining what differentiates it.
- **`video_animated/`** — scroll/video-driven landing page builds, each with `index.html` plus a `prompt.md` recording the build spec used to generate it.
- **`scripts/`** — two-stage Python pipeline that turns `websites/` into embeddable metadata:
  1. `screenshot_sites.py` — Playwright, full-page screenshot of each site.
  2. `generate_metadata.py` — sends screenshot + HTML to an Ollama vision-language model, writes `metadata.json` per site.

## Setup

```
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m playwright install chromium
```

Config: `config.yaml` (`ollama.host`, `ollama.model`) + `.env` (`OLLAMA_API_KEY`).

## Usage

```
.venv/Scripts/python.exe scripts/screenshot_sites.py            # all sites
.venv/Scripts/python.exe scripts/screenshot_sites.py stripe nike # specific sites

.venv/Scripts/python.exe scripts/generate_metadata.py
.venv/Scripts/python.exe scripts/generate_metadata.py --model qwen2.5vl:32b
.venv/Scripts/python.exe scripts/generate_metadata.py stripe nike
```

`generate_metadata.py` requires `screenshot.png` to already exist for each site.
