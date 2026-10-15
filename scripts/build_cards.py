"""Build the live 'Languages' and 'Activity' cards from the GitHub API.

Runs daily in GitHub Actions (stdlib only). Locally:
    GITHUB_TOKEN=$(gh auth token) GH_USER=Dinesh-kumar9 python scripts/build_cards.py
"""

import json
import math
import os
import urllib.request
from datetime import date
from pathlib import Path

from svg_common import BG, CYAN, MONO, MUTED, SANS, TEXT, TEXT_2, VIOLET, esc, font_face_css

USER = os.environ.get("GH_USER", "Dinesh-kumar9")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = Path(__file__).resolve().parent.parent / "assets"

# GitHub's language colours, lightened where they'd vanish on a near-black card.
LANG_COLORS = {
    "Python": "#3572A5", "HTML": "#e34c26", "JavaScript": "#f1e05a", "CSS": "#9b6dd7",
    "TypeScript": "#3178c6", "HCL": "#844FBA", "Java": "#b07219", "Jupyter Notebook": "#DA5B0B",
    "Shell": "#89e051", "Dockerfile": "#7aa1b3", "C": "#a8b9cc", "Mako": "#7e858d",
}
OTHER = "#6b7280"


def api(url: str, body: dict | None = None):
    req = urllib.request.Request(url, data=json.dumps(body).encode() if body else None, headers={
        "Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github+json",
        "User-Agent": f"{USER}-profile-cards"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def languages() -> list[tuple[str, float]]:
    totals: dict[str, int] = {}
    page = 1
    while True:
        repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}")
        for repo in repos:
            if repo["fork"]:
                continue
            for lang, size in api(repo["languages_url"]).items():
                totals[lang] = totals.get(lang, 0) + size
        if len(repos) < 100:
            break
        page += 1
    grand = sum(totals.values()) or 1
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    top = [(name, size / grand) for name, size in ranked[:5]]
    rest = sum(size for _, size in ranked[5:]) / grand
    if rest > 0:
        top.append(("Other", rest))
    return top


def activity() -> dict:
    query = """query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{
      totalContributions weeks{contributionDays{date contributionCount}}}}}}"""
    cal = api("https://api.github.com/graphql", {"query": query, "variables": {"login": USER}})
    cal = cal["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]
    days = [d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"]]
    longest = run = 0
    for count in days:
        run = run + 1 if count else 0
        longest = max(longest, run)
    return {"total": cal["totalContributions"], "longest": longest, "busiest": max(weeks, default=0), "weeks": weeks}


def frame(title: str, subtitle: str, body: str, label: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="600" height="250" viewBox="0 0 600 250" role="img" aria-label="{esc(label)}">
<title>{esc(label)}</title>
<defs><style>{font_face_css()}.sans{{font-family:{SANS}}}.mono{{font-family:{MONO}}}</style>
<clipPath id="card"><rect width="600" height="250" rx="16"/></clipPath>
<radialGradient id="glow" cx="0.05" cy="-0.1" r="0.8"><stop offset="0" stop-color="#6d28d9" stop-opacity="0.35"/><stop offset="1" stop-color="#6d28d9" stop-opacity="0"/></radialGradient>
<linearGradient id="line" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{VIOLET}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
<linearGradient id="area" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{VIOLET}" stop-opacity="0.28"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/></linearGradient>
</defs>
<g clip-path="url(#card)">
<rect width="600" height="250" fill="{BG}"/><rect width="600" height="250" fill="url(#glow)"/>
<text x="26" y="42" class="sans" font-size="18" font-weight="600" fill="{TEXT}">{esc(title)}</text>
<text x="26" y="62" class="mono" font-size="11.5" fill="{MUTED}">{esc(subtitle)}</text>
<text x="574" y="42" text-anchor="end" class="mono" font-size="10.5" fill="{MUTED}">updated {date.today():%d %b %Y}</text>
{body}
<rect x="0.5" y="0.5" width="599" height="249" rx="15.5" fill="none" stroke="rgba(255,255,255,0.1)"/>
</g>
</svg>'''


def languages_card(langs: list[tuple[str, float]]) -> str:
    x, bar_w, parts = 26.0, 548.0, ['<clipPath id="bar"><rect x="26" y="84" width="548" height="12" rx="6"/></clipPath><g clip-path="url(#bar)">']
    for i, (name, share) in enumerate(langs):
        w = bar_w * share
        color = LANG_COLORS.get(name, OTHER)
        gap = 2 if i < len(langs) - 1 else 0
        parts.append(f'<rect x="{x:.1f}" y="84" height="12" width="0" fill="{color}">'
                     f'<animate attributeName="width" from="0" to="{max(0, w - gap):.1f}" dur="0.7s" '
                     f'begin="{0.15 * i:.2f}s" fill="freeze"/></rect>')
        x += w
    parts.append("</g>")
    for i, (name, share) in enumerate(langs):
        col, row = i % 2, i // 2
        lx, ly = 26 + col * 284, 136 + row * 34
        color = LANG_COLORS.get(name, OTHER)
        parts.append(f'<circle cx="{lx + 6}" cy="{ly - 5}" r="5" fill="{color}"/>'
                     f'<text x="{lx + 20}" y="{ly}" class="sans" font-size="14.5" font-weight="500" fill="{TEXT}">{esc(name)}</text>'
                     f'<text x="{lx + 264}" y="{ly}" text-anchor="end" class="mono" font-size="13" fill="{TEXT_2}">{share * 100:.1f}%</text>')
    label = "Languages across public repos: " + ", ".join(f"{n} {s * 100:.1f}%" for n, s in langs)
    return frame("Languages", "across my public repos, by bytes of code", "".join(parts), label)


def activity_card(a: dict) -> str:
    stats = [(f"{a['total']:,}", "contributions"), (f"{a['longest']} days", "longest streak"),
             (f"{a['busiest']}", "busiest week")]
    parts = []
    for i, (value, label) in enumerate(stats):
        sx = 26 + i * 190
        parts.append(f'<text x="{sx}" y="112" class="sans" font-size="30" font-weight="650" letter-spacing="-1" fill="{TEXT}">{esc(value)}</text>'
                     f'<text x="{sx}" y="132" class="mono" font-size="11.5" fill="{MUTED}">{esc(label)}</text>')
    weeks = a["weeks"] or [0]
    top = max(weeks) or 1
    x0, x1, y0, y1 = 26, 574, 226, 156
    pts = [(x0 + (x1 - x0) * i / max(1, len(weeks) - 1), y0 - (y0 - y1) * v / top) for i, v in enumerate(weeks)]
    line = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) + 1
    area = f"{line} L{x1},{y0} L{x0},{y0} Z"
    parts.append(f'<line x1="{x0}" x2="{x1}" y1="{y0}" y2="{y0}" stroke="rgba(255,255,255,0.12)"/>'
                 f'<path d="{area}" fill="url(#area)" opacity="0"><animate attributeName="opacity" from="0" to="1" '
                 f'begin="1s" dur="0.8s" fill="freeze"/></path>'
                 f'<path d="{line}" fill="none" stroke="url(#line)" stroke-width="2" stroke-linejoin="round" '
                 f'stroke-linecap="round" stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}">'
                 f'<animate attributeName="stroke-dashoffset" from="{length:.0f}" to="0" dur="1.6s" fill="freeze"/></path>'
                 f'<text x="574" y="243" text-anchor="end" class="mono" font-size="10.5" fill="{MUTED}">weekly contributions, last 12 months</text>')
    label = (f"Activity in the last 12 months: {a['total']} contributions, longest streak {a['longest']} days, "
             f"busiest week {a['busiest']} contributions.")
    return frame("Activity", "last 12 months on GitHub", "".join(parts), label)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    langs = languages()
    act = activity()
    (OUT / "stats-languages.svg").write_text(languages_card(langs), encoding="utf-8")
    (OUT / "stats-activity.svg").write_text(activity_card(act), encoding="utf-8")
    print("languages:", ", ".join(f"{n} {s:.1%}" for n, s in langs))
    print("activity:", {k: v for k, v in act.items() if k != "weeks"}, "weeks:", len(act["weeks"]))
