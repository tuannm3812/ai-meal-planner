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
INK, BODY, CARD, HAIR, WHITE = '#1B2430', '#5A6370', '#F4F5F6', '#D8DEE3', '#FFFFFF'
ACCENT = {'slate': ('#526174', '#EDF0F3'), 'blue': ('#32658A', '#EAF0F6'), 'plum': ('#825578', '#F3EDF3'),
          'ochre': ('#896521', '#F6F1E5')}
# Data colours (Viridis), one meaning each across the deck: see DESIGN.project.md.
V_DARK, V_BLUE, V_TEAL, V_GREEN = '#440154', '#3B528B', '#21918C', '#5EC962'
ESTIMATED, REFERENCE = V_DARK, V_TEAL
VIRIDIS4 = [V_DARK, V_BLUE, V_TEAL, V_GREEN]


def pale(slide):
    return ACCENT[slide.get('accent', 'slate')][1]
PROTEIN, CARBS, FAT = V_BLUE, V_TEAL, V_GREEN


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


def dot_icon(L, p, glyph, colour, x, y, d=24):
    p.rect(x, y, d, d, colour, 'ELLIPSE')
    img(L, p, f'assets/icons/glyph-{glyph}.png', '', x + d * .17, y + d * .17, d * .66, d * .66)


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
            p.rect(x + k * 26, y + 4, 20, 20, V_TEAL, 'ELLIPSE')
            img(L, p, 'assets/icons/glyph-check_circle.png', '', x + k * 26 + 3, y + 7, 14, 14)
        return
    per_row, step = 24, w / 24
    for k in range(c['total']):
        cx, cy = x + (k % per_row) * step + step / 2, y + (k // per_row) * step + step / 2
        colour = V_DARK if k < c['first'] else V_GREEN
        p.rect(cx - step * .36, cy - step * .36, step * .72, step * .72, colour, 'ELLIPSE')
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
    tone = ACCENT[accent(slide)]
    for i, r in enumerate(rows):
        y = TOP + i * (rh + 10)
        card(p, x0, y, RIGHT - x0, rh, accent(slide), rule='left')
        pin(L, p, i + 1, x0 + 26, y + rh / 2, 11)
        put(L, p, r['question'], x0 + 50, y + 12, 220, 12, 'ink', True)
        inked(L, p, r['fact'], x0 + 50, y + 32, 220, 10)
        bw, cx = 140, x0 + 284
        for k, (label, text) in enumerate((('TODAY', r['today']), ('WITH THE APP', r['app']))):
            bx = cx + k * (bw + 24)
            p.rect(bx, y + 10, bw, rh - 20, WHITE if k == 0 else tone[1])
            if k:
                p.rect(bx, y + 10, 3, rh - 20, V_TEAL)
            put(L, p, label, bx + 10, y + 18, bw - 20, 8, 'body', True)
            put(L, p, text, bx + 10, y + 32, bw - 20, 10, 'ink', True)
        p.connector(cx + bw + 3, y + rh / 2, cx + bw + 21, y + rh / 2)


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
        chip(L, p, s['value'], x + 14, bottom - 36, w - 28, 24)
        if i < 3:
            p.connector(x + w + 2, y + 42, x + w + gap - 2, y + 42)


# -- 7: calorie target --------------------------------------------------------------------------
def mp_calories(L, p, slide):
    bottom = band(L, p, slide) - 14
    steps = slide['steps']
    gap = 18
    w = (W - gap * 3) / 4
    ch = 100
    for i, s in enumerate(steps):
        x = LEFT + i * (w + gap)
        card(p, x, TOP, w, ch, accent(slide))
        dot_icon(L, p, s['icon'], ACCENT[accent(slide)][0], x + 14, TOP + 12, 22)
        put(L, p, s['title'], x + 40, TOP + 15, w - 52, 12, 'ink', True)
        inked(L, p, s['text'], x + 14, TOP + 42, w - 28, 10)
        paint(L, p, s['value'], x + 14, TOP + ch - 26, w - 28, 12, INK, True)
        if i < 3:
            p.connector(x + w + 2, TOP + ch / 2, x + w + gap - 2, TOP + ch / 2)
    chart = slide['chart']
    y = TOP + ch + 18
    p.rect(LEFT, y, W, bottom - y, pale(slide))
    put(L, p, chart['title'], LEFT + 14, y + 10, 500, 12, 'ink', True)
    scale = (W - 28) / chart['total']
    x0 = LEFT + 14
    by = y + 52
    put(L, p, chart['day_label'], x0, by - 16, 300, 10, 'body')
    run = x0
    for part in chart['parts']:
        wpart = part['value'] * scale
        p.rect(run, by, wpart, 26, part['color'])
        if part.get('inside'):
            paint(L, p, part['inside'], run + 8, by + 6, wpart - 16, 10, WHITE, True)
        run += wpart
    last = chart['parts'][-1]
    paint(L, p, last['outside'], x0, by - 16, W - 28, 10, last['color'], True, 'right')
    my = by + 52
    put(L, p, chart['meal_label'], x0, my - 16, 300, 10, 'body')
    mw = chart['meal'] * scale
    p.rect(x0, my, mw, 26, INK)
    paint(L, p, chart['meal_inside'], x0 + 8, my + 6, mw - 16, 10, WHITE, True)
    put(L, p, chart['scale'], x0, bottom - 22, 500, 8, 'body')


# -- 8: choosing --------------------------------------------------------------------------------
def mp_choosing(L, p, slide):
    bottom = band(L, p, slide) - 14
    f = slide['funnel']
    fh = 150
    p.rect(LEFT, TOP, W, fh, pale(slide))
    put(L, p, f['title'], LEFT + 14, TOP + 10, 400, 12, 'ink', True)
    top = max(r['value'] for r in f['rows'])
    bw = W - 28 - 200 - 180
    for i, r in enumerate(f['rows']):
        y = TOP + 36 + i * 27
        put(L, p, r['label'], LEFT + 14, y + 3, 190, 10, 'ink')
        w = bw * r['value'] / top
        p.rect(LEFT + 214, y, w, 20, VIRIDIS4[i % 4])
        put(L, p, r['text'], LEFT + 232 + w, y + 3, 260, 10, 'ink', True)
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
        y = TOP + 50 + i * 62
        colour = {'Protein': PROTEIN, 'Carbs': CARBS, 'Fat': FAT}[m['name']]
        put(L, p, m['name'], bx, y, 120, 10, 'ink', True)
        put(L, p, m['range_label'], bx + bw - 200, y, 200, 10, 'ink', True, 'right')
        p.rect(bx, y + 20, bw, 10, WHITE)
        p.rect(bx + bw * m['low'] / 100, y + 20, bw * (m['high'] - m['low']) / 100, 10, colour)
        cx = bx + bw * m['value'] / 100
        p.rect(cx - 8, y + 17, 16, 16, WHITE, 'ELLIPSE')
        p.rect(cx - 5, y + 20, 10, 10, INK, 'ELLIPSE')
        put(L, p, f"{m['value']}%", cx - 30, y + 36, 60, 8, 'ink', True, 'center')
    put(L, p, slide['macro_caption'], LEFT + 14, bottom - 22, lw - 28, 8, 'body')
    x0 = LEFT + lw + 18
    w = RIGHT - x0
    p.rect(x0, TOP, w, 104, INK)
    paint(L, p, slide['calorie_label'], x0 + 14, TOP + 14, w - 28, 10, '#C9D3CC', True)
    paint(L, p, slide['calorie_value'], x0 + 14, TOP + 32, w - 28, 30, WHITE, True)
    paint(L, p, slide['calorie_text'], x0 + 14, TOP + 74, w - 28, 10, '#C9D3CC')
    y = TOP + 118
    card(p, x0, y, w, bottom - y, accent(slide))
    put(L, p, slide['grid_title'], x0 + 14, y + 12, w - 28, 12, 'ink', True)
    for g, (cols, colour, label) in enumerate(((12, V_BLUE, slide['grid_labels'][0]), (6, V_TEAL, slide['grid_labels'][1]))):
        gx = x0 + 14 + g * 196
        for c in range(cols):
            for r in range(4):
                p.rect(gx + c * 14, y + 40 + r * 14, 10, 10, colour, 'ELLIPSE')
        paint(L, p, label, gx, y + 104, 12 * 14 if g == 0 else w - 28 - 196, 10, colour, True)


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
    paint(L, p, a['stack_label'], LEFT + 10, stack_y + 9, 70, 8, '#C9D3CC', True)
    x = LEFT + 84
    for name, label in a['stack']:
        tw = L.metrics.fonts[(True, False)].getlength(label) / 120 * 9 + 34
        p.rect(x, stack_y + 5, tw, 20, WHITE)
        logo(L, p, name, x + 5, stack_y + 7, 16)
        paint(L, p, label, x + 25, stack_y + 9, tw - 28, 9, INK, True)
        x += tw + 6


# -- 13: engineering ----------------------------------------------------------------------------
def mp_engineering(L, p, slide):
    bottom = band(L, p, slide) - 14
    lh = 168
    p.rect(LEFT, TOP, W, lh, pale(slide))
    put(L, p, slide['line_title'], LEFT + 14, TOP + 10, 400, 12, 'ink', True)
    put(L, p, slide['legend'], LEFT + 420, TOP + 12, W - 434, 8, 'body', False, 'right')
    steps = slide['steps']
    step = (W - 120) / (len(steps) - 1)
    ly = TOP + 66
    for i, s in enumerate(steps):
        x = LEFT + 60 + i * step
        colour = V_TEAL if s['live'] else '#89949D'
        if i < len(steps) - 1:
            nxt = steps[i + 1]['live']
            p.line(x, ly, x + step, ly, V_TEAL if nxt else '#89949D', 3, dash=None if nxt else 'DASH')
    for i, s in enumerate(steps):
        x = LEFT + 60 + i * step
        colour = V_TEAL if s['live'] else '#89949D'
        dot_icon(L, p, s['icon'], colour, x - 18, ly - 18, 36)
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


# -- 14: limits ---------------------------------------------------------------------------------
def mp_limits(L, p, slide):
    bottom = band(L, p, slide) - 14
    steps = slide['steps']
    gap = 16
    w = (W - gap * 2) / 3
    full = bottom - TOP
    put(L, p, slide['stair_title'], LEFT, TOP, 300, 12, 'ink', True)
    put(L, p, slide['stair_text'], LEFT, TOP + 18, 300, 10, 'body')
    for i, s in enumerate(steps):
        h = full * (0.58 + 0.21 * i)
        x, y = LEFT + i * (w + gap), bottom - h
        card(p, x, y, w, h, accent(slide))
        dot_icon(L, p, s['icon'], ACCENT[accent(slide)][0], x + 14, y + 12, 24)
        put(L, p, s['title'], x + 44, y + 16, w - 56, 12, 'ink', True)
        yy = y + 46
        for item in s['items']:
            yy += inked(L, p, f'•  {item}', x + 14, yy, w - 28, 10) + 4


# -- 15: next steps -----------------------------------------------------------------------------
def mp_next(L, p, slide):
    bottom = band(L, p, slide) - 14
    ms = slide['milestones']
    step = (W - 80) / (len(ms) - 1)
    ly = TOP + 8
    for i in range(len(ms) - 1):
        x = LEFT + 40 + i * step
        last = i == len(ms) - 2
        p.line(x, ly, x + step, ly, '#89949D' if last else V_TEAL, 2.5, dash='DASH' if last else None)
    for i, m in enumerate(ms):
        x = LEFT + 40 + i * step
        colour = '#89949D' if i == len(ms) - 1 else V_TEAL
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
            put(L, p, item, x + 20, y + (nh - need(L, item, w - 40, 12, True)) / 2, w - 40, 12, 'ink', True)



# -- 1: cover, 2: agenda, 16: close (cover-like pages clear the kit's header and footer) ----------
def logos(L, p, x, y, size):
    """UTS mark, a hairline, then the AI Meal Planner mark, at the same height."""
    img(L, p, 'assets/brand/uts-logo.svg', 'University of Technology Sydney', x, y, size, size)
    p.line(x + size + 8, y + 4, x + size + 8, y + size - 4, HAIR)
    img(L, p, 'assets/brand/ai-meal-planner-mark.svg', 'AI Meal Planner logo', x + size + 16, y, size, size)


def mp_cover(L, p, slide):
    p.ops.clear()
    slide.pop('chapter_badges', None)
    logos(L, p, LEFT, 39, 62)
    title_h = need(L, slide['title'], 490, 30, True)
    sub_h = need(L, slide['subtitle'], 490, 12)
    panel_h = 14 + 17 + 6 + title_h + 10 + sub_h + 18
    y = 150
    p.rect(0, y, 560, panel_h, ACCENT['slate'][1])
    p.rect(0, y, 8, panel_h, ACCENT['slate'][0])
    put(L, p, slide['section'].upper(), LEFT, y + 14, 490, 9, 'secondary', True)
    put(L, p, slide['title'], LEFT, y + 37, 490, 30, 'ink', True)
    put(L, p, slide['subtitle'], LEFT, y + 37 + title_h + 10, 490, 12, 'ink')
    ay = y + panel_h + 18
    put(L, p, L.content['author'], LEFT, ay, 490, 12, 'ink', True)
    put(L, p, L.content['affiliation'], LEFT, ay + 19, 490, 10, 'body')
    put(L, p, L.content['date'], LEFT, ay + 35, 490, 10, 'body')
    img(L, p, slide['motif']['path'], slide['motif']['alt'], LEFT, 440, 478, 46)
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
    p.rect(505, 0, 455, 540, ACCENT['slate'][1])
    img(L, p, slide['image']['path'], slide['image']['alt'], 540, 100, 385, 385)
    put(L, p, slide['image_caption'], 540, 500, 385, 8, 'body', False, 'center')

LAYOUTS = {f.__name__: f for f in (mp_cover, mp_agenda, mp_close, mp_summary, mp_problem, mp_flow, mp_agents, mp_calories, mp_choosing, mp_nutrition,
                                   mp_good, mp_results, mp_architecture, mp_engineering, mp_limits, mp_next)}
