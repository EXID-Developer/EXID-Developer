#!/usr/bin/env python3
"""Stylish profile / SNS / tech-stack / CTA cards (animated SVG) for both themes."""
import base64
import io
import random
import urllib.request

from build_assets import IMPACT, MONO, SERIF, OUT, n, save, twinkle

OWNER = "EXID-Developer"

ELY = dict(tag="elysium", bg=("#1b3470", "#0a1330"), edge=("#FFF3C4", "#E8C170", "#8a6a2a"), acc="#F5D78E", acc2="#8FD3FF",
           txt="#FFFFFF", sub="#B9CCEE", head=SERIF, body=SERIF, glow="#F5D78E", chip=("#2b4b8f", "#12234a"))
CYB = dict(tag="cyber", bg=("#1b1578", "#07072a"), edge=("#00F0FF", "#9D4DFF", "#FF2BD6"), acc="#00F0FF", acc2="#FF2BD6",
           txt="#FFFFFF", sub="#9FA8D8", head=IMPACT, body=MONO, glow="#FF2BD6", chip=("#2a1f9a", "#0b0a38"))


def cham(w, h, c):
    return f"{c},0 {w - c},0 {w},{c} {w},{h - c} {w - c},{h} {c},{h} 0,{h - c} 0,{c}"


def frame(w, h, T, c=22, sheen=True):
    """Returns (defs, body) for a chamfered glass panel with gradient border and moving sheen."""
    e = T["edge"]
    defs = (f'<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T["bg"][0]}"/><stop offset="1" stop-color="{T["bg"][1]}"/></linearGradient>'
            f'<linearGradient id="ed" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{e[0]}"/><stop offset=".5" stop-color="{e[1]}"/><stop offset="1" stop-color="{e[2]}"/></linearGradient>'
            f'<linearGradient id="sh" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".22"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<linearGradient id="top" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity=".22"/><stop offset=".5" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<filter id="gl" x="-5%" y="-10%" width="110%" height="120%"><feDropShadow dx="0" dy="3" stdDeviation="6" flood-color="{T["glow"]}" flood-opacity=".55"/></filter>'
            f'<filter id="tg" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="4"/></filter>'
            f'<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".28"/></pattern>'
            f'<clipPath id="pc"><polygon points="{cham(w, h, c)}"/></clipPath>')
    body = (f'<g filter="url(#gl)"><polygon points="{cham(w, h, c)}" fill="url(#bg)" stroke="url(#ed)" stroke-width="2.6"/></g>'
            f'<g clip-path="url(#pc)"><rect width="{w}" height="{h * .5}" fill="url(#top)"/>')
    if sheen:
        body += (f'<rect x="-300" width="260" height="{h}" fill="url(#sh)" transform="skewX(-20)"><animate attributeName="x" values="-300;{w + 100};{w + 100}" keyTimes="0;.45;1" dur="7s" repeatCount="indefinite"/></rect>')
    if T["tag"] == "cyber":
        body += f'<rect width="{w}" height="{h}" fill="url(#scan)"/>'
    body += '</g>'
    inner = f'<polygon points="{cham(w - 10, h - 10, c - 3)}" transform="translate(5 5)" fill="none" stroke="{T["edge"][1]}" stroke-opacity=".35"/>'
    return defs, body + inner


def svg(w, h, defs, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"><defs>{defs}</defs>{body}</svg>'


def avatar_href():
    try:
        req = urllib.request.Request(f"https://github.com/{OWNER}.png?size=240", headers={"User-Agent": "profile-readme"})
        data = urllib.request.urlopen(req, timeout=15).read()
        from PIL import Image
        im = Image.open(io.BytesIO(data)).convert("RGB").resize((220, 220))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=86)
        return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception as exc:  # offline / blocked: fall back to a monogram
        print("avatar fallback:", exc)
        return None


# ------------------------------------------------------------------ profile
def profile(T):
    W, H = 1200, 290
    d, b = frame(W, H, T, 26)
    r = random.Random(3 if T["tag"] == "elysium" else 4)
    cx, cy, R = 150, 145, 88
    av = avatar_href()
    d += f'<clipPath id="av"><circle cx="{cx}" cy="{cy}" r="{R}"/></clipPath>'
    d += f'<radialGradient id="ha" cx=".5" cy=".5" r=".5"><stop offset=".6" stop-color="{T["acc"]}" stop-opacity=".0"/><stop offset=".85" stop-color="{T["acc"]}" stop-opacity=".55"/><stop offset="1" stop-color="{T["acc2"]}" stop-opacity="0"/></radialGradient>'
    d += f'<linearGradient id="nm" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{"#FFFBE6" if T["tag"] == "elysium" else "#FFFFFF"}"/><stop offset=".5" stop-color="{T["acc"]}"/><stop offset="1" stop-color="{"#C99A3E" if T["tag"] == "elysium" else T["acc2"]}"/></linearGradient>'
    d += f'<linearGradient id="nmx" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T["acc"]}"/><stop offset="1" stop-color="{T["acc2"]}"/></linearGradient>'
    # decor
    b += f'<g clip-path="url(#pc)">{twinkle(r, 26, 30, 1170, 14, 270, T["acc"] if T["tag"] == "elysium" else "#DDEBFF")}'
    if T["tag"] == "cyber":
        for i in range(14):
            x = 560 + i * 48
            b += f'<line x1="{x}" y1="290" x2="{x + 120}" y2="150" stroke="{T["acc"]}" stroke-opacity=".08"/>'
        b += f'<path d="M0 232H1200" stroke="{T["acc2"]}" stroke-opacity=".35"/>'
    else:
        b += f'<circle cx="600" cy="330" r="360" fill="url(#ha)" opacity=".25"/>'
    b += '</g>'
    # avatar
    b += f'<circle cx="{cx}" cy="{cy}" r="{R + 22}" fill="url(#ha)"><animate attributeName="opacity" values=".6;1;.6" dur="4s" repeatCount="indefinite"/></circle>'
    b += (f'<circle cx="{cx}" cy="{cy}" r="{R + 12}" fill="none" stroke="{T["acc"]}" stroke-width="2" stroke-dasharray="4 10" stroke-opacity=".9">'
          f'<animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};360 {cx} {cy}" dur="30s" repeatCount="indefinite"/></circle>')
    b += (f'<circle cx="{cx}" cy="{cy}" r="{R + 5}" fill="none" stroke="url(#ed)" stroke-width="4"/>')
    if av:
        b += f'<image href="{av}" x="{cx - R}" y="{cy - R}" width="{2 * R}" height="{2 * R}" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>'
    else:
        b += (f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#bg)"/><text x="{cx}" y="{cy + 28}" text-anchor="middle" font-family="{T["head"]}" font-size="84" '
              f'font-weight="900" fill="url(#nm)">E</text>')
    b += (f'<circle cx="{cx + 66}" cy="{cy + 66}" r="13" fill="#0a1330" stroke="url(#ed)" stroke-width="2"/>'
          f'<circle cx="{cx + 66}" cy="{cy + 66}" r="6" fill="#3DFF9A"><animate attributeName="opacity" values="1;.3;1" dur="1.6s" repeatCount="indefinite"/></circle>')
    # name block
    nx = 300
    b += f'<text x="{nx}" y="58" font-family="{T["body"]}" font-size="14" letter-spacing="6" fill="{T["acc2"]}">HELLO, I AM</text>'
    ital = ' font-style="italic"' if T["tag"] == "cyber" else ""
    b += (f'<text x="{nx + 3}" y="146" font-family="{T["head"]}" font-size="92" font-weight="900" letter-spacing="10"{ital} fill="#000" opacity=".45">EXID</text>'
          f'<text x="{nx}" y="142" font-family="{T["head"]}" font-size="92" font-weight="900" letter-spacing="10"{ital} fill="url(#nm)" stroke="{"#6d4d14" if T["tag"] == "elysium" else "#2a0a5e"}" stroke-width="1.2" paint-order="stroke">EXID</text>')
    role = "DAEVA OF ELYSIA  ·  BACKEND DEVELOPER" if T["tag"] == "elysium" else "NETRUNNER // BACKEND DEVELOPER"
    b += f'<text x="{nx + 2}" y="182" font-family="{T["body"]}" font-size="17" font-weight="700" letter-spacing="4" fill="url(#nmx)">{role}</text>'
    b += f'<rect x="{nx + 2}" y="194" width="520" height="2" fill="url(#ed)" opacity=".8"/>'
    b += (f'<text x="{nx + 2}" y="226" font-family="{T["body"]}" font-size="19" font-style="italic" fill="{T["txt"]}">'
          f'&#8220;Think with your code.&#8221;</text>')
    b += (f'<text x="{nx + 2}" y="254" font-family="{T["body"]}" font-size="14" letter-spacing="1" fill="{T["sub"]}">'
          f'Crafting robust architecture and elegant solutions.</text>')
    # status panel (right)
    px, py = 905, 40
    rows = [("FOCUS", "Spring Boot / Spring AI"), ("STACK", "Java · TS · React"), ("STATUS", "First coding story"), ("@", OWNER)]
    b += f'<rect x="{px - 14}" y="{py - 6}" width="2" height="214" fill="url(#ed)" opacity=".7"/>'
    for i, (k, v) in enumerate(rows):
        y = py + 20 + i * 52
        b += (f'<text x="{px}" y="{y}" font-family="{T["body"]}" font-size="12" letter-spacing="4" fill="{T["acc2"]}">{k}</text>'
              f'<text x="{px}" y="{y + 22}" font-family="{T["body"]}" font-size="17" font-weight="700" fill="{T["txt"]}">{v}</text>')
    b += (f'<rect x="{px}" y="{py + 214}" width="240" height="3" fill="url(#nmx)"><animate attributeName="width" values="40;240;120;40" keyTimes="0;.4;.7;1" dur="4s" repeatCount="indefinite"/></rect>')
    save(f"profile-{T['tag']}.svg", svg(W, H, d, b))


# ------------------------------------------------------------------ sns tiles
def glyph(kind, x, y, T):
    a, c = T["acc"], T["acc2"]
    if kind == "github":
        return (f'<g transform="translate({x} {y})" fill="none" stroke="{a}" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round">'
                f'<path d="M-9 -9L-19 0L-9 9M9 -9L19 0L9 9"/><path d="M4 -14L-4 14" stroke="{c}"/></g>')
    if kind == "repos":
        return (f'<g transform="translate({x} {y})" fill="none" stroke="{a}" stroke-width="3" stroke-linejoin="round">'
                f'<rect x="-16" y="-16" width="32" height="10" rx="2"/><rect x="-16" y="-3" width="32" height="10" rx="2" stroke="{c}"/><rect x="-16" y="10" width="32" height="8" rx="2"/></g>')
    pts = " ".join(f"{n(x + (22 if i % 2 == 0 else 9) * __import__('math').cos(-1.5708 + i * .62832))},{n(y + (22 if i % 2 == 0 else 9) * __import__('math').sin(-1.5708 + i * .62832))}" for i in range(10))
    return f'<polygon points="{pts}" fill="{a}" stroke="{c}" stroke-width="1.6" stroke-linejoin="round"/>'


def sns(T, key, label, sub):
    W, H = 380, 92
    d, b = frame(W, H, T, 16)
    d += f'<radialGradient id="ic" cx=".5" cy=".4" r=".7"><stop offset="0" stop-color="{T["chip"][0]}"/><stop offset="1" stop-color="{T["chip"][1]}"/></radialGradient>'
    b += f'<circle cx="52" cy="46" r="31" fill="url(#ic)" stroke="url(#ed)" stroke-width="2.4"/>'
    b += f'<circle cx="52" cy="46" r="38" fill="none" stroke="{T["acc"]}" stroke-opacity=".5" stroke-dasharray="3 7"><animateTransform attributeName="transform" type="rotate" values="0 52 46;360 52 46" dur="14s" repeatCount="indefinite"/></circle>'
    b += glyph(key, 52, 46, T)
    b += f'<text x="104" y="44" font-family="{T["head"]}" font-size="{25 if len(label) > 9 else 27}" font-weight="900" letter-spacing="{2 if len(label) > 9 else 3}" fill="{T["txt"]}">{label}</text>'
    b += f'<text x="105" y="68" font-family="{T["body"]}" font-size="13" letter-spacing="1" fill="{T["sub"]}">{sub}</text>'
    b += (f'<path d="M344 38L358 46L344 54" fill="none" stroke="{T["acc"]}" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round">'
          f'<animateTransform attributeName="transform" type="translate" values="0 0;6 0;0 0" dur="1.6s" repeatCount="indefinite"/></path>')
    save(f"sns-{T['tag']}-{key}.svg", svg(W, H, d, b))


# ------------------------------------------------------------------ tech stack
STACK_ROWS = [
    ("BACKEND", [("Java", "Jv", "Language"), ("Spring Boot", "Sb", "Framework"), ("MyBatis", "Mb", "SQL Mapper"), ("Spring AI", "AI", "AI Integration")]),
    ("FRONTEND &amp; TOOLS", [("TypeScript", "TS", "Language"), ("React", "Re", "UI Library"), ("Vite", "Vi", "Build Tool"), ("Git", "Gt", "Version Control")]),
]


def hexpts(cx, cy, r):
    m = __import__("math")
    return " ".join(f"{n(cx + r * m.cos(m.pi / 3 * i + m.pi / 6))},{n(cy + r * m.sin(m.pi / 3 * i + m.pi / 6))}" for i in range(6))


def stack(T):
    W, H = 1200, 340
    d, b = frame(W, H, T, 24)
    d += f'<linearGradient id="hx" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{T["acc"]}"/><stop offset="1" stop-color="{T["acc2"]}"/></linearGradient>'
    d += f'<radialGradient id="cp" cx=".5" cy=".3" r=".9"><stop offset="0" stop-color="{T["chip"][0]}"/><stop offset="1" stop-color="{T["chip"][1]}"/></radialGradient>'
    for ri, (title, items) in enumerate(STACK_ROWS):
        y0 = 36 + ri * 150
        b += f'<text x="44" y="{y0 + 14}" font-family="{T["body"]}" font-size="14" letter-spacing="7" fill="{T["acc2"]}">{title}</text>'
        b += f'<rect x="44" y="{y0 + 24}" width="1112" height="1.6" fill="url(#ed)" opacity=".6"/>'
        for i, (name, mono, sub) in enumerate(items):
            x = 44 + i * 280
            y = y0 + 40
            b += f'<g><animateTransform attributeName="transform" type="translate" values="0 0;0 -4;0 0" dur="{n(3.4 + (i + ri) * .45)}s" begin="{n(i * .3)}s" repeatCount="indefinite"/>'
            b += f'<polygon points="{cham(256, 84, 12)}" transform="translate({x} {y})" fill="url(#cp)" stroke="url(#ed)" stroke-width="1.8"/>'
            b += f'<polygon points="{hexpts(x + 46, y + 42, 31)}" fill="#07102a" stroke="url(#hx)" stroke-width="2.6"/>'
            b += f'<polygon points="{hexpts(x + 46, y + 42, 38)}" fill="none" stroke="{T["acc"]}" stroke-opacity=".4" stroke-dasharray="3 6"><animateTransform attributeName="transform" type="rotate" values="0 {x + 46} {y + 42};360 {x + 46} {y + 42}" dur="18s" repeatCount="indefinite"/></polygon>'
            b += f'<text x="{x + 46}" y="{y + 50}" text-anchor="middle" font-family="{T["head"]}" font-size="22" font-weight="900" fill="url(#hx)">{mono}</text>'
            b += f'<text x="{x + 94}" y="{y + 40}" font-family="{T["head"]}" font-size="21" font-weight="900" letter-spacing="1" fill="{T["txt"]}">{name}</text>'
            b += f'<text x="{x + 95}" y="{y + 62}" font-family="{T["body"]}" font-size="12" letter-spacing="1" fill="{T["sub"]}">{sub}</text>'
            b += '</g>'
    save(f"stack-{T['tag']}.svg", svg(W, H, d, b))


# ------------------------------------------------------------------ CTA buttons
def cta(T, key, label, sub):
    W, H = 560, 96
    d, b = frame(W, H, T, 18)
    d += f'<linearGradient id="bt" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T["acc"]}" stop-opacity=".30"/><stop offset="1" stop-color="{T["acc2"]}" stop-opacity=".30"/></linearGradient>'
    b += f'<rect x="8" y="8" width="{W - 16}" height="{H - 16}" fill="url(#bt)" clip-path="url(#pc)"><animate attributeName="opacity" values=".6;1;.6" dur="3.2s" repeatCount="indefinite"/></rect>'
    b += f'<text x="40" y="46" font-family="{T["body"]}" font-size="12" letter-spacing="5" fill="{T["acc2"]}">CLICK ME</text>'
    b += f'<text x="40" y="76" font-family="{T["head"]}" font-size="30" font-weight="900" letter-spacing="3" fill="{T["txt"]}">{label}</text>'
    b += f'<text x="{W - 150}" y="58" text-anchor="end" font-family="{T["body"]}" font-size="14" fill="{T["sub"]}">{sub}</text>'
    b += (f'<g fill="none" stroke="{T["acc"]}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"><path d="M{W - 112} 32L{W - 88} 48L{W - 112} 64"/><path d="M{W - 82} 32L{W - 58} 48L{W - 82} 64" stroke="{T["acc2"]}"/>'
          f'<animateTransform attributeName="transform" type="translate" values="0 0;8 0;0 0" dur="1.4s" repeatCount="indefinite"/></g>')
    save(f"cta-{T['tag']}-{key}.svg", svg(W, H, d, b))


def main():
    for T in (ELY, CYB):
        profile(T)
        sns(T, "github", "GITHUB", f"@{OWNER}")
        sns(T, "repos", "REPOSITORIES", "Browse all projects")
        sns(T, "stars", "STARS", "Starred repositories")
        stack(T)
        cta(T, "study", "STUDY LOG", "What I am learning")
        cta(T, "project", "PROJECTS", "What I am building")
    print("cards generated")


if __name__ == "__main__":
    main()
