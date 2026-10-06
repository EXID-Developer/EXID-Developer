#!/usr/bin/env bash
# Rebuild the crest theme hero from the owner-supplied EXID GitHub Promo Pack (assets/porsche/src/).
#   assets/crest/hero-film.mp4    original 1080p film with soundtrack (click-through)
#   assets/crest/hero-motion.webp film once -> crest transition -> banner (stops on the banner)
#   assets/crest/hero-still.webp  banner frame for prefers-reduced-motion
set -euo pipefail
cd "$(dirname "$0")"
ffmpeg -hide_banner -loglevel error -y -i assets/porsche/src/EXID_GitHub_15s.mp4 -c copy -movflags +faststart assets/crest/hero-film.mp4
python3 render_hero.py
