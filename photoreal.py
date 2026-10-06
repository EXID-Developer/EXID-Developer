#!/usr/bin/env python3
"""Slice the approved Elysium artwork into independent cards and add animated light effects.

Input : assets/photoreal/approved-design.png (Elysium) and assets/photoreal-cyber/approved-design.png (Cyberpunk)
Output: <same dir>/<card>.svg (self-contained: cropped WebP + SMIL light animation)
"""
import base64
import io
import pathlib
import random
import re
import zlib
from html import escape

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent

VIEW_E = {
    "profile": (23, 17, 1075, 438),
    "section-sns": (24, 459, 1074, 42),
    "github": (25, 503, 359, 336),
    "repositories": (385, 503, 359, 336),
    "stars": (742, 503, 359, 336),
    "section-stack": (24, 846, 1074, 42),
    "backend": (25, 891, 359, 457),
    "frontend": (385, 891, 359, 457),
    "ai-tools": (742, 891, 359, 457),
}
VIEW_C = {
    "profile": (20, 20, 1160, 474),
    "section-sns": (20, 500, 1160, 56),
    "github": (20, 558, 380, 360),
    "repositories": (412, 558, 380, 360),
    "stars": (796, 558, 384, 360),
    "section-stack": (20, 922, 1160, 56),
    "backend": (20, 982, 380, 486),
    "frontend": (412, 982, 380, 486),
    "ai-tools": (796, 982, 384, 486),
}
TITLE = {
    "profile": "PROFILE - Think with your code. EXID-Developer. Server, Interface, Experiment.",
    "section-sns": "SNS LIST", "section-stack": "LOADOUT",
    "github": "GitHub", "repositories": "Repositories", "stars": "Stars",
    "backend": "Backend - Java, Spring Boot, MyBatis",
    "frontend": "Frontend - TypeScript, React, Vite",
    "ai-tools": "AI and Tools - Spring AI, Git",
}
# glow centres in full-image coordinates: (x, y, radius, colour, period, delay)
GLOW_E = {
    "profile": [(590, 240, 135, "#CFE8FF", 4.5, 0), (570, 392, 120, "#FFD98A", 5.5, 1.2), (900, 210, 70, "#FFD98A", 6, 2)],
    "github": [(210, 615, 115, "#FFE2A0", 5, 0)],
    "repositories": [(552, 632, 115, "#FFF1CC", 5.5, .8)],
    "stars": [(920, 610, 105, "#FFE08A", 4.2, .4)],
    "backend": [(205, 1040, 95, "#FFB84D", 3.6, 0), (205, 1130, 70, "#FFB84D", 4.4, 1)],
    "frontend": [(545, 1050, 105, "#6FD3FF", 4, .5)],
    "ai-tools": [(915, 1050, 105, "#FFD27A", 4.8, 0)],
}
GLOW_C = {
    "profile": [(590, 250, 150, "#9FD8FF", 4.5, 0), (585, 455, 110, "#FF2BD6", 3.8, 1.2), (868, 185, 60, "#00F0FF", 5, 2)],
    "github": [(215, 690, 120, "#00F0FF", 4.6, 0)],
    "repositories": [(600, 690, 120, "#FF2BD6", 5.2, .8)],
    "stars": [(985, 690, 115, "#FF2BD6", 4, .4)],
    "backend": [(215, 1150, 100, "#00F0FF", 3.6, 0)],
    "frontend": [(580, 1130, 115, "#00F0FF", 4.2, .5)],
    "ai-tools": [(985, 1130, 115, "#FF2BD6", 4.8, 0)],
}
SPARK_E = {"profile": (440, 20, 700, 330), "github": (60, 520, 360, 760), "repositories": (420, 520, 740, 760), "stars": (780, 520, 1090, 760),
           "backend": (60, 920, 360, 1130), "frontend": (420, 920, 720, 1130), "ai-tools": (780, 920, 1090, 1130)}
SPARK_C = {"profile": (440, 40, 740, 360), "github": (60, 590, 380, 800), "repositories": (440, 590, 780, 800), "stars": (830, 590, 1160, 800),
           "backend": (60, 1010, 380, 1230), "frontend": (440, 1010, 780, 1230), "ai-tools": (830, 1010, 1160, 1230)}
THEMES = {
    "elysium": dict(dir="photoreal", view=VIEW_E, glow=GLOW_E, spark=SPARK_E, star="#FFFBE6", sweep="#FFF4D0",
                    ink="#E8C170", ink2="#F5D78E", font="Cinzel, Georgia, 'Times New Roman', serif"),
    "cyber": dict(dir="photoreal-cyber", view=VIEW_C, glow=GLOW_C, spark=SPARK_C, star="#DFFBFF", sweep="#BFF6FF",
                  ink="#00F0FF", ink2="#FF2BD6", txt="#DDE6F7", font="Cinzel, Georgia, 'Times New Roman', serif"),
}


def webp_b64(im):
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=90, method=6)
    return base64.b64encode(buf.getvalue()).decode()


def card(key, im, T):
    VIEW, GLOW, SPARK = T["view"], T["glow"], T["spark"]
    x, y, w, h = VIEW[key]
    crop = im.crop((x, y, x + w, y + h))
    defs, body = "", ""
    r = random.Random(zlib.crc32(key.encode()))
    for i, (gx, gy, gr, col, per, dl) in enumerate(GLOW.get(key, [])):
        defs += (f'<radialGradient id="g{i}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{col}" stop-opacity=".75"/>'
                 f'<stop offset=".45" stop-color="{col}" stop-opacity=".25"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></radialGradient>')
        body += (f'<circle cx="{gx - x}" cy="{gy - y}" r="{gr}" fill="url(#g{i})" opacity="0">'
                 f'<animate attributeName="opacity" values="0;.85;0" dur="{per}s" begin="{dl}s" repeatCount="indefinite"/>'
                 f'<animate attributeName="r" values="{gr * .85:.0f};{gr * 1.1:.0f};{gr * .85:.0f}" dur="{per}s" begin="{dl}s" repeatCount="indefinite"/></circle>')
    if key in SPARK:
        x0, y0, x1, y1 = SPARK[key]
        for i in range(9):
            sx, sy, k = r.uniform(x0, x1) - x, r.uniform(y0, y1) - y, r.choice([5, 7, 9])
            body += (f'<path d="M0 -{k}L{k * .22:.1f} 0L0 {k}L-{k * .22:.1f} 0Z" fill="{T["star"]}" transform="translate({sx:.0f} {sy:.0f})" opacity="0">'
                     f'<animate attributeName="opacity" values="0;1;0" dur="{r.uniform(1.8, 3.8):.1f}s" begin="{r.uniform(0, 4):.1f}s" repeatCount="indefinite"/></path>')
    if key not in ("section-sns", "section-stack"):
        defs += (f'<linearGradient id="sw" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T["sweep"]}" stop-opacity="0"/>'
                 f'<stop offset=".5" stop-color="{T["sweep"]}" stop-opacity=".16"/><stop offset="1" stop-color="{T["sweep"]}" stop-opacity="0"/></linearGradient>')
        body += (f'<rect x="-{w * .4:.0f}" y="-20" width="{w * .3:.0f}" height="{h + 40}" fill="url(#sw)" transform="skewX(-18)">'
                 f'<animate attributeName="x" values="-{w * .4:.0f};{w * 1.3:.0f};{w * 1.3:.0f}" keyTimes="0;.4;1" dur="8s" begin="{r.uniform(0, 3):.1f}s" repeatCount="indefinite"/></rect>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f'<title>{escape(TITLE[key])}</title><defs>{defs}</defs>'
            f'<image width="{w}" height="{h}" href="data:image/webp;base64,{webp_b64(crop)}"/>{body}</svg>')


STRIPS = {"stats": "04 / STATS", "snake": "05 / SNAKE", "quest": "06 / QUEST"}


def strip(label, T):
    x0 = 20 + len(label) * 15
    c1, c2 = T["ink"], T["ink2"]
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="1074" height="42" viewBox="0 0 1074 42" role="img">'
            f'<title>{escape(label)}</title><defs><linearGradient id="l" x1="0" x2="1"><stop offset="0" stop-color="{c1}" stop-opacity=".1"/>'
            f'<stop offset="1" stop-color="{c1}" stop-opacity=".9"/></linearGradient></defs>'
            f'<text x="12" y="28" font-family="{T["font"]}" font-size="19" letter-spacing="3" fill="{T.get("txt", c1)}">{escape(label)}</text>'
            f'<rect x="{x0}" y="20" width="{1040 - x0}" height="1.5" fill="url(#l)"/>'
            f'<path d="M1042 21l9-9 9 9-9 9z" fill="{c2}"><animate attributeName="opacity" values=".5;1;.5" dur="3s" repeatCount="indefinite"/></path></svg>')


def stack_thirds():
    """Cut the stack panel into three tiles so it can sit in the same 3-column row as the photoreal cards."""
    for tag in ("elysium", "cyber"):
        src = ROOT / "assets" / f"stack-{tag}.svg"
        if not src.exists():
            continue
        t = src.read_text(encoding="utf-8")
        for i in range(3):
            u = re.sub(r'viewBox="0 0 1200 340" width="1200" height="340"', f'viewBox="{i * 400} 0 400 340" width="400" height="340"', t, count=1)
            (ROOT / "assets" / f"stack-{tag}-{i}.svg").write_text(u, encoding="utf-8")


def main():
    stack_thirds()
    for T in THEMES.values():
        out = ROOT / "assets" / T["dir"]
        src = out / "approved-design.png"
        if not src.exists():
            print(f"photoreal: {src.relative_to(ROOT)} not found, skipped")
            continue
        im = Image.open(src).convert("RGB")
        for key in T["view"]:
            (out / f"{key}.svg").write_text(card(key, im, T), encoding="utf-8")
        for k, label in STRIPS.items():
            (out / f"strip-{k}.svg").write_text(strip(label, T), encoding="utf-8")
        (out / "blank.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1" viewBox="0 0 1200 1"/>', encoding="utf-8")
        print("photoreal cards generated:", T["dir"], len(T["view"]))


if __name__ == "__main__":
    main()
