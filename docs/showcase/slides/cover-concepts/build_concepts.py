# ruff: noqa: E501  (inline HTML mockups)
"""Render the cover concepts for Mike to choose from. Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" \\
      python docs/showcase/slides/cover-concepts/build_concepts.py
"""

import math
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FONTS = (HERE / "../../fonts").resolve().as_uri()
BASE = f"""<style>
@font-face{{font-family:B;font-weight:700;src:url({FONTS}/bricolage-grotesque-latin-700-normal.woff2)}}
@font-face{{font-family:B;font-weight:800;src:url({FONTS}/bricolage-grotesque-latin-800-normal.woff2)}}
@font-face{{font-family:I;font-weight:400;src:url({FONTS}/inter-latin-400-normal.woff2)}}
@font-face{{font-family:I;font-weight:600;src:url({FONTS}/inter-latin-600-normal.woff2)}}
*{{margin:0;box-sizing:border-box}}
body{{width:960px;height:540px;overflow:hidden;background:#15291F;color:#fff;font-family:I;position:relative}}
.brand{{position:absolute;left:43.5px;top:40px;display:flex;gap:10px;align-items:center;font:700 16px B}}
.title{{font:800 60px/1.02 B;letter-spacing:-.02em}}
.tag{{font:400 20px/1.35 I;color:#C9D3CC}}
.tag em{{font-style:normal;font-weight:600;color:#C8431F}}
.foot{{position:absolute;left:43.5px;bottom:40px;font:400 12px I;color:#C9D3CC}}
</style>"""
MARK = (
    '<svg width="26" height="26" viewBox="0 0 64 64"><circle cx="32" cy="32" r="27" fill="none"'
    ' stroke="#C8431F" stroke-width="6"/><circle cx="32" cy="32" r="13" fill="#C8431F"/></svg>'
)
BRAND = f'<div class="brand">{MARK}AI Meal Planner</div>'
FOOT = '<div class="foot">A multi-agent meal planner, a portfolio project by Mike</div>'


def arc(cx, cy, r, start, end):
    a, b = (math.radians(v - 90) for v in (start, end))
    big = 1 if end - start > 180 else 0
    x1, y1, x2, y2 = (
        cx + r * math.cos(a),
        cy + r * math.sin(a),
        cx + r * math.cos(b),
        cy + r * math.sin(b),
    )
    return f"M{x1:.1f} {y1:.1f}A{r} {r} 0 {big} 1 {x2:.1f} {y2:.1f}"


def plate():
    """A plate seen from above: the plate mark grown up, its rim the real 28/46/26 split."""
    cx, cy, r = 742, 270, 232
    segs, angle, out = [(28, "#2F6FAB"), (46, "#9A6A12"), (26, "#7A4E9C")], 0, ""
    for share, colour in segs:
        sweep = share * 3.6
        out += f'<path d="{arc(cx, cy, r, angle + 2, angle + sweep - 2)}" fill="none" stroke="{colour}" stroke-width="30" stroke-linecap="round"/>'
        angle += sweep
    return f"""{BASE}{BRAND}
<svg style="position:absolute;inset:0" width="960" height="540">
<circle cx="{cx}" cy="{cy}" r="{r + 40}" fill="#F6F7F2"/>
<circle cx="{cx}" cy="{cy}" r="{r - 40}" fill="#fff" stroke="#DDE3DA"/>
<circle cx="{cx}" cy="{cy}" r="96" fill="#C8431F"/>
<text x="{cx}" y="{cy + 2}" text-anchor="middle" font-family="B" font-weight="800" font-size="40" fill="#fff">694</text>
<text x="{cx}" y="{cy + 26}" text-anchor="middle" font-family="I" font-size="14" fill="#fff">kcal</text>
<g fill="none">{out}</g></svg>
<div style="position:absolute;left:43.5px;top:170px;width:400px">
<div class="title">Say what you crave.</div>
<div class="tag" style="margin-top:18px">Get a meal that <em>fits you</em>.</div>
<div style="font:400 12px I;color:#C9D3CC;margin-top:14px">Plate rim: a real plan's 28% protein, 46% carbs, 26% fat.</div></div>{FOOT}"""


def product():
    """The real plan screen, cropped off the slide edge."""
    img = (HERE / "../captures/2026-11-06-3-plan-full.png").resolve().as_uri()
    return f"""{BASE}{BRAND}
<div style="position:absolute;left:43.5px;top:170px;width:390px">
<div class="title">Say what you crave.</div>
<div class="tag" style="margin-top:18px">Get a meal that <em>fits you</em>.</div></div>{FOOT}
<div style="position:absolute;left:470px;top:56px;width:560px;height:520px;border-radius:16px;overflow:hidden;background:#F6F7F2">
<img src="{img}" style="width:100%;display:block;margin-top:-92px"></div>"""


def craving():
    """The whole product in one line: a craving goes in, a plan comes out."""
    chips = [
        ("694 kcal", "against a 691 kcal target"),
        ("28 / 46 / 26", "protein, carbs, fat %"),
        ("6 items", "on the shopping list"),
    ]
    cards = "".join(
        f'<div style="background:#fff;color:#15291F;border-radius:14px;padding:14px 16px;width:266px"><div style="font:700 24px B">{a}</div><div style="font:400 13px I;color:#4B5B52;margin-top:2px">{b}</div></div>'
        for a, b in chips
    )
    return f"""{BASE}{BRAND}
<div class="title" style="position:absolute;left:43.5px;top:96px;font-size:50px">Say what you crave.</div>
<div style="position:absolute;left:43.5px;top:176px;width:873px;height:84px;background:#fff;border-radius:42px;display:flex;align-items:center;justify-content:space-between;padding:0 12px 0 34px">
<span style="font:400 30px I;color:#15291F">chicken fried rice<span style="color:#C8431F">|</span></span>
<span style="background:#C8431F;border-radius:30px;padding:16px 28px;font:600 17px I">Plan my meal</span></div>
<div class="title" style="position:absolute;left:43.5px;top:286px;font-size:50px">Get a meal that <span style="color:#C8431F">fits you</span>.</div>
<div style="position:absolute;left:43.5px;top:366px;display:flex;gap:37px">{cards}</div>{FOOT}"""


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=2)
    for name, html in (("a-plate", plate()), ("b-product", product()), ("c-craving", craving())):
        path = HERE / f"concept-{name}.html"
        path.write_text(f"<!doctype html><meta charset=utf-8>{html}")
        page.goto(path.as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        page.screenshot(path=HERE / f"concept-{name}.png")
        path.unlink()
    browser.close()
