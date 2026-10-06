#!/usr/bin/env python3
"""Render README.md for the theme stored in theme.txt (auto | elysium | cyberpunk)."""
import pathlib

OWNER = "EXID-Developer"
REPO = f"https://github.com/{OWNER}/{OWNER}"
RAW = f"https://raw.githubusercontent.com/{OWNER}/{OWNER}/output"
root = pathlib.Path(__file__).parent
tf = root / "theme.txt"
PRE = (root / "assets" / "photoreal" / "approved-design.png").exists()  # photoreal Elysium art present?
PRC = (root / "assets" / "photoreal-cyber" / "approved-design.png").exists()  # photoreal Cyberpunk art present?
mode = tf.read_text().strip() if tf.exists() else "auto"
if mode not in ("auto", "elysium", "cyberpunk"):
    mode = "auto"

E = dict(
    hero="./assets/hero-elysium.webp" if (root / "assets" / "hero-elysium.webp").exists() else "./assets/hero-elysium.svg", footer="./assets/footer-elysium.svg", tag="elysium", snake=f"{RAW}/snake-elysium.svg",
    typing="https://readme-typing-svg.demolab.com?font=Cinzel&weight=600&size=22&duration=3500&pause=1200&color=F5D78E&center=true&vCenter=true&width=640&lines=Welcome+to+Elysium;First+Coding+Story;Spring+Boot+%C2%B7+React+%C2%B7+Spring+AI",
    badge=("12234A", "F5D78E", "8FD3FF"),
    card="bg_color=0B1426&border_color=E8C170&title_color=F5D78E&icon_color=8FD3FF&text_color=DCEBFF",
    streak="background=0B1426&border=E8C170&ring=F5D78E&fire=F5D78E&currStreakLabel=F5D78E&sideLabels=8FD3FF&currStreakNum=FFFFFF&sideNums=FFFFFF&dates=9FB6D9",
    views="color=E8C170&labelColor=12234A", active="F5D78E",
    h=dict(sns="✦ 연락처 (SNS List)", intro="✦ 날개를 펼친 개발자, exid", stack="✦ 장비 (Tech Stack)", stats="✦ 전투 기록 (GitHub Stats)",
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
    h=dict(sns="▌ COMMS LINK // SNS List", intro="▌ 사이버 공간의 개발자, exid", stack="▌ LOADOUT // Tech Stack", stats="▌ SYSTEM LOG // GitHub Stats",
           snake="▌ DATA STREAM // Contribution Snake", quest="▌ ACTIVE MISSIONS // Featured Projects"),
    quote=["네온이 켜진 사이버 공간에서 코드를 쓰는 중입니다.",
           "Java와 Spring으로 서버를 세우고, React로 화면을 그리며, Spring AI로 새로운 가능성을 실험합니다."],
)
NEUTRAL = dict(sns="◆ SNS List", intro="◆ exid", stack="◆ 장비 (Tech Stack)", stats="◆ GitHub Stats",
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


def pr(t):
    return PRE if t is E else PRC


def pdir(t):
    return "./assets/photoreal" if t is E else "./assets/photoreal-cyber"


def plate(key):
    alt = {"elysium": E, "cyberpunk": C}.get(mode, {"h": NEUTRAL})["h"][key]
    def url(t):
        if pr(t):
            d = pdir(t)
            return (d + "/blank.svg" if key == "intro" else
                    d + "/section-%s.svg" % key if key in ("sns", "stack") else d + "/strip-%s.svg" % key)
        return f"./assets/plate-{t['tag']}-{key}.svg"
    return themed(url, width="100%", alt=alt)

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

trophy = lambda t: (f"https://github-profile-trophy.vercel.app/?username={OWNER}&theme="
                    f"{'radical' if t is C else 'gruvbox'}&no-frame=true&no-bg=true&row=1&column=6&margin-w=8")
click = lambda href: f'<a href="{href}">' + themed(lambda t: f"https://img.shields.io/badge/Click!_Me!-{t['active']}?style=for-the-badge", alt="Click Me") + "</a>"

U = f"https://github.com/{OWNER}"

def sns_badge(name, logo, href, ci):
    def url(t):
        return f"https://img.shields.io/badge/{name}-{t['badge'][0]}?style=for-the-badge&logo={logo}&logoColor={t['badge'][ci]}"
    return f'<a href="{href}">{themed(url, alt=name)}</a>'


PRKEY = dict(github="github", repos="repositories", stars="stars")


def sns_tile(key, href):
    return f'<a href="{href}">' + themed(lambda t: "%s/%s.svg" % (pdir(t), PRKEY[key]) if pr(t) else "./assets/sns-%s-%s.svg" % (t["tag"], key), width="32%", alt=key) + "</a>"


def cta_btn(key, href):
    return f'<a href="{href}">' + themed(lambda t: "./assets/cta-%s-%s.svg" % (t["tag"], key), width="48%", alt=key) + "</a>"


def stack_tiles():
    if not (PRE or PRC):
        return themed(lambda t: "./assets/stack-%s.svg" % t["tag"], width="100%", alt="tech stack")
    names = ["backend", "frontend", "ai-tools"]
    return "\n".join(themed(lambda t, i=i: "%s/%s.svg" % (pdir(t), names[i]) if pr(t) else "./assets/stack-%s-%d.svg" % (t["tag"], i),
                            width="32%", alt=names[i]) for i in range(3))


STACKIMG = stack_tiles()
SNS = "\n  ".join([sns_tile("github", U), sns_tile("repos", U + "?tab=repositories"), sns_tile("stars", U + "?tab=stars")])

out = f'''<div align="center">

{themed(lambda t: t["hero"], width="100%", alt="EXID")}

<a href="{REPO}">{themed(lambda t: t["typing"], alt="typing")}</a>

</div>

{plate("intro")}

{themed(lambda t: pdir(t) + "/profile.svg" if pr(t) else "./assets/profile-%s.svg" % t["tag"], width="100%", alt="profile")}

<p align="center">
{text("quote")[0]}<br/>
{text("quote")[1]}
</p>

{plate("sns")}

<p align="center">
  {SNS}
</p>

{plate("stack")}

<details open>
<summary><b>Tech Stack (click to fold)</b></summary>
<br/>
<p align="center">
{STACKIMG}
</p>
</details>

{plate("stats")}

<p align="center">
{themed(lambda t: "./assets/livestat-%s.svg" % t["tag"], width="100%", alt="live GitHub stats")}
</p>



<table align="center">
<tr>
<td align="center">
  {themed(lambda t: f"https://streak-stats.demolab.com?user={OWNER}&{t['streak']}&hide_border=false", alt="streak")}
</td>
<td align="center">
  {themed(lambda t: stats_card(t, f"top-langs/?username={OWNER}&layout=compact&hide_border=false"), height="170", alt="top languages")}
</td>
</tr>
</table>

{plate("snake")}

<p align="center">
  {themed(lambda t: t["snake"], alt="contribution snake")}
</p>

{plate("quest")}

<p align="center">
  <a href="{U}/damso">{pin("damso")}</a>
  <a href="{U}/SpringAiBasic">{pin("SpringAiBasic")}</a>
</p>
<p align="center">
  <a href="{U}/sivertown">{pin("sivertown")}</a>
  <a href="{U}/SpringBootMyBatis">{pin("SpringBootMyBatis")}</a>
</p>

<p align="center">
{cta_btn("study", U + "/SpringAiBasic")}
{cta_btn("project", U + "/damso")}
</p>

<details>
<summary><b>Credits · 이미지 출처</b></summary>
<br/>

| 테마 | 구성 요소 | 출처 |
|:--|:--|:--|
| Elysium (천족) | 포토리얼 카드 (프로필 · SNS · 스택) | ChatGPT(GPT) 이미지 생성으로 만든 원본을 카드별로 잘라 사용, 빛 · 반짝임 애니메이션은 Claude가 추가 |
| Elysium (천족) | 상단 영상 배너 | 소유자(EXID) 제공 영상 EXID_cinematic_v2.mp4를 애니메이션 WebP로 변환 (영상이 끝나면 정지 이미지로 전환) |
| Elysium (천족) | 천사 캐릭터 | 소유자(EXID) 제공 오리지널 캐릭터 이미지 (배경 제거 후 애니메이션 합성) |
| Cyberpunk | 포토리얼 카드 (프로필 · SNS · 스택) | ChatGPT(GPT) 이미지 생성으로 만든 원본을 카드별로 잘라 사용, 빛 · 반짝임 애니메이션은 Claude가 추가 |
| Cyberpunk | 넷러너 캐릭터 | 소유자(EXID) 제공 오리지널 캐릭터 이미지 (배경 제거 후 애니메이션 합성) |
| 공통 | 히어로 · 푸터 · 구분선 · SNS / 스택 / CTA 카드 · 실시간 숫자 | Claude가 Python으로 생성한 SVG (이 저장소의 코드로 자동 생성) |
| 공통 | 외부 서비스 위젯 | [readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg) · [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) · [streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) · [snk](https://github.com/Platane/snk) · [shields.io](https://shields.io) · [komarev](https://komarev.com/ghpvc/) |

AI로 생성된 이미지가 포함되어 있습니다. 테마는 게임 · 애니메이션 분위기에서 영감을 받은 개인 팬 스타일이며, 공식 에셋을 사용하지 않았고 원작 제작사와 관련이 없습니다. 자세한 내용은 [CREDITS.md](./CREDITS.md)를 참고하세요.

</details>

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
