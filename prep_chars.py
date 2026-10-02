#!/usr/bin/env python3
"""Turn the raw character art in assets/src/<theme>/image.png into a cut-out, web-sized WebP (runs once per theme)."""
import pathlib
from PIL import Image

SRC = pathlib.Path(__file__).parent / "assets" / "src"
for theme in ("elysium", "cyber"):
    raw, out = SRC / theme / "image.png", SRC / f"char-{theme}.webp"
    if not raw.exists() or out.exists():
        continue
    im = Image.open(raw)
    if im.mode == "RGBA" and im.getchannel("A").getextrema()[0] < 250:
        im = im.convert("RGBA")  # already transparent
    else:
        from rembg import new_session, remove
        im = remove(im.convert("RGB"), session=new_session("isnet-anime"))
    im = im.crop(im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox())
    H = 820
    W = round(im.width * H / im.height)
    im = im.resize((W, H), Image.LANCZOS).crop((0, 0, W, round(H * .86)))
    im.save(out, "WEBP", quality=80, method=6)
    print("prepared", out.name, im.size)
