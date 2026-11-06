# ruff: noqa: E501  (inline SVG)
"""Render icon assets: white card glyphs and the faint food icon backgrounds.

Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" python docs/showcase/slides/build_icons.py
"""

import re
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
ICONS = HERE / "assets/icons"
GLYPHS = ["person", "health_and_safety", "balance", "shopping_basket"]
# name, x, y, size, rotation: a loose cluster in the free top right corner of content slides.
CORNER = [
    ("rice_bowl", 700, 12, 34, -10),
    ("egg", 748, 44, 26, 12),
    ("nutrition", 790, 10, 32, 8),
    ("local_dining", 836, 40, 30, -8),
    ("eco", 878, 8, 30, 14),
    ("grocery", 884, 62, 32, -6),
    ("restaurant", 760, 84, 24, 6),
    ("soup_kitchen", 824, 86, 26, 10),
]
FOODS = [
    "rice_bowl",
    "egg",
    "nutrition",
    "local_dining",
    "eco",
    "grocery",
    "lunch_dining",
    "ramen_dining",
    "bakery_dining",
    "skillet",
]


def path(name):
    return re.search(r'd="([^"]+)"', (ICONS / f"{name}.svg").read_text()).group(1)


def place(name, x, y, size, turn, colour, opacity):
    k = size / 960
    return f'<g transform="translate({x} {y}) rotate({turn} {size / 2} {size / 2}) scale({k}) translate(0 960)" fill="{colour}" opacity="{opacity}"><path d="{path(name)}"/></g>'


def shot(page, svg, width, height, out, scale=2):
    page.set_viewport_size({"width": width, "height": height})
    page.set_content(f'<body style="margin:0;background:transparent">{svg}</body>')
    page.wait_for_timeout(100)
    page.screenshot(path=out, omit_background=True)


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(device_scale_factor=2)
    for name in GLYPHS:
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48">{place(name, 0, 0, 48, 0, "#FFFFFF", 1)}</svg>'
        shot(page, svg, 48, 48, HERE / f"assets/glyph-{name}.png")
    corner = "".join(place(n, x, y, s, r, "#1B5E3F", 0.13) for n, x, y, s, r in CORNER)
    shot(
        page,
        f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540">{corner}</svg>',
        960,
        540,
        HERE / "assets/bg-corner.png",
    )
    band = "".join(
        place(
            FOODS[(col * 3 + row) % len(FOODS)],
            14 + col * 62 + (row % 2) * 30,
            8 + row * 46,
            26,
            (col * 37 + row * 23) % 40 - 20,
            "#FFFFFF",
            0.07,
        )
        for col in range(14)
        for row in range(3)
    )
    shot(
        page,
        f'<svg xmlns="http://www.w3.org/2000/svg" width="873" height="140">{band}</svg>',
        873,
        140,
        HERE / "assets/bg-band.png",
    )
    browser.close()
