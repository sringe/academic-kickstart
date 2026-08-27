#!/usr/bin/env python3
"""Cut the research overview figure into one image per subgroup.

    python3 scripts/make_research_panels.py [path/to/overview.svg]

Writes assets/media/research/subgroup_{materials,interfaces,multiscale}.png,
which content/research/subgroups.md points at.

The source is an Illustrator export that librsvg refuses (an invalid `xmlns:ns`
URI), so it is rasterised with Inkscape. The split points were measured from the
render's ink-per-column profile rather than guessed — see PANELS.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "media", "research")

DEFAULT_SVG = ("/Users/ringe/Dropbox/DataRinge/Inkscape_Figures/svg/"
               "research_overview_subgroups_ringelab.svg")

RENDER_WIDTH = 3000          # rasterise big, then downscale each panel
PANEL_WIDTH = 1000           # output width per panel
PAD = 14                     # transparent margin kept around each panel

# Fractions of the render width, measured from the render's ink-per-column
# profile. The second split is at 0.725, not at the emptiest column (0.707):
# the interfaces cluster's "chemical reactions, diffusion, migration,
# convection" label and its leader line run on to 0.725, and splitting earlier
# cut it in half, leaving "ons," stranded on the multi-scale panel.
PANELS = [
    ("subgroup_materials.png",  0.000, 0.345),
    ("subgroup_interfaces.png", 0.345, 0.725),
    ("subgroup_multiscale.png", 0.725, 1.000),
]


def rasterise(svg: str, dest: str) -> bool:
    exe = shutil.which("inkscape")
    if not exe:
        print("!! inkscape not found; needed because librsvg rejects this file",
              file=sys.stderr)
        return False
    cmd = [exe, "--export-type=png", f"--export-filename={dest}",
           f"--export-width={RENDER_WIDTH}", svg]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    if not os.path.exists(dest):
        print("!! inkscape failed:\n" + (proc.stderr or "")[-500:], file=sys.stderr)
        return False
    return True


def trim(im: Image.Image, pad: int) -> Image.Image:
    """Crop away fully transparent margins, then add `pad` back."""
    box = im.getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    x0, y0 = max(0, x0 - pad), max(0, y0 - pad)
    x1, y1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
    return im.crop((x0, y0, x1, y1))


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
        print(f"  rendered {full.size[0]}x{full.size[1]}")

        for name, a, b in PANELS:
            x0, x1 = int(full.width * a), int(full.width * b)
            panel = trim(full.crop((x0, 0, x1, full.height)), PAD)
            if panel.width > PANEL_WIDTH:
                h = round(panel.height * PANEL_WIDTH / panel.width)
                panel = panel.resize((PANEL_WIDTH, h), Image.LANCZOS)
            dest = os.path.join(OUT_DIR, name)
            panel.save(dest, optimize=True)
            print(f"  {name:<28} {panel.size[0]}x{panel.size[1]}  "
                  f"{os.path.getsize(dest) // 1024:>4} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
