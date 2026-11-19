"""Build the deck's icon kit: Material Symbols Rounded glyphs on one tile, in the deck's colours.

Run from this folder:  python3 build_icon_kit.py
Every icon is a 48-unit SVG: a white rounded tile, a thin edge in the tone, and the glyph in the
tone at 28 units. Layouts pick a file by glyph and tone hex (see dot_icon in project_layouts.py).
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'showcase/slides/assets/icons'
OUT = HERE / 'assets/icons/kit'
GLYPHS = ['balance', 'block', 'calculate', 'check_circle', 'cloud_upload', 'fact_check', 'fitness_center',
          'flag', 'group', 'inventory_2', 'lock', 'monitor_weight', 'no_food', 'person', 'rice_bowl', 'science',
          'search', 'shopping_basket', 'shopping_cart', 'skillet', 'verified', 'visibility', 'receipt_long',
          'restaurant', 'egg', 'nutrition', 'grocery', 'soup_kitchen', 'storefront']
TONES = {'#526174': 'slate', '#32658A': 'blue', '#825578': 'plum', '#896521': 'ochre', '#21918C': 'teal',
         '#89949D': 'grey'}


def glyph(name):
    return re.search(r'd="([^"]+)"', (SOURCE / f'{name}.svg').read_text()).group(1)


def tile(name, tone):
    k = 28 / 960
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">'
            f'<rect x="0.75" y="0.75" width="46.5" height="46.5" rx="11" fill="#FFFFFF" stroke="{tone}" '
            f'stroke-opacity="0.45" stroke-width="1.5"/>'
            f'<g transform="translate(10 10) scale({k}) translate(0 960)" fill="{tone}"><path d="{glyph(name)}"/></g>'
            f'</svg>\n')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name in GLYPHS:
        for hexcode, tone in TONES.items():
            (OUT / f'{name}-{tone}.svg').write_text(tile(name, hexcode))
    print(f'{len(GLYPHS) * len(TONES)} icons in {OUT}')
