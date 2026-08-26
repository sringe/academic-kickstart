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

from PIL import Image, ImageEnhance, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADERS = os.path.join(ROOT, "assets", "media", "headers")
QUALITY = 84

# Output sizes. CSS scales these with object-fit: cover, so they only need the
# right aspect ratio and enough resolution for a retina screen.
# Tall, to match the height of the centre panel. These renders are ~3.4:1, so a
# crop this shape shows only a narrow vertical band of the source -- which is
# why `bias` below is set deliberately, to put the subject of each figure in the
# middle of that band rather than at its edge.
SIDE_SIZE = (520, 880)
# ~1.25:1, which is the shape the middle panel actually occupies once the two
# square side panels and the gaps are taken out of the row. Generating it wider
# meant the group was cropped at the sides on display.
CENTER_SIZE = (1100, 880)

PANELS = {
    "hero_left.jpg": {
        "image": "smpb_fhiaims11.png",   # continuum solvation
        "size": SIDE_SIZE,
        # Fitted, not cropped: the whole cavity is wider than any panel-shaped
        # crop of this source can contain.
        "mode": "fit",
        "span": (0.33, 0.90),    # the whole cavity, with a little air around it
        "vspan": (0.03, 0.87),   # the object's full height, above its soft reflection
        "zoom": 1.0,
        "focus": (0.5, 0.5),
        "bias": 0.545,
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
        # Slight zoom and a right-shifted band, to clear the dark background
        # outside this render's white ellipse -- it showed as a grey wedge in
        # the top corner.
        "zoom": 1.15,
        "focus": (0.5, 0.5),
        "bias": 0.87,
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


def fit_blur(im: Image.Image, size: tuple[int, int],
             span: tuple[float, float],
             vspan: tuple[float, float] = (0.0, 1.0)) -> Image.Image:
    """Show a whole wide object in a tall panel.

    `cover` cannot do this: the source is only 1554px tall, so any crop with the
    panel's aspect spans barely a sixth of its width and always cuts the object.
    Here the slice between `span` (fractions of the source width) is scaled to
    the panel width and centred, and the bands above and below are filled by
    repeating that slice's own top and bottom rows.

    That is seamless for these renders because their background is a gradient
    that varies across the image but not down it. `vspan` trims the source
    vertically first: without it the bottom row falls inside the object's mirror
    reflection, which then repeats downwards as vertical streaks. Filling the bands
    with a blurred copy instead, tried first, left a visible horizontal seam
    where the blur met the sharp image.
    """
    tw, th = size
    x0, x1 = int(im.width * span[0]), int(im.width * span[1])
    y0, y1 = int(im.height * vspan[0]), int(im.height * vspan[1])
    fg = im.crop((x0, y0, x1, y1))
    fg = fg.resize((tw, max(1, round(fg.height * tw / fg.width))), Image.LANCZOS)
    if fg.height >= th:
        top = (fg.height - th) // 2
        return fg.crop((0, top, tw, top + th))

    canvas = Image.new("RGB", size)
    top = (th - fg.height) // 2
    if top > 0:
        canvas.paste(fg.crop((0, 0, tw, 1)).resize((tw, top)), (0, 0))
    bottom = th - top - fg.height
    if bottom > 0:
        # Both bands are filled from the TOP row. The bottom row still catches
        # the edge of the object's shadow, which repeated downwards as a faint
        # pale column; the background itself is the same all the way down, so
        # the clean top row is the right source for both ends.
        canvas.paste(fg.crop((0, 0, tw, 1)).resize((tw, bottom)),
                     (0, top + fg.height))
    canvas.paste(fg, (0, top))
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
            im = fit_blur(im, cfg["size"], cfg.get("span", (0.0, 1.0)),
                          cfg.get("vspan", (0.0, 1.0)))
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
