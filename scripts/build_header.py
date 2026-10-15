"""Build the animated header and typing-terminal SVGs for the profile README.

Run locally (needs fontTools + brotli to measure text):  python scripts/build_header.py
"""

import random
from pathlib import Path

from fontTools.ttLib import TTFont

from svg_common import (BG, BLUE, CYAN, FONT_DIR, GOOD, MONO, MUTED, SANS, TEXT, TEXT_2, VIOLET,
                        esc, font_face_css)

OUT = Path(__file__).resolve().parent.parent / "assets"
_FONT = TTFont(FONT_DIR / "geist-sub.woff2")
_CMAP, _HMTX, _UPM = _FONT.getBestCmap(), _FONT["hmtx"], _FONT["head"].unitsPerEm


def width(text: str, size: float, tracking: float = 0.0) -> float:
    """Advance width of `text` in Geist at its default weight."""
    units = sum(_HMTX[_CMAP.get(ord(ch), _CMAP[ord("?")])][0] for ch in text)
    return units / _UPM * size + tracking * max(0, len(text) - 1)


def network(rng: random.Random) -> str:
    spec, x0, x1, cy = [3, 5, 6, 5, 3], 770, 1140, 212
    cols = [VIOLET, "#8b9cf9", BLUE, "#3fc4f0", CYAN]
    layers = []
    for li, count in enumerate(spec):
        x = x0 + (x1 - x0) * li / (len(spec) - 1)
        span = 56 * (count - 1)
        layers.append([(x, cy - span / 2 + 56 * i) for i in range(count)])
    parts = ['<g opacity="0.95">']
    for li in range(len(layers) - 1):
        for a in layers[li]:
            for b in layers[li + 1]:
                parts.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" '
                             f'stroke="{cols[li]}" stroke-opacity="0.14"/>')
    # Signals: glowing dots running input -> output along random paths (a forward pass).
    for k in range(12):
        path = [rng.choice(layer) for layer in layers]
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in path)
        color = cols[k % len(cols)]
        dur, begin = 2.6 + rng.random() * 1.4, k * 0.45
        parts.append(
            f'<circle r="3.2" fill="{color}" filter="url(#glow)" opacity="0">'
            f'<animateMotion dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite" path="{d}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;0.08;0.9;1" dur="{dur:.2f}s" '
            f'begin="{begin:.2f}s" repeatCount="indefinite"/></circle>')
    for li, layer in enumerate(layers):
        for i, (x, y) in enumerate(layer):
            begin = rng.random() * 3
            parts.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{cols[li]}">'
                f'<animate attributeName="r" values="3.4;5.6;3.4" dur="2.8s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="fill-opacity" values="0.55;1;0.55" dur="2.8s" begin="{begin:.2f}s" '
                f'repeatCount="indefinite"/></circle>')
    parts.append("</g>")
    return "".join(parts)


def chips(x: float, y: float) -> str:
    items = [("95.1%", "field accuracy"), ("~5,000", "students served"),
             ("3rd / 600+", "PromptWars"), ("IJMRT", "published paper")]
    out = []
    for value, label in items:
        w = max(width(value, 19), len(label) * 11.5 * 0.6) + 28
        out.append(
            f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="58" rx="12" fill="rgba(255,255,255,0.04)" '
            f'stroke="rgba(255,255,255,0.1)"/>'
            f'<text x="{x + 14:.1f}" y="{y + 26}" class="sans" font-size="19" font-weight="650" fill="{TEXT}" '
            f'letter-spacing="-0.4">{esc(value)}</text>'
            f'<text x="{x + 14:.1f}" y="{y + 45}" class="mono" font-size="11.5" fill="{MUTED}">{esc(label)}</text>')
        x += w + 10
    return "".join(out)


def header() -> str:
    rng = random.Random(7)
    pill_text = "Open to AI & ML Engineer roles · Graduating 2027"
    pill_w = 44 + width(pill_text, 15) + 18
    name = "Dinesh Kumar Pathipati"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="420" viewBox="0 0 1200 420" role="img" aria-labelledby="t d">
<title id="t">Dinesh Kumar Pathipati — AI / ML Engineer</title>
<desc id="d">Machine learning that works in the field. 95.1% accuracy on field photos, about 5,000 students served, 3rd of 600+ at PromptWars, published in IJMRT. Open to AI and ML Engineer roles.</desc>
<defs>
<style>{font_face_css()}.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}</style>
<clipPath id="card"><rect width="1200" height="420" rx="22"/></clipPath>
<radialGradient id="a1" cx="0.1" cy="-0.15" r="0.65"><stop offset="0" stop-color="#6d28d9" stop-opacity="0.55"/><stop offset="1" stop-color="#6d28d9" stop-opacity="0"/></radialGradient>
<radialGradient id="a2" cx="0.92" cy="0.05" r="0.6"><stop offset="0" stop-color="#0e7490" stop-opacity="0.45"/><stop offset="1" stop-color="#0e7490" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#ffffff" stroke-opacity="0.05"/></pattern>
<radialGradient id="gf" cx="0.72" cy="0.5" r="0.55"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
<mask id="gm"><rect width="1200" height="420" fill="url(#gf)"/></mask>
<linearGradient id="tg" x1="0" y1="0" x2="0" y2="1"><stop offset="0.35" stop-color="#ffffff"/><stop offset="1" stop-color="#b4b4bd"/></linearGradient>
<linearGradient id="ag" x1="0" y1="0" x2="1" y2="0" spreadMethod="reflect">
<stop offset="0" stop-color="{VIOLET}"/><stop offset="0.5" stop-color="{BLUE}"/><stop offset="1" stop-color="{CYAN}"/>
<animateTransform attributeName="gradientTransform" type="translate" values="0 0;1 0;0 0" dur="6s" repeatCount="indefinite"/>
</linearGradient>
<linearGradient id="sweep" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0"/><stop offset="0.5" stop-color="{CYAN}"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></linearGradient>
<filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<g clip-path="url(#card)">
<rect width="1200" height="420" fill="{BG}"/>
<rect width="1200" height="420" fill="url(#a1)"/>
<rect width="1200" height="420" fill="url(#a2)"/>
<rect width="1200" height="420" fill="url(#grid)" mask="url(#gm)"/>
{network(rng)}
<rect x="64" y="52" width="{pill_w:.1f}" height="36" rx="18" fill="rgba(14,14,20,0.75)" stroke="rgba(255,255,255,0.14)"/>
<circle cx="86" cy="70" r="4.5" fill="{GOOD}"/>
<circle cx="86" cy="70" r="4.5" fill="none" stroke="{GOOD}" stroke-width="2"><animate attributeName="r" values="4.5;12" dur="2s" repeatCount="indefinite"/><animate attributeName="stroke-opacity" values="0.7;0" dur="2s" repeatCount="indefinite"/></circle>
<text x="102" y="75" class="sans" font-size="15" fill="{TEXT_2}">{esc(pill_text)}</text>
<text x="62" y="166" class="sans" font-size="58" font-weight="650" letter-spacing="-2.4" fill="url(#tg)">{esc(name)}</text>
<text x="64" y="218" class="sans" font-size="32" font-weight="600" letter-spacing="-0.9" fill="url(#ag)">AI / ML Engineer</text>
<text x="64" y="258" class="sans" font-size="20" fill="{TEXT_2}">Machine learning that works in the field, not just in the lab.</text>
{chips(64, 292)}
<rect x="0.5" y="0.5" width="1199" height="419" rx="21.5" fill="none" stroke="rgba(255,255,255,0.1)"/>
<rect x="-600" y="417" width="600" height="3" fill="url(#sweep)"><animateTransform attributeName="transform" type="translate" values="0 0;1800 0" dur="5s" repeatCount="indefinite"/></rect>
</g>
</svg>'''


def typing() -> str:
    lines = ["training models that work in the field",
             "shipping LLM agents to production",
             "building drift detection for ML pipelines",
             "deploying serverless ML on AWS"]
    size, x0, base = 22, 58, 86
    cw = size * 0.6
    type_s, hold, del_s, gap = 0.055, 1.8, 0.022, 0.45
    slots = [len(t) * type_s + hold + len(t) * del_s + gap for t in lines]
    total = sum(slots)
    texts, cursor_vals, cursor_times = [], [x0], [0.0]
    start = 0.0
    for i, (line, slot) in enumerate(zip(lines, slots)):
        frames = [(0.0, 0)]
        for k in range(1, len(line) + 1):
            frames.append((start + k * type_s, k))
        del_start = start + len(line) * type_s + hold
        for k in range(len(line) - 1, -1, -1):
            frames.append((del_start + (len(line) - k) * del_s, k))
        frames = sorted({t: n for t, n in frames}.items())
        key_times = ";".join(f"{t / total:.5f}" for t, _ in frames) + ";1"
        widths = ";".join(f"{n * cw:.1f}" for _, n in frames) + ";0"
        texts.append(
            f'<clipPath id="c{i}"><rect x="{x0}" y="{base - 24}" height="32" width="0">'
            f'<animate attributeName="width" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete" '
            f'keyTimes="{key_times}" values="{widths}"/></rect></clipPath>'
            f'<text x="{x0}" y="{base}" class="mono" font-size="{size}" fill="{TEXT}" clip-path="url(#c{i})">{esc(line)}</text>')
        for t, n in frames[1:]:
            cursor_times.append(t / total)
            cursor_vals.append(x0 + n * cw + 2)
        start += slot
    pairs = sorted(dict(zip(cursor_times, cursor_vals)).items())
    c_times = ";".join(f"{t:.5f}" for t, _ in pairs) + ";1"
    c_vals = ";".join(f"{v:.1f}" for _, v in pairs) + f";{x0 + 2}"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="120" viewBox="0 0 1200 120" role="img" aria-labelledby="tt">
<title id="tt">{esc(' · '.join(lines))}</title>
<defs><style>{font_face_css()}.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}</style></defs>
<rect x="0.5" y="0.5" width="1199" height="119" rx="16" fill="#0a0a0f" stroke="rgba(255,255,255,0.1)"/>
<circle cx="28" cy="24" r="5.5" fill="#2a2a33"/><circle cx="46" cy="24" r="5.5" fill="#2a2a33"/><circle cx="64" cy="24" r="5.5" fill="#2a2a33"/>
<text x="600" y="28" text-anchor="middle" class="mono" font-size="12.5" fill="{MUTED}">dinesh@github: ~</text>
<line x1="0" x2="1200" y1="46" y2="46" stroke="rgba(255,255,255,0.08)"/>
<text x="30" y="{base}" class="mono" font-size="{size}" fill="{GOOD}">$</text>
{''.join(texts)}
<rect y="{base - 20}" width="11" height="26" rx="2" fill="{VIOLET}" x="{x0 + 2}">
<animate attributeName="x" dur="{total:.2f}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{c_times}" values="{c_vals}"/>
<animate attributeName="opacity" values="1;1;0.15;0.15" keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/>
</rect>
</svg>'''


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "header.svg").write_text(header(), encoding="utf-8")
    (OUT / "typing.svg").write_text(typing(), encoding="utf-8")
    for name in ("header.svg", "typing.svg"):
        print(name, (OUT / name).stat().st_size, "bytes")
