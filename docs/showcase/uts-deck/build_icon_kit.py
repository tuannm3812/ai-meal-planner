"""Build the deck's icon kit: Material Symbols Rounded glyphs on one tile, in the deck's colours.

Run from this folder:  python3 build_icon_kit.py
Every icon is a bare 48-unit SVG glyph in one tone: no tile, no background. Layouts pick a file by glyph and tone hex (see dot_icon in project_layouts.py).
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / 'showcase/slides/assets/icons'
OUT = HERE / 'assets/icons/kit'
GLYPHS = ['balance', 'block', 'calculate', 'check_circle', 'cloud_upload', 'fact_check', 'fitness_center',
          'flag', 'group', 'inventory_2', 'lock', 'monitor_weight', 'no_food', 'person', 'rice_bowl', 'science',
          'search', 'shopping_basket', 'shopping_cart', 'skillet', 'verified', 'visibility', 'receipt_long',
          'restaurant', 'menu_book', 'egg', 'nutrition', 'grocery', 'soup_kitchen', 'storefront']
TONES = {'#526174': 'slate', '#32658A': 'blue', '#825578': 'plum', '#896521': 'ochre', '#21918C': 'teal',
         '#89949D': 'grey', '#FFFFFF': 'white', '#1B2430': 'ink'}


def glyph(name):
    return re.search(r'd="([^"]+)"', (SOURCE / f'{name}.svg').read_text()).group(1)


def tile(name, tone):
    k = 48 / 960
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">'
            f'<g transform="scale({k}) translate(0 960)" fill="{tone}"><path d="{glyph(name)}"/></g>'
            f'</svg>\n')


if __name__ == '__main__':
    OUT.mkdir(parents=True, exist_ok=True)
    for name in GLYPHS:
        for hexcode, tone in TONES.items():
            (OUT / f'{name}-{tone}.svg').write_text(tile(name, hexcode))
    print(f'{len(GLYPHS) * len(TONES)} icons in {OUT}')
