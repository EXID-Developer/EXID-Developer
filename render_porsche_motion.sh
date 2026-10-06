#!/usr/bin/env bash
# Rebuild the profile hero from the owner-supplied EXID GitHub Promo Pack.
#   assets/porsche/hero-film.mp4    original 1080p film with soundtrack (click-through)
#   assets/porsche/hero-motion.webp film once -> crest transition -> banner (stops on the banner)
#   assets/porsche/hero-still.webp  banner frame for prefers-reduced-motion
set -euo pipefail
cd "$(dirname "$0")"
ffmpeg -hide_banner -loglevel error -y -i assets/porsche/src/EXID_GitHub_15s.mp4 -c copy -movflags +faststart assets/porsche/hero-film.mp4
python3 render_hero.py
