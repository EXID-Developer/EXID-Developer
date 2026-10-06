#!/usr/bin/env python3
"""Live GitHub numbers (repos / followers / stars) rendered as themed SVG strips.

Output: assets/livestat-elysium.svg, assets/livestat-cyber.svg
Uses GITHUB_TOKEN when present (higher rate limit). If the API is unreachable the previous files are kept.
"""
import json
import os
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
USER = "EXID-Developer"

PAL = {
    "elysium": dict(bg1="#0B1426", bg2="#12234A", edge1="#F5D78E", edge2="#8FD3FF", label="#9FB6D9", num="#FFF3D2",
                    glow="#F5D78E", font="Cinzel, Georgia, 'Times New Roman', serif"),
    "cyber": dict(bg1="#0A0A2E", bg2="#1B0A3D", edge1="#FF2BD6", edge2="#00F0FF", label="#9FA8D8", num="#FFFFFF",
                  glow="#00F0FF", font="'Share Tech Mono', 'Courier New', monospace"),
}


def api(path):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={"User-Agent": "profile-livestat", "Accept": "application/vnd.github+json"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def fetch():
    u = api(f"/users/{USER}")
    stars, page = 0, 1
    while True:
        repos = api(f"/users/{USER}/repos?per_page=100&page={page}")
        stars += sum(r.get("stargazers_count", 0) for r in repos)
        if len(repos) < 100:
            break
        page += 1
    return [("REPOSITORIES", u["public_repos"]), ("FOLLOWERS", u["followers"]), ("STARS", stars), ("FOLLOWING", u["following"])]


def svg(tag, items):
    p = PAL[tag]
    W, H, n = 1074, 96, len(items)
    cw = (W - 40) / n
    cells = ""
    for i, (label, val) in enumerate(items):
        cx = 20 + cw * i + cw / 2
        if i:
            cells += f'<rect x="{20 + cw * i:.0f}" y="22" width="1" height="52" fill="{p["edge1"]}" opacity=".35"/>'
        cells += (f'<text x="{cx:.0f}" y="42" text-anchor="middle" font-family="{p["font"]}" font-size="12" letter-spacing="4" fill="{p["label"]}">{label}</text>'
                  f'<text x="{cx:.0f}" y="76" text-anchor="middle" font-family="{p["font"]}" font-size="34" font-weight="700" fill="{p["num"]}">{val}'
                  f'<animate attributeName="opacity" values="1;.78;1" dur="{3 + i * .6:.1f}s" repeatCount="indefinite"/></text>')
    ch = 14
    outline = f"M{ch} 2H{W - ch}L{W - 2} {ch}V{H - ch}L{W - ch} {H - 2}H{ch}L2 {H - ch}V{ch}Z"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img">'
            f'<title>GitHub live stats: ' + ", ".join(f"{l} {v}" for l, v in items) + '</title>'
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{p["bg1"]}"/><stop offset="1" stop-color="{p["bg2"]}"/></linearGradient>'
            f'<linearGradient id="ed" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{p["edge1"]}"/><stop offset=".5" stop-color="{p["edge2"]}"/><stop offset="1" stop-color="{p["edge1"]}"/></linearGradient>'
            f'<linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="{p["glow"]}" stop-opacity="0"/><stop offset=".5" stop-color="{p["glow"]}" stop-opacity=".18"/><stop offset="1" stop-color="{p["glow"]}" stop-opacity="0"/></linearGradient>'
            f'<clipPath id="c"><path d="{outline}"/></clipPath></defs>'
            f'<path d="{outline}" fill="url(#bg)" stroke="url(#ed)" stroke-width="2"/>'
            f'<g clip-path="url(#c)"><rect x="-200" y="0" width="160" height="{H}" fill="url(#sw)" transform="skewX(-18)">'
            f'<animate attributeName="x" values="-200;{W + 100};{W + 100}" keyTimes="0;.4;1" dur="7s" repeatCount="indefinite"/></rect></g>'
            f'{cells}</svg>')


def main():
    try:
        items = fetch()
    except Exception as e:  # keep previous files on any failure
        print("livestat: API unavailable, keeping previous files:", e)
        items = None
    out = ROOT / "assets"
    out.mkdir(exist_ok=True)
    for tag in PAL:
        f = out / f"livestat-{tag}.svg"
        if items is not None:
            f.write_text(svg(tag, items), encoding="utf-8")
        elif not f.exists():
            f.write_text(svg(tag, [("REPOSITORIES", "-"), ("FOLLOWERS", "-"), ("STARS", "-"), ("FOLLOWING", "-")]), encoding="utf-8")
    print("livestat:", items)


if __name__ == "__main__":
    main()
