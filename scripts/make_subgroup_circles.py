#!/usr/bin/env python3
"""Cut each research subgroup's circle out on its own, normalised across the three.

    python3 scripts/make_subgroup_circles.py [path/to/overview.svg]

Writes assets/media/research/subgroup_{materials,interfaces,multiscale}_circle.png
-- one square per subgroup, same circle diameter, circle centred, which is what
content/research/subgroups.md points the cards at. The full annotated panels
made by make_research_panels.py are left alone beside them.

Why the circle alone
--------------------
make_research_panels.py splits the overview into one panel per subgroup and
trims each to its ink. That leaves the circles at different sizes and in
different places, because the annotations are not symmetric: the Materials
labels run off to the left of its circle, the other two to the right. Centring
the circle inside the full panel would need a canvas 1284px wide in which the
circle covers 38% of the width -- more dead space than before, not less. And at
the size a card shows, the annotation text is far too small to read anyway.

Rendered from the SVG, not from those panels
--------------------------------------------
The panels are downscaled to 1000px wide, which puts each circle at about 510px
across -- so cropping a 760px square out of one upscaled it by 1.4x and the
result was soft. This rasterises the source again at RENDER_WIDTH, where a
circle is around 1050px, and crops from that.

Finding the circle
------------------
A euclidean distance transform of the filled silhouette: for every pixel it
gives the distance to the nearest transparent pixel, so its maximum sits at the
centre of the largest inscribed circle and its value *is* that circle's radius.
Exact for a filled disc, and unlike a centroid it is not dragged off-centre by
the leader lines touching the rim -- those are far thinner than the radius. No
colour assumptions either, which matters because the multi-scale circle is
divided into coloured bands.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "media", "research")

DEFAULT_SVG = ("/Users/ringe/Dropbox/DataRinge/Inkscape_Figures/svg/"
               "research_overview_subgroups_ringelab.svg")

# Same column splits as make_research_panels.py -- keep the two in step.
PANELS = [
    ("subgroup_materials_circle.png",  0.000, 0.345),
    ("subgroup_interfaces_circle.png", 0.345, 0.725),
    ("subgroup_multiscale_circle.png", 0.725, 1.000),
]

RENDER_WIDTH = 6000   # circles land near 1050px across, so nothing is upscaled
OUT_SIZE = 900        # px square
MARGIN = 0.02         # of the radius, kept outside the rim
FEATHER = 1.5         # px of soft edge on the mask, so the rim is not aliased
ALPHA_FLOOR = 40      # below this a pixel is background


def rasterise(svg: str, dest: str) -> bool:
    exe = shutil.which("inkscape")
    if not exe:
        print("!! inkscape not found; librsvg rejects this file's xmlns:ns URI",
              file=sys.stderr)
        return False
    cmd = [exe, "--export-type=png", f"--export-filename={dest}",
           f"--export-width={RENDER_WIDTH}", svg]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    if not os.path.exists(dest):
        print("!! inkscape failed:\n" + (proc.stderr or "")[-500:], file=sys.stderr)
        return False
    return True


def find_circle(im: Image.Image) -> tuple[float, float, float]:
    """Return (cx, cy, r) of the largest inscribed circle, in pixels."""
    solid = ndimage.binary_fill_holes(np.array(im.convert("RGBA"))[..., 3] > ALPHA_FLOOR)
    dist = ndimage.distance_transform_edt(solid)
    cy, cx = np.unravel_index(int(np.argmax(dist)), dist.shape)
    return float(cx), float(cy), float(dist[cy, cx])


def mask_to_circle(im: Image.Image, r: float) -> Image.Image:
    """Clear everything outside the rim.

    The square crop catches whatever annotation happens to fall in the corners
    -- a stray "ic repulsions" here, an orphaned "m" there, and each subgroup's
    own caption under its circle, which the card title already says. Sliced
    mid-word by the crop they read as damage, so they go. The edge is feathered
    over FEATHER px because a hard threshold on a curve aliases visibly at the
    size a card renders these at.
    """
    a = np.array(im.convert("RGBA")).astype(np.float32)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.hypot(xx - (w - 1) / 2.0, yy - (h - 1) / 2.0)
    keep = np.clip((r - d) / FEATHER + 1.0, 0.0, 1.0)
    a[..., 3] *= keep
    return Image.fromarray(a.round().astype(np.uint8), "RGBA")


def main() -> int:
    svg = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SVG
    if not os.path.exists(svg):
        print(f"!! no such file: {svg}", file=sys.stderr)
        return 1

    os.makedirs(OUT_DIR, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        render = os.path.join(tmp, "overview.png")
        if not rasterise(svg, render):
            return 1
        full = Image.open(render).convert("RGBA")
        print(f"  rendered {full.width}x{full.height}")

        found = []
        for name, a, b in PANELS:
            panel = full.crop((int(full.width * a), 0, int(full.width * b), full.height))
            cx, cy, r = find_circle(panel)
            found.append((name, panel, cx, cy, r))
            print(f"  {name:<34} circle r={r:7.1f} at ({cx:7.1f},{cy:7.1f})")

        # One radius for all three -- the smallest, so no circle is enlarged
        # past its own resolution. The crop is the same number of radii across
        # in every panel, which is what makes the three outputs line up.
        r_target = min(r for *_, r in found)
        print(f"\n  common radius {r_target:.1f}px, frame {2 * (1 + MARGIN):.2f} radii wide")

        for name, panel, cx, cy, r in found:
            half = r * (1.0 + MARGIN)
            # crop() pads with transparency past the edges, so a circle close to
            # a panel boundary still comes out centred rather than shifted.
            box = (round(cx - half), round(cy - half), round(cx + half), round(cy + half))
            # Mask before the resize, so the feathered rim is downsampled with
            # the artwork rather than drawn at output resolution.
            cropped = mask_to_circle(panel.crop(box), r)
            out = cropped.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
            dest = os.path.join(OUT_DIR, name)
            out.save(dest, optimize=True)
            print(f"  {name:<34} {OUT_SIZE}x{OUT_SIZE}  "
                  f"{os.path.getsize(dest) // 1024:>4} KB  (x{OUT_SIZE / (2 * half):.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
