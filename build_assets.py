#!/usr/bin/env python3
"""Generate layered, 3D-style SVG scenes (hero / section plates / footer) for both themes."""
import base64
import pathlib
import random

OUT = pathlib.Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "'Courier New', Courier, monospace"
IMPACT = "Impact, 'Arial Black', 'Helvetica Neue', sans-serif"


def n(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")


def save(name, svg):
    (OUT / name).write_text(svg, encoding="utf-8")


def char_href(theme):
    """Character art lives in assets/src/char-<theme>.webp and is embedded so it works inside <img>."""
    p = OUT / "src" / f"char-{theme}.webp"
    if not p.exists():
        return None, 0, 0
    from PIL import Image
    w, h = Image.open(p).size
    return "data:image/webp;base64," + base64.b64encode(p.read_bytes()).decode(), w, h


CHAR_BOX = dict(elysium=(782, -8, .74), cyber=(796, -10, .74))  # x, y, scale (relative to 705px-tall art)


def char_elysium(r):
    href, iw, ih = char_href("elysium")
    if not href:
        return "", ""
    x, y, s = CHAR_BOX["elysium"]
    s *= 705 / ih
    w, h = iw * s, ih * s
    cx, cy = x + w / 2, y + h * .42
    defs = (f'<image id="chE" href="{href}" width="{n(w)}" height="{n(h)}"/>'
            '<filter id="glowE" x="-20%" y="-20%" width="140%" height="140%"><feColorMatrix type="matrix" '
            'values="0 0 0 0 1  0 0 0 0 .97  0 0 0 0 .86  0 0 0 1 0"/><feGaussianBlur stdDeviation="10"/></filter>'
            '<filter id="litE"><feColorMatrix type="matrix" values="1.25 0 0 0 .08  0 1.25 0 0 .08  0 0 1.3 0 .12  0 0 0 1 0"/></filter>'
            '<radialGradient id="auraE" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".85"/>'
            '<stop offset=".35" stop-color="#CFE2FF" stop-opacity=".45"/><stop offset="1" stop-color="#9DB8FF" stop-opacity="0"/></radialGradient>')
    sparks = "".join(
        f'<path d="M0 -{n(k)}L{n(k * .25)} 0L0 {n(k)}L-{n(k * .25)} 0Z" fill="#FFFFFF" transform="translate({n(r.uniform(x + 10, x + w - 10))} {n(r.uniform(15, 300))})">'
        f'<animate attributeName="opacity" values="0;1;0" dur="{n(r.uniform(1.8, 3.6))}s" begin="{n(r.uniform(0, 3))}s" repeatCount="indefinite"/></path>'
        for k in [r.choice([4, 6, 8]) for _ in range(16)])
    body = f"""<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(w * .62)}" ry="{n(h * .5)}" fill="url(#auraE)"><animate attributeName="opacity" values=".55;.95;.55" dur="5s" repeatCount="indefinite"/></ellipse>
<g><animateTransform attributeName="transform" type="translate" values="{n(x)} {n(y)};{n(x)} {n(y - 8)};{n(x)} {n(y)}" dur="6s" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1" repeatCount="indefinite"/>
<use href="#chE" filter="url(#glowE)" opacity=".55"><animate attributeName="opacity" values=".35;.75;.35" dur="5s" repeatCount="indefinite"/></use>
<use href="#chE"/>
<use href="#chE" filter="url(#litE)" opacity="0"><animate attributeName="opacity" values="0;0;.45;0;0" keyTimes="0;.55;.7;.85;1" dur="7s" repeatCount="indefinite"/></use>
</g>
{sparks}"""
    return defs, body


def twinkle(r, count, x0, x1, y0, y1, color="#FFF3C4"):
    s = ""
    for _ in range(count):
        s += (f'<circle cx="{n(r.uniform(x0, x1))}" cy="{n(r.uniform(y0, y1))}" r="{r.choice([.7, 1, 1.3, 1.8])}" fill="{color}">'
              f'<animate attributeName="opacity" values=".1;1;.1" dur="{n(r.uniform(1.5, 4.5))}s" begin="{n(r.uniform(0, 4))}s" repeatCount="indefinite"/></circle>')
    return s


def motes(r, count, color, y0, y1, rise=(90, 200)):
    s = ""
    for _ in range(count):
        x, y = r.uniform(40, 1160), r.uniform(y0, y1)
        d, dx, up = r.uniform(5, 10), r.uniform(-30, 30), r.uniform(*rise)
        s += (f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r.uniform(1, 2.6))}" fill="{color}" filter="url(#bl1)">'
              f'<animate attributeName="cy" values="{n(y)};{n(y - up)}" dur="{n(d)}s" begin="{n(r.uniform(0, 8))}s" repeatCount="indefinite"/>'
              f'<animate attributeName="cx" values="{n(x)};{n(x + dx)}" dur="{n(d)}s" begin="{n(r.uniform(0, 8))}s" repeatCount="indefinite"/>'
              f'<animate attributeName="opacity" values="0;.9;0" dur="{n(d)}s" begin="{n(r.uniform(0, 8))}s" repeatCount="indefinite"/></circle>')
    return s


def title3d(text, x, y, size, ls, family, depth, dark, face, stroke, glow, dx=.9, dy=1.7, weight="700", style=""):
    base = f'text-anchor="middle" font-family="{family}" font-size="{size}" font-weight="{weight}" {style} letter-spacing="{ls}"'
    s = f'<text x="{x}" y="{y}" {base} fill="{glow}" filter="url(#bl6)" opacity=".7">{text}</text>'
    for i in range(depth, 0, -1):
        s += f'<text x="{n(x + i * dx)}" y="{n(y + i * dy)}" {base} fill="{dark}">{text}</text>'
    s += f'<text x="{x}" y="{y}" {base} fill="{face}" stroke="{stroke}" stroke-width="1.2" paint-order="stroke">{text}</text>'
    return s


# ---------------------------------------------------------------- ELYSIUM
CLOUD = ('<g id="cl"><ellipse cx="0" cy="0" rx="92" ry="26"/><ellipse cx="-56" cy="7" rx="62" ry="20"/>'
         '<ellipse cx="58" cy="9" rx="72" ry="21"/><ellipse cx="8" cy="-15" rx="52" ry="22"/></g>')


def cloud_layer(r, count, ymin, ymax, smin, smax, fill, op, dur, blur):
    items = ""
    for _ in range(count):
        x, y, s = r.uniform(0, 1200), r.uniform(ymin, ymax), r.uniform(smin, smax)
        for dx in (0, 1200):
            items += f'<use href="#cl" transform="translate({n(x + dx)} {n(y)}) scale({n(s)} {n(s * .78)})"/>'
    return (f'<g fill="{fill}" opacity="{op}" filter="url(#{blur})"><g>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;-1200 0" dur="{dur}s" repeatCount="indefinite"/>'
            f'{items}</g></g>')


def island(x, y, s, op, bob, delay):
    cols = "".join(f'<rect x="{n(-31 + i * 12.4)}" y="-42" width="5" height="30" fill="#fff6dc"/>' for i in range(6))
    return (f'<g transform="translate({n(x)} {n(y)}) scale({n(s)})" opacity="{op}"><g>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 -9;0 0" dur="{bob}s" begin="{delay}s" repeatCount="indefinite"/>'
            '<path d="M-72 0 C-64 36 -36 66 -8 124 C-3 134 3 134 8 124 C36 66 64 36 72 0 Z" fill="url(#rock)"/>'
            '<ellipse cx="0" cy="0" rx="72" ry="11" fill="url(#turf)"/>'
            '<circle cx="-58" cy="-8" r="8" fill="#5fb89a"/><circle cx="-49" cy="-12" r="6" fill="#74cdb0"/><circle cx="58" cy="-7" r="7" fill="#5fb89a"/>'
            '<rect x="-36" y="-12" width="72" height="5" fill="#efe4c4"/>' + cols +
            '<rect x="-38" y="-48" width="76" height="6" fill="#f6e9bd" stroke="#e8c170" stroke-width=".8"/>'
            '<polygon points="-40,-48 0,-72 40,-48" fill="#fff3c8" stroke="#e8c170" stroke-width=".8"/>'
            '<circle cx="0" cy="-56" r="3" fill="#8fd3ff"><animate attributeName="opacity" values=".4;1;.4" dur="2.5s" repeatCount="indefinite"/></circle>'
            '</g></g>')


def feathers(side_x, y, sc, flip):
    angs = [(-58, .52), (-44, .7), (-30, .86), (-16, 1), (-2, 1.08), (12, 1), (26, .84), (40, .66)]
    f = ""
    for i, (a, s) in enumerate(angs):
        f += (f'<g><animateTransform attributeName="transform" type="rotate" values="0;{n(-5 - i * .4)};4;0" keyTimes="0;.35;.7;1" calcMode="spline" '
              f'keySplines=".4 0 .2 1;.4 0 .2 1;.4 0 .2 1" dur="4.5s" begin="{n(i * .1)}s" repeatCount="indefinite"/>'
              f'<path transform="rotate({a}) scale({n(s)})" d="M0 0 C-60 -34 -190 -46 -330 -26 C-220 -12 -120 12 0 14 Z" fill="url(#wing)" stroke="#F5D78E" stroke-opacity=".55"/></g>')
    t = f"translate({side_x} {y}) scale({-sc if flip else sc} {sc})"
    return f'<g transform="{t}">{f}</g>'


def hero_elysium():
    r = random.Random(5)
    cdefs, cbody = char_elysium(random.Random(11))
    rays = "".join(f'<polygon points="430,300 {n(430 + 900 * __import__("math").cos(a))},{n(300 + 900 * __import__("math").sin(a))} '
                   f'{n(430 + 900 * __import__("math").cos(a + .07))},{n(300 + 900 * __import__("math").sin(a + .07))}" fill="#FFF3C4" opacity=".11"/>'
                   for a in [i * 6.2832 / 16 for i in range(16)])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 440" width="1200" height="440">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050b22"/><stop offset=".34" stop-color="#14295a"/><stop offset=".6" stop-color="#3f6cab"/><stop offset=".78" stop-color="#c3d8ef"/><stop offset="1" stop-color="#fbe7ae"/></linearGradient>
<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFBE6" stop-opacity=".95"/><stop offset=".3" stop-color="#FFE9A8" stop-opacity=".5"/><stop offset="1" stop-color="#FFE9A8" stop-opacity="0"/></radialGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".6" stop-color="#02060f" stop-opacity="0"/><stop offset="1" stop-color="#02060f" stop-opacity=".62"/></radialGradient>
<linearGradient id="rock" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#8a7f6c"/><stop offset="1" stop-color="#3b4a63"/></linearGradient>
<linearGradient id="turf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#bff2dc"/><stop offset="1" stop-color="#6fc9a8"/></linearGradient>
<linearGradient id="wing" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#FFF8DC" stop-opacity=".95"/><stop offset=".55" stop-color="#CFE8FF" stop-opacity=".4"/><stop offset="1" stop-color="#8FD3FF" stop-opacity="0"/></linearGradient>
<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFBE6"/><stop offset=".45" stop-color="#F8DC93"/><stop offset="1" stop-color="#C99A3E"/></linearGradient>
<linearGradient id="shine" gradientUnits="userSpaceOnUse" x1="-300" y1="0" x2="-150" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".95"/><stop offset="1" stop-color="#fff" stop-opacity="0"/><animate attributeName="x1" values="130;130;730;730" keyTimes="0;.55;.8;1" dur="7s" repeatCount="indefinite"/><animate attributeName="x2" values="280;280;880;880" keyTimes="0;.55;.8;1" dur="7s" repeatCount="indefinite"/></linearGradient>
<filter id="bl1"><feGaussianBlur stdDeviation=".8"/></filter><filter id="bl6"><feGaussianBlur stdDeviation="6"/></filter><filter id="bl9"><feGaussianBlur stdDeviation="9"/></filter>
<clipPath id="cp"><rect width="1200" height="440"/></clipPath>{CLOUD}{cdefs}
</defs>
<g clip-path="url(#cp)">
<rect width="1200" height="440" fill="url(#sky)"/>
{twinkle(r, 70, 10, 1190, 8, 220)}
<g><animateTransform attributeName="transform" type="rotate" values="0 430 300;360 430 300" dur="170s" repeatCount="indefinite"/>{rays}</g>
<circle cx="430" cy="300" r="270" fill="url(#halo)"><animate attributeName="opacity" values=".75;1;.75" dur="6s" repeatCount="indefinite"/></circle>
{cloud_layer(r, 7, 250, 330, .9, 1.5, "#dfeaf8", .55, 110, "bl9")}
{island(690, 92, .34, .6, 7, 0)}{island(150, 105, .38, .6, 8, 1)}
{cloud_layer(r, 6, 280, 350, 1.1, 1.8, "#ffffff", .6, 75, "bl9")}
{island(70, 225, .9, 1, 6.5, 0)}
{feathers(300, 225, 1.15, False)}{feathers(560, 225, 1.15, True)}
<circle cx="430" cy="205" r="165" fill="none" stroke="#F5D78E" stroke-opacity=".5" stroke-dasharray="3 9"><animateTransform attributeName="transform" type="rotate" values="0 430 205;360 430 205" dur="60s" repeatCount="indefinite"/></circle>
<circle cx="430" cy="205" r="182" fill="none" stroke="#FFF3C4" stroke-opacity=".28" stroke-width="1"/>
{title3d("EXID", 430, 246, 120, 20, SERIF, 9, "#6d4d14", "url(#gold)", "#fff6d6", "#FFE9A8")}
<text x="430" y="246" text-anchor="middle" font-family="{SERIF}" font-size="120" font-weight="700" letter-spacing="20" fill="url(#shine)">EXID</text>
<g stroke="#F5D78E" stroke-opacity=".85"><path d="M160 300H350M510 300H700"/></g>
<g fill="#F5D78E"><path d="M430 293l7 7-7 7-7-7z"/><path d="M352 300l-6-3v6z"/><path d="M508 300l6-3v6z"/></g>
<text x="431" y="307" text-anchor="middle" font-family="{SERIF}" font-size="16" letter-spacing="1" fill="#0b1630" opacity=".0"> </text>
<text x="430" y="346" text-anchor="middle" font-family="{SERIF}" font-size="17" font-weight="700" letter-spacing="6" fill="#FFFFFF" filter="url(#bl6)" opacity=".95">DAEVA OF ELYSIA  ·  BACKEND DEVELOPER</text>
<text x="430" y="346" text-anchor="middle" font-family="{SERIF}" font-size="17" font-weight="700" letter-spacing="6" fill="#10204a">DAEVA OF ELYSIA  ·  BACKEND DEVELOPER</text>
{motes(r, 30, "#FFE9A8", 300, 420)}
{cbody}
{cloud_layer(r, 6, 400, 450, 1.7, 2.6, "#ffffff", .95, 38, "bl9")}
</g>
<rect width="1200" height="440" fill="url(#vig)"/>
<rect x="12" y="12" width="1176" height="416" fill="none" stroke="#F5D78E" stroke-opacity=".7"/>
<g fill="none" stroke="#F5D78E" stroke-width="2.4"><path d="M12 46V12H46M1154 12H1188V46M12 394V428H46M1154 428H1188V394"/></g>
</svg>'''
    save("hero-elysium.svg", svg)


# ---------------------------------------------------------------- CYBER
def skyline(r, base, hmin, hmax, wmin, wmax, fill, wdens, wcolor, sway, dur, gap=2, blink=.08, sign=False, lane=None):
    out, x = [], -20
    while x < 1240:
        w = r.uniform(wmin, wmax)
        h = r.uniform(hmin, hmax)
        if lane and lane[0] < x + w / 2 < lane[1]:
            h = hmin * .6
        out.append(f'<rect x="{n(x)}" y="{n(base - h)}" width="{n(w)}" height="{n(h + 40)}" fill="{fill}"/>')
        if r.random() < .3:
            out.append(f'<rect x="{n(x + w / 2)}" y="{n(base - h - r.uniform(10, 28))}" width="1.6" height="{n(r.uniform(10, 28) + 2)}" fill="{fill}"/>')
        cols, rows = int((w - 6) // 8), int((h - 8) // 11)
        for cx in range(cols):
            for ry in range(rows):
                if r.random() < wdens:
                    a = ""
                    if r.random() < blink:
                        a = f'<animate attributeName="opacity" values="1;1;.1;1" keyTimes="0;.5;.55;1" dur="{n(r.uniform(2, 7))}s" begin="{n(r.uniform(0, 5))}s" repeatCount="indefinite"/>'
                    out.append(f'<rect x="{n(x + 4 + cx * 8)}" y="{n(base - h + 6 + ry * 11)}" width="3" height="4.5" fill="{wcolor}">{a}</rect>')
        if sign and r.random() < .25 and h > 60:
            col = r.choice(["#FCEE0A", "#FCEE0A", "#00F0FF", "#FF2A6D"])
            out.append(f'<rect x="{n(x + 3)}" y="{n(base - h + r.uniform(8, h - 30))}" width="{n(max(4, w - 8) / 3)}" height="{n(r.uniform(22, 44))}" fill="{col}" filter="url(#bl3)" opacity=".9">'
                       f'<animate attributeName="opacity" values=".95;.95;.3;.95" keyTimes="0;.6;.65;1" dur="{n(r.uniform(3, 6))}s" repeatCount="indefinite"/></rect>')
        x += w + gap
    return (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;{-sway} 0;0 0" dur="{dur}s" repeatCount="indefinite"/>'
            + "".join(out) + '</g>')


def grid_floor(horizon=330, bottom=440, N=12):
    ys = [horizon + (bottom - horizon) * (j / N) ** 2 for j in range(N + 1)]
    lines = ""
    for j in range(N):
        o1, o2 = .12 + .55 * j / N, .12 + .55 * (j + 1) / N
        lines += (f'<rect x="0" width="1200" height="1.6" fill="#FCEE0A" y="{n(ys[j])}" opacity="{n(o1)}">'
                  f'<animate attributeName="y" values="{n(ys[j])};{n(ys[j + 1])}" dur="1.8s" repeatCount="indefinite"/>'
                  f'<animate attributeName="opacity" values="{n(o1)};{n(o2)}" dur="1.8s" repeatCount="indefinite"/></rect>')
    for k in range(-16, 17):
        lines += f'<line x1="600" y1="{horizon}" x2="{600 + k * 120}" y2="{bottom}" stroke="#FCEE0A" stroke-opacity=".32"/>'
    return lines


def rain(r, count):
    s = ""
    for _ in range(count):
        x = r.uniform(0, 1260)
        d = r.uniform(.7, 1.5)
        s += (f'<line x1="{n(x)}" y1="-20" x2="{n(x - 3)}" y2="-8" stroke="#FFF8A0" stroke-opacity="{n(r.uniform(.15, .4))}">'
              f'<animateTransform attributeName="transform" type="translate" values="0 0;-70 480" dur="{n(d)}s" begin="{n(r.uniform(0, 1.5))}s" repeatCount="indefinite"/></line>')
    return s


def hero_cyber():
    r = random.Random(9)
    slits = "".join(f'<rect x="460" y="{258 + i * 16}" width="280" height="{n(2 + i * .8)}" fill="#000"/>' for i in range(-1, 6))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 440" width="1200" height="440">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#040404"/><stop offset=".55" stop-color="#14110a"/><stop offset=".75" stop-color="#5a4f00"/><stop offset="1" stop-color="#0a0a0a"/></linearGradient>
<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF76B"/><stop offset=".45" stop-color="#FCEE0A"/><stop offset="1" stop-color="#b8aa00"/></linearGradient>
<radialGradient id="sg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FCEE0A" stop-opacity=".45"/><stop offset="1" stop-color="#FCEE0A" stop-opacity="0"/></radialGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".75"/></radialGradient>
<linearGradient id="fl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FCEE0A" stop-opacity=".28"/><stop offset=".4" stop-color="#0a0a0a"/><stop offset="1" stop-color="#050505"/></linearGradient>
<linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FCEE0A" stop-opacity="0"/><stop offset=".5" stop-color="#FCEE0A" stop-opacity=".16"/><stop offset="1" stop-color="#FCEE0A" stop-opacity="0"/></linearGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".4"/></pattern>
<pattern id="haz" width="28" height="28" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="14" height="28" fill="#FCEE0A"/></pattern>
<filter id="bl1"><feGaussianBlur stdDeviation=".8"/></filter><filter id="bl3"><feGaussianBlur stdDeviation="3"/></filter><filter id="bl6"><feGaussianBlur stdDeviation="6"/></filter>
<mask id="sm"><rect width="1200" height="440" fill="#fff"/><g><animateTransform attributeName="transform" type="translate" values="0 0;0 16" dur="2.4s" repeatCount="indefinite"/>{slits}</g></mask>
<clipPath id="cp"><rect width="1200" height="440"/></clipPath>
<clipPath id="above"><rect width="1200" height="330"/></clipPath>
</defs>
<g clip-path="url(#cp)">
<rect width="1200" height="440" fill="url(#sky)"/>
{twinkle(r, 40, 10, 1190, 8, 200, "#FFF8A0")}
<circle cx="600" cy="326" r="250" fill="url(#sg)"><animate attributeName="opacity" values=".7;1;.7" dur="4s" repeatCount="indefinite"/></circle>
<g clip-path="url(#above)"><circle cx="600" cy="326" r="128" fill="url(#sun)" mask="url(#sm)"/></g>
<g clip-path="url(#above)">
{skyline(r, 330, 30, 120, 18, 40, "#161309", .12, "#8f8500", 4, 9, blink=.04)}
{skyline(r, 330, 50, 170, 24, 54, "#0c0b07", .22, "#d4c600", 9, 7, blink=.07, sign=True, lane=(420, 780))}
{skyline(r, 340, 90, 250, 34, 74, "#050505", .3, "#FCEE0A", 16, 6, gap=6, blink=.1, sign=True, lane=(430, 770))}
</g>
<rect y="330" width="1200" height="110" fill="url(#fl)"/>
<g>{grid_floor()}</g>
<rect y="329" width="1200" height="2" fill="#FCEE0A" opacity=".9"/>
{rain(r, 70)}
{title3d("EXID", 600, 196, 118, 16, IMPACT, 10, "#4f4700", "#FCEE0A", "#0a0a0a", "#FCEE0A", style='font-style="italic"', weight="900")}
<g font-family="{IMPACT}" font-size="118" font-weight="900" font-style="italic" letter-spacing="16" text-anchor="middle">
<text x="600" y="196" fill="#00F0FF" opacity=".8"><animateTransform attributeName="transform" type="translate" values="0 0;0 0;-7 1;5 -2;0 0;0 0;-4 0;0 0" keyTimes="0;.5;.52;.54;.56;.8;.82;1" calcMode="discrete" dur="4s" repeatCount="indefinite"/>EXID</text>
<text x="600" y="196" fill="#FF2A6D" opacity=".8"><animateTransform attributeName="transform" type="translate" values="0 0;0 0;7 -1;-5 2;0 0;0 0;4 0;0 0" keyTimes="0;.5;.52;.54;.56;.8;.82;1" calcMode="discrete" dur="4s" repeatCount="indefinite"/>EXID</text>
<text x="600" y="196" fill="#FCEE0A" stroke="#0a0a0a" stroke-width="3" paint-order="stroke">EXID</text></g>
<clipPath id="type"><rect x="300" y="362" width="0" height="34"><animate attributeName="width" values="0;600;600;0" keyTimes="0;.3;.92;1" dur="9s" repeatCount="indefinite"/></rect></clipPath>
<g clip-path="url(#type)"><text x="300" y="386" font-family="{MONO}" font-size="22" font-weight="700" letter-spacing="5" fill="#FCEE0A" stroke="#000" stroke-width="3" paint-order="stroke">NETRUNNER // BACKEND DEVELOPER</text></g>
<rect x="300" y="368" width="12" height="22" fill="#FCEE0A"><animate attributeName="x" values="300;850;850;300" keyTimes="0;.3;.92;1" dur="9s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0;1" dur=".8s" repeatCount="indefinite"/></rect>
{motes(r, 18, "#FCEE0A", 300, 430, (60, 140))}
<g font-family="{MONO}" font-size="12" font-weight="700" fill="#FCEE0A"><text x="40" y="42">SYS://ONLINE<animate attributeName="opacity" values="1;1;.2;1;1" keyTimes="0;.5;.55;.6;1" dur="2s" repeatCount="indefinite"/></text><text x="1160" y="42" text-anchor="end">BUILD 2026.10</text></g>
<g fill="#FCEE0A"><rect x="40" y="380" width="6" height="30" opacity=".9"><animate attributeName="height" values="30;12;24;30" dur="2.1s" repeatCount="indefinite"/><animate attributeName="y" values="380;398;386;380" dur="2.1s" repeatCount="indefinite"/></rect><rect x="52" y="380" width="6" height="30" opacity=".6"><animate attributeName="height" values="14;30;8;14" dur="1.7s" repeatCount="indefinite"/><animate attributeName="y" values="396;380;402;396" dur="1.7s" repeatCount="indefinite"/></rect><rect x="64" y="380" width="6" height="30" opacity=".8"><animate attributeName="height" values="24;10;30;24" dur="2.6s" repeatCount="indefinite"/><animate attributeName="y" values="386;400;380;386" dur="2.6s" repeatCount="indefinite"/></rect></g>
<rect width="1200" height="40" y="-40" fill="url(#bar)"><animateTransform attributeName="transform" type="translate" values="0 0;0 500" dur="5s" repeatCount="indefinite"/></rect>
</g>
<rect width="1200" height="440" fill="url(#vig)"/>
<rect width="1200" height="440" fill="url(#scan)" opacity=".55"/>
<rect width="1200" height="9" fill="url(#haz)"/><rect y="431" width="1200" height="9" fill="url(#haz)"/>
<g fill="none" stroke="#FCEE0A" stroke-width="2.4"><path d="M18 56V22H52M1148 22H1182V56M18 384V418H52M1148 418H1182V384"/></g>
</svg>'''
    save("hero-cyber.svg", svg)


# ---------------------------------------------------------------- PLATES
SECTIONS = {
    "intro": ("PROFILE", "PROFILE", "I", "01"),
    "sns": ("SNS LIST", "COMMS LINK", "II", "02"),
    "stack": ("LOADOUT", "LOADOUT", "III", "03"),
    "stats": ("BATTLE LOG", "SYSTEM LOG", "IV", "04"),
    "snake": ("FLIGHT PATH", "DATA STREAM", "V", "05"),
    "quest": ("QUESTS", "MISSIONS", "VI", "06"),
}


def plate_elysium(title, idx):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 92" width="1200" height="92">
<defs>
<linearGradient id="pl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a4a86"/><stop offset=".5" stop-color="#15294f"/><stop offset="1" stop-color="#0b1630"/></linearGradient>
<linearGradient id="bd" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8f6a22"/><stop offset=".5" stop-color="#FBE3A0"/><stop offset="1" stop-color="#8f6a22"/></linearGradient>
<linearGradient id="gd" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFFBE6"/><stop offset=".5" stop-color="#F8DC93"/><stop offset="1" stop-color="#C99A3E"/></linearGradient>
<linearGradient id="ln" x1="0" x2="1"><stop offset="0" stop-color="#F5D78E"/><stop offset="1" stop-color="#F5D78E" stop-opacity="0"/></linearGradient>
<linearGradient id="sh" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".3"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<filter id="ds" x="-5%" y="-30%" width="110%" height="190%"><feDropShadow dx="0" dy="7" stdDeviation="6" flood-color="#000" flood-opacity=".55"/></filter>
<clipPath id="pc"><path id="shape" d="M46 12H1154L1180 36V52L1154 76H46L20 52V36Z"/></clipPath>
</defs>
<g filter="url(#ds)"><path d="M46 12H1154L1180 36V52L1154 76H46L20 52V36Z" fill="url(#pl)" stroke="url(#bd)" stroke-width="2.4"/></g>
<path d="M50 17H1150" stroke="#fff" stroke-opacity=".28"/>
<path d="M36 40L52 24H92" fill="none" stroke="#F5D78E" stroke-opacity=".7"/>
<g clip-path="url(#pc)"><rect y="6" width="160" height="80" fill="url(#sh)" transform="skewX(-20)"><animate attributeName="x" values="-300;1400;1400" keyTimes="0;.45;1" dur="6s" repeatCount="indefinite"/></rect></g>
<g transform="translate(70 44)"><path d="M0 -14L12 0L0 14L-12 0Z" fill="none" stroke="#F5D78E" stroke-width="2"/><path d="M0 -7L6 0L0 7L-6 0Z" fill="#F5D78E"><animate attributeName="opacity" values=".6;1;.6" dur="3s" repeatCount="indefinite"/></path></g>
<text x="106" y="56" font-family="{SERIF}" font-size="32" font-weight="700" letter-spacing="8" fill="#050b22" opacity=".65">{title}</text>
<text x="105" y="54" font-family="{SERIF}" font-size="32" font-weight="700" letter-spacing="8" fill="url(#gd)" stroke="#7a5a1c" stroke-width=".6" paint-order="stroke">{title}</text>
<rect x="480" y="43" width="640" height="1.5" fill="url(#ln)"/>
<text x="1148" y="50" text-anchor="end" font-family="{SERIF}" font-size="18" letter-spacing="4" fill="#F5D78E" opacity=".9">{idx}</text>
</svg>'''.replace("{SERIF}", SERIF)


def plate_cyber(title, idx):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 92" width="1200" height="92">
<defs>
<pattern id="haz" width="16" height="16" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="8" height="16" fill="#FCEE0A"/></pattern>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".45"/></pattern>
</defs>
<polygon points="34,22 1180,22 1194,38 1194,82 54,82 34,64" fill="#5a5300"/>
<polygon points="26,14 1172,14 1186,30 1186,74 46,74 26,56" fill="#0b0b0b" stroke="#FCEE0A" stroke-width="2.4"/>
<polygon points="26,14 130,14 130,74 46,74 26,56" fill="#FCEE0A"/>
<text x="78" y="55" text-anchor="middle" font-family="{IMPACT}" font-size="34" font-weight="900" fill="#0a0a0a">{idx}</text>
<text x="154" y="56" font-family="{IMPACT}" font-size="34" letter-spacing="5" fill="#FCEE0A" opacity=".95">{title}</text>
<rect x="154" y="64" width="120" height="3" fill="#FCEE0A"><animate attributeName="width" values="40;260;120;40" keyTimes="0;.4;.6;1" dur="3s" repeatCount="indefinite"/></rect>
<rect x="1000" y="24" width="170" height="40" fill="url(#haz)" opacity=".9"/><rect x="1000" y="24" width="170" height="40" fill="#0b0b0b" opacity=".35"/>
<text x="990" y="50" text-anchor="end" font-family="{MONO}" font-size="14" font-weight="700" fill="#FCEE0A"> //<animate attributeName="opacity" values="1;1;.2;1" keyTimes="0;.6;.65;1" dur="2s" repeatCount="indefinite"/></text>
<rect x="26" y="14" width="1160" height="60" fill="url(#scan)"/>
</svg>'''.replace("{IMPACT}", IMPACT).replace("{MONO}", MONO)


# ---------------------------------------------------------------- FOOTERS
def footer_elysium():
    r = random.Random(21)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 220" width="1200" height="220">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#14295a"/><stop offset=".6" stop-color="#7fa3d1"/><stop offset="1" stop-color="#fbe7ae"/></linearGradient>
<radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#FFFBE6" stop-opacity=".95"/><stop offset=".4" stop-color="#FFE9A8" stop-opacity=".45"/><stop offset="1" stop-color="#FFE9A8" stop-opacity="0"/></radialGradient>
<filter id="bl1"><feGaussianBlur stdDeviation=".8"/></filter><filter id="bl9"><feGaussianBlur stdDeviation="9"/></filter>
<clipPath id="cp"><rect width="1200" height="220"/></clipPath>{CLOUD}
</defs>
<g clip-path="url(#cp)"><rect width="1200" height="220" fill="url(#sky)"/>
{twinkle(r, 30, 10, 1190, 5, 90)}
<circle cx="600" cy="220" r="240" fill="url(#halo)"><animate attributeName="opacity" values=".8;1;.8" dur="5s" repeatCount="indefinite"/></circle>
{cloud_layer(r, 6, 150, 215, 1.0, 1.7, "#ffffff", .7, 90, "bl9")}
<text x="600" y="102" text-anchor="middle" font-family="{SERIF}" font-size="22" letter-spacing="10" fill="#0d1a3a" opacity=".55">MAY THE LIGHT GUIDE YOUR WAY</text>
<text x="600" y="100" text-anchor="middle" font-family="{SERIF}" font-size="22" letter-spacing="10" fill="#FFFFFF">MAY THE LIGHT GUIDE YOUR WAY</text>
<path d="M400 124H560M640 124H800" stroke="#FFF3C4" stroke-opacity=".9"/><path d="M600 117l7 7-7 7-7-7z" fill="#FFF3C4"/>
{motes(r, 16, "#FFFBE6", 120, 210, (60, 120))}
{cloud_layer(r, 6, 195, 235, 1.8, 2.7, "#ffffff", .96, 40, "bl9")}
</g><rect x="1" y="1" width="1198" height="218" fill="none" stroke="#F5D78E" stroke-opacity=".6"/></svg>'''
    save("footer-elysium.svg", svg)


def footer_cyber():
    r = random.Random(33)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 220" width="1200" height="220">
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#050505"/><stop offset=".7" stop-color="#4a4200"/><stop offset="1" stop-color="#0a0a0a"/></linearGradient>
<linearGradient id="fl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FCEE0A" stop-opacity=".28"/><stop offset=".4" stop-color="#0a0a0a"/><stop offset="1" stop-color="#050505"/></linearGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".4"/></pattern>
<pattern id="haz" width="28" height="28" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="14" height="28" fill="#FCEE0A"/></pattern>
<filter id="bl3"><feGaussianBlur stdDeviation="3"/></filter><filter id="bl1"><feGaussianBlur stdDeviation=".8"/></filter>
<clipPath id="cp"><rect width="1200" height="220"/></clipPath><clipPath id="above"><rect width="1200" height="150"/></clipPath>
</defs>
<g clip-path="url(#cp)"><rect width="1200" height="220" fill="url(#sky)"/>
<g clip-path="url(#above)">{skyline(r, 150, 8, 36, 18, 40, "#0c0b07", .2, "#d4c600", 6, 8, blink=.06, sign=True)}{skyline(r, 156, 14, 56, 30, 66, "#050505", .3, "#FCEE0A", 12, 6, gap=6, blink=.1, sign=True)}</g>
<rect y="150" width="1200" height="70" fill="url(#fl)"/><g transform="translate(0 -180) scale(1 1.0)"><g transform="translate(0 0)">{grid_floor(330, 440, 8).replace('y2="440"', 'y2="440"')}</g></g>
<rect y="149" width="1200" height="2" fill="#FCEE0A" opacity=".9"/>
<text x="600" y="100" text-anchor="middle" font-family="{MONO}" font-size="26" font-weight="700" letter-spacing="8" fill="#FCEE0A" stroke="#000" stroke-width="4" paint-order="stroke">// END OF TRANSMISSION<animate attributeName="opacity" values="1;1;.35;1;1" keyTimes="0;.7;.74;.78;1" dur="3s" repeatCount="indefinite"/></text>
{motes(r, 10, "#FCEE0A", 120, 210, (40, 90))}
</g><rect width="1200" height="220" fill="url(#scan)" opacity=".5"/>
<rect y="211" width="1200" height="9" fill="url(#haz)"/></svg>'''
    save("footer-cyber.svg", svg)


def main():
    hero_elysium()
    hero_cyber()
    footer_elysium()
    footer_cyber()
    for key, (te, tc, ie, ic) in SECTIONS.items():
        save(f"plate-elysium-{key}.svg", plate_elysium(te, ie))
        save(f"plate-cyber-{key}.svg", plate_cyber(tc, ic))
    print("assets generated:", len(list(OUT.glob("*.svg"))))


if __name__ == "__main__":
    main()
