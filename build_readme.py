#!/usr/bin/env python3
"""Render README.md for the theme stored in theme.txt (auto | elysium | cyberpunk)."""
import pathlib

OWNER = "ryuwook42-byte"
REPO = f"https://github.com/{OWNER}/{OWNER}"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{OWNER}/output"
root = pathlib.Path(__file__).parent
tf = root / "theme.txt"
mode = tf.read_text().strip() if tf.exists() else "auto"
if mode not in ("auto", "elysium", "cyberpunk"):
    mode = "auto"

E = dict(
    hero="./assets/hero-elysium.svg", footer="./assets/footer-elysium.svg", tag="elysium", snake=f"{RAW}/snake-elysium.svg",
    typing="https://readme-typing-svg.demolab.com?font=Cinzel&weight=600&size=22&duration=3500&pause=1200&color=F5D78E&center=true&vCenter=true&width=640&lines=Welcome+to+Elysium;First+Coding+Story;Spring+Boot+%C2%B7+React+%C2%B7+Spring+AI",
    badge=("12234A", "F5D78E", "8FD3FF"),
    card="bg_color=0B1426&border_color=E8C170&title_color=F5D78E&icon_color=8FD3FF&text_color=DCEBFF",
    streak="background=0B1426&border=E8C170&ring=F5D78E&fire=F5D78E&currStreakLabel=F5D78E&sideLabels=8FD3FF&currStreakNum=FFFFFF&sideNums=FFFFFF&dates=9FB6D9",
    views="color=E8C170&labelColor=12234A", active="F5D78E",
    h=dict(intro="✦ 날개를 펼친 개발자, exid", stack="✦ 장비 (Tech Stack)", stats="✦ 전투 기록 (GitHub Stats)",
           snake="✦ 비행 궤적 (Contribution Snake)", quest="✦ 대표 퀘스트 (Featured Projects)"),
    quote=["빛의 땅 엘리시움에서 첫 코딩 이야기를 써 내려가는 중입니다.",
           "Java와 Spring으로 서버를 세우고, React로 화면을 그리며, Spring AI로 새로운 가능성을 실험합니다."],
)
C = dict(
    hero="./assets/hero-cyber.svg", footer="./assets/footer-cyber.svg", tag="cyber", snake=f"{RAW}/snake-cyber.svg",
    typing="https://readme-typing-svg.demolab.com?font=Share+Tech+Mono&weight=600&size=22&duration=3000&pause=1000&color=00F0FF&center=true&vCenter=true&width=640&lines=%3E+jack_in()%3B;First+Coding+Story;Spring+Boot+%2F%2F+React+%2F%2F+Spring+AI",
    badge=("0A0A2E", "FF2BD6", "00F0FF"),
    card="bg_color=0A0A2E&border_color=FF2BD6&title_color=00F0FF&icon_color=FF2BD6&text_color=DDEBFF",
    streak="background=0A0A2E&border=FF2BD6&ring=00F0FF&fire=FF2BD6&currStreakLabel=00F0FF&sideLabels=FF2BD6&currStreakNum=FFFFFF&sideNums=FFFFFF&dates=9FA8D8",
    views="color=FF2BD6&labelColor=0A0A2E", active="FF2BD6",
    h=dict(intro="▌ 사이버 공간의 개발자, exid", stack="▌ LOADOUT // Tech Stack", stats="▌ SYSTEM LOG // GitHub Stats",
           snake="▌ DATA STREAM // Contribution Snake", quest="▌ ACTIVE MISSIONS // Featured Projects"),
    quote=["네온이 켜진 사이버 공간에서 코드를 쓰는 중입니다.",
           "Java와 Spring으로 서버를 세우고, React로 화면을 그리며, Spring AI로 새로운 가능성을 실험합니다."],
)
NEUTRAL = dict(intro="◆ exid", stack="◆ 장비 (Tech Stack)", stats="◆ GitHub Stats",
               snake="◆ Contribution Snake", quest="◆ 대표 프로젝트 (Featured Projects)")


def themed(fn, **attrs):
    """Image whose URL depends on the theme. In auto mode: dark -> Elysium, light -> Cyberpunk."""
    a = " ".join(f'{k}="{v}"' for k, v in attrs.items())
    e, c = fn(E), fn(C)
    if mode == "elysium":
        return f'<img src="{e}" {a}/>'
    if mode == "cyberpunk":
        return f'<img src="{c}" {a}/>'
    return (f'<picture><source media="(prefers-color-scheme: light)" srcset="{c}">'
            f'<img src="{e}" {a}/></picture>')


def head(key):
    t = E if mode == "elysium" else C if mode == "cyberpunk" else None
    return (t["h"] if t else NEUTRAL)[key]


def text(key):
    t = C if mode == "cyberpunk" else E
    return t[key]


divider = lambda: ""


def plate(key):
    alt = {"elysium": E, "cyberpunk": C}.get(mode, {"h": NEUTRAL})["h"][key]
    return themed(lambda t: f"./assets/plate-{t['tag']}-{key}.svg", width="100%", alt=alt)

STACK = [("Java", "openjdk", 0), ("Spring_Boot", "springboot", 0), ("MyBatis", None, 0), ("Spring_AI", "spring", 0),
         ("TypeScript", "typescript", 1), ("React", "react", 1), ("Vite", "vite", 1), ("Git", "git", 0)]


def badge(name, logo, idx):
    def url(t):
        bg, a, b = t["badge"]
        u = f"https://img.shields.io/badge/{name}-{bg}?style=for-the-badge"
        if logo:
            u += f"&logo={logo}&logoColor={(a, b)[idx]}"
        return u
    return "  " + themed(url, alt=name.replace("_", " "))


def switch_buttons():
    def btn(label, key, color):
        on = mode == key
        msg, col = ("active", color) if on else ("switch", "333333")
        href = f"{REPO}/issues/new?title=theme%3A{key}&body=Submit+this+issue+to+switch+the+profile+theme+%28owner+only%29."
        img = f"https://img.shields.io/badge/{label}-{msg}-{col}?style=flat-square&labelColor=1a1a1a"
        return f'<a href="{href}"><img src="{img}" alt="{label}"/></a>'
    return "\n  ".join([btn("AUTO", "auto", "8FD3FF"), btn("ELYSIUM", "elysium", "F5D78E"), btn("CYBERPUNK", "cyberpunk", "FF2BD6")])


stats_card = lambda t, n: f"https://github-readme-stats.vercel.app/api/{n}&{t['card']}&border_radius=10"
pin = lambda repo: themed(lambda t: f"https://github-readme-stats.vercel.app/api/pin/?username={OWNER}&repo={repo}&{t['card']}", alt=repo)

U = f"https://github.com/{OWNER}"

out = f'''<div align="center">

{themed(lambda t: t["hero"], width="100%", alt="EXID")}

<a href="{REPO}">{themed(lambda t: t["typing"], alt="typing")}</a>

{divider()}

</div>

{plate("intro")}

> {text("quote")[0]}
> {text("quote")[1]}

{divider()}

{plate("stack")}

<p align="center">
{chr(10).join(badge(*s) for s in STACK)}
</p>

{divider()}

{plate("stats")}

<p align="center">
  {themed(lambda t: stats_card(t, f"top-langs/?username={OWNER}&layout=compact&hide_border=false"), height="170", alt="top languages")}
</p>

<p align="center">
  {themed(lambda t: f"https://streak-stats.demolab.com?user={OWNER}&{t['streak']}&hide_border=false", alt="streak")}
</p>

{divider()}

{plate("snake")}

<p align="center">
  {themed(lambda t: t["snake"], alt="contribution snake")}
</p>

{divider()}

{plate("quest")}

<p align="center">
  <a href="{U}/damso">{pin("damso")}</a>
  <a href="{U}/SpringAiBasic">{pin("SpringAiBasic")}</a>
</p>
<p align="center">
  <a href="{U}/sivertown">{pin("sivertown")}</a>
  <a href="{U}/SpringBootMyBatis">{pin("SpringBootMyBatis")}</a>
</p>

{divider()}

<div align="center">

{themed(lambda t: f"https://komarev.com/ghpvc/?username={OWNER}&label=Visitors&style=for-the-badge&{t['views']}", alt="views")}

<sub>THEME SWITCH (owner only: opens an issue, submit it and the profile re-renders)</sub><br/>
  {switch_buttons()}

{themed(lambda t: t["footer"], width="100%", alt="footer")}

</div>
'''
import re
out = re.sub(r"\n{3,}", "\n\n", out)
(root / "README.md").write_text(out, encoding="utf-8")
print(f"README.md rendered ({mode}), {len(out)} bytes")
