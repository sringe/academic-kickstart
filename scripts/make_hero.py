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
# Square, not tall and narrow. These renders are ~3.4:1; in a 1:2 panel any
# crop that fills the frame is a ~15% slice, i.e. an unrecognisable close-up,
# and fitting the whole figure instead leaves it tiny between stretched edges.
# A square panel shows nearly a third of the width, enough to read the object.
SIDE_SIZE = (760, 760)
# ~1.25:1, which is the shape the middle panel actually occupies once the two
# square side panels and the gaps are taken out of the row. Generating it wider
# meant the group was cropped at the sides on display.
CENTER_SIZE = (1100, 880)

PANELS = {
    "hero_left.jpg": {
        "image": "smpb_fhiaims11.png",   # continuum solvation
        "size": SIDE_SIZE,
        "zoom": 1.0,
        "focus": (0.5, 0.5),
        "bias": 0.62,          # place the square over the cavity
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
        # No zoom needed once the panel is square; `bias` slides the square over
        # the slab and the water column, which sit well right of centre.
        "zoom": 1.0,
        "focus": (0.5, 0.5),
        "bias": 0.86,
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


def fit_width(im: Image.Image, size: tuple[int, int]) -> Image.Image:
    """Show the whole figure: scale it to the panel width, centre it, and fill
    the space above and below by stretching the image's own edge rows.

    `cover` is wrong for a very wide figure in a tall panel — it crops a narrow
    vertical slice, which reads as an unrecognisable close-up however the focus
    is placed. This shows the entire object instead, and because these renders
    sit on a smooth gradient the stretched edges are invisible.
    """
    tw, th = size
    scaled = im.resize((tw, max(1, round(im.height * tw / im.width))), Image.LANCZOS)
    if scaled.height >= th:
        top = (scaled.height - th) // 2
        return scaled.crop((0, top, tw, top + th))

    canvas = Image.new("RGB", size)
    top = (th - scaled.height) // 2
    # Extend the top and bottom edge rows over the empty bands.
    canvas.paste(scaled.crop((0, 0, tw, 1)).resize((tw, top)), (0, 0))
    bottom_h = th - top - scaled.height
    if bottom_h > 0:
        canvas.paste(
            scaled.crop((0, scaled.height - 1, tw, scaled.height)).resize((tw, bottom_h)),
            (0, top + scaled.height))
    canvas.paste(scaled, (0, top))
    return canvas


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
        if cfg.get("mode") == "fit":
            im = fit_width(im, cfg["size"])
        else:
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
