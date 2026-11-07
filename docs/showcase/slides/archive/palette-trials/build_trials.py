# ruff: noqa: E501  (inline HTML mockups)
"""Render colour theme trials on three real slide layouts. Run from the repo root:

    uv run --no-project --with "playwright==1.60.0" --with pillow \\
      python docs/showcase/slides/palette-trials/build_trials.py
"""

from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
FONTS = (HERE / "../../fonts").resolve().as_uri()
SCREEN = (HERE / "../captures/2026-11-06-3-plan.jpg").resolve().as_uri()
THEMES = {
    "a-garden": dict(
        name="A. Garden green",
        primary="#1B5E3F",
        dark="#15291F",
        accent="#C8431F",
        panel="#EEF4EF",
        text="#15291F",
        grey="#4B5B52",
    ),
    "b-tomato": dict(
        name="B. Tomato kitchen",
        primary="#B23A17",
        dark="#5E1F0D",
        accent="#2F6B4F",
        panel="#FBF1EA",
        text="#2A211C",
        grey="#5F5650",
    ),
    "c-blue": dict(
        name="C. Portfolio blue",
        primary="#0F4BEB",
        dark="#17243B",
        accent="#E6A23C",
        panel="#FAF7F0",
        text="#17243B",
        grey="#59636E",
    ),
    "d-teal": dict(
        name="D. Teal and saffron",
        primary="#0F5C63",
        dark="#0F3D44",
        accent="#D98E04",
        panel="#EAF4F3",
        text="#12303A",
        grey="#50636A",
    ),
}
BASE = f"""<style>
@font-face{{font-family:G;font-weight:400;src:url({FONTS}/google-sans-latin-400-normal.woff2)}}
@font-face{{font-family:G;font-weight:500;src:url({FONTS}/google-sans-latin-500-normal.woff2)}}
@font-face{{font-family:G;font-weight:700;src:url({FONTS}/google-sans-latin-700-normal.woff2)}}
*{{margin:0;box-sizing:border-box}}
body{{width:960px;height:540px;overflow:hidden;background:#fff;font-family:G;position:relative}}
.a{{position:absolute}}
</style>"""


def head(t, label, title, sub):
    return f"""<div class=a style="left:43.5px;top:22px;font:700 10px G;color:{t["text"]}">{label}</div>
<div class=a style="left:43.5px;top:46px;font:700 24px G;color:{t["primary"]}">{title}</div>
<div class=a style="left:43.5px;top:90px;font:400 12px G;color:{t["grey"]}">{sub}</div>
<div class=a style="left:43.5px;top:502px;font:400 10px G;color:{t["grey"]}">AI Meal Planner</div>"""


def cover(t):
    return f"""<body style="background:{t["dark"]}"><div class=a style="left:60px;top:170px;font:700 58px G;color:#fff">AI Meal Planner</div>
<div class=a style="left:60px;top:250px;font:400 24px/1.35 G;color:#fff">Say what you crave.<br>Get a meal that <b style="color:{t["accent"] if t["accent"] != "#2F6B4F" else "#F2B8A0"}">fits you</b>.</div>
<div class=a style="left:60px;top:345px;font:400 13px G;color:#ffffffcc">A multi-agent meal planner, a portfolio project by Mike</div>"""


def results(t):
    bars = "".join(
        f'<div class=a style="left:{70 + i * 140}px;top:{340 - v * 2.2:.0f}px;width:92px;height:{v * 2.2:.0f}px;background:{t["primary"] if i else "#9AA5A0"}"></div>'
        f'<div class=a style="left:{70 + i * 140}px;top:{314 - v * 2.2:.0f}px;width:92px;text-align:center;font:700 16px G;color:{t["text"]}">{v}</div>'
        f'<div class=a style="left:{50 + i * 140}px;top:348px;width:132px;text-align:center;font:400 10px G;color:{t["grey"]}">{n}</div>'
        for i, (n, v) in enumerate(
            [
                ("First run", 10),
                ("Portion balancing", 41),
                ("Honest fallback", 47),
                ("Fat and rounding", 72),
            ]
        )
    )
    card = "".join(
        f'<div class=a style="left:{43.5 + i * 205}px;top:398px;width:197px;height:72px;background:{t["panel"]};border-radius:12px;padding:12px"><div style="font:700 16px G;color:{t["text"]}">{a}</div><div style="font:400 12px G;color:{t["grey"]}">{b}</div></div>'
        for i, (a, b) in enumerate(
            [
                ("0.3%", "median deviation"),
                ("9.9%", "worst deviation"),
                ("5 of 5", "guardrails hold"),
            ]
        )
    )
    take = "".join(
        f'<div class=a style="left:666px;top:{y}px;width:12px;height:12px;border-radius:9px;background:{t["accent"]}"></div><div class=a style="left:684px;top:{y - 2}px;width:232px;font:400 12px/1.35 G;color:{t["grey"]}"><b style="color:{t["text"]}">{h}</b><br>{b}</div>'
        for y, h, b in [
            (
                132,
                "61 plans match; 11 are fallbacks",
                "Both pass, but a fallback isn't what was asked for.",
            ),
            (222, "68 of 72 include an estimate", "The benchmark runs without provider keys."),
        ]
    )
    return (
        head(
            t,
            "EVIDENCE &gt; RESULTS",
            "Three fixes took the planner from 10 to 72 of 72",
            "Plans meeting the targets on the project's own benchmark.",
        )
        + bars
        + card
        + take
    )


def flow(t):
    steps = "".join(
        f'<div class=a style="left:640px;top:{y}px;width:276px;height:96px;background:{t["panel"]};border-radius:12px;padding:12px"><div style="font:700 16px G;color:{t["primary"]}">{h}</div><div style="font:400 12px G;color:{t["grey"]};margin-top:3px">{b}</div></div>'
        for y, h, b in [
            (130, "You", "Body, goal and what to avoid"),
            (238, "Craving", "What you feel like eating"),
            (346, "Your plan", "One meal and a shopping list"),
        ]
    )
    return (
        head(
            t,
            "SOLUTION &gt; THE FLOW",
            "One craving in, one meal and a shopping list out",
            "Three steps in the React app, with its own colours.",
        )
        + f'<img class=a src="{SCREEN}" style="left:43.5px;top:130px;width:570px;border:1px solid #DDE3DA">'
        + steps
    )


with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 960, "height": 540}, device_scale_factor=1)
    rows = []
    for key, t in THEMES.items():
        tiles = []
        for i, fn in enumerate((cover, results, flow)):
            path = HERE / "t.html"
            path.write_text(f"<!doctype html><meta charset=utf-8>{BASE}{fn(t)}")
            page.goto(path.as_uri())
            page.evaluate("document.fonts.ready")
            page.wait_for_timeout(150)
            shot = HERE / f"t{i}.png"
            page.screenshot(path=shot)
            tiles.append(Image.open(shot).convert("RGB"))
            path.unlink()
        sheet = Image.new("RGB", (960 * 3 + 40, 540), "#FFFFFF")
        for i, tile in enumerate(tiles):
            sheet.paste(tile, (i * 980, 0))
        sheet.save(HERE / f"theme-{key}.png")
        rows.append(sheet)
        for i in range(3):
            (HERE / f"t{i}.png").unlink()
    browser.close()
    all_ = Image.new("RGB", (2920, 540 * 4 + 60), "#8A8F8C")
    for i, row in enumerate(rows):
        all_.paste(row, (0, i * 560))
    all_.resize((1460, (540 * 4 + 60) // 2)).save(HERE / "all-themes.png")


def lum(h):
    c = [int(h[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


for t in THEMES.values():
    ratio = 1.05 / (lum(t["primary"]) + 0.05)
    ratio2 = 1.05 / (lum(t["accent"]) + 0.05)
    print(t["name"], f"primary on white {ratio:.1f}:1, accent on white {ratio2:.1f}:1")
