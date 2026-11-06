# ruff: noqa: E501  (inline SVG and HTML mockups)
"""Render image-led cover ideas. The plate is a drawn stand-in for a real photo.

Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" \\
      python docs/showcase/slides/cover-concepts/build_image_concepts.py
"""

import math
import random
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FONTS = (HERE / "../../fonts").resolve().as_uri()
MARK = (
    (HERE / "../assets/logo-mark-dark.svg")
    .read_text()
    .replace('width="64" height="64"', 'width="28" height="28"')
)
BASE = f"""<style>
@font-face{{font-family:G;font-weight:400;src:url({FONTS}/google-sans-latin-400-normal.woff2)}}
@font-face{{font-family:G;font-weight:500;src:url({FONTS}/google-sans-latin-500-normal.woff2)}}
@font-face{{font-family:G;font-weight:700;src:url({FONTS}/google-sans-latin-700-normal.woff2)}}
*{{margin:0;box-sizing:border-box}}
body{{width:960px;height:540px;overflow:hidden;background:#15291F;color:#fff;font-family:G;position:relative}}
.a{{position:absolute}}
.t{{font:700 50px/1.05 G;letter-spacing:-.01em}}
.s{{font:400 17px/1.4 G;color:#C9D3CC}}
.l{{font:500 13px/1.25 G;color:#fff}}.l span{{display:block;color:#C9D3CC;font-weight:400;font-size:11px}}
</style>
<div class=a style="left:43.5px;top:36px;display:flex;gap:10px;align-items:center;font:700 16px G">{MARK}AI Meal Planner</div>"""


def plate(cx, cy, r, seed=7):
    rnd = random.Random(seed)
    inner = r * 0.72
    out = [
        f'<circle cx="{cx}" cy="{cy + 8}" r="{r + 4}" fill="#0C1A13"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#FAFAF6"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{inner + 12}" fill="#EFEFE8"/>',
    ]

    def spot():
        a, d = rnd.uniform(0, 2 * math.pi), inner * math.sqrt(rnd.random())
        return cx + d * math.cos(a), cy + d * math.sin(a)

    for _ in range(1500):
        x, y = spot()
        c = rnd.choice(["#F3E2B8", "#EBD49C", "#E5C988", "#F7EBCB"])
        out.append(
            f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 0.03:.1f}" ry="{r * 0.012:.1f}" fill="{c}" transform="rotate({rnd.randint(0, 180)} {x:.1f} {y:.1f})"/>'
        )
    for _ in range(26):
        x, y = spot()
        s = r * rnd.uniform(0.05, 0.085)
        out.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{s * 1.5:.1f}" height="{s:.1f}" rx="{s / 3:.1f}" fill="{rnd.choice(["#D9B27C", "#C99A5E", "#E4C493"])}" transform="rotate({rnd.randint(0, 180)} {x:.1f} {y:.1f})"/>'
        )
    for _ in range(36):
        x, y = spot()
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * 0.024:.1f}" fill="{rnd.choice(["#5E9A3A", "#6FAE45"])}"/>'
        )
    for _ in range(26):
        x, y = spot()
        s = r * 0.04
        out.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{s:.1f}" height="{s:.1f}" rx="1.5" fill="#E8833A"/>'
        )
    for _ in range(16):
        x, y = spot()
        out.append(
            f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="{r * 0.06:.1f}" ry="{r * 0.035:.1f}" fill="#F6D25A" transform="rotate({rnd.randint(0, 180)} {x:.1f} {y:.1f})"/>'
        )
    return "".join(out)


def callout(x1, y1, x2, y2):
    return f'<circle cx="{x1}" cy="{y1}" r="4" fill="#fff"/><path d="M{x1} {y1}L{x2} {y2}" stroke="#fff" stroke-width="1.2"/>'


def label(x, y, a, b, align="left"):
    return f'<div class="a l" style="left:{x}px;top:{y}px;width:150px;text-align:{align}">{a}<span>{b}</span></div>'


def annotated():
    cx, cy = 650, 280
    lines = (
        callout(610, 190, 500, 118)
        + callout(720, 200, 812, 118)
        + callout(600, 345, 500, 432)
        + callout(705, 360, 812, 432)
    )
    labels = (
        label(350, 104, "Chicken breast, 100 g", "Estimated", "right")
        + label(820, 104, "Egg, 50 g", "Reference")
        + label(350, 418, "Cooked rice, 220 g", "Estimated", "right")
        + label(820, 418, "Vegetables, 115 g", "Reference")
    )
    return f"""{BASE}<svg class=a style="inset:0" width="960" height="540">{plate(cx, cy, 200)}{lines}</svg>{labels}
<div class="a t" style="left:43.5px;top:176px;width:310px;font-size:44px">What's really on your plate?</div>
<div class="a s" style="left:43.5px;top:318px;width:290px;font-size:15px">Say what you crave. Get one meal sized to you, and see where every number comes from.</div>"""


def checkout():
    rows = [
        ("Chicken breast 500 g", "$7.80"),
        ("Cooked white rice", "$3.20"),
        ("Whole egg", "$3.50"),
        ("Mixed vegetables", "$3.50"),
        ("Sesame oil", "$3.50"),
        ("Soy sauce 250 ml", "$3.00"),
    ]
    items = "".join(
        f'<div style="display:flex;justify-content:space-between;margin-top:8px"><span>{a}</span><span>{b}</span></div>'
        for a, b in rows
    )
    return f"""{BASE}<svg class=a style="inset:0" width="960" height="540">{plate(560, 300, 215, 11)}</svg>
<div class="a t" style="left:43.5px;top:110px;width:330px">From craving to checkout.</div>
<div class=a style="left:43.5px;top:262px;width:370px;height:58px;background:#fff;border-radius:30px;color:#15291F;display:flex;align-items:center;padding:0 24px;font:400 20px G">chicken fried rice<span style="color:#C8431F">|</span></div>
<div class="a s" style="left:43.5px;top:342px;width:310px;font-size:15px">One meal sized to you, with the shopping list already written.</div>
<div class=a style="left:716px;top:120px;width:206px;height:262px;background:#fff;color:#15291F;padding:20px 18px;font:400 12px G;transform:rotate(3deg)">
<div style="font:700 15px G">Shopping list</div>{items}
<div style="display:flex;justify-content:space-between;margin-top:16px;padding-top:10px;border-top:1px dashed #9AA5A0;font:700 14px G"><span>Estimated</span><span>$24.50</span></div></div>"""


def question():
    return f"""{BASE}<svg class=a style="inset:0" width="960" height="540">{plate(480, 620, 400, 5)}</svg>
<div class="a t" style="left:0;width:960px;top:84px;text-align:center;font-size:62px">What should I eat tonight?</div>
<div class="a s" style="left:0;width:960px;top:168px;text-align:center">One craving in. One meal, sized to you, out.</div>"""


def call2(x1, y1, x2, y2):
    return (
        f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#15291F" stroke-width="3.5"/>'
        f'<path d="M{x1} {y1}L{x2} {y2}" stroke="#fff" stroke-width="1.3"/>'
        f'<circle cx="{x1}" cy="{y1}" r="5.5" fill="#fff" stroke="#15291F" stroke-width="2"/>'
    )


def receipt_list(rows):
    items = "".join(
        f'<div style="display:flex;justify-content:space-between;margin-top:6px"><span>{a}</span><span>{b}</span></div>'
        for a, b in rows
    )
    return f"""<div class=a style="left:750px;top:62px;width:176px;height:216px;background:#fff;color:#15291F;padding:16px 14px;font:400 10.5px M;transform:rotate(3deg)">
<div style="font:700 12px M;letter-spacing:.06em">SHOPPING LIST</div>{items}
<div style="display:flex;justify-content:space-between;margin-top:12px;padding-top:8px;border-top:1px dashed #15291F;font:700 11.5px M"><span>ESTIMATED</span><span>$24.50</span></div></div>"""


def combined():
    """The question leads, the craving answers it, the plate proves it, the list finishes it."""
    rows = [
        ("Chicken breast", "$7.80"),
        ("Cooked rice", "$3.20"),
        ("Whole egg", "$3.50"),
        ("Vegetables", "$3.50"),
        ("Sesame oil", "$3.50"),
        ("Soy sauce", "$3.00"),
    ]
    rows = [(a.upper(), b) for a, b in rows]
    lines = call2(560, 215, 508, 118) + call2(530, 400, 366, 470) + call2(690, 420, 800, 470)
    labels = (
        label(352, 88, "Chicken breast, 100 g", "Estimated", "right")
        + label(210, 458, "Cooked rice, 220 g", "Estimated", "right")
        + label(806, 458, "Vegetables, 115 g", "Reference")
    )
    extra = f"""<style>
@font-face{{font-family:M;font-weight:400;src:url({FONTS}/google-sans-code-latin-400-normal.woff2)}}
@font-face{{font-family:M;font-weight:700;src:url({FONTS}/google-sans-code-latin-700-normal.woff2)}}
</style>"""
    return f"""{BASE}{extra}<svg class=a style="inset:0" width="960" height="540">{plate(610, 330, 232, 11)}{lines}</svg>{labels}
<div class="a t" style="left:43.5px;top:92px;width:300px;font-size:46px">What should I eat tonight?</div>
<div class=a style="left:43.5px;top:262px;width:300px;height:50px;background:#fff;border-radius:26px;color:#15291F;display:flex;align-items:center;padding:0 22px;font:400 18px G">chicken fried rice<span style="color:#C8431F">|</span></div>
<div class="a s" style="left:43.5px;top:328px;width:280px;font-size:14px">One meal sized to you, every number explained, the shopping list ready.</div>
<div class=a style="left:540px;top:86px;width:150px;background:#1B5E3F;color:#fff;border-radius:16px;padding:6px 0;text-align:center;font:700 13px G">694 kcal, target 691</div>
{receipt_list(rows)}"""


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=2)
    for name, html in (
        ("image-1-annotated", annotated()),
        ("image-2-checkout", checkout()),
        ("image-3-question", question()),
        ("image-4-combined", combined()),
    ):
        path = HERE / f"{name}.html"
        path.write_text(f"<!doctype html><meta charset=utf-8>{html}")
        page.goto(path.as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        page.screenshot(path=HERE / f"concept-{name}.png")
        path.unlink()
    browser.close()
