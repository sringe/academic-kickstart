#!/usr/bin/env python3
"""Compose the homepage hero: the group photo blended into a research render.

    python3 scripts/make_hero.py

Writes assets/media/headers/hero_blend.jpg, which content/home/hero_card.md
points at. Re-run after swapping either source image.

The two sources are joined by a wide horizontal gradient rather than a hard
seam, so the render appears to grow out of the right-hand side of the photo.
Everything is tunable through the constants below.
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADERS = os.path.join(ROOT, "assets", "media", "headers")

PHOTO = "Pic_3.jpg"                 # group photo (un-padded original)
RENDER = "qmmm_3.png"               # research render blended in on the right
OUT = "hero_blend.jpg"

SIZE = (1600, 760)                  # hero crop

# The photo keeps the left-hand panel to itself and the render takes the right,
# joined by a soft overlap. An earlier version faded the render across the whole
# frame, which laid the solvation cavity over people's faces.
PHOTO_SHARE = 0.58                  # fraction of the width belonging to the photo
OVERLAP = 180                       # px over which one dissolves into the other
RENDER_CROP_BIAS = 0.50             # which part of the wide render to keep (0=left, 1=right)
# Zoom into the render before cropping, so a busy figure reads as one clear
# object instead of a field of small atoms. FOCUS is the point to keep centred,
# as fractions of the source width/height.
RENDER_ZOOM = 2.15
RENDER_FOCUS = (0.775, 0.50)
RENDER_BRIGHTNESS = 1.02
QUALITY = 82


def cover(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Scale to fill `size`, cropping the overflow (CSS object-fit: cover)."""
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    im = im.resize((max(tw, round(im.width * scale)),
                    max(th, round(im.height * scale))), Image.LANCZOS)
    left = (im.width - tw) // 2
    top = (im.height - th) // 2
    return im.crop((left, top, left + tw, top + th))


def zoom_in(im: Image.Image, factor: float, focus: tuple[float, float]) -> Image.Image:
    """Crop to 1/factor of the frame around `focus`, i.e. an optical zoom."""
    if factor <= 1.0:
        return im
    w, h = im.width / factor, im.height / factor
    cx, cy = im.width * focus[0], im.height * focus[1]
    left = min(max(cx - w / 2, 0), im.width - w)
    top = min(max(cy - h / 2, 0), im.height - h)
    return im.crop((int(left), int(top), int(left + w), int(top + h)))


def cover_biased(im: Image.Image, size: tuple[int, int], bias: float) -> Image.Image:
    """Like cover(), but choose which part of a too-wide image to keep.
    bias 0 keeps the left edge, 1 the right."""
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    im = im.resize((max(tw, round(im.width * scale)),
                    max(th, round(im.height * scale))), Image.LANCZOS)
    left = int(round((im.width - tw) * min(max(bias, 0.0), 1.0)))
    top = (im.height - th) // 2
    return im.crop((left, top, left + tw, top + th))


def horizontal_ramp(size: tuple[int, int], x0: int, x1: int) -> Image.Image:
    """Left-to-right alpha mask: 0 at x0 or below, 255 at x1 or above."""
    w, h = size
    mask = Image.new("L", (w, 1))
    px = mask.load()
    for x in range(w):
        if x <= x0:
            a = 0.0
        elif x >= x1:
            a = 1.0
        else:
            t = (x - x0) / float(x1 - x0)
            a = t * t * (3 - 2 * t)          # smoothstep: no visible seam
        px[x, 0] = int(round(a * 255))
    return mask.resize((w, h))


def main() -> int:
    photo_path = os.path.join(HEADERS, PHOTO)
    render_path = os.path.join(HEADERS, RENDER)
    for p in (photo_path, render_path):
        if not os.path.exists(p):
            print(f"!! missing {p}", file=sys.stderr)
            return 1

    w, h = SIZE
    seam = int(round(PHOTO_SHARE * w))

    # The photo is squeezed into its own panel rather than the full frame, so the
    # group still fills the space it is given.
    photo_panel = cover(Image.open(photo_path).convert("RGB"),
                        (seam + OVERLAP // 2, h))
    base = Image.new("RGB", SIZE)
    base.paste(photo_panel, (0, 0))

    render_src = zoom_in(Image.open(render_path).convert("RGB"),
                         RENDER_ZOOM, RENDER_FOCUS)
    render_panel = cover_biased(render_src,
                                (w - seam + OVERLAP // 2, h), RENDER_CROP_BIAS)
    render_panel = ImageEnhance.Brightness(render_panel).enhance(RENDER_BRIGHTNESS)
    render_full = Image.new("RGB", SIZE)
    render_full.paste(render_panel, (seam - OVERLAP // 2, 0))

    out = Image.composite(render_full, base,
                          horizontal_ramp(SIZE, seam - OVERLAP // 2, seam + OVERLAP // 2))

    dest = os.path.join(HEADERS, OUT)
    out.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    print(f"wrote {os.path.relpath(dest, ROOT)}  "
          f"{out.size[0]}x{out.size[1]}  {os.path.getsize(dest) // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
