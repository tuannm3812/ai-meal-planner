"""Render the poster and LinkedIn image from their HTML. The deck is build_deck.js.

Every figure comes from the fact sheet in README.md; update that first.
Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" python docs/showcase/render.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
PAGES = [
    ("poster.html", "ai-meal-planner-poster.png", 1200, 1800),
    ("linkedin.html", "ai-meal-planner-linkedin.png", 1080, 1350),
    ("capstone-poster.html", "ai-meal-planner-capstone-poster.png", 1684, 2384),
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
        if src in ("poster.html", "capstone-poster.html"):
            page.pdf(
                path=HERE / out.replace(".png", ".pdf"),
                width=f"{width}px",
                height=f"{height}px",
                print_background=True,
            )
        print("wrote", out)
    browser.close()
