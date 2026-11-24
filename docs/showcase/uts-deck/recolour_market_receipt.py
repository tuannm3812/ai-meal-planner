"""Move the deck and poster from UTS palette A to the app's Market Receipt colours (DEC-44).

One fixed old-to-new map, applied to every source file that holds a colour; the build
regenerates storyline.json and the icon kit from them. Run from this folder:
    python3 recolour_market_receipt.py && python3 build_icon_kit.py
Each new value is a token in frontend/src/theme/tokens.js. The four section accents become
ink, cobalt, coral and the estimate yellow; Viridis stops snap to the app's macro colours.
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAP = {
    # neutrals
    '#1B2430': '#14213D', '#1D2229': '#14213D', '#3A4452': '#22325A',
    '#5A6370': '#55607A', '#89949D': '#8A93A8', '#BCC3CA': '#C3CADB', '#AEB6BF': '#B4BCCF',
    '#D8DEE3': '#D5DBE8', '#F4F5F6': '#F4F6FB', '#FBF8F1': '#F4F6FB', '#C9D3CC': '#C9D6F5',
    # section accents: slate -> raised ink, blue -> cobalt, plum -> coral, ochre -> estimate
    '#526174': '#22325A', '#EDF0F3': '#EEF1F7',
    '#32658A': '#2448C9', '#375A8C': '#2448C9', '#EAF0F6': '#E7EDFB',
    '#825578': '#C2361A', '#F3EDF3': '#FFEDE7',
    '#896521': '#6B4A00', '#F6F1E5': '#FFF1C2', '#B89245': '#E0A100', '#765718': '#6B4A00',
    # brand marks
    '#B8452E': '#D63C1A', '#C8431F': '#FF5A36', '#1B5E3F': '#2448C9',
    '#1F7A4F': '#2448C9', '#2E6B66': '#2A788E', '#3BBB75': '#22A884', '#E8F2F0': '#E7EDFB',
    # Viridis stops -> the app's macro colours
    '#3B528B': '#414487', '#21918C': '#2A788E', '#5EC962': '#22A884',
    # status
    '#B3261E': '#A1260E', '#F9E8E6': '#FDE3DC', '#E6F2F1': '#E3F4E8',
}
FILES = ['deck-kit.json', 'brief-content.json', 'project_layouts.py', 'build_icon_kit.py',
         'assets/figures/cover-motif.svg', *[f'assets/figures/shapes/{p.name}' for p in (HERE / 'assets/figures/shapes').glob('*.svg')],
         *[f'poster/{p.name}' for p in (HERE / 'poster').iterdir() if p.suffix in {'.css', '.json', '.py', '.svg'}]]
pattern = re.compile('|'.join(re.escape(k) for k in MAP), re.IGNORECASE)
for name in FILES:
    path = HERE / name
    text = path.read_text()
    new = pattern.sub(lambda m: MAP[m.group(0).upper()], text)
    if new != text:
        path.write_text(new)
        print('recoloured', name)
