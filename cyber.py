#!/usr/bin/env python3
"""Neon cyberpunk scenes (magenta / cyan / violet night city). Overwrites the *-cyber.svg assets."""
import random

from build_assets import IMPACT, MONO, SECTIONS, n, save, title3d, twinkle

MAG, CYA, VIO, BLU, YEL = "#FF2BD6", "#00F0FF", "#9D4DFF", "#2D6BFF", "#FFE14D"
WINDOW_COLORS = [CYA, CYA, CYA, MAG, MAG, MAG, BLU, YEL, "#FFFFFF"]


def skyline(r, base, hmin, hmax, wmin, wmax, fill, wdens, sway, dur, gap=2, blink=.08, neon=False, lane=None, boards=False):
    out, x = [], -20
    while x < 1240:
        w, h = r.uniform(wmin, wmax), r.uniform(hmin, hmax)
        if lane and lane[0] < x + w / 2 < lane[1]:
            h = hmin * .6
        out.append(f'<rect x="{n(x)}" y="{n(base - h)}" width="{n(w)}" height="{n(h + 40)}" fill="{fill}"/>')
        if r.random() < .3:
            out.append(f'<rect x="{n(x + w / 2)}" y="{n(base - h - r.uniform(10, 26))}" width="1.6" height="{n(r.uniform(10, 26) + 2)}" fill="{fill}"/>')
        cols, rows = int((w - 6) // 8), int((h - 8) // 11)
        for cx in range(cols):
            for ry in range(rows):
                if r.random() < wdens:
                    a = ""
                    if r.random() < blink:
                        a = f'<animate attributeName="opacity" values="1;1;.1;1" keyTimes="0;.5;.55;1" dur="{n(r.uniform(2, 7))}s" begin="{n(r.uniform(0, 5))}s" repeatCount="indefinite"/>'
                    out.append(f'<rect x="{n(x + 4 + cx * 8)}" y="{n(base - h + 6 + ry * 11)}" width="3" height="4.5" fill="{r.choice(WINDOW_COLORS)}">{a}</rect>')
        if neon and w > 28 and h > 70 and r.random() < .3:
            c = r.choice([CYA, MAG, VIO])
            out.append(f'<rect x="{n(x)}" y="{n(base - h)}" width="2.4" height="{n(h)}" fill="{c}" filter="url(#bl3)"/>')
            out.append(f'<rect x="{n(x)}" y="{n(base - h)}" width="{n(w)}" height="2" fill="{c}" opacity=".8"/>')
        if boards and w > 46 and h > 110 and r.random() < .3:
            g = r.choice(["bb1", "bb2"])
            out.append(f'<rect x="{n(x + 5)}" y="{n(base - h + r.uniform(14, h - 70))}" width="{n(w - 10)}" height="{n(r.uniform(36, 62))}" fill="url(#{g})" filter="url(#bl1)">'
                       f'<animate attributeName="opacity" values="1;.85;1;.5;1" keyTimes="0;.3;.5;.55;1" dur="{n(r.uniform(2.5, 5))}s" repeatCount="indefinite"/></rect>')
        x += w + gap
    return (f'<g><animateTransform attributeName="transform" type="translate" values="0 0;{-sway} 0;0 0" dur="{dur}s" repeatCount="indefinite"/>' + "".join(out) + '</g>')


def rain(r, count):
    s = ""
    for _ in range(count):
        x, d = r.uniform(0, 1260), r.uniform(.7, 1.5)
        s += (f'<line x1="{n(x)}" y1="-20" x2="{n(x - 3)}" y2="-8" stroke="{r.choice(["#BFEFFF", "#FFB3F0", "#DDEBFF"])}" stroke-opacity="{n(r.uniform(.2, .5))}">'
              f'<animateTransform attributeName="transform" type="translate" values="0 0;-70 480" dur="{n(d)}s" begin="{n(r.uniform(0, 1.5))}s" repeatCount="indefinite"/></line>')
    return s


def reflections(r, top, bottom, count):
    s = ""
    for i in range(count):
        c = ["refC", "refM", "refB", "refM", "refC"][i % 5]
        x, w = r.uniform(0, 1200), r.uniform(5, 16)
        s += (f'<rect x="{n(x)}" y="{top}" width="{n(w)}" height="{bottom - top}" fill="url(#{c})">'
              f'<animate attributeName="opacity" values=".35;.9;.35" dur="{n(r.uniform(1.5, 4))}s" begin="{n(r.uniform(0, 3))}s" repeatCount="indefinite"/></rect>')
    return s


COMMON_DEFS = f'''<linearGradient id="bb1" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{MAG}"/><stop offset="1" stop-color="{BLU}"/></linearGradient>
<linearGradient id="bb2" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYA}"/><stop offset="1" stop-color="{VIO}"/></linearGradient>
<linearGradient id="refC" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYA}" stop-opacity=".55"/><stop offset="1" stop-color="{CYA}" stop-opacity="0"/></linearGradient>
<linearGradient id="refM" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{MAG}" stop-opacity=".6"/><stop offset="1" stop-color="{MAG}" stop-opacity="0"/></linearGradient>
<linearGradient id="refB" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{BLU}" stop-opacity=".55"/><stop offset="1" stop-color="{BLU}" stop-opacity="0"/></linearGradient>
<linearGradient id="face" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{CYA}"/><stop offset=".5" stop-color="#C58BFF"/><stop offset="1" stop-color="{MAG}"/></linearGradient>
<linearGradient id="neonbar" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{MAG}"/><stop offset=".5" stop-color="{VIO}"/><stop offset="1" stop-color="{CYA}"/></linearGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".4"/></pattern>
<filter id="bl1"><feGaussianBlur stdDeviation=".8"/></filter><filter id="bl3"><feGaussianBlur stdDeviation="3"/></filter><filter id="bl6"><feGaussianBlur stdDeviation="6"/></filter>'''


def hero():
    r = random.Random(77)
    slits = "".join(f'<rect x="460" y="{268 + i * 16}" width="280" height="{n(2 + i * .8)}" fill="#000"/>' for i in range(-1, 6))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 440" width="1200" height="440">
<defs>
{COMMON_DEFS}
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#04051a"/><stop offset=".45" stop-color="#1d1a7a"/><stop offset=".78" stop-color="#8a24c8"/><stop offset="1" stop-color="#1a0b3d"/></linearGradient>
<linearGradient id="sun" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFB3F0"/><stop offset=".5" stop-color="{MAG}"/><stop offset="1" stop-color="#7A1FFF"/></linearGradient>
<radialGradient id="sg" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{MAG}" stop-opacity=".55"/><stop offset=".6" stop-color="{VIO}" stop-opacity=".2"/><stop offset="1" stop-color="{VIO}" stop-opacity="0"/></radialGradient>
<linearGradient id="fog" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{MAG}" stop-opacity="0"/><stop offset=".6" stop-color="{MAG}" stop-opacity=".5"/><stop offset="1" stop-color="{VIO}" stop-opacity="0"/></linearGradient>
<linearGradient id="street" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a0f55"/><stop offset=".4" stop-color="#0c0a30"/><stop offset="1" stop-color="#04051a"/></linearGradient>
<radialGradient id="vig" cx=".5" cy=".5" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".7"/></radialGradient>
<linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{CYA}" stop-opacity="0"/><stop offset=".5" stop-color="{CYA}" stop-opacity=".16"/><stop offset="1" stop-color="{CYA}" stop-opacity="0"/></linearGradient>
<mask id="sm"><rect width="1200" height="440" fill="#fff"/><g><animateTransform attributeName="transform" type="translate" values="0 0;0 16" dur="2.4s" repeatCount="indefinite"/>{slits}</g></mask>
<clipPath id="cp"><rect width="1200" height="440"/></clipPath><clipPath id="above"><rect width="1200" height="345"/></clipPath>
</defs>
<g clip-path="url(#cp)">
<rect width="1200" height="440" fill="url(#sky)"/>
{twinkle(r, 45, 10, 1190, 8, 170, "#DDEBFF")}
<circle cx="600" cy="336" r="270" fill="url(#sg)"><animate attributeName="opacity" values=".7;1;.7" dur="4s" repeatCount="indefinite"/></circle>
<g clip-path="url(#above)"><circle cx="600" cy="336" r="130" fill="url(#sun)" mask="url(#sm)"/></g>
<g clip-path="url(#above)">
{skyline(r, 305, 40, 150, 18, 40, "#1c1470", .16, 4, 9, blink=.04)}
<rect y="200" width="1200" height="145" fill="url(#fog)"><animate attributeName="opacity" values=".7;1;.7" dur="7s" repeatCount="indefinite"/></rect>
{skyline(r, 325, 60, 190, 24, 54, "#100f48", .24, 9, 7, blink=.07, neon=True, lane=(420, 780))}
<rect y="240" width="1200" height="105" fill="url(#fog)" opacity=".6"/>
{skyline(r, 340, 90, 250, 30, 70, "#090a2c", .3, 14, 6, gap=4, blink=.1, neon=True, boards=True, lane=(430, 770))}
{skyline(r, 352, 110, 280, 46, 96, "#04051a", .36, 20, 5, gap=10, blink=.12, neon=True, boards=True, lane=(400, 800))}
</g>
<rect y="345" width="1200" height="95" fill="url(#street)"/>
{reflections(r, 346, 440, 18)}
<line x1="-20" y1="436" x2="720" y2="347" stroke="{MAG}" stroke-width="4" filter="url(#bl3)" opacity=".9"/>
<line x1="-20" y1="436" x2="720" y2="347" stroke="#FFD6F7" stroke-width="1.2" stroke-dasharray="40 18"><animate attributeName="stroke-dashoffset" values="0;-58" dur="1.2s" repeatCount="indefinite"/></line>
<rect y="344" width="1200" height="2" fill="url(#neonbar)" opacity=".95"/>
{rain(r, 80)}
{title3d("EXID", 600, 196, 118, 16, IMPACT, 10, "#2a0a5e", "url(#face)", "#FFFFFF", MAG, style='font-style="italic"', weight="900")}
<g font-family="{IMPACT}" font-size="118" font-weight="900" font-style="italic" letter-spacing="16" text-anchor="middle">
<text x="600" y="196" fill="{CYA}" opacity=".7"><animateTransform attributeName="transform" type="translate" values="0 0;0 0;-7 1;5 -2;0 0;0 0;-4 0;0 0" keyTimes="0;.5;.52;.54;.56;.8;.82;1" calcMode="discrete" dur="4s" repeatCount="indefinite"/>EXID</text>
<text x="600" y="196" fill="{MAG}" opacity=".7"><animateTransform attributeName="transform" type="translate" values="0 0;0 0;7 -1;-5 2;0 0;0 0;4 0;0 0" keyTimes="0;.5;.52;.54;.56;.8;.82;1" calcMode="discrete" dur="4s" repeatCount="indefinite"/>EXID</text>
<text x="600" y="196" fill="url(#face)" stroke="#FFFFFF" stroke-width="1.6" paint-order="stroke">EXID</text></g>
<clipPath id="type"><rect x="300" y="362" width="0" height="34"><animate attributeName="width" values="0;600;600;0" keyTimes="0;.3;.92;1" dur="9s" repeatCount="indefinite"/></rect></clipPath>
<g clip-path="url(#type)"><text x="300" y="386" font-family="{MONO}" font-size="22" font-weight="700" letter-spacing="5" fill="{CYA}" stroke="#04051a" stroke-width="3" paint-order="stroke">NETRUNNER // BACKEND DEVELOPER</text></g>
<rect x="300" y="368" width="12" height="22" fill="{MAG}"><animate attributeName="x" values="300;850;850;300" keyTimes="0;.3;.92;1" dur="9s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0;1" dur=".8s" repeatCount="indefinite"/></rect>
<g font-family="{MONO}" font-size="12" font-weight="700" fill="{CYA}"><text x="40" y="42">SYS://ONLINE<animate attributeName="opacity" values="1;1;.2;1;1" keyTimes="0;.5;.55;.6;1" dur="2s" repeatCount="indefinite"/></text><text x="1160" y="42" text-anchor="end" fill="{MAG}">BUILD 2026.10</text></g>
<rect width="1200" height="40" y="-40" fill="url(#bar)"><animateTransform attributeName="transform" type="translate" values="0 0;0 500" dur="5s" repeatCount="indefinite"/></rect>
</g>
<rect width="1200" height="440" fill="url(#vig)"/>
<rect width="1200" height="440" fill="url(#scan)" opacity=".5"/>
<rect width="1200" height="4" fill="url(#neonbar)"/><rect y="436" width="1200" height="4" fill="url(#neonbar)"/>
<g fill="none" stroke="{CYA}" stroke-width="2.4"><path d="M18 56V22H52M1148 22H1182V56M18 384V418H52M1148 418H1182V384"/></g>
</svg>'''
    save("hero-cyber.svg", svg)


def plate(title, idx):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 92" width="1200" height="92">
<defs>
<linearGradient id="pl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#14125a"/><stop offset="1" stop-color="#0a0a2e"/></linearGradient>
<linearGradient id="nb" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{MAG}"/><stop offset=".5" stop-color="{VIO}"/><stop offset="1" stop-color="{CYA}"/></linearGradient>
<linearGradient id="blk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{MAG}"/><stop offset="1" stop-color="#7A1FFF"/></linearGradient>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".4"/></pattern>
<filter id="glow" x="-5%" y="-40%" width="110%" height="180%"><feDropShadow dx="0" dy="0" stdDeviation="5" flood-color="{MAG}" flood-opacity=".8"/></filter>
</defs>
<g filter="url(#glow)"><polygon points="26,14 1172,14 1186,30 1186,74 46,74 26,56" fill="url(#pl)" stroke="url(#nb)" stroke-width="2.4"/></g>
<polygon points="26,14 130,14 130,74 46,74 26,56" fill="url(#blk)"/>
<text x="78" y="55" text-anchor="middle" font-family="{IMPACT}" font-size="34" font-weight="900" fill="#FFFFFF">{idx}</text>
<text x="156" y="57" font-family="{IMPACT}" font-size="34" letter-spacing="5" fill="{MAG}" opacity=".85">{title}</text>
<text x="154" y="56" font-family="{IMPACT}" font-size="34" letter-spacing="5" fill="{CYA}" opacity=".85">{title}</text>
<text x="155" y="56" font-family="{IMPACT}" font-size="34" letter-spacing="5" fill="#FFFFFF">{title}</text>
<rect x="154" y="64" width="120" height="3" fill="url(#nb)"><animate attributeName="width" values="40;260;120;40" keyTimes="0;.4;.6;1" dur="3s" repeatCount="indefinite"/></rect>
<g fill="{CYA}"><rect x="1010" y="30" width="6" height="28"><animate attributeName="height" values="28;10;22;28" dur="1.9s" repeatCount="indefinite"/><animate attributeName="y" values="30;48;36;30" dur="1.9s" repeatCount="indefinite"/></rect>
<rect x="1024" y="30" width="6" height="28" fill="{MAG}"><animate attributeName="height" values="12;28;8;12" dur="1.5s" repeatCount="indefinite"/><animate attributeName="y" values="46;30;50;46" dur="1.5s" repeatCount="indefinite"/></rect>
<rect x="1038" y="30" width="6" height="28" fill="{VIO}"><animate attributeName="height" values="22;8;28;22" dur="2.3s" repeatCount="indefinite"/><animate attributeName="y" values="36;50;30;36" dur="2.3s" repeatCount="indefinite"/></rect>
<rect x="1052" y="30" width="6" height="28"><animate attributeName="height" values="18;28;12;18" dur="1.7s" repeatCount="indefinite"/><animate attributeName="y" values="40;30;46;40" dur="1.7s" repeatCount="indefinite"/></rect></g>
<text x="1160" y="50" text-anchor="end" font-family="{MONO}" font-size="14" font-weight="700" fill="{CYA}">//<animate attributeName="opacity" values="1;1;.2;1" keyTimes="0;.6;.65;1" dur="2s" repeatCount="indefinite"/></text>
<rect x="26" y="14" width="1160" height="60" fill="url(#scan)"/>
</svg>'''


def footer():
    r = random.Random(83)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 220" width="1200" height="220">
<defs>
{COMMON_DEFS}
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#04051a"/><stop offset=".7" stop-color="#4a1a8f"/><stop offset="1" stop-color="#1a0b3d"/></linearGradient>
<linearGradient id="street" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a0f55"/><stop offset=".5" stop-color="#0c0a30"/><stop offset="1" stop-color="#04051a"/></linearGradient>
<clipPath id="cp"><rect width="1200" height="220"/></clipPath><clipPath id="above"><rect width="1200" height="150"/></clipPath>
</defs>
<g clip-path="url(#cp)"><rect width="1200" height="220" fill="url(#sky)"/>
{twinkle(r, 25, 10, 1190, 4, 70, "#DDEBFF")}
<g clip-path="url(#above)">{skyline(r, 150, 8, 40, 18, 40, "#1c1470", .2, 6, 8, blink=.06)}{skyline(r, 158, 14, 62, 30, 66, "#090a2c", .32, 12, 6, gap=6, blink=.1, neon=True, boards=True)}</g>
<rect y="150" width="1200" height="70" fill="url(#street)"/>
{reflections(r, 151, 220, 12)}
<rect y="149" width="1200" height="2" fill="url(#neonbar)"/>
<text x="600" y="102" text-anchor="middle" font-family="{MONO}" font-size="26" font-weight="700" letter-spacing="8" fill="{MAG}" filter="url(#bl3)">// END OF TRANSMISSION</text>
<text x="600" y="102" text-anchor="middle" font-family="{MONO}" font-size="26" font-weight="700" letter-spacing="8" fill="#FFFFFF" stroke="{CYA}" stroke-width=".8" paint-order="stroke">// END OF TRANSMISSION<animate attributeName="opacity" values="1;1;.4;1;1" keyTimes="0;.7;.74;.78;1" dur="3s" repeatCount="indefinite"/></text>
</g><rect width="1200" height="220" fill="url(#scan)" opacity=".5"/>
<rect y="216" width="1200" height="4" fill="url(#neonbar)"/></svg>'''
    save("footer-cyber.svg", svg)


def main():
    hero()
    footer()
    for key, (_, tc, _, ic) in SECTIONS.items():
        save(f"plate-cyber-{key}.svg", plate(tc, ic))
    print("cyber assets generated")


if __name__ == "__main__":
    main()
