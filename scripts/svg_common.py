"""Shared helpers for the profile's SVG cards: embedded fonts and palette."""

import base64
from pathlib import Path

FONT_DIR = Path(__file__).parent / "fonts"

BG = "#050507"
TEXT = "#ededf0"
TEXT_2 = "#a1a1aa"
MUTED = "#8a8a93"
LINE = "rgba(255,255,255,0.08)"
VIOLET = "#a78bfa"
BLUE = "#60a5fa"
CYAN = "#22d3ee"
GOOD = "#34d399"


def font_face_css() -> str:
    """@font-face rules with the subset Geist fonts inlined, so GitHub renders them."""
    rules = []
    for family, filename in (("Geist", "geist-sub.woff2"), ("Geist Mono", "geistmono-sub.woff2")):
        data = base64.b64encode((FONT_DIR / filename).read_bytes()).decode()
        rules.append(
            f"@font-face{{font-family:'{family}';font-weight:100 900;"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}"
        )
    return "".join(rules)


SANS = "'Geist',ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,sans-serif"
MONO = "'Geist Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def esc(text: str) -> str:
    return (text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))
