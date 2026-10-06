#!/usr/bin/env python3
"""EXID gold-crest profile theme.

Design language taken from the owner-supplied EXID GitHub Promo Pack: black field,
faint gold circuit traces, polished gold bevels, wine-red jewels, Cinzel capitals
and wide-tracked sans-serif captions.

  python crest.py          build assets/crest/*.svg (needs Pillow + fontTools + brotli)
  python build_readme.py   render README.md when theme.txt is "crest"

Every panel is a self-contained SVG: fonts are embedded as subset WOFF2 (SIL OFL,
see assets/crest/fonts/), the crest thumbnail as WebP. Statistics are dated
snapshots, not live counters.
"""
import base64, io, math
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "assets" / "crest"
FONTS = OUT / "fonts"
OWNER = "EXID-Developer"
U = f"https://github.com/{OWNER}"
SNAPSHOT = "2026-10-06"

# ---------------------------------------------------------------- palette
GOLD_HI, GOLD, GOLD_LO = "#fbe7b0", "#d9a646", "#6e4613"
IVORY, MUTED, DIM = "#efe4c8", "#a8987a", "#5c4f3a"
WINE, WINE_HI = "#7d1522", "#c23345"
INK, PANEL = "#080807", "#0f0d0a"
KR = "'Noto Sans KR','Apple SD Gothic Neo','Malgun Gothic',sans-serif"

STACK = [("I", "BACKEND", "{ }", ["Java", "Spring Boot", "MyBatis"]),
         ("II", "FRONTEND", "</>", ["TypeScript", "React", "Vite"]),
         ("III", "AI & TOOLS", "AI", ["Spring AI", "Git"])]
LANGS = [("Java", 53.76, "#d9a441"), ("TypeScript", 30.41, "#b8323f"), ("Python", 13.09, "#eadcb4"),
         ("HTML", 2.30, "#9a6a2f"), ("CSS", 0.36, "#8a8790"), ("JavaScript", 0.09, "#f3df85")]
ACTIVITY = [("114", "CONTRIBUTIONS"), ("1", "CURRENT STREAK"), ("5", "LONGEST STREAK")]
PROJECTS = [("damso", "TypeScript", "Explore source code and development history."),
            ("SpringAiBasic", "Java", "Spring AI study notes and experiments."),
            ("sivertown", "HTML", "React + Vite web project."),
            ("SpringBootMyBatis", "Java", "Spring Boot MyBatis project.")]
LANG_DOT = {"TypeScript": "#b8323f", "Java": "#d9a441", "HTML": "#9a6a2f"}
LINKS = [("github", "GITHUB", "@EXID-Developer", U),
         ("repositories", "REPOSITORIES", "Browse every project", U + "?tab=repositories"),
         ("stars", "STARS", "Starred collection", U + "?tab=stars")]
SECTIONS = {"stack": "TECH STACK", "connect": "CONNECT", "activity": "ACTIVITY", "projects": "FEATURED PROJECTS"}

# ---------------------------------------------------------------- fonts
_FONT_FILES = {"Cinzel": "Cinzel-Bold.ttf", "Mont": "Montserrat-Medium.ttf", "MontB": "Montserrat-Bold.ttf"}


def font_face(family, text):
    """Subset WOFF2 @font-face for exactly the characters used."""
    from fontTools import subset
    from fontTools.ttLib import TTFont
    chars = {c for c in text if ord(c) < 0x2E80} | set(" ")
    font = TTFont(FONTS / _FONT_FILES[family])
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["kern", "liga"]
    opts.name_IDs = []
    opts.notdef_outline = True
    s = subset.Subsetter(opts)
    s.populate(text="".join(sorted(chars)))
    s.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"@font-face{{font-family:'{family}E';src:url(data:font/woff2;base64,{b64}) format('woff2')}}"


# ---------------------------------------------------------------- svg helpers
class Svg:
    def __init__(self, w, h, title):
        self.w, self.h, self.title = w, h, title
        self.body, self.defs, self.css = [], [], []
        self.text_by_family = {"Cinzel": "", "Mont": "", "MontB": ""}

    def add(self, s):
        self.body.append(s)

    def text(self, x, y, value, size, family="Mont", fill=IVORY, anchor="start", spacing=0, extra=""):
        self.text_by_family[family] += str(value)
        fam = {"Cinzel": f"'CinzelE',serif", "Mont": f"'MontE',{KR}", "MontB": f"'MontBE',{KR}"}[family]
        ls = f' letter-spacing="{spacing}"' if spacing else ""
        self.add(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" fill="{fill}" '
                 f'text-anchor="{anchor}"{ls} {extra}>{escape(str(value))}</text>')

    def render(self):
        faces = "".join(font_face(f, t) for f, t in self.text_by_family.items() if t)
        css = faces + "".join(self.css)
        return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
                f'width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" role="img">'
                f'<title>{escape(self.title)}</title><defs>{common_defs(self.w, self.h)}{"".join(self.defs)}'
                f'<style>{css}</style></defs>{"".join(self.body)}</svg>')

    def save(self, name):
        (OUT / f"{name}.svg").write_text(self.render(), encoding="utf-8")


def common_defs(w, h):
    return (
        f'<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{GOLD_HI}"/><stop offset=".3" stop-color="#f0c96f"/>'
        f'<stop offset=".55" stop-color="#b98432"/><stop offset=".78" stop-color="{GOLD_LO}"/>'
        f'<stop offset="1" stop-color="#e2b65e"/></linearGradient>'
        f'<linearGradient id="goldEdge" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#fff0c4"/><stop offset=".25" stop-color="#c8913a"/>'
        f'<stop offset=".5" stop-color="#5f3c10"/><stop offset=".75" stop-color="#e3b55a"/>'
        f'<stop offset="1" stop-color="#8a5c1c"/></linearGradient>'
        f'<linearGradient id="goldLine" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{GOLD}" stop-opacity="0"/><stop offset=".5" stop-color="{GOLD_HI}"/>'
        f'<stop offset="1" stop-color="{GOLD}" stop-opacity="0"/></linearGradient>'
        f'<linearGradient id="wine" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{WINE_HI}"/><stop offset="1" stop-color="#3e070e"/></linearGradient>'
        f'<radialGradient id="field" cx=".5" cy=".42" r=".75">'
        f'<stop offset="0" stop-color="#1d170e"/><stop offset=".55" stop-color="#0d0b08"/>'
        f'<stop offset="1" stop-color="{INK}"/></radialGradient>'
        f'<radialGradient id="glow" cx=".5" cy=".5" r=".5">'
        f'<stop offset="0" stop-color="#f3c66b" stop-opacity=".35"/><stop offset="1" stop-color="#f3c66b" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="sheen" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#fff6dc" stop-opacity="0"/><stop offset=".5" stop-color="#fff6dc" stop-opacity=".16"/>'
        f'<stop offset="1" stop-color="#fff6dc" stop-opacity="0"/></linearGradient>'
    )


def chamfer(x, y, w, h, c):
    return (f"M{x + c},{y} H{x + w - c} L{x + w},{y + c} V{y + h - c} L{x + w - c},{y + h} "
            f"H{x + c} L{x},{y + h - c} V{y + c} Z")


def circuits(svg, w, h, seed=1, opacity=0.14):
    """Faint gold circuit traces like the banner background."""
    import random
    rnd = random.Random(seed)
    g = [f'<g fill="none" stroke="{GOLD}" stroke-opacity="{opacity}" stroke-width="1.4">']
    for _ in range(max(4, w // 160)):
        y0 = rnd.randrange(20, h - 20)
        side = rnd.choice(["l", "r"])
        x0 = 0 if side == "l" else w
        run = rnd.randrange(w // 10, w // 4)
        x1 = x0 + run if side == "l" else x0 - run
        dy = rnd.choice([-1, 1]) * rnd.randrange(15, 60)
        x2 = x1 + (abs(dy) if side == "l" else -abs(dy))
        x3 = x2 + (rnd.randrange(40, 160) if side == "l" else -rnd.randrange(40, 160))
        y1 = max(10, min(h - 10, y0 + dy))
        g.append(f'<path d="M{x0},{y0} H{x1} L{x2},{y1} H{x3}"/>')
        g.append(f'<circle cx="{x3}" cy="{y1}" r="3.2" fill="{INK}"/>')
    g.append("</g>")
    svg.add("".join(g))


def field(svg, seed=1):
    svg.add(f'<rect width="{svg.w}" height="{svg.h}" fill="url(#field)"/>')
    circuits(svg, svg.w, svg.h, seed)


def plaque(svg, x, y, w, h, c=26, cid="p", shine=True, gem=True):
    """Gold bevelled plate with cut corners, inner hairline, optional jewel and sheen."""
    outer = chamfer(x, y, w, h, c)
    inner = chamfer(x + 9, y + 9, w - 18, h - 18, c - 7)
    svg.defs.append(f'<clipPath id="{cid}"><path d="{outer}"/></clipPath>')
    svg.add(f'<path d="{outer}" fill="{PANEL}"/>')
    svg.add(f'<g clip-path="url(#{cid})"><rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#field)" opacity=".9"/>'
            f'<ellipse cx="{x + w / 2}" cy="{y}" rx="{w * .55}" ry="{h * .35}" fill="url(#glow)" opacity=".5"/></g>')
    svg.add(f'<path d="{outer}" fill="none" stroke="url(#goldEdge)" stroke-width="4"/>')
    svg.add(f'<path d="{inner}" fill="none" stroke="{GOLD}" stroke-opacity=".35" stroke-width="1.2"/>')
    if gem:
        jewel(svg, x + w / 2, y, 9)
    if shine:
        svg.add(f'<g clip-path="url(#{cid})"><rect class="sheen" x="{x - w * .4}" y="{y}" width="{w * .35}" '
                f'height="{h}" fill="url(#sheen)" transform="skewX(-18)"/></g>')
        if not any("sheen{" in c for c in svg.css):
            svg.css.append(
                f"@keyframes sw{{0%,20%{{transform:translateX(0) skewX(-18deg)}}70%,100%{{transform:translateX({svg.w * 1.6}px) skewX(-18deg)}}}}"
                ".sheen{animation:sw 8s ease-in-out infinite}"
                "@media (prefers-reduced-motion:reduce){.sheen{animation:none;opacity:0}}")


def jewel(svg, cx, cy, r):
    svg.add(f'<g transform="translate({cx},{cy}) rotate(45)"><rect x="{-r}" y="{-r}" width="{2 * r}" height="{2 * r}" '
            f'fill="url(#wine)" stroke="url(#gold)" stroke-width="2.4"/>'
            f'<rect x="{-r * .45}" y="{-r * .85}" width="{r * .5}" height="{r * .5}" fill="#ffd9de" opacity=".5"/></g>')


def diamond(svg, cx, cy, r, fill=None):
    svg.add(f'<path d="M{cx},{cy - r} L{cx + r},{cy} L{cx},{cy + r} L{cx - r},{cy} Z" fill="{fill or "url(#gold)"}"/>')


def hline(x1, x2, y, t=2):
    return f'<rect x="{min(x1, x2)}" y="{y - t / 2}" width="{abs(x2 - x1)}" height="{t}" fill="url(#goldLine)"/>'


def gold_rule(svg, x1, x2, y, ends=True):
    svg.add(hline(x1, x2, y))
    if ends:
        diamond(svg, (x1 + x2) / 2, y, 5)


def hexagon(svg, cx, cy, r, glyph):
    pts = " ".join(f"{cx + r * math.cos(math.radians(a))},{cy + r * math.sin(math.radians(a))}" for a in range(-90, 270, 60))
    pts2 = " ".join(f"{cx + (r - 12) * math.cos(math.radians(a))},{cy + (r - 12) * math.sin(math.radians(a))}" for a in range(-90, 270, 60))
    svg.add(f'<circle cx="{cx}" cy="{cy}" r="{r * 1.5}" fill="url(#glow)"/>')
    svg.add(f'<polygon points="{pts}" fill="url(#wine)" stroke="url(#goldEdge)" stroke-width="5"/>')
    svg.add(f'<polygon points="{pts2}" fill="{INK}" fill-opacity=".85" stroke="{GOLD}" stroke-opacity=".6" stroke-width="1.5"/>')
    svg.text(cx, cy + r * .25, glyph, r * .62, "MontB", "url(#gold)", "middle")


def crest_image(height):
    from PIL import Image
    c = Image.open(ROOT / "assets/porsche/src/EXID_Crest_Transparent.png").convert("RGBA")
    c = c.crop(c.getbbox())
    w = round(height * 2 * c.width / c.height)
    c = c.resize((w, height * 2), Image.LANCZOS)  # 2x for sharpness
    buf = io.BytesIO()
    c.save(buf, "WEBP", quality=86)
    return base64.b64encode(buf.getvalue()).decode(), w / 2


# ---------------------------------------------------------------- panels
def build_about():
    s = Svg(1600, 470, "EXID — Software Developer. Java와 Spring으로 서버를 세우고, React로 화면을 그리며, Spring AI로 새로운 가능성을 실험합니다.")
    plaque(s, 24, 24, 1552, 422, 34, "pa", gem=False)
    s.add('<g clip-path="url(#pa)">')
    circuits(s, 1600, 470, 3, 0.12)
    s.add('</g>')
    b64, cw = crest_image(330)
    s.add(f'<ellipse cx="{95 + cw / 2}" cy="235" rx="230" ry="210" fill="url(#glow)"/>')
    s.add(f'<image x="95" y="70" width="{cw}" height="330" href="data:image/webp;base64,{b64}"/>')
    x = 470
    s.text(x, 112, "PROFILE", 20, "MontB", WINE_HI, spacing=8)
    s.text(x, 205, "EXID", 104, "Cinzel", "url(#gold)", spacing=6)
    s.text(x + 4, 252, "SOFTWARE DEVELOPER", 27, "Mont", IVORY, spacing=9)
    s.add(hline(x - 40, x + 660, 282))
    s.text(x, 335, "Java와 Spring으로 서버를 세우고, React로 화면을 그리며,", 26, "Mont", IVORY)
    s.text(x, 375, "Spring AI로 새로운 가능성을 실험합니다.", 26, "Mont", IVORY)
    s.text(x, 418, "CODE · BUILD · SHIP", 18, "MontB", MUTED, spacing=7)
    s.save("about")


def build_section(key, label):
    s = Svg(1600, 120, label)
    tw = len(label) * 30 + 60
    l, r = 800 - tw / 2 - 30, 800 + tw / 2 + 30
    s.add(hline(120, l, 60) + hline(r, 1480, 60))
    diamond(s, l, 60, 6)
    diamond(s, r, 60, 6)
    jewel(s, 120, 60, 6)
    jewel(s, 1480, 60, 6)
    s.text(800, 73, label, 38, "Cinzel", "url(#gold)", "middle", spacing=10)
    s.save(f"section-{key}")


def build_stack():
    s = Svg(1600, 520, "Tech stack — Backend: Java, Spring Boot, MyBatis. Frontend: TypeScript, React, Vite. AI & Tools: Spring AI, Git.")
    for i, (num, title, glyph, items) in enumerate(STACK):
        x = 40 + i * 520
        plaque(s, x, 30, 480, 460, 30, f"ps{i}")
        s.text(x + 34, 82, num, 22, "Cinzel", MUTED, spacing=2)
        hexagon(s, x + 240, 135, 62, glyph)
        s.text(x + 240, 255, title, 36, "Cinzel", "url(#gold)", "middle", spacing=5)
        gold_rule(s, x + 90, x + 390, 282)
        for j, item in enumerate(items):
            yy = 340 + j * 50
            diamond(s, x + 240 - 120, yy - 9, 5, WINE_HI)
            s.text(x + 240 - 100, yy, item, 27, "Mont", IVORY)
    s.save("stack")


ICONS = {
    "github": lambda cx, cy: (f'<circle cx="{cx}" cy="{cy - 10}" r="13" fill="url(#gold)"/>'
                              f'<path d="M{cx - 24},{cy + 22} Q{cx},{cy - 6} {cx + 24},{cy + 22} Z" fill="url(#gold)"/>'),
    "repositories": lambda cx, cy: (f'<rect x="{cx - 20}" y="{cy - 24}" width="40" height="48" rx="4" fill="none" stroke="url(#gold)" stroke-width="4"/>'
                                    f'<path d="M{cx - 10},{cy - 10} H{cx + 10} M{cx - 10},{cy} H{cx + 10} M{cx - 10},{cy + 10} H{cx + 4}" stroke="url(#gold)" stroke-width="3"/>'),
    "stars": lambda cx, cy: '<polygon points="' + " ".join(
        f"{cx + (26 if k % 2 == 0 else 11) * math.cos(math.radians(-90 + k * 36))},{cy + 2 + (26 if k % 2 == 0 else 11) * math.sin(math.radians(-90 + k * 36))}"
        for k in range(10)) + '" fill="url(#gold)"/>',
}


def build_links():
    for key, title, sub, _ in LINKS:
        s = Svg(520, 160, f"{title.title()} — {sub}")
        plaque(s, 6, 10, 508, 140, 22, "pl", gem=False)
        s.add(f'<circle cx="82" cy="80" r="44" fill="url(#wine)" stroke="url(#goldEdge)" stroke-width="4"/>')
        s.add(ICONS[key](82, 80))
        s.text(150, 82, title, 30, "Cinzel", "url(#gold)", spacing=3)
        s.text(151, 114, sub, 18, "Mont", MUTED, spacing=1)
        s.text(476, 92, "→", 34, "MontB", GOLD, "end")
        s.save(f"link-{key}")


def build_activity():
    s = Svg(800, 470, f"Contribution snapshot {SNAPSHOT}: 114 total contributions, current streak 1, longest streak 5.")
    plaque(s, 10, 14, 780, 442, 28, "pac")
    s.text(52, 80, "CONTRIBUTIONS · TELEMETRY", 17, "MontB", MUTED, spacing=5)
    for i, (n, label) in enumerate(ACTIVITY):
        cx, cy, r = 160 + i * 240, 225, 74
        s.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{INK}" stroke="#2c2416" stroke-width="10"/>')
        a0, a1 = math.radians(135), math.radians(405)
        s.add(f'<path d="M{cx + r * math.cos(a0)},{cy + r * math.sin(a0)} A{r},{r} 0 1 1 {cx + r * math.cos(a1)},{cy + r * math.sin(a1)}" '
              f'fill="none" stroke="url(#goldEdge)" stroke-width="6" stroke-linecap="round"/>')
        jewel(s, cx, cy + r, 7)
        s.text(cx, cy + 20, n, 60, "Cinzel", "url(#gold)", "middle")
        s.text(cx, cy + 128, label, 15, "MontB", IVORY, "middle", spacing=3)
    s.text(52, 418, f"SNAPSHOT {SNAPSHOT}", 15, "MontB", DIM, spacing=4)
    s.text(748, 418, "LIVE STATS ↗", 15, "MontB", WINE_HI, "end", spacing=4)
    s.save("activity")


def build_languages():
    s = Svg(800, 470, "Most used languages: " + ", ".join(f"{n} {v:.2f}%" for n, v, _ in LANGS) + f". Snapshot {SNAPSHOT}.")
    plaque(s, 10, 14, 780, 442, 28, "pla")
    s.text(52, 80, "MOST USED LANGUAGES", 17, "MontB", MUTED, spacing=5)
    x, bw = 52, 696
    s.defs.append(f'<clipPath id="bar"><rect x="52" y="112" width="{bw}" height="16" rx="8"/></clipPath>')
    s.add('<g clip-path="url(#bar)">')
    for name, v, col in LANGS:
        w = bw * v / 100
        s.add(f'<rect x="{x}" y="112" width="{w + .5}" height="16" fill="{col}"/>')
        x += w
    s.add("</g>")
    s.add(f'<rect x="52" y="112" width="{bw}" height="16" rx="8" fill="none" stroke="url(#goldEdge)" stroke-width="1.5"/>')
    for i, (name, v, col) in enumerate(LANGS):
        cx, cy = 60 + (i // 3) * 360, 196 + (i % 3) * 64
        diamond(s, cx, cy - 9, 8, col)
        s.text(cx + 24, cy, name, 25, "Mont", IVORY)
        s.text(cx + 318, cy, f"{v:.2f}%", 25, "MontB", GOLD_HI, "end")
    s.text(52, 418, f"GITHUB README STATS · SNAPSHOT {SNAPSHOT}", 15, "MontB", DIM, spacing=4)
    s.save("languages")


def build_projects():
    for i, (repo, lang, desc) in enumerate(PROJECTS, 1):
        s = Svg(800, 380, f"{repo} — {lang}. {desc} Open repository.")
        plaque(s, 10, 14, 780, 352, 28, "pp")
        s.text(52, 82, f"FEATURED · 0{i}", 17, "MontB", MUTED, spacing=5)
        size = 50 if len(repo) < 14 else 42
        s.text(50, 160, repo, size, "Cinzel", "url(#gold)", spacing=1)
        s.text(52, 212, desc, 22, "Mont", IVORY)
        gold_rule(s, 52, 748, 258, ends=False)
        diamond(s, 62, 304, 8, LANG_DOT.get(lang, GOLD))
        s.text(84, 313, lang, 23, "Mont", IVORY)
        s.text(748, 313, "OPEN REPOSITORY →", 17, "MontB", GOLD_HI, "end", spacing=3)
        s.save(f"project-{repo}")


def build_footer():
    s = Svg(1600, 280, "EXID — Code. Build. Ship.")
    b64, cw = crest_image(150)
    s.add(f'<ellipse cx="800" cy="105" rx="200" ry="110" fill="url(#glow)"/>')
    s.add(hline(120, 800 - cw / 2 - 40, 105) + hline(800 + cw / 2 + 40, 1480, 105))
    jewel(s, 120, 105, 6)
    jewel(s, 1480, 105, 6)
    s.add(f'<image x="{800 - cw / 2}" y="30" width="{cw}" height="150" href="data:image/webp;base64,{b64}"/>')
    s.text(800, 228, "CODE · BUILD · SHIP", 24, "Cinzel", "url(#gold)", "middle", spacing=12)
    s.text(800, 262, "EXID-DEVELOPER", 15, "MontB", DIM, "middle", spacing=8)
    s.save("footer")


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    build_about()
    for k, v in SECTIONS.items():
        build_section(k, v)
    build_stack()
    build_links()
    build_activity()
    build_languages()
    build_projects()
    build_footer()
    print("Built crest theme assets:", len(list(OUT.glob("*.svg"))), "SVGs")


# ---------------------------------------------------------------- README
def img(name, alt, width="100%"):
    return f'<img src="./assets/crest/{name}.svg" width="{width}" alt="{escape(alt)}"/>'


def switches():
    out = []
    for label, key, col in [("AUTO", "auto", "8FD3FF"), ("ELYSIUM", "elysium", "F5D78E"), ("CYBERPUNK", "cyberpunk", "FF2BD6"),
                            ("PORSCHE", "porsche", "D73636"), ("CREST", "crest", "D9A646")]:
        url = f"{U}/{OWNER}/issues/new?title=theme%3A{key}&body=Submit+to+switch+the+profile+theme."
        state = "active" if key == "crest" else "switch"
        color = col if key == "crest" else "333333"
        out.append(f'<a href="{url}"><img src="https://img.shields.io/badge/{label}-{state}-{color}?style=flat-square&amp;labelColor=0B0A08" alt="{label}"/></a>')
    return " ".join(out)


def render():
    links = "\n".join(f'<a href="{href}">{img("link-" + k, f"{t.title()} — {sub}", "32%")}</a>' for k, t, sub, href in LINKS)
    p = [f'<a href="{U}/{r}">{img("project-" + r, f"{r} — {l}. {d} Open repository.", "49%")}</a>' for r, l, d in PROJECTS]
    s = f'''<!-- Generated by crest.py via build_readme.py. -->
<p align="right"><a href="#profile">PROFILE</a> · <a href="#stack">STACK</a> · <a href="#projects">PROJECTS</a></p>

<a href="./assets/crest/hero-film.mp4"><picture><source media="(prefers-reduced-motion: reduce)" srcset="./assets/crest/hero-still.webp"/><img src="./assets/crest/hero-motion.webp" width="100%" alt="EXID — Software Developer. Gold crest intro film that settles on the EXID banner: Explore my work on GitHub. Click to open MP4."/></picture></a>

<p align="right"><a href="./assets/crest/hero-film.mp4">▶ WATCH FILM · MP4</a></p>

<a name="profile"></a>

{img("about", "EXID — Software Developer. Java와 Spring으로 서버를 세우고, React로 화면을 그리며, Spring AI로 새로운 가능성을 실험합니다.")}

<a name="stack"></a>

{img("section-stack", "Tech Stack")}

{img("stack", "Backend: Java, Spring Boot, MyBatis. Frontend: TypeScript, React, Vite. AI & Tools: Spring AI, Git.")}

{img("section-connect", "Connect")}

<p align="center">
{links}
</p>

<details>
<summary>소개 · 기술 스택 · 링크를 텍스트로 보기</summary>

**EXID — Software Developer**

Java와 Spring으로 서버를 세우고, React로 화면을 그리며, Spring AI로 새로운 가능성을 실험합니다.

- **Backend:** Java · Spring Boot · MyBatis
- **Frontend:** TypeScript · React · Vite
- **AI & Tools:** Spring AI · Git
- [GitHub]({U}) · [Repositories]({U}?tab=repositories) · [Stars]({U}?tab=stars)

</details>

{img("section-activity", "Activity")}

<p align="center">
<a href="https://streak-stats.demolab.com?user={OWNER}">{img("activity", f"Contribution snapshot {SNAPSHOT}: total 114, current streak 1, longest streak 5. Click for live stats.", "49%")}</a>
{img("languages", "Most used languages: " + ", ".join(f"{n} {v:.2f}%" for n, v, _ in LANGS) + f". Snapshot {SNAPSHOT}.", "49%")}
</p>

<details>
<summary>Contribution trail</summary>
<p align="center"><img src="https://raw.githubusercontent.com/{OWNER}/{OWNER}/output/snake-crest.svg" width="100%" alt="Contribution snake"/></p>
</details>

<a name="projects"></a>

{img("section-projects", "Featured Projects")}

<p align="center">{" ".join(p[:2])}</p>
<p align="center">{" ".join(p[2:])}</p>

<p align="center"><a href="{U}/SpringAiBasic">공부 기록</a> · <a href="{U}/damso">진행 중인 프로젝트</a></p>

{img("footer", "EXID — Code. Build. Ship.")}

<p align="center">{switches()}</p>

<p align="center"><a href="./CREDITS.md">Credits · 이미지 출처</a> · <a href="./CREST_THEME.md">Crest 테마 제작 방식</a></p>

<p align="center"><sub>Theme switch: 저장소 소유자가 이슈를 제출하면 테마가 변경됩니다.</sub></p>
'''
    (ROOT / "README.md").write_text(s, encoding="utf-8")
    print("README.md rendered (crest)")


if __name__ == "__main__":
    build()
