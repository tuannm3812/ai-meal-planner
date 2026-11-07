# ruff: noqa: E501  (inline SVG)
"""Paint the four flat kitchen station illustrations for slide 6. Run from the repo root:

uv run --no-project --with "playwright==1.60.0" python docs/showcase/slides/build_station_art.py
"""

import random
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
rnd = random.Random(3)


def rice(cx, cy, rx, ry, n=70):
    out = ""
    for _ in range(n):
        x, y = cx + rnd.uniform(-rx, rx), cy + rnd.uniform(-ry, ry)
        if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 < 1:
            out += f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="3.4" ry="1.5" fill="{rnd.choice(["#F7EBCB", "#EBD49C", "#E5C988"])}" transform="rotate({rnd.randint(0, 179)} {x:.1f} {y:.1f})"/>'
    return out


SCALE = f"""<rect x="52" y="74" width="96" height="20" rx="6" fill="#1B5E3F"/>
<rect x="88" y="58" width="24" height="18" fill="#2F7A55"/>
<ellipse cx="100" cy="54" rx="58" ry="10" fill="#15291F"/>
<ellipse cx="100" cy="46" rx="50" ry="13" fill="#FAFAF6"/>
<path d="M60 46a40 26 0 0 1 80 0z" fill="#E5C988"/>{rice(100, 34, 36, 12)}
<circle cx="100" cy="84" r="6" fill="#FAFAF6"/><path d="M100 84l3-4" stroke="#C8431F" stroke-width="2"/>"""

PAN = f"""<path d="M70 18q-6-8 0-14M100 16q-6-8 0-14M130 18q-6-8 0-14" fill="none" stroke="#C8431F" stroke-width="3" stroke-linecap="round" opacity=".55"/>
<path d="M36 48h128a12 40 0 0 1-12 36H48a12 40 0 0 1-12-36z" fill="#15291F"/>
<rect x="158" y="50" width="42" height="9" rx="4.5" fill="#15291F"/>
<ellipse cx="100" cy="48" rx="64" ry="14" fill="#2B3F35"/>
<ellipse cx="100" cy="46" rx="56" ry="11" fill="#E5C988"/>{rice(100, 45, 54, 10, 90)}
<circle cx="78" cy="44" r="4" fill="#5E9A3A"/><circle cx="120" cy="48" r="4" fill="#5E9A3A"/><rect x="96" y="40" width="9" height="9" rx="2" fill="#E8833A"/><rect x="60" y="48" width="14" height="8" rx="3" fill="#C99A5E"/><rect x="128" y="39" width="14" height="8" rx="3" fill="#C99A5E"/>"""

TASTER = """<rect x="46" y="8" width="84" height="88" rx="8" fill="#7A4A0C"/><rect x="53" y="16" width="70" height="74" rx="4" fill="#FAFAF6"/><rect x="72" y="3" width="32" height="12" rx="4" fill="#15291F"/>
<circle cx="64" cy="33" r="5" fill="#1B5E3F"/><rect x="74" y="30" width="40" height="6" rx="3" fill="#DDE3DA"/>
<circle cx="64" cy="52" r="5" fill="#1B5E3F"/><rect x="74" y="49" width="34" height="6" rx="3" fill="#DDE3DA"/>
<circle cx="64" cy="71" r="5" fill="#F2C23E"/><rect x="74" y="68" width="38" height="6" rx="3" fill="#DDE3DA"/>
<circle cx="132" cy="58" r="24" fill="#FBEBD6" stroke="#15291F" stroke-width="7"/><path d="M149 76l20 20" stroke="#15291F" stroke-width="9" stroke-linecap="round"/>
<path d="M122 62q10-18 20-8q-2 16-20 8z" fill="#5E9A3A"/>"""

BASKET = """<path d="M78 40q-6-26 8-34q6 20 0 34z" fill="#5E9A3A"/><path d="M104 44l16-36q10 4 6 12l-12 28z" fill="#E8833A"/><path d="M118 8q4-8 12-6q0 8-8 10z" fill="#5E9A3A"/>
<circle cx="74" cy="46" r="15" fill="#C8431F"/><rect x="92" y="18" width="14" height="30" rx="4" fill="#F2C23E"/><circle cx="130" cy="46" r="14" fill="#F6D25A"/>
<path d="M38 46h124l-14 50H52z" fill="#15291F"/><path d="M38 46h124" stroke="#15291F" stroke-width="8" stroke-linecap="round"/>
<path d="M72 58l6 28M100 58v28M128 58l-6 28" stroke="#DDE3DA" stroke-width="4" stroke-linecap="round"/>"""

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 200, "height": 100}, device_scale_factor=3)
    for name, art in (("scale", SCALE), ("pan", PAN), ("taster", TASTER), ("basket", BASKET)):
        page.set_content(
            f'<body style="margin:0;background:transparent"><svg xmlns="http://www.w3.org/2000/svg" width="200" height="100" viewBox="0 0 204 100">{art}</svg></body>'
        )
        page.wait_for_timeout(100)
        page.screenshot(path=HERE / f"assets/station-{name}.png", omit_background=True)
    browser.close()
