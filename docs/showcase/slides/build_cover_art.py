# ruff: noqa: E501  (inline SVG)
"""Paint the wordless cover plate: chicken fried rice from above, lit from the top left.

Writes assets/cover-art.png, a full-slide transparent layer. Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" python docs/showcase/slides/build_cover_art.py
"""

import math
import random
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
CX, CY, R = 610, 330, 232
FOOD = R * 0.70
rnd = random.Random(21)


def mix(a, b, t):
    t = max(0.0, min(1.0, t))
    ca = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb, strict=True))


def edge(angle):
    """A slightly uneven mound outline, so the rice doesn't look stamped."""
    return FOOD * (
        1
        + 0.016 * math.sin(3 * angle + 1)
        + 0.011 * math.sin(7 * angle)
        + 0.007 * math.sin(11 * angle + 2)
    )


def blob():
    pts = []
    for i in range(72):
        a = 2 * math.pi * i / 72
        pts.append(f"{CX + edge(a) * math.cos(a):.1f},{CY + edge(a) * math.sin(a):.1f}")
    return " ".join(pts)


def spot(spread=0.97):
    a = rnd.uniform(0, 2 * math.pi)
    d = edge(a) * spread * math.sqrt(rnd.random())
    return CX + d * math.cos(a), CY + d * math.sin(a)


def light(x, y):
    """0 in shadow at the bottom right of the mound, 1 lit at the top left."""
    dx, dy = (x - CX) / FOOD, (y - CY) / FOOD
    height = max(0.0, 1 - (dx * dx + dy * dy))
    return max(0.0, min(1.0, 0.5 + 0.34 * (-dx - dy) * 0.7 + 0.32 * height - 0.12))


def grain(x, y, scale=1.0):
    t = light(x, y) + rnd.uniform(-0.12, 0.12)
    colour = mix("#C28A38", "#FFF0C0", t)
    if rnd.random() < 0.16:
        colour = mix(colour, "#A9662A", 0.5)  # soy-browned grains
    length, width = rnd.uniform(11, 15) * scale, rnd.uniform(4.2, 5.2) * scale
    angle = rnd.randint(0, 179)
    return (
        f'<g transform="translate({x:.1f} {y:.1f}) rotate({angle})">'
        f'<rect x="{-length / 2:.1f}" y="{-width / 2 + 0.9:.1f}" width="{length:.1f}" height="{width:.1f}" rx="{width / 2:.1f}" fill="#7A5427" opacity=".22"/>'
        f'<rect x="{-length / 2:.1f}" y="{-width / 2:.1f}" width="{length:.1f}" height="{width:.1f}" rx="{width / 2:.1f}" fill="{colour}"/>'
        f'<rect x="{-length / 2 + 2:.1f}" y="{-width / 2 + 0.8:.1f}" width="{length * 0.55:.1f}" height="{width * 0.28:.1f}" rx="1" fill="#fff" opacity=".35"/></g>'
    )


def cast(x, y, rx, ry, angle=0):
    return f'<ellipse cx="{x + 2:.1f}" cy="{y + 3:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="#4A2F12" opacity=".28" transform="rotate({angle} {x:.1f} {y:.1f})"/>'


def wobble(rx, ry, n=9, jitter=0.2):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n
        k = 1 + rnd.uniform(-jitter, jitter)
        pts.append((rx * k * math.cos(a), ry * k * math.sin(a)))
    d = f"M{(pts[0][0] + pts[-1][0]) / 2:.1f} {(pts[0][1] + pts[-1][1]) / 2:.1f}"
    for i, p in enumerate(pts):
        n2 = pts[(i + 1) % n]
        d += f"Q{p[0]:.1f} {p[1]:.1f} {(p[0] + n2[0]) / 2:.1f} {(p[1] + n2[1]) / 2:.1f}"
    return d + "z"


def chicken(x, y):
    rx, ry, a = rnd.uniform(15, 21), rnd.uniform(10, 13), rnd.randint(0, 179)
    path = wobble(rx, ry, 8, 0.16)
    streaks = "".join(
        f'<path d="M{rnd.uniform(-rx * 0.6, 0):.1f} {rnd.uniform(-ry * 0.5, ry * 0.5):.1f}q{rx * 0.4:.1f} {rnd.uniform(-3, 3):.1f} {rx * 0.8:.1f} 0" stroke="#A9672C" stroke-width="1.3" fill="none" opacity=".55"/>'
        for _ in range(3)
    )
    return cast(x, y, rx, ry, a) + (
        f'<g transform="translate({x:.1f} {y:.1f}) rotate({a})"><path d="{path}" fill="url(#chicken)"/>{streaks}'
        f'<path d="{wobble(rx * 0.5, ry * 0.35, 6, 0.1)}" transform="translate({-rx * 0.2:.1f} {-ry * 0.3:.1f})" fill="#fff" opacity=".22"/></g>'
    )


def egg(x, y):
    rx, ry, a = rnd.uniform(13, 19), rnd.uniform(6, 9), rnd.randint(0, 179)
    path = wobble(rx, ry, 7, 0.28)
    return cast(x, y, rx, ry, a) + (
        f'<g transform="translate({x:.1f} {y:.1f}) rotate({a})"><path d="{path}" fill="url(#egg)"/>'
        f'<path d="{wobble(rx * 0.55, ry * 0.35, 6, 0.2)}" transform="translate({-rx * 0.15:.1f} {-ry * 0.25:.1f})" fill="#FFF3B8" opacity=".75"/></g>'
    )


def carrot(x, y):
    s, a = rnd.uniform(8, 10.5), rnd.randint(0, 89)
    return cast(x, y, s * 0.7, s * 0.7) + (
        f'<g transform="translate({x:.1f} {y:.1f}) rotate({a})"><rect x="{-s / 2:.1f}" y="{-s / 2:.1f}" width="{s:.1f}" height="{s:.1f}" rx="2.2" fill="url(#carrot)"/>'
        f'<rect x="{-s / 2 + 1.2:.1f}" y="{-s / 2 + 1.2:.1f}" width="{s * 0.42:.1f}" height="{s * 0.28:.1f}" rx="1" fill="#FFD3A8" opacity=".7"/></g>'
    )


def pea(x, y):
    r = rnd.uniform(5, 6.4)
    return cast(x, y, r, r) + f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="url(#pea)"/>'


def scallion(x, y):
    r = rnd.uniform(4.2, 5.8)
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.8:.1f}" fill="#BFE08A" stroke="#5DA83A" stroke-width="1.6"/>'


def sesame(x, y):
    return f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="2.6" ry="1.5" fill="#FFF6DC" stroke="#B8914F" stroke-width=".4" transform="rotate({rnd.randint(0, 179)} {x:.1f} {y:.1f})"/>'


layers = []
for _ in range(2500):
    layers.append(grain(*spot(1.03)))
pieces = [chicken] * 18 + [egg] * 18 + [carrot] * 32 + [pea] * 34
rnd.shuffle(pieces)
for draw in pieces:
    layers.append(draw(*spot(0.9)))
for _ in range(150):
    layers.append(grain(*spot(0.94)))
for _ in range(16):
    layers.append(scallion(*spot(0.8)))
for _ in range(46):
    layers.append(sesame(*spot(0.85)))

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
<defs>
<radialGradient id="rim" cx=".38" cy=".32" r=".8"><stop offset="0" stop-color="#FFFFFF"/><stop offset=".72" stop-color="#F6F4EC"/><stop offset="1" stop-color="#DAD7CA"/></radialGradient>
<radialGradient id="well" cx=".42" cy=".38" r=".72"><stop offset="0" stop-color="#FBFAF5"/><stop offset=".82" stop-color="#F0EEE4"/><stop offset="1" stop-color="#D9D6C8"/></radialGradient>
<linearGradient id="chicken" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#EDC58A"/><stop offset=".55" stop-color="#CF8F48"/><stop offset="1" stop-color="#9E5F28"/></linearGradient>
<linearGradient id="egg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFE27A"/><stop offset="1" stop-color="#EFAE2D"/></linearGradient>
<linearGradient id="carrot" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F9A24E"/><stop offset="1" stop-color="#D5641B"/></linearGradient>
<radialGradient id="pea" cx=".35" cy=".3" r=".8"><stop offset="0" stop-color="#B9E07A"/><stop offset=".6" stop-color="#6DAE3F"/><stop offset="1" stop-color="#3F7E27"/></radialGradient>
<filter id="soft" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="softer" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
</defs>
<circle cx="{CX + 12}" cy="{CY + 18}" r="{R + 2}" fill="#050C08" opacity=".55" filter="url(#soft)"/>
<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#rim)"/>
<circle cx="{CX}" cy="{CY}" r="{R - 3}" fill="none" stroke="#fff" stroke-width="1.5" opacity=".8"/>
<circle cx="{CX}" cy="{CY}" r="{R * 0.8:.1f}" fill="url(#well)"/>
<circle cx="{CX}" cy="{CY}" r="{R * 0.8:.1f}" fill="none" stroke="#C9C6B6" stroke-width="1"/>
<polygon points="{blob()}" transform="translate(7 10)" fill="#6B5A3A" opacity=".4" filter="url(#softer)"/>
<polygon points="{blob()}" transform="translate({CX * 0.05:.1f} {CY * 0.05:.1f}) scale(.95)" fill="#D2A04E"/>
{"".join(layers)}
</svg>"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=2)
    page.set_content(f'<body style="margin:0;background:transparent">{svg}</body>')
    page.wait_for_timeout(300)
    page.screenshot(path=HERE / "assets/cover-art.png", omit_background=True)
    browser.close()
