# ruff: noqa: E501  (inline SVG and HTML mockups)
"""Render the refined logo options at real sizes. Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" \\
      python docs/showcase/slides/logo-concepts/build_logos.py
"""

import math
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FONTS = (HERE / "../../fonts").resolve().as_uri()
GREEN, TOMATO, INK = "#1B5E3F", "#C8431F", "#15291F"


def arc(r, start, end):
    a, b = (math.radians(v - 90) for v in (start, end))
    big = 1 if end - start > 180 else 0
    return f"M{32 + r * math.cos(a):.2f} {32 + r * math.sin(a):.2f}A{r} {r} 0 {big} 1 {32 + r * math.cos(b):.2f} {32 + r * math.sin(b):.2f}"


def svg(body, size):
    return f'<svg width="{size}" height="{size}" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">{body}</svg>'


def current(ring=TOMATO):
    return f'<circle cx="32" cy="32" r="27" fill="none" stroke="{ring}" stroke-width="6"/><circle cx="32" cy="32" r="13" fill="{TOMATO}"/>'


def refined(ring=GREEN):
    """A. The same plate, cleaned up: green rim, tomato centre, more air between them."""
    return f'<circle cx="32" cy="32" r="28" fill="none" stroke="{ring}" stroke-width="5"/><circle cx="32" cy="32" r="14" fill="{TOMATO}"/>'


def tomato(ring=GREEN):
    """B. A green rim with a leaf: the plate also reads as a tomato seen from above."""
    leaf = "M32 18c1-7 6-11 13-12 0 7-4 12-13 12z"
    return f'<circle cx="32" cy="35" r="25" fill="none" stroke="{ring}" stroke-width="5"/><circle cx="32" cy="35" r="12.5" fill="{TOMATO}"/><path d="{leaf}" fill="{ring}"/>'


def rim(ring=GREEN):
    """C. The rim split into three arcs: the macro balance every plan is judged on."""
    arcs = "".join(
        f'<path d="{arc(27.5, a + 9, b - 9)}" fill="none" stroke="{ring}" stroke-width="6" stroke-linecap="round"/>'
        for a, b in ((0, 101), (101, 266), (266, 360))
    )
    return f'{arcs}<circle cx="32" cy="32" r="13" fill="{TOMATO}"/>'


def calendar(ring=GREEN):
    """D. A plate on a calendar: planning a meal, in one shape."""
    return (
        f'<rect x="8" y="13" width="48" height="44" rx="10" fill="none" stroke="{ring}" stroke-width="5"/>'
        f'<path d="M22 7v11M42 7v11" stroke="{ring}" stroke-width="5" stroke-linecap="round"/>'
        f'<circle cx="32" cy="36" r="12" fill="{TOMATO}"/>'
    )


def tick(ring=GREEN):
    """E. A plate with a tick: this meal is sorted."""
    return (
        f'<circle cx="32" cy="32" r="28" fill="none" stroke="{ring}" stroke-width="5"/>'
        f'<path d="M20 33l9 9 16-19" fill="none" stroke="{TOMATO}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>'
    )


def fork(ring=GREEN):
    """F. A fork whose tines are bars: food and measured balance in one mark."""
    return (
        f'<path d="M15 35a17 12 0 0 0 34 0" fill="none" stroke="{ring}" stroke-width="6"/>'
        f'<rect x="12" y="20" width="6" height="16" rx="3" fill="{ring}"/>'
        f'<rect x="29" y="5" width="6" height="31" rx="3" fill="{TOMATO}"/>'
        f'<rect x="46" y="13" width="6" height="23" rx="3" fill="{ring}"/>'
        f'<rect x="29" y="46" width="6" height="16" rx="3" fill="{ring}"/>'
    )


def bowl(ring=GREEN):
    """G. A full bowl with a tick: a meal that is planned."""
    mark = "#15291F" if ring == "#FFFFFF" else "#FFFFFF"
    return (
        f'<circle cx="32" cy="23" r="13" fill="{TOMATO}"/>'
        f'<path d="M6 29h52a26 26 0 0 1-52 0z" fill="{ring}"/>'
        f'<path d="M22 40l7 7 13-14" fill="none" stroke="{mark}" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>'
    )


MEAL = [
    ("D. Plate on a calendar", calendar),
    ("E. Plate and tick", tick),
    ("F. Fork of bars", fork),
    ("G. Bowl and tick", bowl),
]
OPTIONS = [
    ("Current", current),
    ("A. Refined plate", refined),
    ("B. Plate and leaf", tomato),
    ("C. Balanced rim", rim),
]


def row(name, fn):
    small = "".join(
        f'<div style="width:{s + 16}px;text-align:center">{svg(fn(), s)}</div>'
        for s in (96, 48, 24, 16)
    )
    return f"""<div class=r><div class=n>{name}</div><div class=s>{small}</div>
<div class=w>{svg(fn(), 34)}<b>AI Meal Planner</b></div>
<div class="w d">{svg(fn("#FFFFFF"), 34)}<b>AI Meal Planner</b></div></div>"""


html = f"""<!doctype html><meta charset=utf-8><style>
@font-face{{font-family:G;font-weight:500;src:url({FONTS}/google-sans-latin-500-normal.woff2)}}
@font-face{{font-family:G;font-weight:700;src:url({FONTS}/google-sans-latin-700-normal.woff2)}}
body{{margin:0;width:1280px;background:#fff;font-family:G;color:{INK}}}
.r{{display:grid;grid-template-columns:190px 300px 1fr 1fr;align-items:center;gap:20px;padding:22px 32px;border-bottom:1px solid #DDE3DA}}
.n{{font:700 18px G}}.s{{display:flex;align-items:center}}
.w{{display:flex;align-items:center;gap:12px;font:700 24px G;padding:20px 22px;border-radius:12px;background:#fff;border:1px solid #DDE3DA}}
.d{{background:{INK};color:#fff;border-color:{INK}}}
</style>"""
sheets = {"logo-options.png": OPTIONS, "logo-options-meal.png": MEAL}

for name, fn in OPTIONS[1:] + MEAL:
    (HERE / f"logo-{name[0].lower()}.svg").write_text(svg(fn(), 64) + "\n")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 400}, device_scale_factor=2)
    for out, options in sheets.items():
        path = HERE / "t.html"
        path.write_text(html + "".join(row(n, f) for n, f in options))
        page.goto(path.as_uri())
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(200)
        page.screenshot(path=HERE / out, full_page=True)
        path.unlink()
    browser.close()
