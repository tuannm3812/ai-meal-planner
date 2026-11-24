"""AI Meal Planner poster blocks for the deck-kit poster engine, on top of the UTS poster blocks.

The spec's "plugin" points here; this file loads uts_poster_blocks.py (the kit's template copy, for the answer band
"ptake") and adds the blocks this poster needs. Styles live in meal_poster.css (the spec's "css").

  mproblem   the problem: an illustration and three questions, each with a big icon and one fact
  mplates    one craving sized for four people: plate illustrations, scaled by calories
  mstations  four agents as kitchen stations, with the order ticket's value under each
  mapp       the React app in three steps, with a close-up capture for each
  mrings     two simple two-ring donuts: the day's budget, then this meal's share of it
  mresults   Viridis bars for the three fixes, with insight figures beside them
  mfunnel    recipes left after each hard limit, then what happens when nothing fits
  march      how it runs: clients, the live API, the planning service, and the engineering checks
  minsights  limits written as insights, each with a big icon
  mtry       links and a QR code to try it
"""
from __future__ import annotations

import html
import importlib.util
import math
from pathlib import Path

from deck_kit import poster as P

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('uts_poster_blocks', HERE / 'uts_poster_blocks.py')
UTS = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(UTS)

# Viridis, dark to light, and palette A section accents (deck-kit.json).
VIR = ['#440154', '#414487', '#2A788E', '#22A884', '#FDE725']
ACCENT = {'slate': '#22325A', 'blue': '#2448C9', 'plum': '#C2361A', 'ochre': '#6B4A00'}
FILL = {'slate': '#EEF1F7', 'blue': '#E7EDFB', 'plum': '#FFEDE7', 'ochre': '#FFF1C2'}


def rich(text, t):
    return UTS.rich(text, t)


def img(base, path, cls='', alt=''):
    return f'<img class="{cls}" src="{P.data_uri((base / path).expanduser())}" alt="{html.escape(alt)}">'


def card(kind, block, inner):
    accent = block.get('accent', 'slate')
    style = f'grid-column: span {block.get("span", 12)}; --acc: {ACCENT[accent]}; --accfill: {FILL[accent]}'
    # "vars": per-block layout variables, so one stylesheet serves portrait and landscape (e.g. {"n": 2}).
    style += ''.join(f'; --{k}: {v}' for k, v in block.get('vars', {}).items())
    return f'<section class="block card m {kind}" style="{style}">{inner}</section>'


def head(block, t):
    return f'<h2>{rich(block["heading"], t)}</h2>' if block.get('heading') else ''


def note(block, t, key='caption'):
    return f'<p class="caption">{rich(block[key], t)}</p>' if block.get(key) else ''


def mproblem(block, base, t):
    rows = ''.join(
        f'<div class="qrow">{img(base, r["icon"], "qicon")}<div><b>{rich(r["question"], t)}</b>'
        f'<p>{rich(r["fact"], t)}</p></div></div>' for r in block['rows'])
    art = (f'<figure class="qart">{img(base, block["image"], "", block.get("alt", ""))}'
           f'<figcaption>{rich(block["craving"], t)}</figcaption></figure>')
    return card('mproblem', block, head(block, t) + f'<div class="qgrid">{art}<div class="qrows">{rows}</div></div>'
                + note(block, t))


def mplates(block, base, t):
    top = max(p['kcal'] for p in block['plates'])
    plates = ''.join(
        f'<div class="plate"><div class="pimg"><div style="height:{math.sqrt(p["kcal"] / top) * 100:.1f}%">'
        f'{img(base, p["image"], "", p.get("alt", ""))}</div></div>'
        f'<b>{p["kcal"]} kcal</b><span class="pro">{html.escape(p["protein"])}</span>'
        f'<span class="who">{html.escape(p["who"])}</span></div>' for p in block['plates'])
    return card('mplates', block, head(block, t) + f'<div class="plates">{plates}</div>' + note(block, t))


def mstations(block, base, t):
    st = ''.join(
        f'<div class="station">{img(base, s["image"], "sart", s.get("alt", ""))}'
        f'<span class="role">{html.escape(s["role"])}</span><b>{html.escape(s["title"])}</b>'
        f'<p>{rich(s["text"], t)}</p><span class="out">{html.escape(s["value"])}</span></div>'
        for s in block['stations'])
    order = f'<p class="order"><span>Order</span>{rich(block["order"], t)}</p>' if block.get('order') else ''
    return card('mstations', block, head(block, t) + order + f'<div class="stations">{st}</div>' + note(block, t))


def mapp(block, base, t):
    steps = ''.join(
        f'<div class="astep"><div class="ashot">{img(base, s["image"], "", s.get("alt", ""))}</div>'
        f'<div class="ahead">{img(base, s["icon"], "aicon")}<b>{html.escape(s["title"])}</b></div>'
        f'<p>{rich(s["text"], t)}</p></div>' for s in block['steps'])
    return card('mapp', block, head(block, t) + f'<div class="asteps">{steps}</div>' + note(block, t))


def ring(parts, centre, centre_label):
    """A simple donut: one ring, two parts, a gap between them; the first part starts at twelve o'clock."""
    total = sum(v for v, _ in parts)
    r, w, c = 44, 10, 2 * math.pi * 44
    gap = 1.2
    arcs, start = '', 0.0
    for v, colour in parts:
        length = v / total * c
        arcs += (f'<circle cx="50" cy="50" r="{r}" fill="none" stroke="{colour}" stroke-width="{w}" '
                 f'stroke-dasharray="{max(length - gap, 0.6):.2f} {c:.2f}" stroke-dashoffset="{-start:.2f}" '
                 f'transform="rotate(-90 50 50)"/>')
        start += length
    return (f'<div class="donut"><svg viewBox="0 0 100 100">{arcs}</svg>'
            f'<div class="dc"><b>{html.escape(centre)}</b><span>{html.escape(centre_label)}</span></div></div>')


def mrings(block, base, t):
    out = ''
    for rg in block['rings']:
        key = ''.join(f'<span class="k"><i style="background:{c}"></i>{rich(label, t)}</span>' for _, c, label in rg['parts'])
        out += (f'<div class="rg">{ring([(v, c) for v, c, _ in rg["parts"]], rg["centre"], rg["centre_label"])}'
                f'<div class="rgtext"><b>{rich(rg["headline"], t)}</b><div class="rkey">{key}</div></div></div>')
    return card('mrings', block, head(block, t) + f'<div class="rings">{out}</div>' + note(block, t))


def mresults(block, base, t):
    top = block['maximum']
    prev = None
    bars = ''
    for i, b in enumerate(block['bars']):
        gain = f'<em>+{b["value"] - prev}</em>' if prev is not None else ''
        colour = VIR[min(i, len(VIR) - 1)]
        bars += (f'<div class="rbar"><div class="rcol"><span class="rv">{b["value"]}</span>'
                 f'<i style="height:{b["value"] / top * 100:.1f}%;background:{colour}"></i></div>'
                 f'<b>{html.escape(b["label"])}</b><span>{html.escape(b["change"])}</span>{gain}</div>')
        prev = b['value']
    metrics = ''.join(
        f'<div class="metric">{img(base, m["icon"], "micon")}<div><b>{html.escape(m["value"])}</b>'
        f'<span>{rich(m["label"], t)}</span></div></div>' for m in block['metrics'])
    return card('mresults', block, head(block, t)
                + f'<div class="rgrid"><div><p class="ctitle">{rich(block["chart_title"], t)}</p>'
                f'<div class="rbars">{bars}</div></div><div class="metrics">{metrics}</div></div>' + note(block, t))


def mfunnel(block, base, t):
    top = block['rows'][0]['value']
    rows = ''.join(
        f'<div class="fnrow"><span>{html.escape(r["label"])}</span><span class="ftrack">'
        f'<i style="width:{max(r["value"] / top * 100, 1.2):.1f}%;background:{VIR[min(i, 3)]}"></i></span>'
        f'<b>{html.escape(r["text"])}</b></div>' for i, r in enumerate(block['rows']))
    outs = ''.join(
        f'<div class="fout">{img(base, o["icon"], "ficon")}<div><b>{html.escape(o["title"])}</b>'
        f'<p>{rich(o["text"], t)}</p></div></div>' for o in block['outcomes'])
    return card('mfunnel', block, head(block, t) + f'<p class="ctitle">{rich(block["title"], t)}</p>'
                + f'<div class="frows">{rows}</div><div class="fouts">{outs}</div>' + note(block, t))


def logos(base, names):
    return ''.join(img(base, f'../assets/logos/{n}.png', 'lg', n) for n in names)


def march(block, base, t):
    def node(n, cls='node'):
        icon = img(base, n['icon'], 'nicon') if n.get('icon') else ''
        return (f'<div class="{cls}"><div class="nhead">{icon}<b>{html.escape(n["title"])}</b>'
                f'<span class="lgs">{logos(base, n.get("logos", []))}</span></div>'
                f'<p>{rich(n["text"], t)}</p></div>')
    clients = ''.join(node(c) for c in block['clients'])
    agents = ''.join(node(a, 'node agent') for a in block['agents'])
    checks = ''.join(
        f'<div class="chk">{img(base, c["icon"], "cicon")}<div><b>{html.escape(c["value"])}</b>'
        f'<span>{rich(c["label"], t)}</span></div></div>' for c in block['checks'])
    return card('march', block, head(block, t)
                + f'<div class="agrid"><div class="col"><span class="lab">Clients</span>{clients}</div>'
                f'<div class="arrow"></div><div class="col"><span class="lab">API</span>{node(block["api"], "node api")}'
                f'{node(block["store"], "node store") if block.get("store") else ""}</div>'
                f'<div class="arrow"></div><div class="col svc"><span class="lab">{html.escape(block["service"])}</span>'
                f'<div class="agents">{agents}</div></div></div><div class="mchecks">{checks}</div>' + note(block, t))


def minsights(block, base, t):
    items = ''.join(
        f'<div class="ins">{img(base, i["icon"], "iicon")}<div><span class="itag">{html.escape(i["tag"])}</span>'
        f'<b>{rich(i["insight"], t)}</b><p>{rich(i["text"], t)}</p></div></div>' for i in block['items'])
    return card('minsights', block, head(block, t) + f'<div class="insights">{items}</div>' + note(block, t))


def mtry(block, base, t):
    import segno
    q = segno.make(block['qr'], error='m')
    size = q.symbol_size(scale=1, border=0)[0]
    code = q.svg_inline(scale=1, border=0, dark='#14213D', light=None).replace(
        'class="segno"', f'class="segno" viewBox="0 0 {size} {size}"', 1)
    links = ''.join(f'<p><span>{html.escape(a)}</span>{html.escape(b)}</p>' for a, b in block['links'])
    return card('mtry', block, head(block, t) + f'<div class="tgrid"><div class="qr">{code}</div>'
                f'<div class="tlinks">{links}</div></div>' + note(block, t))


PLUGIN_BLOCKS = dict(UTS.PLUGIN_BLOCKS)
PLUGIN_BLOCKS.update({'mproblem': mproblem, 'mplates': mplates, 'mstations': mstations, 'mapp': mapp,
                      'mrings': mrings, 'mresults': mresults, 'mfunnel': mfunnel, 'march': march,
                      'minsights': minsights, 'mtry': mtry})


def header_extra(spec, t, base):
    return UTS.header_extra(spec, t, base)
