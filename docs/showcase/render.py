"""Render the showcase posters to PNG at 2x.

Run from the repo root (fonts load from frontend/node_modules, so run
`npm install` in frontend/ first):

    uv run --no-project --with "playwright==1.60.0" python docs/showcase/render.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PAGES = [
    ("poster.html", "ai-meal-planner-poster.png", 1200, 1800),
    ("linkedin.html", "ai-meal-planner-linkedin.png", 1080, 1350),
]

with sync_playwright() as p:
    browser = p.chromium.launch()
    for src, out, width, height in PAGES:
        if not (HERE / src).exists():
            continue
        page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=2)
        page.goto((HERE / src).as_uri())
        page.evaluate("document.fonts.ready")
        page.screenshot(path=HERE / out)
        print("wrote", out)
    browser.close()
