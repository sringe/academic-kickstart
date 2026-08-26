#!/usr/bin/env python3
"""Crop the hero panels: the group photo, and the research renders that rotate
beside it.

    python3 scripts/make_hero.py

Writes assets/media/headers/hero_center.jpg and hero_side_1..N.jpg, which
content/home/hero_card.md points at. The side images are cycled by
assets/js/hero_slideshow.js.

This does the pixel work CSS cannot: an optical zoom onto the interesting part
of each render, and a crop to the panel's aspect ratio. Everything is driven by
the tables below — add a dict to SIDES and re-run to add a slide.
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageEnhance

Image.MAX_IMAGE_PIXELS = None       # some sources are very large print artwork

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADERS = os.path.join(ROOT, "assets", "media", "headers")
QUALITY = 84

# CSS scales these with object-fit: cover, so they need the right aspect ratio
# and enough resolution for a retina screen, not exact pixel sizes.
SIDE_SIZE = (520, 880)      # tall, matching the height of the centre panel
CENTER_SIZE = (1240, 880)   # roughly the shape the middle panel occupies

CENTER = {
    "image": "Pic_3.jpg",   # group photo (the un-padded original)
    "zoom": 1.0,
    "focus": (0.5, 0.5),
    "bias": 0.5,
}

# Rotated through, in order.
#
# `bias` matters more than it looks: these renders are roughly 3.4:1 while the
# panel is 0.6:1, so a crop that fills the frame keeps only a narrow vertical
# band of the source, and `bias` decides which band — i.e. what the slide is of.
# Fitting the whole figure into the panel instead was tried and rejected: it
# leaves the object small between filled bands, and no fill matches the source
# gradient closely enough to hide the join.
SIDES = [
    {
        "image": "smpb_fhiaims11.png",   # continuum solvation
        # Centred on the molecule inside its isosurface.
        "zoom": 1.0,
        "focus": (0.5, 0.5),
        "bias": 0.545,
        "brightness": 1.02,
    },
    {
        "image": "qmmm_3.png",           # electrified interface
        # Zoomed and shifted right to clear the dark background outside this
        # render's white ellipse, which otherwise shows as a grey corner.
        "zoom": 1.15,
        "focus": (0.5, 0.5),
        "bias": 0.87,
        "brightness": 1.02,
    },
    {
        "image": "co2_electrolyzer.jpg",  # CO2 electrolyser cover artwork
        # Landscape artwork in a tall panel: centred on the cell stack.
        "zoom": 1.0,
        "focus": (0.5, 0.5),
        "bias": 0.5,
    },
]


def zoom_in(im: Image.Image, factor: float, focus: tuple[float, float]) -> Image.Image:
    """Crop to 1/factor of the frame around `focus`: an optical zoom."""
    if factor <= 1.0:
        return im
    w, h = im.width / factor, im.height / factor
    cx, cy = im.width * focus[0], im.height * focus[1]
    left = min(max(cx - w / 2, 0), im.width - w)
    top = min(max(cy - h / 2, 0), im.height - h)
    return im.crop((int(left), int(top), int(left + w), int(top + h)))


def cover(im: Image.Image, size: tuple[int, int], bias: float) -> Image.Image:
    """Scale to fill `size`, cropping the overflow. `bias` chooses which part of
    an over-wide image survives: 0 the left edge, 1 the right."""
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    im = im.resize((max(tw, round(im.width * scale)),
                    max(th, round(im.height * scale))), Image.LANCZOS)
    b = min(max(bias, 0.0), 1.0)
    left = int(round((im.width - tw) * b))
    top = int(round((im.height - th) * 0.5))
    return im.crop((left, top, left + tw, top + th))


def render(cfg: dict, size: tuple[int, int], out_name: str) -> bool:
    src = os.path.join(HEADERS, cfg["image"])
    if not os.path.exists(src):
        print(f"!! missing {src}", file=sys.stderr)
        return False
    im = Image.open(src).convert("RGB")
    im = zoom_in(im, cfg.get("zoom", 1.0), cfg.get("focus", (0.5, 0.5)))
    im = cover(im, size, cfg.get("bias", 0.5))
    if cfg.get("brightness", 1.0) != 1.0:
        im = ImageEnhance.Brightness(im).enhance(cfg["brightness"])
    dest = os.path.join(HEADERS, out_name)
    im.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
    print(f"  {out_name:<20} {im.size[0]}x{im.size[1]}  "
          f"{os.path.getsize(dest) // 1024:>4} KB   <- {cfg['image']}")
    return True


def main() -> int:
    ok = render(CENTER, CENTER_SIZE, "hero_center.jpg")
    for i, cfg in enumerate(SIDES, start=1):
        ok = render(cfg, SIDE_SIZE, f"hero_side_{i}.jpg") and ok

    # Drop slides left over from a longer list, so the folder matches SIDES.
    i = len(SIDES) + 1
    while os.path.exists(os.path.join(HEADERS, f"hero_side_{i}.jpg")):
        os.remove(os.path.join(HEADERS, f"hero_side_{i}.jpg"))
        print(f"  removed stale hero_side_{i}.jpg")
        i += 1

    # The old two-sided layout's files.
    for stale in ("hero_left.jpg", "hero_right.jpg"):
        p = os.path.join(HEADERS, stale)
        if os.path.exists(p):
            os.remove(p)
            print(f"  removed {stale} (superseded by hero_side_*.jpg)")

    if ok:
        print(f"\n  {len(SIDES)} slides — list them in content/home/hero_card.md")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
