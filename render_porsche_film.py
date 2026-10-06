#!/usr/bin/env python3
"""Render the Porsche hero from the owner's 24s film.

Source: assets/porsche/src/EXID_Precision_24s.mp4 (owner-supplied).
The film plays in full (the corner sparkle watermark is inpainted out); on the closing "Think with your code." banner the
tail-light bar ignites (flicker -> flare -> breathing glow, with a red floor
reflection), a specular sweep runs across the chassis and a small glint
sparks on the rear haunch. The closing shot is held a little longer so the
effects can finish before the loop restarts.

Outputs:
  assets/porsche/hero-film.mp4    full-res H.264 (click-through)
  assets/porsche/hero-motion.webp animated WebP shown in the README
Requires: ffmpeg, Python 3 with numpy, opencv-python, Pillow.
"""
import pathlib, subprocess, sys
import cv2
import numpy as np

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "assets/porsche/src/EXID_Precision_24s.mp4"
OUT = ROOT / "assets/porsche"
FPS = 24
BANNER_Y0, BANNER_Y1 = 202, 518   # letterboxed closing banner inside the 1280x720 frame
FX_START = 468                    # frame where the closing banner begins fading in (19.5s)
HOLD_EXTRA = 3.5                  # seconds the closing shot is held for the effects
CAR_X0, CAR_X1 = 645, 1195        # car area inside the banner


def read_frames():
    cap = cv2.VideoCapture(str(SRC))
    frames = []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        frames.append(f)
    cap.release()
    if not frames:
        sys.exit(f"cannot read {SRC}")
    return frames


# Four-pointed sparkle watermark in the bottom-right corner of the cinematic part.
LOGO_BOX = (1128, 568, 1192, 630)   # x0, y0, x1, y1 around the sparkle


def remove_logo(frames):
    """Detect the sparkle from a reference frame and inpaint it wherever it appears."""
    x0, y0, x1, y1 = LOGO_BOX
    pad = 24
    X0, Y0, X1, Y1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad

    def bright_spots(f):
        g = cv2.cvtColor(f[Y0:Y1, X0:X1], cv2.COLOR_BGR2GRAY)
        bg = cv2.medianBlur(g, 31).astype(np.int16)
        m = (g.astype(np.int16) - bg > 18).astype(np.uint8)
        keep = np.zeros_like(m)
        keep[pad:pad + (y1 - y0), pad:pad + (x1 - x0)] = 1
        return m & keep

    ref = bright_spots(frames[24])
    if ref.sum() < 50:
        return frames
    # solid four-pointed star (astroid) centred on the sparkle, slightly enlarged
    cx, cy, r = 1160 - X0, 600 - Y0, 29
    yy, xx = np.mgrid[0:Y1 - Y0, 0:X1 - X0]
    star = (np.abs(xx - cx) ** (2 / 3) + np.abs(yy - cy) ** (2 / 3)) <= r ** (2 / 3)
    mask = cv2.dilate((star | ref.astype(bool)).astype(np.uint8), np.ones((5, 5), np.uint8))
    for i, f in enumerate(frames):
        cur = bright_spots(f)
        if (cur & ref).sum() / ref.sum() < 0.2:
            continue
        roi = f[Y0:Y1, X0:X1]
        f[Y0:Y1, X0:X1] = cv2.inpaint(roi, mask, 6, cv2.INPAINT_TELEA)
    return frames


def masks(banner):
    """Soft masks (float32 0..1) for tail light, red floor reflection and silver body."""
    b = banner.astype(np.float32)
    B, G, R = b[..., 0], b[..., 1], b[..., 2]
    h, w = R.shape
    xs = np.arange(w)[None, :]
    ys = np.arange(h)[:, None]
    in_car = (xs >= CAR_X0) & (xs <= CAR_X1)

    def box(x0, x1, y0, y1):
        return (xs >= x0) & (xs <= x1) & (ys >= y0) & (ys <= y1)

    # tail-light bar and diffuser reflector only (brake calipers excluded)
    lamp_zone = box(875, 1185, 140, 182) | box(880, 990, 214, 238)
    reddish = (R > 60) & (R > G * 1.45) & (R > B * 1.35)
    light = reddish & lamp_zone
    light = cv2.dilate(light.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(np.float32)
    light = cv2.GaussianBlur(light, (0, 0), 1.2)
    floor = reddish & box(820, 1200, 250, h)
    floor = cv2.GaussianBlur(floor.astype(np.float32), (0, 0), 3)

    hsv = cv2.cvtColor(banner, cv2.COLOR_BGR2HSV).astype(np.float32)
    body = (hsv[..., 1] < 75) & (hsv[..., 2] > 42) & in_car & (ys > 72) & (ys < 262)
    body = cv2.morphologyEx(body.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    body = cv2.morphologyEx(body, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(body)
    if n > 1:
        body = (lab == 1 + np.argmax(stats[1:, cv2.CC_STAT_AREA])).astype(np.uint8)
    body = cv2.GaussianBlur(body.astype(np.float32), (0, 0), 5)
    return light, floor, body


def light_level(t):
    """Tail-light intensity over time t (s) since the banner started."""
    if t < 0.9:
        return 0.3
    flicker = [(0.9, 0.85), (1.0, 0.3), (1.08, 0.75), (1.16, 0.35), (1.3, 1.0)]
    if t < 1.3:
        lvl = 0.3
        for ts, v in flicker:
            if t >= ts:
                lvl = v
        return lvl
    if t < 2.0:                                   # ignition flare, settles to 1.0
        return 1.0 + 0.7 * np.exp(-(t - 1.3) * 5)
    return 1.0 + 0.12 * np.sin((t - 2.0) * 2 * np.pi / 2.2)   # breathing


def apply_fx(frame, t, light, floor, body, sweep_x, glint_xy):
    out = frame.astype(np.float32)
    band = out[BANNER_Y0:BANNER_Y1]
    lvl = light_level(t)

    # 1) tail light: dim when "off", add red glow + bloom when lit
    base_scale = np.clip(lvl, 0.3, 1.0)
    band *= (1 - light[..., None] * (1 - base_scale))
    glow_amt = max(lvl - 0.35, 0) / 0.65
    if glow_amt > 0:
        core = light * glow_amt
        bloom = cv2.GaussianBlur(light, (0, 0), 7) * glow_amt * 1.6
        halo = cv2.GaussianBlur(light, (0, 0), 22) * glow_amt * 1.2
        add = np.zeros_like(band)
        add[..., 2] = core * 120 + bloom * 210 + halo * 140
        add[..., 1] = core * 70 + bloom * 25 + halo * 10
        add[..., 0] = core * 60 + bloom * 30 + halo * 18
        fl = cv2.GaussianBlur(floor, (0, 0), 4) * glow_amt
        add[..., 2] += fl * 170
        add[..., 1] += fl * 10
        add[..., 0] += fl * 15
        band = 255 - (255 - band) * (1 - np.clip(add / 255, 0, 1))  # screen blend

    # 2) chassis shine: diagonal specular band sweeping left -> right over the body
    if 2.2 <= t <= 3.8:
        p = (t - 2.2) / 1.6
        p = p * p * (3 - 2 * p)                     # ease in-out
        cx = CAR_X0 - 120 + p * (CAR_X1 - CAR_X0 + 240)
        h, w = body.shape
        xx, yy = np.meshgrid(np.arange(w), np.arange(h))
        d = (xx - cx) + (yy - 160) * 0.55           # slanted band
        streak = np.exp(-(d / 22) ** 2) + 0.5 * np.exp(-((d + 48) / 8) ** 2)
        lum = band.mean(axis=2) / 255
        s = np.clip(streak * body * (0.25 + 0.9 * lum) * 0.75, 0, 0.75)
        band = 255 - (255 - band) * (1 - s[..., None])

    # 3) glint star on the rear haunch
    if 3.5 <= t <= 4.3:
        k = np.sin((t - 3.5) / 0.8 * np.pi)
        gx, gy = glint_xy
        h, w = body.shape
        xx, yy = np.meshgrid(np.arange(w) - gx, np.arange(h) - gy)
        star = (np.exp(-(xx / 40) ** 2 - (yy / 2.0) ** 2) + np.exp(-(xx / 2.0) ** 2 - (yy / 22) ** 2)
                + 1.3 * np.exp(-(xx ** 2 + yy ** 2) / 18)) * 1.4
        s = np.clip(star * k, 0, 1)
        band = 255 - (255 - band) * (1 - s[..., None])

    out[BANNER_Y0:BANNER_Y1] = band
    return np.clip(out, 0, 255).astype(np.uint8)


def main():
    frames = remove_logo(read_frames())
    final_banner = frames[-1][BANNER_Y0:BANNER_Y1]
    light, floor, body = masks(final_banner)

    # brightest point on the rear haunch for the glint
    region = cv2.cvtColor(final_banner, cv2.COLOR_BGR2GRAY).astype(np.float32) * body
    region[:, : CAR_X0 + 60] = 0
    region[:, CAR_X0 + 260:] = 0
    gy, gx = np.unravel_index(np.argmax(cv2.GaussianBlur(region, (0, 0), 3)), region.shape)

    frames += [frames[-1]] * int(HOLD_EXTRA * FPS)
    banner_t0 = 480  # 20.0s: banner fully shown
    rendered = []
    for i, f in enumerate(frames):
        if i >= FX_START:
            t = (i - banner_t0) / FPS
            f = apply_fx(f, max(t, -1), light, floor, body, None, (gx, gy))
        rendered.append(f)

    h, w = rendered[0].shape[:2]
    mp4 = OUT / "hero-film.mp4"
    enc = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                            "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", "-an", str(mp4)], stdin=subprocess.PIPE)
    for f in rendered:
        enc.stdin.write(f.tobytes())
    enc.stdin.close()
    enc.wait()

    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(mp4),
                    "-vf", "fps=12,scale=800:-2:flags=lanczos", "-c:v", "libwebp_anim",
                    "-quality", "62", "-compression_level", "6", "-loop", "0", "-an",
                    str(OUT / "hero-motion.webp")], check=True)
    for p in (mp4, OUT / "hero-motion.webp"):
        print(f"{p.relative_to(ROOT)}  {p.stat().st_size/1e6:.2f} MB")


if __name__ == "__main__":
    main()
