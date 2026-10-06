#!/usr/bin/env python3
"""Build the profile hero: promo film once -> emblem transition -> banner (hold).

Inputs (owner-supplied EXID GitHub Promo Pack):
  assets/porsche/src/EXID_GitHub_15s.mp4         15 s promo film
  assets/porsche/src/EXID_Crest_Transparent.png  transparent crest
  assets/porsche/src/EXID_GitHub_Banner.png      wide banner
Outputs:
  assets/crest/hero-motion.webp    800x450 animated WebP, plays ONCE and stops on the banner
  assets/crest/hero-still.webp     final banner frame (prefers-reduced-motion)
Sequence after the film: the crest fades/scales in at the centre, a light sweep
crosses it, then it glides to the crest position of the banner while the banner
fades in underneath; the last frame (the banner) stays on screen.
Requires ffmpeg and Pillow (+numpy).
"""
import glob, pathlib, subprocess, tempfile
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageChops

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "assets/porsche/src"
OUT = ROOT / "assets/crest"
W, H, FPS = 800, 450, 12

# crest position inside the banner image (2170x725 source pixels)
BANNER_CREST = (275, 54, 849, 670)   # measured by template matching the crest against the banner


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def film_frames():
    tmp = tempfile.mkdtemp()
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(SRC / "EXID_GitHub_15s.mp4"),
                    "-vf", f"fps={FPS},scale={W}:{H}:flags=lanczos", f"{tmp}/%04d.png"], check=True)
    return [Image.open(f).convert("RGB") for f in sorted(glob.glob(f"{tmp}/*.png"))]


def final_layout(banner):
    """Banner centred on a 16:9 canvas over a dark, blurred extension of itself."""
    bw = W
    bh = round(banner.height * W / banner.width)
    by = (H - bh) // 2
    cover_h = H
    cover_w = round(banner.width * cover_h / banner.height)
    bg = banner.resize((cover_w, cover_h), Image.LANCZOS).filter(ImageFilter.GaussianBlur(18))
    bg = bg.crop(((cover_w - W) // 2, 0, (cover_w - W) // 2 + W, H))
    bg = ImageEnhance.Brightness(bg).enhance(0.28)
    fg = banner.resize((bw, bh), Image.LANCZOS)
    # soften the banner's top/bottom edges into the background
    m = np.ones((bh, bw), np.float32)
    f = 18
    ramp = np.linspace(0, 1, f, dtype=np.float32)
    m[:f] *= ramp[:, None]
    m[-f:] *= ramp[::-1][:, None]
    mask = Image.fromarray((m * 255).astype(np.uint8))
    canvas = bg.copy()
    canvas.paste(fg, (0, by), mask)
    scale = bw / banner.width
    x0, y0, x1, y1 = BANNER_CREST
    crest_box = (x0 * scale, by + y0 * scale, (x1 - x0) * scale, (y1 - y0) * scale)  # x, y, w, h
    return canvas, bg, crest_box


def shine(crest, p):
    """Diagonal light sweep over the crest (p: 0..1)."""
    w, h = crest.size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    cx = -0.3 * w + p * 1.6 * w
    d = (xx - cx) + (yy - h / 2) * 0.45
    band = np.exp(-(d / (0.07 * w)) ** 2) * 0.75
    a = np.asarray(crest)[..., 3].astype(np.float32) / 255
    rgb = np.asarray(crest)[..., :3].astype(np.float32)
    lum = rgb.mean(2) / 255
    s = (band * a * (0.35 + 0.65 * lum))[..., None]
    out = 255 - (255 - rgb) * (1 - s)
    return Image.fromarray(np.dstack([out, a * 255]).astype(np.uint8), "RGBA")


def glow(alpha_img, radius, strength, color=(255, 190, 90)):
    a = alpha_img.filter(ImageFilter.GaussianBlur(radius))
    a = a.point(lambda v: min(255, int(v * strength)))
    g = Image.new("RGBA", alpha_img.size, color + (0,))
    g.putalpha(a)
    return g


def main():
    film = film_frames()
    banner = Image.open(SRC / "EXID_GitHub_Banner.png").convert("RGB")
    crest = Image.open(SRC / "EXID_Crest_Transparent.png").convert("RGBA")
    crest = crest.crop(crest.getbbox())
    final, bg, (fx, fy, fw, fh) = final_layout(banner)

    # crest at centre: 78% of canvas height
    ch0 = H * 0.78
    cw0 = ch0 * crest.width / crest.height
    cx0, cy0 = (W - cw0) / 2, (H - ch0) / 2
    dark = Image.new("RGB", (W, H), (8, 8, 10))
    bg_dark = Image.blend(dark, bg, 0.3)
    # banner with its own crest masked out (shown while the moving crest is still travelling)
    hole = Image.new("L", (W, H), 0)
    hole.paste(crest.getchannel("A").resize((round(fw), round(fh)), Image.LANCZOS), (round(fx), round(fy)))
    hole = hole.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(6))
    final_holed = Image.composite(bg_dark, final, hole)

    outro = []
    n_in, n_shine, n_move, n_settle = 9, 10, 14, 6   # 0.75 s, 0.83 s, 1.17 s, 0.5 s
    total = n_in + n_shine + n_move + n_settle
    for i in range(total):
        if i < n_in:                                 # fade + scale in at centre
            p = ease((i + 1) / n_in)
            sc, x, y, w, h = 0.86 + 0.14 * p, cx0, cy0, cw0, ch0
            alpha, banner_a, sp = p, 0.0, None
        elif i < n_in + n_shine:                     # light sweep
            p = (i - n_in + 1) / n_shine
            sc, x, y, w, h, alpha, banner_a, sp = 1.0, cx0, cy0, cw0, ch0, 1.0, 0.0, p
        elif i < n_in + n_shine + n_move:            # glide into the banner's crest slot
            p = ease((i - n_in - n_shine + 1) / n_move)
            sc, alpha, banner_a, sp = 1.0, 1.0, p, None
            x, y = cx0 + (fx - cx0) * p, cy0 + (fy - cy0) * p
            w, h = cw0 + (fw - cw0) * p, ch0 + (fh - ch0) * p
        else:                                        # hand over to the banner's own crest
            p = ease((i - n_in - n_shine - n_move + 1) / n_settle)
            sc, x, y, w, h, alpha, banner_a, sp = 1.0, fx, fy, fw, fh, 1 - p, 1.0, None

        settling = i >= n_in + n_shine + n_move
        target = final if settling else final_holed
        base = Image.blend(bg_dark, target, banner_a).convert("RGBA")
        cw, chh = max(1, round(w * sc)), max(1, round(h * sc))
        c = crest.resize((cw, chh), Image.LANCZOS)
        if sp is not None:
            c = shine(c, sp)
        px, py = round(x + (w - cw) / 2), round(y + (h - chh) / 2)
        a = c.getchannel("A").point(lambda v: int(v * alpha))
        halo = glow(a, 14, 0.55 * (1 - banner_a * 0.6))
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layer.alpha_composite(halo, (px, py))
        c.putalpha(a)
        layer.alpha_composite(c, (px, py))
        outro.append(Image.alpha_composite(base, layer).convert("RGB"))

    frames = film + outro + [final]
    durations = [round(1000 / FPS)] * (len(frames) - 1) + [3000]
    frames[0].save(OUT / "hero-motion.webp", save_all=True, append_images=frames[1:],
                   duration=durations, loop=1,               # play once, stop on the banner
                   quality=80, method=4, kmin=0, kmax=1,     # all keyframes: no blocky trails
                   minimize_size=False, allow_mixed=False)
    final.save(OUT / "hero-still.webp", quality=88)
    for p in ("hero-motion.webp", "hero-still.webp"):
        print(p, f"{(OUT / p).stat().st_size / 1e6:.2f} MB")
    print("frames:", len(film), "film +", len(outro), "outro + 1 hold")


if __name__ == "__main__":
    main()
