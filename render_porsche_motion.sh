#!/usr/bin/env bash
# Rebuild the Porsche hero (WebP + MP4) from the owner-supplied 24s film.
set -euo pipefail
cd "$(dirname "$0")"
python3 render_porsche_film.py
