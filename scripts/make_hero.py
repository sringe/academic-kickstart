#!/usr/bin/env python3
"""Crop the three hero panels: two research renders and the group photo.

    python3 scripts/make_hero.py

Writes assets/media/headers/hero_left.jpg, hero_center.jpg and hero_right.jpg,
which content/home/hero_card.md points at.

The panels are laid out as three separate framed images by
layouts/partials/widgets/hero_card.html — this script only does the pixel work
that CSS cannot: an optical zoom onto the interesting part of each render, and a
crop to the panel's aspect ratio. An earlier version dissolved the renders into
the photo; keeping them as distinct panels reads more deliberately and means
nothing is ever laid over anyone's face.
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageEnhance

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADERS = os.path.join(ROOT, "assets", "media", "headers")
QUALITY = 84

# Output sizes. CSS scales these with object-fit: cover, so they only need the
# right aspect ratio and enough resolution for a retina screen.
SIDE_SIZE = (440, 880)     # tall and narrow
CENTER_SIZE = (1440, 880)

PANELS = {
    "hero_left.jpg": {
        "image": "smpb_fhiaims11.png",   # continuum solvation
        "size": SIDE_SIZE,
        # A very wide figure in a narrow portrait panel is always a vertical
        # slice, so zooming in leaves a featureless blob. Keep the zoom at 1 and
        # use `bias` to place the slice over the cavity.
        "zoom": 1.0,
        "focus": (0.62, 0.52),
        "bias": 0.63,
        "brightness": 1.02,
    },
    "hero_center.jpg": {
        "image": "Pic_3.jpg",            # group photo (the un-padded original)
        "size": CENTER_SIZE,
        "zoom": 1.0,
        "focus": (0.5, 0.5),
        "bias": 0.5,
        "brightness": 1.0,
    },
    "hero_right.jpg": {
        "image": "qmmm_3.png",           # electrified interface
        "size": SIDE_SIZE,
        # Zoom tuned for the narrow panel: enough that the atoms read as objects,
        # not so much that a couple of spheres fill the frame.
        "zoom": 1.55,
        "focus": (0.775, 0.50),
        "bias": 0.5,
        "brightness": 1.02,
    },
}


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
    a too-wide image survives: 0 the left edge, 1 the right."""
    tw, th = size
    scale = max(tw / im.width, th / im.height)
    im = im.resize((max(tw, round(im.width * scale)),
                    max(th, round(im.height * scale))), Image.LANCZOS)
    left = int(round((im.width - tw) * min(max(bias, 0.0), 1.0)))
    top = (im.height - th) // 2
    return im.crop((left, top, left + tw, top + th))


def main() -> int:
    rc = 0
    for out_name, cfg in PANELS.items():
        src = os.path.join(HEADERS, cfg["image"])
        if not os.path.exists(src):
            print(f"!! missing {src}", file=sys.stderr)
            rc = 1
            continue
        im = Image.open(src).convert("RGB")
        im = zoom_in(im, cfg["zoom"], cfg["focus"])
        im = cover(im, cfg["size"], cfg["bias"])
        if cfg.get("brightness", 1.0) != 1.0:
            im = ImageEnhance.Brightness(im).enhance(cfg["brightness"])
        dest = os.path.join(HEADERS, out_name)
        im.save(dest, "JPEG", quality=QUALITY, optimize=True, progressive=True)
        print(f"  {out_name:<18} {im.size[0]}x{im.size[1]}  "
              f"{os.path.getsize(dest) // 1024} KB   <- {cfg['image']}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
