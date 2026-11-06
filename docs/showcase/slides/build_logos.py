"""Render the tech stack logos in their brand colours for the architecture slide.

Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" python docs/showcase/slides/build_logos.py
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
LOGOS = HERE / "assets/logos"
COLOURS = {
    "python": "#3776AB",
    "fastapi": "#009688",
    "pydantic": "#E92063",
    "scikitlearn": "#F7931E",
    "react": "#149ECA",
    "vite": "#646CFF",
    "tailwindcss": "#06B6D4",
    "streamlit": "#FF4B4B",
    "sqlite": "#003B57",
    "docker": "#2496ED",
    "githubactions": "#2088FF",
    "googlecloud": "#4285F4",
    "opentelemetry": "#F5A800",
    "scipy": "#0054A6",
    "googlegemini": "#8E75B2",
}

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 96, "height": 96}, device_scale_factor=2)
    for name, colour in COLOURS.items():
        svg = (LOGOS / f"src/{name}.svg").read_text().replace("<svg ", f'<svg fill="{colour}" ', 1)
        page.set_content(
            f'<body style="margin:0;background:transparent"><div style="width:96px;height:96px">{svg}</div></body>'
        )
        page.wait_for_timeout(50)
        page.screenshot(path=LOGOS / f"{name}.png", omit_background=True)
    browser.close()
