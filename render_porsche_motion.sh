#!/usr/bin/env bash
# Requires ffmpeg. Render a six-second seamless photographic camera/light loop.
set -euo pipefail
cd "$(dirname "$0")"
python - <<'PY'
from PIL import Image
Image.open('assets/porsche/approved-design.webp').crop((0,58,1536,438)).save('/tmp/exid-hero-source.png')
PY
ffmpeg -hide_banner -loglevel error -y -i /tmp/exid-hero-source.png -vf "zoompan=z='1.015+0.015*sin(2*PI*on/144)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=144:s=1280x316:fps=24,eq=brightness='0.008*sin(2*PI*t/6)':eval=frame" -an -c:v libx264 -preset medium -crf 21 -pix_fmt yuv420p -movflags +faststart assets/porsche/hero-film.mp4
ffmpeg -hide_banner -loglevel error -y -i assets/porsche/hero-film.mp4 -vf 'fps=12,scale=960:-2' -c:v libwebp_anim -quality 65 -loop 0 -an assets/porsche/hero-motion.webp
