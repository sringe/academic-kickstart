#!/usr/bin/env python3
"""Compose the homepage hero: the group photo flanked by two research renders.

    python3 scripts/make_hero.py

Writes assets/media/headers/hero_blend.jpg, which content/home/hero_card.md
points at. Re-run after changing any source image or constant.

Layout, left to right:

    continuum render | group photo | interface render

Each render gets a narrow panel and dissolves into the photo across a soft ramp,
so no seam shows and — the reason for the panels — nothing is laid over anyone's
face. Each side has its own optical zoom: these figures are very wide, and at
full extent they read as a field of small atoms rather than one clear object.
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADERS = os.path.join(ROOT, "assets", "media", "headers")
OUT = "hero_blend.jpg"

PHOTO = "Pic_3.jpg"                  # group photo (the un-padded original)
SIZE = (1600, 760)                   # hero crop
OVERLAP = 150                        # px over which a render dissolves into the photo
QUALITY = 82

# Each side: source image, share of the total width, optical zoom, the point to
# keep centred (fractions of the source width/height), and which part of the
# too-wide panel survives the crop (0 = left edge, 1 = right edge).
SIDES = {
    "left": {
        "image": "smpb_fhiaims11.png",   # continuum solvation
        "share": 0.185,
        # A very wide figure in a narrow portrait panel is always a vertical
        # slice, so zooming in leaves a featureless blob; keep it near 1 and use
        # `bias` to place the slice over the cavity instead.
        "zoom": 1.0,
        "focus": (0.62, 0.52),
        "bias": 0.63,
        "brightness": 1.02,
    },
    "right": {
        "image": "qmmm_3.png",           # electrified interface
        "share": 0.185,
        "zoom": 2.15,
        "focus": (0.775, 0.50),
        "bias": 0.50,
        "brightness": 1.02,
    },
}


def cover(im: Image.Image, size: tuple[int, int], bias: float = 0.5) -> Image.Image:
    """Scale to fill `size`, cropping the overflow. `bias` chooses which part of
    a too-wide image survives: 0 the left edge, 1 the right."""
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    im = im.resize((max(tw, round(im.width * scale)),
                    max(th, round(im.height * scale))), Image.LANCZOS)
    left = int(round((im.width - tw) * min(max(bias, 0.0), 1.0)))
    top = (im.height - th) // 2
    return im.crop((left, top, left + tw, top + th))


def zoom_in(im: Image.Image, factor: float, focus: tuple[float, float]) -> Image.Image:
    """Crop to 1/factor of the frame around `focus`: an optical zoom."""
    if factor <= 1.0:
        return im
    w, h = im.width / factor, im.height / factor
    cx, cy = im.width * focus[0], im.height * focus[1]
    left = min(max(cx - w / 2, 0), im.width - w)
    top = min(max(cy - h / 2, 0), im.height - h)
    return im.crop((int(left), int(top), int(left + w), int(top + h)))


def ramp(size: tuple[int, int], x0: int, x1: int) -> Image.Image:
    """Alpha mask rising 0 -> 255 between x0 and x1, smoothstepped so the join
    has no visible edge."""
    w, h = size
    row = Image.new("L", (w, 1))
    px = row.load()
    for x in range(w):
        if x <= x0:
            a = 0.0
        elif x >= x1:
            a = 1.0
        else:
            t = (x - x0) / float(x1 - x0)
            a = t * t * (3 - 2 * t)
        px[x, 0] = int(round(a * 255))
    return row.resize((w, h))


def side_panel(cfg: dict, panel_size: tuple[int, int]) -> Image.Image:
    im = Image.open(os.path.join(HEADERS, cfg["image"])).convert("RGB")
    im = zoom_in(im, cfg["zoom"], cfg["focus"])
    im = cover(im, panel_size, cfg.get("bias", 0.5))
    return ImageEnhance.Brightness(im).enhance(cfg.get("brightness", 1.0))


def main() -> int:
    needed = [os.path.join(HEADERS, PHOTO)] + \
             [os.path.join(HEADERS, s["image"]) for s in SIDES.values()]
    missing = [p for p in needed if not os.path.exists(p)]
    if missing:
        for p in missing:
            print(f"!! missing {p}", file=sys.stderr)
        return 1

    w, h = SIZE
    left_w = int(round(SIDES["left"]["share"] * w))
    right_w = int(round(SIDES["right"]["share"] * w))
    left_seam, right_seam = left_w, w - right_w

    # The photo takes the middle, widened by half an overlap at each end so the
    # ramps have photo pixels to dissolve into.
    photo_w = (right_seam - left_seam) + OVERLAP
    canvas = Image.new("RGB", SIZE)
    canvas.paste(cover(Image.open(os.path.join(HEADERS, PHOTO)).convert("RGB"),
                       (photo_w, h)),
                 (left_seam - OVERLAP // 2, 0))

    # Left render, then right, each composited under a ramp at its seam.
    layer = Image.new("RGB", SIZE)
    layer.paste(side_panel(SIDES["left"], (left_w + OVERLAP // 2, h)), (0, 0))
    canvas = Image.composite(canvas, layer,
                             ramp(SIZE, left_seam - OVERLAP // 2,
                                  left_seam + OVERLAP // 2))

    layer = Image.new("RGB", SIZE)
    layer.paste(side_panel(SIDES["right"], (right_w + OVERLAP // 2, h)),
                (right_seam - OVERLAP // 2, 0))
    canvas = Image.composite(layer, canvas,
                             ramp(SIZE, right_seam - OVERLAP // 2,
                                  right_seam + OVERLAP // 2))

    dest = os.path.join(HEADERS, OUT)
    canvas.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    print(f"wrote {os.path.relpath(dest, ROOT)}  {w}x{h}  "
          f"{os.path.getsize(dest) // 1024} KB")
    print(f"  panels: left {left_w}px | photo {right_seam - left_seam}px | "
          f"right {right_w}px")
    return 0


if __name__ == "__main__":
    sys.exit(main())
