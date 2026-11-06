# ruff: noqa: E501  (inline SVG)
"""Paint the wordless cover plate: a flat illustration of chicken fried rice from above.

Writes assets/cover-art.png, a full-slide transparent layer. Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" python docs/showcase/slides/build_cover_art.py
"""

import math
import random
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
CX, CY, R = 610, 330, 232
FOOD = R * 0.84
rnd = random.Random(11)


def spot(spread=1.0):
    a, d = rnd.uniform(0, 2 * math.pi), FOOD * spread * math.sqrt(rnd.random())
    return CX + d * math.cos(a), CY + d * math.sin(a)


def rotated(x, y):
    return f'transform="rotate({rnd.randint(0, 179)} {x:.1f} {y:.1f})"'


def rice():
    x, y = spot(1.02)
    colour = rnd.choice(["#F3E2B8", "#EBD49C", "#E5C988", "#F7EBCB", "#DDBB72"])
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="7.4" ry="3" fill="{colour}" {rotated(x, y)}/>'


def chicken():
    x, y = spot(0.93)
    w, h = rnd.uniform(26, 36), rnd.uniform(17, 23)
    colour = rnd.choice(["#D9B27C", "#C99A5E", "#E4C493", "#BE8A4C"])
    return f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="7" fill="{colour}" {rotated(x, y)}/>'


def egg():
    x, y = spot(0.93)
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{rnd.uniform(15, 21):.1f}" ry="{rnd.uniform(8, 11):.1f}" fill="{rnd.choice(["#F6D25A", "#F9DC6E", "#F2C23E"])}" {rotated(x, y)}/>'


def pea():
    x, y = spot(0.96)
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{rnd.uniform(6, 7.4):.1f}" fill="{rnd.choice(["#5E9A3A", "#6FAE45", "#4F8C31"])}"/>'


def carrot():
    x, y = spot(0.96)
    s = rnd.uniform(10, 13)
    return f'<rect x="{x - s / 2:.1f}" y="{y - s / 2:.1f}" width="{s:.1f}" height="{s:.1f}" rx="2.5" fill="{rnd.choice(["#E8833A", "#EE9345"])}" {rotated(x, y)}/>'


def scallion():
    x, y = spot(0.9)
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.6" fill="none" stroke="#3F7E27" stroke-width="2.4"/>'


def scene(seed, chickens):
    """One plate. The dish stays the same; chicken pieces follow the plan's protein."""
    rnd.seed(seed)
    food = [rice() for _ in range(3000)]
    pieces = [chicken] * chickens + [egg] * 20 + [carrot] * 40 + [pea] * 52 + [scallion] * 12
    rnd.shuffle(pieces)
    food += [draw() for draw in pieces]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
<circle cx="{CX}" cy="{CY + 8}" r="{R + 4}" fill="#0C1A13"/>
<circle cx="{CX}" cy="{CY}" r="{R}" fill="#FAFAF6"/>
<circle cx="{CX}" cy="{CY}" r="{FOOD + 8:.1f}" fill="#EFEFE8"/>
<circle cx="{CX}" cy="{CY}" r="{FOOD:.1f}" fill="#E5C988"/>
{"".join(food)}
</svg>"""


svg = scene(11, 26)
# kcal on slide 2 -> chicken pieces, in proportion to each plan's protein (26, 48, 60, 63 g).
PLATES = {363: 11, 694: 20, 809: 25, 850: 27}

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=2)
    page.set_content(f'<body style="margin:0;background:transparent">{svg}</body>')
    page.wait_for_timeout(300)
    page.screenshot(path=HERE / "assets/cover-art.png", omit_background=True)
    # Whole plates on their own, for slide 2.
    side = 2 * R + 32
    page.set_viewport_size({"width": side, "height": side})
    for kcal, chickens in PLATES.items():
        square = scene(kcal, chickens).replace(
            'width="960" height="540" viewBox="0 0 960 540"',
            f'width="{side}" height="{side}" viewBox="{CX - side / 2} {CY - side / 2 + 4} {side} {side}"',
        )
        page.set_content(f'<body style="margin:0;background:transparent">{square}</body>')
        page.wait_for_timeout(300)
        page.screenshot(path=HERE / f"assets/plate-{kcal}.png", omit_background=True)
        if kcal == 850:  # the same plate with a soft shadow, for white slides
            page.set_content(
                f'<body style="margin:0;background:transparent">{square.replace("#0C1A13", "#DDE3DA")}</body>'
            )
            page.wait_for_timeout(300)
            page.screenshot(path=HERE / "assets/plate-light.png", omit_background=True)
    browser.close()
