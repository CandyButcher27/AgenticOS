# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A design-reference catalogue and pipeline for building a semantic search + generation system: given a query like "make me a website for a SaaS page", retrieve real design patterns/components from a large catalogue of static site clones and use them to compose new frontend sites.

Three content collections plus a Python tooling layer that turns collection #1 into searchable metadata:

- **`websites/`** — ~75 static single-page site homages (`<site>/index.html`, `styles.css`/`style.css`, `script.js`/`app.js`, `DESIGN-<site>.md`). Each `DESIGN-<site>.md` is a structured design-token spec (YAML frontmatter: colors, typography, spacing, rounded corners, component tokens) followed by prose documenting the brand's visual language, do's/don'ts, and responsive behavior. This is the primary catalogue the retrieval pipeline indexes.
- **`portfolio-concepts/`** — a handful of original (non-brand-derived) design concepts (`blueprint`, `mixdown`, `physics`, `starchart`, `terminal`, `woven`), each with `index.html`, `DESIGN-<name>.md`, and a `unique.md` explaining what differentiates that concept from the others in the set.
- **`video_animated/`** — scroll/video-driven landing page builds, each folder holding `index.html` plus a `prompt.md` recording the exact build spec (tech stack, animation timing, component-by-component layout) used to generate it.

Some `websites/*/index.html` files are unregenerated placeholder stubs (generic boilerplate copy, not real per-brand content) — see `REGENERATE.md` for the tracked list and regeneration status. Don't index or trust stub files as real design references until they're marked regenerated.

## Pipeline (scripts/)

Two-stage Python pipeline that turns `websites/` into embeddable metadata:

1. **`scripts/screenshot_sites.py`** — Playwright (Chromium, headless), opens each `websites/<site>/index.html` via `file://`, full-page screenshot → `websites/<site>/screenshot.png`.
   ```
   .venv/Scripts/python.exe scripts/screenshot_sites.py            # all sites
   .venv/Scripts/python.exe scripts/screenshot_sites.py stripe nike # specific sites
   ```
2. **`scripts/generate_metadata.py`** — sends each site's `screenshot.png` + `index.html` to an Ollama Cloud vision-language model, writes `websites/<site>/metadata.json` using the fixed 15-field schema defined in `SCHEMA_FIELDS` (title, industry, description, design_style, layout_style, mood, color_style, typography_style, theme, visual_density, complexity, uniqueness, best_for, keywords) plus an auto-derived `embedding_text` field meant to be fed to an embedding model for semantic retrieval.
   ```
   .venv/Scripts/python.exe scripts/generate_metadata.py                    # all sites, default model from config.yaml
   .venv/Scripts/python.exe scripts/generate_metadata.py --model qwen2.5vl:32b
   .venv/Scripts/python.exe scripts/generate_metadata.py stripe nike        # specific sites
   ```
   Requires `screenshot.png` to already exist (run stage 1 first). Config: `config.yaml` (`ollama.host`, `ollama.model`) + `.env` (`OLLAMA_API_KEY`).

When changing the metadata schema, keep whole-page fields (industry, design_style, layout_style, etc.) separate from any future component-level fields (navbar/footer/button style) — those belong to a later component-extraction phase, not this schema. Enum-constrained fields (`theme`, `visual_density`, `complexity`, `uniqueness`) need their exact allowed values spelled out in the prompt — the VLM drifts off-schema (e.g. `"light-mode"` instead of `"light"`) if only described in a code comment.

## Environment

No Node/npm anywhere in this repo — all tooling is Python, using a `.venv` per global convention. Setup:
```
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m playwright install chromium
```
`requirements.txt`: `playwright`, `ollama`, `pyyaml`, `python-dotenv`.

Each `websites/*/index.html` is a standalone static page (own `styles.css`/`style.css` + `script.js`/`app.js`, no build step) — open directly in a browser or via `file://` for Playwright.

<!-- OPENWIKI:START -->

## OpenWiki

This repository uses OpenWiki for recurring code documentation. Start with `openwiki/quickstart.md`, then follow its links to architecture, workflows, domain concepts, operations, integrations, testing guidance, and source maps.

The scheduled OpenWiki GitHub Actions workflow refreshes the repository wiki. Do not hand-edit generated OpenWiki pages unless explicitly asked; prefer updating source code/docs and letting OpenWiki regenerate.

<!-- OPENWIKI:END -->
