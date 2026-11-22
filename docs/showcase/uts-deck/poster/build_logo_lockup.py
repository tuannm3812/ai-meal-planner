"""Write logo-lockup.svg: the AI Meal Planner mark and the UTS logo at one height, with a grey divider.

POSTER-TEMPLATE.md: the UTS logo is unaltered, square, at the top right; a partner or project logo sits to its left
at the same height with a thin grey divider. Run: python3 build_logo_lockup.py
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
BRAND = HERE.parent / 'assets' / 'brand'


def inner(svg: str) -> tuple[str, str]:
    view = re.search(r'viewBox="([^"]+)"', svg).group(1)
    body = re.sub(r'^.*?<svg[^>]*>', '', svg, flags=re.S)
    return view, body.rsplit('</svg>', 1)[0]


mark_view, mark = inner((BRAND / 'ai-meal-planner-mark.svg').read_text())
uts_view, uts = inner((BRAND / 'uts-logo.svg').read_text())
# Units are mm at poster scale: two 32 mm squares, 8 mm clear space each side of a 1 mm divider (POSTER-TEMPLATE.md).
H, GAP, RULE = 32, 8, 1
W = H + GAP + RULE + GAP + H
out = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm">'
       f'<svg x="0" y="0" width="{H}" height="{H}" viewBox="{mark_view}">{mark}</svg>'
       f'<rect x="{H + GAP}" y="0" width="{RULE}" height="{H}" fill="#D8DEE3"/>'
       f'<svg x="{H + GAP + RULE + GAP}" y="0" width="{H}" height="{H}" viewBox="{uts_view}">{uts}</svg></svg>\n')
(HERE / 'logo-lockup.svg').write_text(out)
print('wrote', HERE / 'logo-lockup.svg')
