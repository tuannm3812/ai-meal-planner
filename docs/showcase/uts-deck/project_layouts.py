"""Project-owned layouts for the AI Meal Planner deck on the UTS kit.

Loaded through brief-content.json "project_layouts". Every word comes from the slide's fields; these functions add
geometry, colours, icons and images only. Kit rules kept: rails 43.5-919, content 132-476, kit type sizes,
neutral cards with the chapter accent as a top rule (structure only), Viridis for data, warm-yellow takeaway band.
Data colours are listed in DESIGN.project.md.
"""
import sys

sys.dont_write_bytecode = True

LEFT, RIGHT, TOP, END = 43.5, 919.0, 132.0, 476.0
W = RIGHT - LEFT
INK, BODY, CARD, HAIR, WHITE = '#14213D', '#55607A', '#F4F6FB', '#D5DBE8', '#FFFFFF'
ACCENT = {'slate': ('#22325A', '#EEF1F7'), 'blue': ('#2448C9', '#E7EDFB'), 'plum': ('#C2361A', '#FFEDE7'),
          'ochre': ('#6B4A00', '#FFF1C2')}
# Data colours (Viridis), one meaning each across the deck: see DESIGN.project.md.
V_DARK, V_BLUE, V_TEAL, V_GREEN = '#440154', '#414487', '#2A788E', '#22A884'
ESTIMATED, REFERENCE = V_DARK, V_TEAL
VIRIDIS4 = [V_DARK, V_BLUE, V_TEAL, V_GREEN]


def pale(slide):
    return ACCENT[slide.get('accent', 'slate')][1]
# Macro colours match the React app's tokens (frontend/src/theme/tokens.js, DEC-38).
PROTEIN, CARBS, FAT = '#440154', '#2A788E', '#22A884'


# -- primitives ---------------------------------------------------------------------------------
def need(L, raw, w, size, bold=False):
    return L.metrics.wrap(str(raw), w, size, bold=bold)[2] * size * 1.35


def put(L, p, raw, x, y, w, size=10, role='body', bold=False, align=None, h=None):
    h = need(L, raw, w, size, bold) if h is None else h
    L.text(p, raw, x, y, w, h, size, role, bold, align)
    return h


def paint(L, p, raw, x, y, w, size, colour, bold=False, align=None, h=None):
    text, spans, lines = L.metrics.wrap(str(raw), w, size, bold=bold)
    need_h = lines * size * 1.35
    p.text(text, x, y, w, h or need_h, size=size, color=colour, bold=bold, spans=spans, spacing=135, align=align)
    return need_h


def inked(L, p, raw, x, y, w, size=10, h=None, align=None):
    """Body text whose **key terms** are bold ink."""
    first = len(p.ops)
    used = put(L, p, raw, x, y, w, size, 'body', False, align, h)
    for op in p.ops[first:]:
        if op['op'] == 'style-text' and op.get('bold'):
            op['color'] = INK
    return used


def card(p, x, y, w, h, accent=None, fill=None, rule='top'):
    p.rect(x, y, w, h, fill or (ACCENT[accent][1] if accent else CARD))
    if accent:
        colour = ACCENT[accent][0]
        if rule == 'top':
            p.rect(x, y, w, 2.5, colour)
        else:
            p.rect(x, y, 3, h, colour)


def img(L, p, path, alt, x, y, w, h):
    L.image(p, {'path': path, 'alt': alt}, x, y, w, h)


TONE = {'#22325A': 'slate', '#2448C9': 'blue', '#C2361A': 'plum', '#6B4A00': 'ochre', '#2A788E': 'teal',
        '#8A93A8': 'grey', '#FFFFFF': 'white', '#14213D': 'ink'}


def dot_icon(L, p, glyph, colour, x, y, d=24, size=18):
    """A bare glyph from the deck's kit (build_icon_kit.py), sized to sit beside 12 pt text.

    The slot (x, y, d) is kept so callers' text offsets stay put; the glyph is centred in it.
    """
    s = min(size, d * 1.3)
    img(L, p, f'assets/icons/kit/{glyph}-{TONE[colour]}.svg', '', x + (d - s) / 2, y + (d - s) / 2, s, s)


def chip(L, p, text, x, y, w, h, colour=INK, fill=WHITE, size=10):
    p.rect(x, y, w, h, fill)
    paint(L, p, text, x + 4, y + (h - need(L, text, w - 8, size, True)) / 2, w - 8, size, colour, True, 'center')


def band(L, p, slide):
    text = slide.get('takeaway')
    if not text:
        return END
    from uts_kit.takeaway import inline_height
    h = inline_height(L, text, 875.5)
    L.band(p, text)
    return END - h


def accent(slide):
    return slide.get('accent', 'slate')


# -- 3: summary ---------------------------------------------------------------------------------
def mini_chart(L, p, c, x, y, w, ink):
    """A small unit chart under a finding: what the number looks like, not a second claim."""
    if c['kind'] == 'gap':
        lim = c['limit']
        mid = x + w / 2
        scale = (w / 2 - 4) / lim
        p.rect(x, y + 8, w, 12, WHITE)
        p.line(mid, y + 4, mid, y + 24, ink, .75)
        for v, colour, r, word in ((c['worst'], V_DARK, 3, 'worst'), (c['median'], V_TEAL, 5, 'median')):
            p.rect(mid + v * scale - r, y + 14 - r, 2 * r, 2 * r, colour, 'ELLIPSE')
            paint(L, p, word, mid + v * scale - 20, y - 8, 40, 8, colour, True, 'center')
        paint(L, p, f"-{lim}%", x, y + 26, 40, 8, BODY)
        paint(L, p, 'target', mid - 20, y + 26, 40, 8, BODY, False, 'center')
        paint(L, p, f"+{lim}%", x + w - 40, y + 26, 40, 8, BODY, False, 'right')
        return
    if c['kind'] == 'checks':
        for k in range(c['total']):
            dot_icon(L, p, 'check_circle', V_TEAL, x + k * 26, y + 2, 24, 22)
        return
    per_row, step = 24, w / 24
    for k in range(c['total']):
        cx, cy = x + (k % per_row) * step + step / 2, y + (k // per_row) * step + step / 2
        colour = V_DARK if k < c['first'] else V_GREEN
        p.rect(cx - step * .36, cy - step * .36, step * .72, step * .72, colour, 'ELLIPSE')
    if c.get('label'):
        paint(L, p, c['label'], x, y + 3 * step + 4, w, 8, BODY)


def mp_summary(L, p, slide):
    bottom = band(L, p, slide) - 14
    plates = slide['plates']
    p.rect(LEFT, TOP, W, 104, pale(slide))
    biggest = max(pl['kcal'] for pl in plates)
    for i, pl in enumerate(plates):
        x = LEFT + 14 + i * (W - 28) / 4
        d = 84 * (pl['kcal'] / biggest) ** .5
        img(L, p, pl['image'], pl['alt'], x + 42 - d / 2, TOP + 52 - d / 2, d, d)
        put(L, p, f"{pl['kcal']:,} kcal", x + 92, TOP + 22, 110, 18, 'ink', True)
        put(L, p, pl['protein'], x + 92, TOP + 46, 110, 10, 'ink', True)
        put(L, p, pl['who'], x + 92, TOP + 61, 112, 10, 'body')
    findings = slide['findings']
    gap = 16
    w = (W - gap * (len(findings) - 1)) / len(findings)
    y = TOP + 104 + 16
    h = bottom - y
    for i, f in enumerate(findings):
        x = LEFT + i * (w + gap)
        ink, fill = ACCENT[f['accent']]
        card(p, x, y, w, h, f['accent'], fill)
        dot_icon(L, p, f['icon'], ink, x + 14, y + 14, 24)
        paint(L, p, f['label'], x + 44, y + 19, w - 56, 12, ink, True)
        paint(L, p, f['value'], x + 14, y + 48, w - 28, 24, ink, True)
        inked(L, p, f['text'], x + 14, y + 80, w - 28, 10)
        if f.get('chart'):
            mini_chart(L, p, f['chart'], x + 14, bottom - 50, w - 28, ink)


# -- 4: problem ---------------------------------------------------------------------------------
def pin(L, p, n, x, y, r=9):
    p.rect(x - r - 2, y - r - 2, 2 * r + 4, 2 * r + 4, WHITE, 'ELLIPSE')
    p.rect(x - r, y - r, 2 * r, 2 * r, INK, 'ELLIPSE')
    paint(L, p, str(n), x - r, y - 6.5, 2 * r, 10, WHITE, True, 'center')


def row_visual(L, p, v, x, y, w, h):
    """The answer to a row's question, drawn from the offline run."""
    if v['kind'] == 'range':
        # One kcal scale from zero for both lines, so the meal reads as a share of a day.
        lab = 72
        sx = lambda k: x + lab + k / v['axis'] * (w - lab)
        y1, y2 = y + 10, y + 38
        for yy, word in ((y1, v['day_label']), (y2, 'One meal')):
            paint(L, p, word, x, yy - 1, lab - 6, 8, BODY, True)
            p.rect(sx(0), yy, sx(v['axis']) - sx(0), 8, WHITE)
        p.rect(sx(v['low']), y1, sx(v['high']) - sx(v['low']), 8, V_BLUE)
        p.rect(sx(v['mark']) - 4, y1 - 2, 8, 12, INK)
        paint(L, p, v['mark_label'], sx(v['mark']) - 60, y1 + 12, 120, 8, INK, True, 'center')
        p.rect(sx(0), y2, sx(v['meal']) - sx(0), 8, V_TEAL)
        paint(L, p, v['meal_label'], sx(v['meal']) + 8, y2 - 1, 70, 8, V_TEAL, True)
        paint(L, p, '0', sx(0), y2 + 12, 20, 8, BODY)
        paint(L, p, f"{v['low']:,}", sx(v['low']) - 20, y1 - 12, 40, 8, BODY, False, 'center')
        paint(L, p, f"{v['high']:,} kcal", sx(v['high']) - 50, y1 - 12, 60, 8, BODY, False, 'right')
        return
    if v['kind'] == 'swaps':
        ch = (h - 8) / 2
        for k, (who, was, now) in enumerate(v['items']):
            cy = y + k * (ch + 8)
            p.rect(x, cy, w, ch, WHITE)
            p.rect(x, cy, 3, ch, V_TEAL)
            paint(L, p, who.upper(), x + 10, cy + ch / 2 - 6, 52, 8, BODY, True)
            paint(L, p, was, x + 62, cy + ch / 2 - 7, 84, 10, BODY)
            p.connector(x + 150, cy + ch / 2, x + 166, cy + ch / 2)
            paint(L, p, now, x + 170, cy + ch / 2 - 7, w - 176, 10, INK, True)
        return
    p.rect(x, y, w, h, WHITE)
    items = v['items']
    col = (w - 116) / 2
    for k, (name, price) in enumerate(items):
        cx, cy = x + 10 + (k // 3) * (col + 6), y + 8 + (k % 3) * 15
        put(L, p, f'`{name.upper()}`', cx, cy, col - 40, 8, 'body')
        put(L, p, f'`{price}`', cx + col - 40, cy, 34, 8, 'body', False, 'right')
    tx = x + w - 96
    p.line(tx - 6, y + 8, tx - 6, y + h - 8, HAIR)
    put(L, p, f"`{v['total_label'].upper()}`", tx, y + h / 2 - 16, 88, 8, 'body', True)
    paint(L, p, v['total'], tx, y + h / 2 - 4, 88, 18, INK, True)


def mp_problem(L, p, slide):
    bottom = band(L, p, slide) - 14
    lw = 250
    p.rect(LEFT, TOP, lw, bottom - TOP, pale(slide))
    p.rect(LEFT + 14, TOP + 12, lw - 28, 28, WHITE)
    put(L, p, slide['craving'], LEFT + 18, TOP + 18, lw - 36, 12, 'ink', True, 'center')
    d = bottom - TOP - 82
    px, py = LEFT + (lw - d) / 2, TOP + 48
    img(L, p, slide['image']['path'], slide['image']['alt'], px, py, d, d)
    for n, (ix, iy) in enumerate(slide['pins'], 1):
        pin(L, p, n, px + ix / 1000 * d, py + iy / 1000 * d)
    put(L, p, slide['answer'], LEFT + 14, bottom - 26, lw - 28, 12, 'ink', True, 'center')
    x0 = LEFT + lw + 16
    rows = slide['rows']
    rh = (bottom - TOP - 10 * (len(rows) - 1)) / len(rows)
    for i, r in enumerate(rows):
        y = TOP + i * (rh + 10)
        card(p, x0, y, RIGHT - x0, rh, accent(slide), rule='left')
        pin(L, p, i + 1, x0 + 24, y + 22, 11)
        put(L, p, r['question'], x0 + 44, y + 13, 210, 12, 'ink', True)
        inked(L, p, r['fact'], x0 + 44, y + 33, 210, 10)
        paint(L, p, f"Today: {r['today']}", x0 + 44, y + rh - 20, 210, 8, BODY)
        vx = x0 + 270
        row_visual(L, p, r['visual'], vx, y + 12, RIGHT - 14 - vx, rh - 24)


# -- 5: flow ------------------------------------------------------------------------------------
def mp_flow(L, p, slide):
    bottom = band(L, p, slide) - 14
    steps = slide['steps']
    gap = 22
    w = (W - gap * 2) / 3
    for i, s in enumerate(steps):
        x = LEFT + i * (w + gap)
        card(p, x, TOP, w, bottom - TOP, accent(slide))
        ih = w * 900 / 1280 - 20 * 900 / 1280
        p.rect(x + 9.5, TOP + 11.5, w - 19, ih + 1, HAIR)
        img(L, p, s['image'], s['alt'], x + 10, TOP + 12, w - 20, ih)
        y = TOP + 12 + ih + 12
        dot_icon(L, p, s['icon'], ACCENT[accent(slide)][0], x + 14, y, 24)
        put(L, p, s['title'], x + 44, y + 4, w - 56, 12, 'ink', True)
        inked(L, p, s['text'], x + 14, y + 32, w - 28, 10)
        chip(L, p, s['value'], x + 14, bottom - 30, w - 28, 22)
        if i < 2:
            p.connector(x + w + 3, TOP + 80, x + w + gap - 3, TOP + 80)


# -- 6: agents ----------------------------------------------------------------------------------
def mp_agents(L, p, slide):
    bottom = band(L, p, slide) - 14
    p.rect(LEFT, TOP, W, 26, WHITE)
    p.line(LEFT, TOP, RIGHT, TOP, HAIR)
    p.line(LEFT, TOP + 26, RIGHT, TOP + 26, HAIR)
    put(L, p, slide['order'], LEFT + 8, TOP + 6, W - 16, 10, 'ink')
    stations = slide['stations']
    gap = 18
    w = (W - gap * 3) / 4
    y = TOP + 40
    for i, s in enumerate(stations):
        x = LEFT + i * (w + gap)
        card(p, x, y, w, bottom - y, accent(slide))
        img(L, p, s['image'], s['alt'], x + (w - 120) / 2, y + 12, 120, 60)
        put(L, p, s['role'].upper(), x + 14, y + 82, w - 28, 8, 'accent', True)
        put(L, p, s['title'], x + 14, y + 96, w - 28, 12, 'ink', True)
        inked(L, p, s['text'], x + 14, y + 116, w - 28, 10)
        # The order ticket fills up as it passes each station; the newest line is this station's output.
        tk = slide['ticket']
        lines = tk['lines'][:i + 1]
        th = 22 + 4 * 12 + 6
        ty = bottom - 12 - th
        p.rect(x + 12, ty, w - 24, th, WHITE)
        for k in range(int((w - 24) / 6)):
            p.rect(x + 12 + k * 6 + 1, ty - 2, 3, 2, WHITE)
        paint(L, p, tk['title'].upper(), x + 20, ty + 7, w - 40, 8, BODY, True)
        for k, line in enumerate(lines):
            ly = ty + 22 + k * 12
            new_line = k == i
            if new_line:
                p.rect(x + 12, ly, 3, 11, V_TEAL)
            paint(L, p, line, x + 20, ly, w - 40, 8, INK if new_line else BODY, new_line)
        if i < 3:
            p.connector(x + w + 2, y + 42, x + w + gap - 2, y + 42)


# -- 7: calorie target --------------------------------------------------------------------------
def mp_calories(L, p, slide):
    bottom = band(L, p, slide) - 14
    steps = slide['steps']
    overlap, notch, ch = 8, 18, 108
    cw = (W + 3 * overlap) / 4
    for i, s in enumerate(steps):
        # Each chevron wears the colour of its part in the rings below.
        x = LEFT + i * (cw - overlap)
        ink = INK if i == 3 else WHITE
        img(L, p, f'assets/figures/shapes/chevron-{i + 1}.svg', '', x, TOP, cw, ch)
        tx = x + (16 if i == 0 else notch + 12)
        tw = cw - (tx - x) - notch - 8
        dot_icon(L, p, s['icon'], ink, tx, TOP + 14, 22)
        paint(L, p, s['title'], tx + 32, TOP + 17, tw - 32, 12, ink, True)
        paint(L, p, s['text'], tx, TOP + 44, tw, 10, ink)
        paint(L, p, s['value'], tx, TOP + ch - 28, tw, 12, ink, True)
    y = TOP + ch + 16
    p.rect(LEFT, y, W, bottom - y, pale(slide))
    rings = slide['chart']['rings']
    half = W / 2
    d = min(bottom - y - 24, 150)
    for k, r in enumerate(rings):
        x = LEFT + k * half
        dx, dy = x + 24, y + (bottom - y - d) / 2
        img(L, p, r['image'], r['alt'], dx, dy, d, d)
        paint(L, p, r['centre'], dx + d * .2, dy + d / 2 - 15, d * .6, 18, INK, True, 'center')
        paint(L, p, r['centre_label'], dx + d * .2, dy + d / 2 + 8, d * .6, 8, BODY, False, 'center')
        gx = dx + d + 20
        hy = y + (bottom - y) / 2 - 22
        put(L, p, r['headline'], gx, hy, x + half - 16 - gx, 12, 'ink', True)
        put(L, p, r['text'], gx, hy + 22, x + half - 16 - gx, 10, 'body')


# -- 8: choosing --------------------------------------------------------------------------------
def mp_choosing(L, p, slide):
    bottom = band(L, p, slide) - 14
    f = slide['funnel']
    fh = 150
    p.rect(LEFT, TOP, W, fh, pale(slide))
    put(L, p, f['title'], LEFT + 14, TOP + 10, 400, 12, 'ink', True)
    top = max(r['value'] for r in f['rows'])
    step = (W - 28 - 200 - 190) / top
    for i, r in enumerate(f['rows']):
        y = TOP + 36 + i * 27
        put(L, p, r['label'], LEFT + 14, y + 3, 190, 10, 'ink')
        # One dot per recipe: kept recipes in colour, the ones this step removed as faint rings.
        for k in range(top):
            cx, cy = LEFT + 214 + k * step + step / 2, y + 10
            if k < r['value']:
                p.rect(cx - 5, cy - 5, 10, 10, VIRIDIS4[i % 4], 'ELLIPSE')
            else:
                L.outlined(p, cx - 5, cy - 5, 10, 10, 'transparent', HAIR, 1.2, 'ELLIPSE')
        put(L, p, r['text'], LEFT + 214 + top * step + 18, y + 3, 164, 10, 'ink', True)
    outcomes = slide['outcomes']
    gap = 16
    w = (W - gap * (len(outcomes) - 1)) / len(outcomes)
    y = TOP + fh + 14
    for i, o in enumerate(outcomes):
        x = LEFT + i * (w + gap)
        card(p, x, y, w, bottom - y, accent(slide))
        dot_icon(L, p, o['icon'], ACCENT[accent(slide)][0], x + 14, y + 12, 22)
        put(L, p, o['title'], x + 40, y + 15, w - 52, 12, 'ink', True)
        inked(L, p, o['text'], x + 14, y + 42, w - 28, 10)
        put(L, p, o['count'], x + 14, bottom - 12 - need(L, o['count'], w - 28, 12, True), w - 28, 12, 'ink', True)


# -- 9: nutrition -------------------------------------------------------------------------------
def mp_nutrition(L, p, slide):
    bottom = band(L, p, slide) - 14
    tw = 400
    p.rect(LEFT, TOP, tw, bottom - TOP, CARD)
    cols = slide['columns']
    xs = [LEFT + 14, LEFT + 180, LEFT + 250, LEFT + 312]
    for c, x in zip(cols, xs):
        put(L, p, c, x, TOP + 12, 90, 10, 'ink', True)
    rh = (bottom - TOP - 44) / len(slide['rows'])
    for i, r in enumerate(slide['rows']):
        y = TOP + 36 + i * rh
        p.line(LEFT + 14, y, LEFT + tw - 14, y, HAIR)
        put(L, p, r[0], xs[0], y + (rh - 13.5) / 2, 160, 10, 'ink')
        put(L, p, r[1], xs[1], y + (rh - 13.5) / 2, 60, 10, 'body')
        put(L, p, r[2], xs[2], y + (rh - 13.5) / 2, 50, 10, 'body')
        colour = ESTIMATED if r[3] == 'Estimated' else REFERENCE
        p.rect(xs[3], y + rh / 2 - 4, 8, 8, colour)
        paint(L, p, r[3], xs[3] + 14, y + (rh - 13.5) / 2, 70, 10, colour, True)
    x0 = LEFT + tw + 20
    w = RIGHT - x0
    sp = slide['split']
    put(L, p, sp['title'], x0, TOP, w, 12, 'ink', True)
    total = sum(s['value'] for s in sp['parts'])
    run = x0
    for s in sp['parts']:
        ww = w * s['value'] / total
        colour = ESTIMATED if s['kind'] == 'Estimated' else REFERENCE
        p.rect(run, TOP + 22, ww, 30, colour)
        paint(L, p, s['label'], run + 8, TOP + 30, ww - 16, 10, WHITE, True)
        run += ww
    put(L, p, slide['order_title'], x0, TOP + 72, w, 12, 'ink', True)
    steps = slide['order']
    sh = (bottom - TOP - 96 - 10 * (len(steps) - 1)) / len(steps)
    for i, s in enumerate(steps):
        y = TOP + 96 + i * (sh + 10)
        card(p, x0, y, w, sh, accent(slide), rule='left')
        dot_icon(L, p, s['icon'], ACCENT[accent(slide)][0], x0 + 14, y + sh / 2 - 11, 22)
        put(L, p, s['title'], x0 + 46, y + 10, w - 60, 12, 'ink', True)
        inked(L, p, s['text'], x0 + 46, y + 28, w - 60, 10)


# -- 10: what good means ------------------------------------------------------------------------
def mp_good(L, p, slide):
    bottom = band(L, p, slide) - 14
    lw = 520
    card(p, LEFT, TOP, lw, bottom - TOP, accent(slide))
    put(L, p, slide['macro_title'], LEFT + 14, TOP + 14, lw - 28, 12, 'ink', True)
    bx, bw = LEFT + 14, lw - 28
    for i, m in enumerate(slide['macros']):
        y = TOP + 56 + i * 82
        colour = {'Protein': PROTEIN, 'Carbs': CARBS, 'Fat': FAT}[m['name']]
        put(L, p, m['name'], bx, y, 120, 10, 'ink', True)
        put(L, p, m['range_label'], bx + bw - 200, y, 200, 10, 'ink', True, 'right')
        p.rect(bx, y + 20, bw, 10, WHITE)
        p.rect(bx + bw * m['low'] / 100, y + 20, bw * (m['high'] - m['low']) / 100, 10, colour)
        cx = bx + bw * m['value'] / 100
        p.rect(cx - 8, y + 17, 16, 16, WHITE, 'ELLIPSE')
        p.rect(cx - 5, y + 20, 10, 10, INK, 'ELLIPSE')
        put(L, p, f"{m['value']}%", cx - 30, y + 36, 60, 8, 'ink', True, 'center')
    x0 = LEFT + lw + 18
    w = RIGHT - x0
    bh = 132
    p.rect(x0, TOP, w, bh, INK)
    paint(L, p, slide['calorie_label'], x0 + 14, TOP + 14, w - 28, 10, '#C9D6F5', True)
    paint(L, p, slide['calorie_value'], x0 + 14, TOP + 30, w - 28, 30, WHITE, True)
    paint(L, p, slide['calorie_text'], x0 + 14, TOP + 70, w - 28, 10, '#C9D6F5')
    # The pass band, with the worked example's meal on it.
    ex = slide['calorie_example']
    tx, tw, ty = x0 + 14, w - 28, TOP + 100
    span = ex['limit'] * 1.5
    sx = lambda v: tx + (v + span) / (2 * span) * tw
    p.rect(tx, ty, tw, 8, '#22325A')
    p.rect(sx(-ex['limit']), ty, sx(ex['limit']) - sx(-ex['limit']), 8, V_GREEN)
    p.rect(sx(ex['value']) - 5, ty - 1, 10, 10, WHITE, 'ELLIPSE')
    paint(L, p, f"-{ex['limit']}%", sx(-ex['limit']) - 20, ty + 11, 40, 8, '#C9D6F5', False, 'center')
    paint(L, p, f"+{ex['limit']}%", sx(ex['limit']) - 20, ty + 11, 40, 8, '#C9D6F5', False, 'center')
    paint(L, p, ex['label'], sx(ex['value']) + 8, ty - 14, 140, 8, WHITE, True)
    y = TOP + bh + 14
    card(p, x0, y, w, bottom - y, accent(slide))
    put(L, p, slide['grid_title'], x0 + 14, y + 12, w - 28, 12, 'ink', True)
    for g, (cols, colour, label) in enumerate(((12, V_BLUE, slide['grid_labels'][0]), (6, V_TEAL, slide['grid_labels'][1]))):
        gx = x0 + 14 + g * 196
        for c in range(cols):
            for r in range(4):
                p.rect(gx + c * 14, y + 36 + r * 13, 9, 9, colour, 'ELLIPSE')
        paint(L, p, label, gx, y + 92, 12 * 14 if g == 0 else w - 28 - 196, 10, colour, True)


# -- 11: results --------------------------------------------------------------------------------
def mp_results(L, p, slide):
    bottom = band(L, p, slide) - 14
    lw = 560
    p.rect(LEFT, TOP, lw, bottom - TOP, pale(slide))
    put(L, p, slide['chart_title'], LEFT + 14, TOP + 10, lw - 28, 10, 'body')
    base = bottom - 50
    top = TOP + 50
    bars = slide['bars']
    slot = (lw - 28) / len(bars)
    for i, b in enumerate(bars):
        x = LEFT + 14 + i * slot
        h = (base - top) * b['value'] / slide['maximum']
        p.rect(x + slot * .2, base - h, slot * .6, h, VIRIDIS4[i % 4])
        put(L, p, str(b['value']), x, base - h - 22, slot, 16, 'ink', True, 'center')
        put(L, p, b['label'], x, base + 6, slot, 10, 'ink', True, 'center')
        put(L, p, b['change'], x, base + 20, slot, 8, 'body', False, 'center')
    p.line(LEFT + 14, base, LEFT + lw - 14, base, HAIR)
    # Each fix's gain, on a dashed step between bar tops.
    for i in range(len(bars) - 1):
        a, b = bars[i], bars[i + 1]
        ya = base - (base - top) * a['value'] / slide['maximum']
        yb = base - (base - top) * b['value'] / slide['maximum']
        xa = LEFT + 14 + i * slot + slot * .8
        xb = LEFT + 14 + (i + 1) * slot + slot * .2
        p.line(xa, ya, xb, ya, BODY, .75, dash='DASH')
        chip(L, p, f"+{b['value'] - a['value']}", (xa + xb) / 2 - 22, ya - 24, 36, 18, INK, WHITE, 10)
    x0 = LEFT + lw + 18
    w = RIGHT - x0
    mets = slide['metrics']
    mh = (bottom - TOP - 12 * (len(mets) - 1)) / len(mets)
    for i, m in enumerate(mets):
        y = TOP + i * (mh + 12)
        card(p, x0, y, w, mh, accent(slide), rule='left')
        dot_icon(L, p, m['icon'], ACCENT[accent(slide)][0], x0 + 14, y + mh / 2 - 12, 24)
        put(L, p, m['value'], x0 + 50, y + mh / 2 - 22, w - 64, 18, 'ink', True)
        put(L, p, m['label'], x0 + 50, y + mh / 2 + 4, w - 64, 10, 'body')


# -- 12: architecture ---------------------------------------------------------------------------
def logo(L, p, name, x, y, d=18):
    img(L, p, f'assets/logos/{name}.png', f'{name} logo', x, y, d, d)


def mp_architecture(L, p, slide):
    bottom = band(L, p, slide) - 14
    stack_y = bottom - 40
    a = slide['arch']
    cw, aw = 120, 120
    y0, y1 = TOP + 16, stack_y - 12
    for t, x in ((a['labels'][0], LEFT), (a['labels'][1], LEFT + cw + 16), (a['labels'][2], LEFT + cw + aw + 32)):
        put(L, p, t.upper(), x, TOP, 200, 8, 'body', True)
    ch = (y1 - y0 - 12) / 2
    for i, c in enumerate(a['clients']):
        y = y0 + i * (ch + 12)
        card(p, LEFT, y, cw, ch, accent(slide))
        for k, lg in enumerate(c['logos']):
            logo(L, p, lg, LEFT + 10 + k * 22, y + 12)
        put(L, p, c['title'], LEFT + 10, y + 38, cw - 20, 12, 'ink', True)
        put(L, p, c['text'], LEFT + 10, y + 56, cw - 20, 10, 'body')
        p.connector(LEFT + cw + 2, y + ch / 2, LEFT + cw + 14, y + ch / 2)
    ax = LEFT + cw + 16
    card(p, ax, y0, aw, y1 - y0, accent(slide))
    for k, lg in enumerate(a['api']['logos']):
        logo(L, p, lg, ax + 10 + k * 22, y0 + 12)
    put(L, p, a['api']['title'], ax + 10, y0 + 38, aw - 20, 12, 'ink', True)
    put(L, p, a['api']['text'], ax + 10, y0 + 56, aw - 20, 10, 'body')
    st = a['store']
    sy = y1 - 92
    p.rect(ax + 8, sy, aw - 16, 84, WHITE)
    logo(L, p, st['logo'], ax + 16, sy + 8)
    put(L, p, st['title'], ax + 16, sy + 30, aw - 32, 10, 'ink', True)
    put(L, p, st['text'], ax + 16, sy + 46, aw - 32, 8, 'body')
    sx = ax + aw + 16
    p.connector(ax + aw + 2, (y0 + y1) / 2, sx - 2, (y0 + y1) / 2)
    sw = RIGHT - sx
    p.rect(sx, y0, sw, y1 - y0, pale(slide))
    logo(L, p, 'python', sx + 10, y0 + 8, 14)
    put(L, p, a['service'], sx + 30, y0 + 8, sw - 40, 10, 'ink', True)
    rows = a['agents']
    rh = (y1 - y0 - 34 - 6 * (len(rows) - 1)) / len(rows)
    for i, r in enumerate(rows):
        y = y0 + 30 + i * (rh + 6)
        p.rect(sx + 8, y, sw - 16, rh, WHITE)
        dot_icon(L, p, r['icon'], ACCENT[accent(slide)][0], sx + 16, y + rh / 2 - 10, 20)
        put(L, p, r['title'], sx + 44, y + rh / 2 - 13, 220, 10, 'ink', True)
        put(L, p, r['text'], sx + 44, y + rh / 2 + 1, sw - 120, 10, 'body')
        for k, lg in enumerate(r.get('logos', [])):
            logo(L, p, lg, RIGHT - 34 - k * 22, y + rh / 2 - 9)
    p.rect(LEFT, stack_y, W, 30, INK)
    paint(L, p, a['stack_label'], LEFT + 10, stack_y + 9, 70, 8, '#C9D6F5', True)
    x = LEFT + 84
    for name, label in a['stack']:
        tw = L.metrics.fonts[(True, False)].getlength(label) / 120 * 9 + 34
        p.rect(x, stack_y + 5, tw, 20, WHITE)
        logo(L, p, name, x + 5, stack_y + 7, 16)
        paint(L, p, label, x + 25, stack_y + 9, tw - 28, 9, INK, True)
        x += tw + 6



# -- 12: architecture as a stage flow ----------------------------------------------------------
LANE_TONE = {'slate': ACCENT['slate'], 'blue': ACCENT['blue'], 'plum': ACCENT['plum'], 'teal': (V_TEAL, '#E3F4E8'),
             'ochre': ACCENT['ochre'], 'red': ('#A1260E', '#FDE3DC')}


def badge_n(L, p, n, x, y, colour, r=7):
    p.rect(x, y, 2 * r, 2 * r, colour, 'ELLIPSE')
    paint(L, p, str(n), x, y + r - 5.5, 2 * r, 8, WHITE, True, 'center')


def step_card(L, p, x, y, w, h, colour, n, title, logos_=(), fill=WHITE):
    L.outlined(p, x, y, w, h, fill, colour, .8)
    badge_n(L, p, n, x + 7, y + 7, colour)
    paint(L, p, title, x + 26, y + 6, w - 34, 10, INK, True)
    for k, lg in enumerate(logos_):
        logo(L, p, lg, x + w - 20 - k * 17, y + 6, 14)


def bullets(L, p, items, x, y, w, size=8):
    for k, b in enumerate(items):
        p.rect(x, y + k * 12 + 4.5, 2.5, 2.5, BODY, 'ELLIPSE')
        paint(L, p, b, x + 7, y + k * 12, w - 7, size, BODY)


def mp_arch_flow(L, p, slide):
    bottom = band(L, p, slide) - 14
    f = slide['flow']
    lanes_h = 214
    gap = 8
    widths = [128, 132, 420]
    widths.append(W - sum(widths) - 3 * gap)
    xs = [LEFT]
    for wd in widths[:-1]:
        xs.append(xs[-1] + wd + gap)
    lane = {}
    for (x, wd, ln) in zip(xs, widths, f['lanes']):
        ink, tint = LANE_TONE[ln['tone']]
        p.rect(x, TOP, wd, lanes_h, tint)
        tw = L.metrics.fonts[(True, False)].getlength(ln['title']) / 120 * 12
        paint(L, p, ln['title'], x + 8, TOP + 6, tw + 4, 12, ink, True)
        paint(L, p, ln['sub'], x + 14 + tw, TOP + 9, wd - tw - 22, 8, BODY)
        lane[ln['key']] = (x, wd, ink)
    cy = TOP + 28
    # 1 ask, then the two clients that send it
    x, wd, ink = lane['ask']
    a = f['ask']
    step_card(L, p, x + 6, cy, wd - 12, 40, ink, a['step']['n'], a['step']['title'])
    paint(L, p, a['step']['text'], x + 32, cy + 21, wd - 44, 8, BODY)
    ch = (lanes_h - 28 - 40 - 8 - 6 - 6) / 2
    for k, c in enumerate(a['clients']):
        y = cy + 48 + k * (ch + 6)
        L.outlined(p, x + 6, y, wd - 12, ch, WHITE, HAIR, .8)
        for j, lg in enumerate(c['logos']):
            logo(L, p, lg, x + 13 + j * 18, y + 8, 14)
        paint(L, p, c['title'], x + 18, y + 28, wd - 30, 10, INK, True)
        paint(L, p, c['text'], x + 18, y + 43, wd - 30, 8, BODY)
    p.connector(x + wd - 6, cy + 20, lane['api'][0] + 6, cy + 20)
    # 2 validate, and the local store
    x, wd, ink = lane['api']
    a = f['api']
    vh = 96
    step_card(L, p, x + 6, cy, wd - 12, vh, ink, a['step']['n'], a['step']['title'], a['step']['logos'])
    bullets(L, p, a['step']['bullets'], x + 14, cy + 26, wd - 28)
    st = a['store']
    sy = cy + vh + 24
    L.outlined(p, x + 6, sy, wd - 12, TOP + lanes_h - 8 - sy, WHITE, HAIR, .8)
    logo(L, p, st['logos'][0], x + 13, sy + 8, 14)
    paint(L, p, st['title'], x + 32, sy + 9, wd - 46, 10, INK, True)
    paint(L, p, st['text'], x + 13, sy + 28, wd - 26, 8, BODY)
    p.line(x + wd / 2, cy + vh, x + wd / 2, sy, BODY, .75, dash='DASH')
    p.connector(x + wd - 6, cy + 20, lane['plan'][0] + 6, cy + 20)
    # 3 to 7: the planning service, one row per step
    x, wd, ink = lane['plan']
    rows = f['plan']
    rg = 6
    rh = (lanes_h - 28 - 8 - rg * (len(rows) - 1)) / len(rows)
    exit_y = None
    for k, r in enumerate(rows):
        y = cy + k * (rh + rg)
        step_card(L, p, x + 6, y, wd - 12, rh, ink, r['n'], r['title'], r.get('logos', ()))
        paint(L, p, r['text'], x + 92, y + 7, wd - 140, 8, BODY)
        if k < len(rows) - 1:
            p.connector(x + 20, y + rh, x + 20, y + rh + rg)
        if r.get('exit'):
            exit_y = y + rh / 2
    # The two exits sit level with step 4; 8 show sits level with step 7, so both arrows run straight.
    x, wd, ink = lane['answer']
    a = f['answer']
    exits = a['exits']
    eh = 32
    k4 = next(k for k, r in enumerate(rows) if r.get('exit'))
    row_mid = lambda k: cy + k * (rh + rg) + rh / 2
    ey0 = max(cy, row_mid(k4) - eh - 3)
    for k, e in enumerate(exits):
        ey = ey0 + k * (eh + 6)
        e_ink, e_tint = LANE_TONE[e['tone']]
        L.outlined(p, x + 6, ey, wd - 12, eh, e_tint, e_ink, .8)
        paint(L, p, e['title'], x + 14, ey + 4, wd - 28, 10, e_ink, True)
        paint(L, p, e['text'], x + 14, ey + 18, wd - 28, 8, BODY)
    px = lane['plan'][0] + lane['plan'][1] - 6
    mx = x - gap / 2
    exit_ink = LANE_TONE['ochre'][0]
    p.line(px, row_mid(k4), mx, row_mid(k4), exit_ink, .75, dash='DASH')
    p.line(mx, ey0 + eh / 2, mx, ey0 + eh + 6 + eh / 2, exit_ink, .75, dash='DASH')
    for k in range(len(exits)):
        p.connector(mx, ey0 + k * (eh + 6) + eh / 2, x + 6, ey0 + k * (eh + 6) + eh / 2, color=exit_ink)
    s8 = a['step']
    sy8 = ey0 + 2 * (eh + 6) + 4
    sh = TOP + lanes_h - 8 - sy8
    step_card(L, p, x + 6, sy8, wd - 12, sh, ink, s8['n'], s8['title'], s8['logos'])
    bullets(L, p, s8['bullets'], x + 14, sy8 + 26, wd - 28)
    last = row_mid(len(rows) - 1)
    p.connector(px, last, x + 6, last)
    # what the whole flow guarantees
    gy = TOP + lanes_h + 8
    gh = bottom - gy
    p.rect(LEFT, gy, W, gh, CARD)
    gs = f['guarantees']
    gw = (W - 16 - 8 * (len(gs) - 1)) / len(gs)
    for k, g in enumerate(gs):
        gx = LEFT + 8 + k * (gw + 8)
        p.rect(gx, gy + 8, gw, gh - 16, WHITE)
        dot_icon(L, p, g['icon'], ACCENT[accent(slide)][0], gx + 8, gy + 15, 16, 16)
        paint(L, p, g['title'], gx + 32, gy + 16, gw - 62, 10, INK, True)
        paint(L, p, g['text'], gx + 32, gy + 31, gw - 40, 8, BODY)
        for j, lg in enumerate(g.get('logos', [])):
            logo(L, p, lg, gx + gw - 22 - j * 17, gy + 15, 14)

# -- 13: engineering ----------------------------------------------------------------------------
def mp_engineering(L, p, slide):
    bottom = band(L, p, slide) - 14
    lh = 168
    p.rect(LEFT, TOP, W, lh, pale(slide))
    put(L, p, slide['line_title'], LEFT + 14, TOP + 10, 400, 12, 'ink', True)
    if slide.get('legend'):
        put(L, p, slide['legend'], LEFT + 420, TOP + 12, W - 434, 8, 'body', False, 'right')
    steps = slide['steps']
    step = (W - 120) / (len(steps) - 1)
    ly = TOP + 74
    for i, s in enumerate(steps):
        x = LEFT + 60 + i * step
        colour = V_TEAL if s['live'] else '#8A93A8'
        if i < len(steps) - 1:
            nxt = steps[i + 1]['live']
            p.line(x, ly, x + step, ly, V_TEAL if nxt else '#8A93A8', 3, dash=None if nxt else 'DASH')
    for i, s in enumerate(steps):
        x = LEFT + 60 + i * step
        colour = V_TEAL if s['live'] else '#8A93A8'
        p.rect(x - 6, ly - 6, 12, 12, colour, 'ELLIPSE')
        dot_icon(L, p, s['icon'], colour, x - 13, ly - 38, 26, 22)
        put(L, p, s['title'], x - 60, ly + 26, 120, 10, 'ink', True, 'center')
        put(L, p, s['text'], x - 60, ly + 41, 120, 8, 'body', False, 'center')
        put(L, p, s['file'], x - 60, ly + 56, 120, 8, 'body', False, 'center')
    stats = slide['stats']
    gap = 16
    w = (W - gap * (len(stats) - 1)) / len(stats)
    y = TOP + lh + 14
    for i, s in enumerate(stats):
        x = LEFT + i * (w + gap)
        card(p, x, y, w, bottom - y, accent(slide))
        put(L, p, s['value'], x + 14, y + 12, w - 28, 30, 'ink', True)
        put(L, p, s['label'], x + 14, y + 56, w - 28, 10, 'body')
        v, vy, vw = s.get('viz'), bottom - 30, w - 28
        if not v:
            continue
        if v['kind'] == 'split':
            total = sum(n for n, _ in v['parts'])
            run = x + 14
            for n, colour in v['parts']:
                p.rect(run, vy, vw * n / total, 12, colour)
                run += vw * n / total
        elif v['kind'] == 'floor':
            p.rect(x + 14, vy, vw, 12, WHITE)
            p.rect(x + 14, vy, vw * v['value'] / 100, 12, V_GREEN)
            fx = x + 14 + vw * v['floor'] / 100
            p.line(fx, vy - 5, fx, vy + 17, INK, 1.5)
        else:
            for k in range(v['total']):
                dot_icon(L, p, 'check_circle', V_TEAL, x + 14 + k * 28, vy - 6, 24, 22)


# -- 14: limits ---------------------------------------------------------------------------------
def mp_limits(L, p, slide):
    bottom = band(L, p, slide) - 14
    steps = slide['steps']
    gap = 16
    w = (W - gap * 2) / 3
    full = bottom - TOP
    ink, tint = ACCENT[accent(slide)]
    strength_colour = {3: V_GREEN, 2: V_TEAL, 1: V_BLUE}
    for i, s in enumerate(steps):
        h = full * 0.62 + i * 3 * 17.5   # whole bullet pitches, so rows line up across cards
        x, y = LEFT + i * (w + gap), bottom - h
        card(p, x, y, w, h, accent(slide))
        dot_icon(L, p, s['icon'], ink, x + 14, y + 12, 24)
        put(L, p, s['title'], x + 44, y + 16, w - 120, 12, 'ink', True)
        # How strong the evidence is: filled dots out of three.
        for k in range(3):
            cx = x + w - 54 + k * 14
            if k < s['strength']:
                p.rect(cx, y + 18, 10, 10, strength_colour[s['strength']], 'ELLIPSE')
            else:
                L.outlined(p, cx, y + 18, 10, 10, 'transparent', HAIR, 1.2, 'ELLIPSE')
        yy = y + 46
        for item in s['items']:
            yy += inked(L, p, f'\u2022  {item}', x + 14, yy, w - 28, 10) + 4
        p.rect(x + 10, bottom - 50, w - 20, 40, WHITE)
        p.rect(x + 10, bottom - 50, 3, 40, ink)
        paint(L, p, 'CLOSES IT', x + 22, bottom - 44, w - 40, 8, ink, True)
        paint(L, p, s['next'], x + 22, bottom - 31, w - 40, 10, INK, True)


# -- 15: next steps -----------------------------------------------------------------------------
def mp_next(L, p, slide):
    bottom = band(L, p, slide) - 14
    ms = slide['milestones']
    step = (W - 80) / (len(ms) - 1)
    ly = TOP + 8
    for i in range(len(ms) - 1):
        x = LEFT + 40 + i * step
        last = i == len(ms) - 2
        p.line(x, ly, x + step, ly, '#8A93A8' if last else V_TEAL, 2.5, dash='DASH' if last else None)
    for i, m in enumerate(ms):
        x = LEFT + 40 + i * step
        colour = '#8A93A8' if i == len(ms) - 1 else V_TEAL
        p.rect(x - 7, ly - 7, 14, 14, colour, 'ELLIPSE')
        put(L, p, m['date'], x - 70, ly + 12, 140, 10, 'ink', True, 'center')
        put(L, p, m['text'], x - 70, ly + 27, 140, 8, 'body', False, 'center')
    cols = slide['columns']
    gap = 16
    w = (W - gap * 2) / 3
    y0 = TOP + 72
    for i, c in enumerate(cols):
        x = LEFT + i * (w + gap)
        card(p, x, y0, w, bottom - y0, accent(slide))
        put(L, p, c['title'].upper(), x + 14, y0 + 12, w - 28, 10, 'accent', True)
        nh = (bottom - y0 - 40 - 8 * (len(c['items']) - 1)) / len(c['items'])
        for k, item in enumerate(c['items']):
            y = y0 + 34 + k * (nh + 8)
            p.rect(x + 10, y, w - 20, nh, WHITE)
            if c.get('icons'):
                dot_icon(L, p, c['icons'][k], ACCENT[accent(slide)][0], x + 22, y + nh / 2 - 11, 22, 20)
            put(L, p, item, x + 52, y + (nh - need(L, item, w - 72, 12, True)) / 2, w - 72, 12, 'ink', True)



# -- 1: cover, 2: agenda, 16: close (cover-like pages clear the kit's header and footer) ----------
def logos(L, p, x, y, size):
    """UTS mark, a hairline, then the AI Meal Planner mark, at the same height."""
    img(L, p, 'assets/brand/uts-logo.svg', 'University of Technology Sydney', x, y, size, size)
    p.line(x + size + 8, y + 4, x + size + 8, y + size - 4, HAIR)
    img(L, p, 'assets/brand/ai-meal-planner-mark.svg', 'AI Meal Planner logo', x + size + 16, y, size, size)


def mp_cover(L, p, slide):
    """The app's home banner as a cover: a full-height cobalt half with the question, three proof
    chips and the presenter, beside the labelled plate (Market Receipt, DEC-44)."""
    p.ops.clear()
    slide.pop('chapter_badges', None)
    COBALT, PEACH, ON_INK = '#2448C9', '#FFD3C7', '#DCE4FF'
    p.rect(0, 0, 560, 540, COBALT)
    logos(L, p, LEFT, 36, 56)
    w = 560 - LEFT - 40
    y = 140
    y += paint(L, p, slide['section'].upper(), LEFT, y, w, 9.5, PEACH, True) + 16
    first, second = slide['title_lines']
    y += paint(L, p, first, LEFT, y, w, 50, WHITE, True)
    y += paint(L, p, second, LEFT, y - 6, w, 50, PEACH, True) + 6
    y += paint(L, p, slide['subtitle'], LEFT, y, w, 13, ON_INK) + 26
    chips = slide['chips']
    gap = 10
    cw = (w - gap * (len(chips) - 1)) / len(chips)
    ch = 84
    y = max(y, 476 - ch - 14)  # the chips sit on the bottom margin, so the half fills
    for i, chip in enumerate(chips):
        x = LEFT + i * (cw + gap)
        p.rect(x, y, cw, ch, WHITE)
        p.rect(x, y, 4, ch, '#D63C1A')
        paint(L, p, chip['value'], x + 14, y + 12, cw - 22, 22, INK, True)
        paint(L, p, chip['label'], x + 14, y + 44, cw - 22, 8.5, BODY)
    paint(L, p, L.content['date'], LEFT, 490, w, 10, ON_INK)
    # The labelled plate: the cover's own illustration, with native tags and a native receipt.
    art = slide['art']
    img(L, p, art['image'], art['alt'], 560, 0, 400, 540)
    for tag in art['tags']:
        (dx, dy), (bx, by), w, h = tag['dot'], tag['box'], 132, 32
        # The leader runs from the dot to the nearest point on the tag's edge.
        ex, ey = min(max(dx, bx), bx + w), min(max(dy, by), by + h)
        p.line(dx, dy, ex, ey, WHITE, 2.5)
        p.line(dx, dy, ex, ey, INK, 1)
        p.rect(dx - 5, dy - 5, 10, 10, WHITE, 'ELLIPSE')
        p.rect(dx - 3, dy - 3, 6, 6, INK, 'ELLIPSE')
        p.rect(bx, by, w, h, WHITE)
        p.rect(bx, by, 3, h, ESTIMATED if tag['source'] == 'Estimated' else REFERENCE)
        put(L, p, tag['name'], bx + 10, by + 3, w - 16, 10, 'ink', True)
        paint(L, p, tag['source'], bx + 10, by + 17, w - 16, 8, ESTIMATED if tag['source'] == 'Estimated' else REFERENCE, True)
    target = art['target']
    p.rect(586, 112, 160, 26, INK)
    paint(L, p, target, 590, 118, 152, 10, WHITE, True, 'center')
    r = art['receipt']
    rx, ry, rw = 732, 20, 176
    lines = r['items']
    rh = 34 + len(lines) * 14 + 26
    p.rect(rx, ry, rw, rh, WHITE)
    put(L, p, r['title'], rx + 10, ry + 9, rw - 20, 9, 'ink', True)
    for i, (name, price) in enumerate(lines):
        put(L, p, f'`{name}`', rx + 10, ry + 28 + i * 14, 110, 8, 'body')
        put(L, p, f'`{price}`', rx + rw - 60, ry + 28 + i * 14, 50, 8, 'body', False, 'right')
    yy = ry + 28 + len(lines) * 14 + 4
    p.line(rx + 10, yy, rx + rw - 10, yy, HAIR)
    put(L, p, f"`{r['total_label']}`", rx + 10, yy + 5, 110, 9, 'ink', True)
    put(L, p, f"`{r['total']}`", rx + rw - 60, yy + 5, 50, 9, 'ink', True, 'right')


def mp_agenda(L, p, slide):
    p.ops.clear()
    slide.pop('chapter_badges', None)
    L.chapter_agenda(p, slide)
    p.line(851, 48, 851, 100, HAIR)
    img(L, p, 'assets/brand/ai-meal-planner-mark.svg', 'AI Meal Planner logo', 783, 44, 60, 60)
    L.footer(p, slide['n'])


def mp_close(L, p, slide):
    p.ops.clear()
    slide.pop('chapter_badges', None)
    logos(L, p, LEFT, 39, 62)
    y = 160
    p.rect(0, y, 505, 124, ACCENT['slate'][1])
    p.rect(0, y, 8, 124, ACCENT['slate'][0])
    put(L, p, slide['title'], LEFT, y + 18, 420, 36, 'ink', True)
    put(L, p, slide['thanks'], LEFT, y + 80, 430, 12, 'ink')
    put(L, p, L.content['author'], LEFT, 306, 420, 12, 'ink', True)
    put(L, p, L.content['affiliation'], LEFT, 324, 420, 10, 'body')
    for i, (label, url) in enumerate(slide['links']):
        put(L, p, f'**{label}** {url}', LEFT, 344 + i * 16, 330, 10, 'body')
    p.rect(LEFT + 340, 300, 96, 96, WHITE)
    img(L, p, 'assets/figures/qr.png', 'QR code to the live demo', LEFT + 344, 304, 88, 88)
    put(L, p, slide['qr_label'], LEFT + 340, 402, 96, 8, 'body', False, 'center')
    img(L, p, 'assets/figures/cover-motif.svg', 'A row of plates and grains in palette A', LEFT, 440, 430, 41)
    img(L, p, slide['image']['path'], slide['image']['alt'], 505, 0, 455, 540)
    cw = 320
    p.rect(RIGHT - cw, 436, cw, 40, WHITE)
    p.rect(RIGHT - cw, 436, 3, 40, V_GREEN)
    paint(L, p, slide['image_caption'], RIGHT - cw + 12, 442, cw - 24, 10, INK, True)
    paint(L, p, slide['image_note'], RIGHT - cw + 12, 458, cw - 24, 8, BODY)


# -- appendix: app walkthrough ------------------------------------------------------------------
def mp_walk(L, p, slide):
    """One app screen on the left with numbered pins; the matching callouts on the right."""
    bottom = band(L, p, slide) - 14
    shot = slide['image']
    h = bottom - TOP
    w = min(h * shot['aspect'], 470)
    h = w / shot['aspect']
    p.rect(LEFT - 0.5, TOP - 0.5, w + 1, h + 1, HAIR)
    img(L, p, shot['path'], shot['alt'], LEFT, TOP, w, h)
    for n, (ix, iy) in enumerate(slide['pins'], 1):
        pin(L, p, n, LEFT + ix / 1000 * w, TOP + iy / 1000 * h)
    x0 = LEFT + w + 24
    cw = RIGHT - x0
    rows = slide['callouts']
    rh = (bottom - TOP) / len(rows)
    for i, r in enumerate(rows):
        y = TOP + i * rh
        if i:
            p.line(x0, y - 0.5, RIGHT, y - 0.5, HAIR)
        pin(L, p, i + 1, x0 + 11, y + 15, 10)
        put(L, p, r['title'], x0 + 32, y + 6, cw - 32, 12, 'ink', True)
        inked(L, p, r['text'], x0 + 32, y + 25, cw - 32, 10)


# -- appendix: benchmark runs -------------------------------------------------------------------
def chart_key(L, p, keys, x, y, w):
    """The chart's encoding key, right-aligned above the plot: a swatch per series, then its words."""
    widths = [L.metrics.fonts[(False, False)].getlength(k['label']) * 8 / 120 for k in keys]
    xx = x + w
    for k, kw in reversed(list(zip(keys, widths))):
        xx -= kw + 4
        paint(L, p, k['label'], xx, y, kw + 4, 8, BODY)
        xx -= 14
        if k.get('outline'):
            L.outlined(p, xx, y + 2, 10, 8, 'transparent', k['colour'], 1, 'RECTANGLE')
        else:
            p.rect(xx, y + 2, 10, 8, k['colour'])
        xx -= 14


def bench_stack(L, p, c, x, top, w, base):
    """One stacked bar per day: the body's day, the workout on it, and an outline for what used to be added."""
    bars = c['bars']
    slot = w / len(bars)
    scale = (base - top) / c['maximum']
    for i, b in enumerate(bars):
        bx, bw = x + i * slot + slot * .22, slot * .56
        y = base
        for value, colour in ((b['body'], V_BLUE), (b['workout'], V_TEAL)):
            h = value * scale
            if h > 0:
                p.rect(bx, y - h, bw, h, colour)
            y -= h
        gh = b['removed'] * scale
        L.outlined(p, bx + .5, y - gh, bw - 1, gh, 'transparent', V_DARK, 1, 'RECTANGLE')
        paint(L, p, f"was {b['before']:,}", bx, y - gh + 5, bw, 8, V_DARK, True, 'center')
        paint(L, p, f"{b['now']:,}", bx, y + 5, bw, 12, WHITE, True, 'center')
        put(L, p, b['label'], x + i * slot, base + 6, slot, 10, 'ink', True, 'center')
        put(L, p, b['detail'], x + i * slot, base + 20, slot, 8, 'body', False, 'center')
    p.line(x, base, x + w, base, HAIR)


def bench_groups(L, p, c, x, top, w, base):
    """Runs side by side; in each, one bar per measure, out of the same total."""
    groups = c['groups']
    slot = w / len(groups)
    scale = (base - top) / c['maximum']
    colours = [k['colour'] for k in c['keys']]
    for i, g in enumerate(groups):
        n = len(g['values'])
        bw = slot * .6 / n
        x0 = x + i * slot + slot * .2
        for k, v in enumerate(g['values']):
            h = v * scale
            p.rect(x0 + k * bw + 2, base - h, bw - 4, h, colours[k])
            put(L, p, str(v), x0 + k * bw - 6, base - h - 20, bw + 12, 12, 'ink', True, 'center')
        put(L, p, g['label'], x + i * slot, base + 6, slot, 10, 'ink', True, 'center')
        put(L, p, g['detail'], x + i * slot, base + 20, slot, 8, 'body', False, 'center')
    p.line(x, base, x + w, base, HAIR)


def mp_bench(L, p, slide):
    """A benchmark run: its chart on the left, three numbers that explain it on the right."""
    bottom = band(L, p, slide) - 14
    lw = 560
    c = slide['chart']
    p.rect(LEFT, TOP, lw, bottom - TOP, pale(slide))
    put(L, p, c['title'], LEFT + 14, TOP + 10, lw - 28, 10, 'body')
    chart_key(L, p, c['keys'], LEFT + 14, TOP + 28, lw - 28)
    base = bottom - 50
    top = TOP + 62
    (bench_stack if c['kind'] == 'stack' else bench_groups)(L, p, c, LEFT + 14, top, lw - 28, base)
    x0 = LEFT + lw + 18
    w = RIGHT - x0
    mets = slide['metrics']
    mh = (bottom - TOP - 12 * (len(mets) - 1)) / len(mets)
    for i, m in enumerate(mets):
        y = TOP + i * (mh + 12)
        card(p, x0, y, w, mh, accent(slide), rule='left')
        dot_icon(L, p, m['icon'], ACCENT[accent(slide)][0], x0 + 14, y + 14, 24)
        put(L, p, m['value'], x0 + 50, y + 12, w - 64, 18, 'ink', True)
        inked(L, p, m['label'], x0 + 50, y + 38, w - 64, 10)


LAYOUTS = {f.__name__: f for f in (mp_arch_flow, mp_cover, mp_agenda, mp_close, mp_summary, mp_problem, mp_flow, mp_agents, mp_calories, mp_choosing, mp_nutrition,
                                   mp_good, mp_results, mp_architecture, mp_engineering, mp_limits, mp_next, mp_walk,
                                   mp_bench)}
