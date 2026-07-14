"""Full-page screenshot every websites/<site>/index.html into the same folder."""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
WEBSITES = ROOT / "websites"


def main():
    only = set(sys.argv[1:])
    sites = sorted(p for p in WEBSITES.iterdir() if p.is_dir() and (p / "index.html").exists())
    if only:
        sites = [p for p in sites if p.name in only]

    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        for site_dir in sites:
            url = (site_dir / "index.html").resolve().as_uri()
            out = site_dir / "screenshot.png"
            page.goto(url, wait_until="networkidle")
            page.screenshot(path=str(out), full_page=True)
            print(f"{site_dir.name}: {out.name}")
        browser.close()


if __name__ == "__main__":
    main()
