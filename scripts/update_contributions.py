#!/usr/bin/env python3
"""Regenerate assets/contributions.svg from live GitHub contribution data.

Runs in GitHub Actions every 12h (see .github/workflows/update-profile.yml).
Source: the public contributions API (jogruber.de), cross-checked against
github.com/users/Manan-Khanna05/contributions. If the fetch fails, the
existing SVG is left untouched and the script exits 0.
"""
import json, pathlib, urllib.request

USER = "Manan-Khanna05"
SVG = pathlib.Path(__file__).resolve().parent.parent / "assets" / "contributions.svg"

def main():
    try:
        with urllib.request.urlopen(
            f"https://github-contributions-api.jogruber.de/v4/{USER}", timeout=20
        ) as r:
            data = json.loads(r.read())
    except Exception as e:
        print("fetch failed, keeping existing SVG:", e)
        return
    days = sorted(data["contributions"], key=lambda c: c["date"])[-30:]
    total_year = sum(data["total"].values())
    in30 = sum(c["count"] for c in days)
    peak = max(c["count"] for c in days)
    W, H, X0, X1, Y0, Y1 = 1000, 300, 50, 980, 250, 60
    vmax = max(peak, 6)
    def x(i): return X0 + i * (X1 - X0) / 29
    def y(v): return Y0 - v / vmax * (Y0 - Y1)
    pts = " ".join(f"{x(i):.1f},{y(c['count']):.1f}" for i, c in enumerate(days))
    area = f"M{x(0):.1f},{Y0} " + " ".join(f"L{x(i):.1f},{y(c['count']):.1f}" for i, c in enumerate(days)) + f" L{x(29):.1f},{Y0} Z"
    grid = "".join(
        f'<line x1="{X0}" y1="{y(v)}" x2="{X1}" y2="{y(v)}" stroke="#21262d"/>'
        f'<text x="{X0-8}" y="{y(v)+4}" fill="#8b949e" font-size="11" text-anchor="end">{v}</text>'
        for v in (0, vmax // 2, vmax))
    labels = "".join(
        f'<text x="{x(i):.1f}" y="{Y0+20}" fill="#8b949e" font-size="11" text-anchor="middle">{d[5:]}</text>'
        for i, d in enumerate(c["date"] for c in days) if i % 6 == 0)
    dots = "".join(
        f'<circle cx="{x(i):.1f}" cy="{y(c["count"]):.1f}" r="3.5" fill="#ffffff"/>'
        for i, c in enumerate(days) if c["count"])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="300" viewBox="0 0 1000 300" font-family="Segoe UI, Helvetica, Arial, sans-serif">
<rect width="1000" height="300" rx="12" fill="#0d1117" stroke="#30363d"/>
<text x="24" y="34" font-size="15" font-weight="600" fill="#e6edf3">📈 Activity &amp; Contribution Flow</text>
<text x="976" y="34" font-size="12" fill="#8b949e" text-anchor="end">{total_year} Total Year · {in30} in 30D · Peak: {peak}/day</text>
<line x1="24" y1="48" x2="976" y2="48" stroke="#30363d"/>
{grid}
<defs><linearGradient id="ag" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#2997ff" stop-opacity="0.35"/><stop offset="100%" stop-color="#2997ff" stop-opacity="0.02"/></linearGradient></defs>
<path d="{area}" fill="url(#ag)"/>
<polyline points="{pts}" fill="none" stroke="#ffffff" stroke-width="2" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="1400" stroke-dashoffset="1400"><animate attributeName="stroke-dashoffset" from="1400" to="0" dur="2s" fill="freeze"/></polyline>
{dots}
{labels}
<text x="24" y="288" font-size="11" fill="#8b949e">Source: github.com/{USER} contributions · auto-updated every 12h</text>
</svg>'''
    SVG.write_text(svg)
    print(f"wrote {SVG}: year={total_year}, 30D={in30}, peak={peak}")

if __name__ == "__main__":
    main()
