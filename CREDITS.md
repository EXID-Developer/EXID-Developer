# Credits · 이미지 출처

이 프로필 README에 쓰인 이미지와 위젯의 출처를 정리한 문서입니다.

## Elysium (천족) 테마

| 구성 요소 | 파일 | 출처 |
|:--|:--|:--|
| 포토리얼 카드 원본 | `assets/photoreal/approved-design.png` | ChatGPT(GPT) 이미지 생성으로 만든 이미지 (소유자 EXID 제공) |
| 포토리얼 카드 (프로필 · SNS 3종 · 스택 3종) | `assets/photoreal/*.svg` | 위 원본을 카드별로 잘라 사용. 빛 · 반짝임 · 광택 애니메이션은 Claude가 `photoreal.py`로 추가 |
| 상단 영상 배너 | `assets/hero-elysium.webp` | 소유자 제공 영상 `EXID_cinematic_v2.mp4`를 애니메이션 WebP로 변환 (영상이 끝나면 정지 이미지로 전환) |
| 천사 캐릭터 | `assets/src/elysium/image.png`, `assets/src/char-elysium.webp` | 소유자 제공 오리지널 캐릭터 이미지. 배경 제거 후 배너에 합성 |
| 04~06 구분선 | `assets/photoreal/strip-*.svg` | Claude가 Python으로 생성한 SVG |

## Cyberpunk 테마

| 구성 요소 | 파일 | 출처 |
|:--|:--|:--|
| 포토리얼 카드 원본 | `assets/photoreal-cyber/approved-design.png` | ChatGPT(GPT) 이미지 생성으로 만든 이미지 (소유자 EXID 제공) |
| 포토리얼 카드 (프로필 · SNS 3종 · 스택 3종) | `assets/photoreal-cyber/*.svg` | 위 원본을 카드별로 잘라 사용. 빛 · 반짝임 · 광택 애니메이션은 Claude가 `photoreal.py`로 추가 |
| 넷러너 캐릭터 | `assets/src/cyber/image.png`, `assets/src/char-cyber.webp` | 소유자 제공 오리지널 캐릭터 이미지. 배경 제거 후 배너에 합성 |
| 히어로 · 푸터 · 구분선 | `assets/hero-cyber.svg` 등 | Claude가 Python으로 생성한 SVG |
| 04~06 구분선 | `assets/photoreal-cyber/strip-*.svg` | Claude가 Python으로 생성한 SVG |

## Porsche 테마

| 구성 요소 | 파일 | 출처 |
|:--|:--|:--|
| 시네마틱 영상 원본 | `assets/porsche/src/EXID_Precision_24s.mp4` | 소유자(EXID) 제공 24초 영상. 포르쉐(Porsche) 이미지를 참고해 제작 |
| 상단 히어로 영상 | `assets/porsche/hero-motion.webp`, `assets/porsche/hero-film.mp4` | 위 영상을 그대로 사용(모서리 워터마크 제거). 마지막 배너 구간의 후미등 점등 · 바닥 붉은 반사 · 차체 광택 스윕 · 반짝임 효과는 Claude가 `render_porsche_film.py`로 추가 |
| 프로필 디자인 원본 | `assets/porsche/approved-design.webp` | 포르쉐(Porsche) 이미지를 참고해 소유자가 만든 디자인 |
| 계기판 패널 재질 | `assets/porsche/panel-material.webp` | AI 이미지 생성으로 만든 빈 패널. 글자와 수치는 SVG 코드로 덧입힘 |
| 패널 · 카드 SVG | `assets/porsche/*.svg` | Claude가 Python(`porsche.py`, `porsche_panels.py`)으로 생성 |

## Crest (EXID 골드 엠블럼) 테마

| 구성 요소 | 파일 | 출처 |
|:--|:--|:--|
| 홍보 영상 · 배너 · 엠블럼 원본 | `assets/porsche/src/EXID_GitHub_15s.mp4`, `EXID_GitHub_Banner.png`, `EXID_Crest_Transparent.png` | 소유자(EXID) 제공 EXID GitHub Promo Pack (15초 영상 + 전자음 사운드트랙, 가로 배너, 투명 엠블럼) |
| 상단 히어로 | `assets/crest/hero-motion.webp`, `hero-still.webp`, `hero-film.mp4` | 영상 한 번 재생 → 투명 엠블럼이 배너의 엠블럼 자리로 이동 → 배너에서 멈추도록 Claude가 `render_hero.py`로 구성. 원본 영상 · 배너 · 엠블럼은 편집하지 않음 |
| 소개 · 기술 스택 · 링크 · 활동 · 프로젝트 · 푸터 패널 | `assets/crest/*.svg` | 프로모 팩의 디자인(검정 바탕, 금 회로선, 금 베벨, 와인레드 보석)에 맞춰 Claude가 `crest.py`로 그린 벡터 SVG. 소개 · 푸터의 엠블럼은 위 투명 엠블럼 축소본 |
| 서체 | `assets/crest/fonts/` | [Cinzel](https://github.com/NDISCOVER/Cinzel), [Montserrat](https://github.com/JulietaUla/Montserrat) — SIL Open Font License 1.1 (라이선스 원문 동봉). SVG 안에 필요한 글자만 넣어 사용 |
| 활동 · 언어 수치 | `activity.svg`, `languages.svg` | 2026-10-06 스냅샷 (실시간 아님). 활동 카드를 누르면 실시간 통계로 이동 |

## 공통

| 구성 요소 | 출처 |
|:--|:--|
| 히어로 · 푸터 · 구분선 · SNS / 스택 / CTA 카드 · 실시간 숫자 스트립 | Claude가 Python(`build_assets.py`, `cyber.py`, `cards.py`, `livestat.py`)으로 만든 SVG. 저장소의 GitHub Actions가 자동 생성 |
| 캐릭터 배경 제거 | [rembg](https://github.com/danielgatis/rembg) (`isnet-anime` 모델) |
| 컨트리뷰션 스네이크 | [Platane/snk](https://github.com/Platane/snk) |
| 타이핑 문구 | [DenverCoder1/readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg) |
| GitHub 통계 카드 | [anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats) |
| 스트릭 통계 | [DenverCoder1/github-readme-streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) |
| 배지 | [shields.io](https://shields.io) |
| 방문자 수 | [komarev.com/ghpvc](https://komarev.com/ghpvc/) |
| 서체 | Cinzel, Share Tech Mono (Google Fonts, SIL Open Font License). 이미지 안의 글자는 서체가 없는 환경에서는 기본 서체로 대체됩니다. |

## 안내

- AI로 생성된 이미지가 포함되어 있습니다 (위 표의 "ChatGPT(GPT) 이미지 생성" 항목).
- Elysium 테마: Aion 2 게임에서 영감을 받은 개인 팬 스타일입니다.
- Cyberpunk 테마: Cyberpunk 2077 게임에서 영감을 받은 개인 팬 스타일입니다.
- Porsche 테마: 포르쉐(Porsche) 이미지를 참고해 만든 개인 팬 스타일입니다.
- Crest 테마: 소유자가 제공한 EXID 홍보 팩(영상 · 배너 · 엠블럼)을 바탕으로 한 개인 브랜드 디자인입니다.
- 공식 게임 에셋을 직접 사용하지 않았으며, 각 원작사(NCSOFT, CD Projekt Red, Porsche AG)와는 관련이 없습니다.
- 모든 커스텀 이미지와 SVG는 개인 프로젝트용으로 제작되었습니다.
