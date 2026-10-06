#!/usr/bin/env bash
# Rebuild the profile hero from the owner-supplied 15s promo film (EXID_GitHub_15s.mp4).
#   assets/porsche/hero-film.mp4    full 1080p H.264 + AAC (click-through, keeps the soundtrack)
#   assets/porsche/hero-motion.webp 800x450, 12 fps, looping animated WebP shown in the README
set -euo pipefail
cd "$(dirname "$0")"
SRC=assets/porsche/src/EXID_GitHub_15s.mp4
ffmpeg -hide_banner -loglevel error -y -i "$SRC" -c copy -movflags +faststart assets/porsche/hero-film.mp4
# Every frame is stored as a keyframe: partial-frame updates left blocky trails on the dark background.
TMP=$(mktemp -d)
ffmpeg -hide_banner -loglevel error -i "$SRC" -vf 'fps=12,scale=800:-2:flags=lanczos' "$TMP/%04d.png"
python3 - "$TMP" <<'PY'
import glob, sys
from PIL import Image
frames = [Image.open(f).convert('RGB') for f in sorted(glob.glob(sys.argv[1] + '/*.png'))]
frames[0].save('assets/porsche/hero-motion.webp', save_all=True, append_images=frames[1:],
               duration=83, loop=0, quality=80, method=4, kmin=0, kmax=1,
               minimize_size=False, allow_mixed=False)
PY
rm -rf "$TMP"
# Still frame (crest + title) for prefers-reduced-motion viewers
ffmpeg -hide_banner -loglevel error -y -ss 12 -i "$SRC" -frames:v 1 -vf 'scale=1280:-2:flags=lanczos' \
  -c:v libwebp -quality 85 assets/porsche/hero-still.webp
