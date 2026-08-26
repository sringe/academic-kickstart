#!/usr/bin/env python3
"""Build a word cloud from the group's publication titles and abstracts.

    python3 scripts/make_wordcloud.py

Reads every content/publication/*/index.md, counts the terms, and writes
static/media/wordcloud.png (transparent, 2x for retina) plus a small JSON
sidecar listing the terms it used, so the result can be sanity-checked.

Rendered with Pillow rather than emitted as SVG on purpose: the layout needs
exact text metrics to guarantee that nothing overlaps, and measuring with the
same rasteriser that draws the text is the only way to be sure. The font is
therefore only needed when regenerating, not when serving.

Tune STOPWORDS / PHRASES below and re-run; the layout is seeded, so an unchanged
corpus produces an identical image.
"""
from __future__ import annotations

import glob
import html
import json
import math
import os
import random
import re
import sys
from collections import Counter

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB_DIR = os.path.join(ROOT, "content", "publication")
OUT_PNG = os.path.join(ROOT, "static", "media", "wordcloud.png")
OUT_JSON = os.path.join(ROOT, "static", "media", "wordcloud.json")

SIZE = (1500, 620)          # logical size; rendered at 2x
SCALE = 2
MAX_WORDS = 90
MIN_COUNT = 4
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]
FONT_MIN, FONT_MAX = 15, 96
SEED = 20260827

# Blues and greys picked to sit on either a white or a dark section background.
PALETTE = ["#1f6f9c", "#328cc1", "#5aa9d6", "#0f4c68", "#7f9bab", "#134b63"]

# Words carrying no information about the science.
STOPWORDS = set("""
a an the and or but if then than that this these those there here of in on at to
for from with without within into onto by as is are was were be been being it its
we our us they their he she his her you your i me my not no nor so such both each
few more most other some any all can could may might must shall should will would
do does did done have has had having however therefore thus hence moreover further
furthermore also additionally although though while whereas because since due
between among across over under above below up down out off again once during
before after new novel present presented presents study studies work works
show shows shown showing report reports reported reveal reveals revealed
find finds found demonstrate demonstrates demonstrated observe observed
investigate investigated investigation examine examined use used using uses
approach approaches method methods result results conclusion conclusions
paper article here herein via towards toward well highly very much many
large small high low higher lower increase increases increased decrease
decreases decreased different various several respectively addition
based upon key role important significant significantly recent recently
provide provides provided enable enables enabled allow allows allowed
lead leads led obtain obtained determine determined suggest suggests
compare compared comparison consider considered including include includes
which whose whom what when where who why how one two three first second
third finally overall general generally particular particularly specific
respect regard terms order given known well-known state states
""".split())

# Multi-word terms worth keeping whole. Matched before single words and removed
# from the text so their components are not also counted.
PHRASES = [
    "co2 reduction", "electric double layer", "density functional theory",
    "molecular dynamics", "electrochemical co2 reduction", "cation effect",
    "hydrogen evolution", "oxygen reduction", "implicit solvent",
    "machine learning", "charge transfer", "electrified interface",
    "reaction energetics", "gas diffusion electrode", "single atom",
    "free energy", "electric field", "double layer", "active site",
    "electrochemical interface", "solvation free energy",
]

# Display forms for terms that should not be shown lower-cased.
# ASCII digits, not Unicode subscripts: Arial Bold has no U+2082, so "CO₂"
# rendered as a tofu box.
PRETTY = {
    "co2": "CO2", "co": "CO", "ph": "pH", "dft": "DFT", "cu": "Cu",
    "ag": "Ag", "pt": "Pt", "au": "Au", "h2": "H2", "o2": "O2",
    "c2": "C2", "c1": "C1", "nmr": "NMR", "md": "MD", "gde": "GDE",
    "co2rr": "CO2RR", "orr": "ORR", "her": "HER", "oer": "OER",
    "ni": "Ni", "sn": "Sn", "zn": "Zn", "pd": "Pd",
    "co2 reduction": "CO2 reduction",
    "electrochemical co2 reduction": "electrochemical CO2 reduction",
}


def read(path: str) -> str:
    with open(path, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def corpus() -> str:
    parts = []
    for f in sorted(glob.glob(os.path.join(PUB_DIR, "*", "index.md"))):
        txt = read(f)
        for field in ("title", "abstract"):
            # No DOTALL: these are single-line quoted scalars. With it, the
            # greedy match ran to the last quote in the file and swallowed the
            # rest of the front matter, so "doi", "volume" and "featured" came
            # out as the most frequent terms in the corpus.
            m = re.search(rf'^{field}:\s*"(.*)"\s*$', txt, re.M)
            if m:
                parts.append(m.group(1))
    s = " ".join(parts)
    s = html.unescape(s)
    # Pull subscripts into the word first, so CO<sub>2</sub> becomes "co2"
    # rather than "co" and a stray "2".
    s = re.sub(r"<su[bp]>(.*?)</su[bp]>", r"\1", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\\[a-zA-Z]+", " ", s)
    return s.lower()


def count_terms(text: str) -> Counter:
    counts: Counter = Counter()

    # Phrases first, then blank them out so their words are not double counted.
    for phrase in sorted(PHRASES, key=len, reverse=True):
        pat = re.compile(r"\b" + re.escape(phrase).replace(r"\ ", r"\s+") + r"\b")
        n = len(pat.findall(text))
        if n:
            counts[phrase] += n
            text = pat.sub(" ", text)

    for w in re.findall(r"[a-z][a-z0-9\-]{1,}", text):
        w = w.strip("-")
        if len(w) < 2 or w in STOPWORDS:
            continue
        if re.fullmatch(r"\d+", w):
            continue
        # crude plural fold, so "electrodes" and "electrode" are one term
        if w.endswith("ies") and len(w) > 4:
            w = w[:-3] + "y"
        elif w.endswith("ses") and len(w) > 4:
            w = w[:-2]
        elif w.endswith("s") and not w.endswith("ss") and len(w) > 3:
            w = w[:-1]
        if w in STOPWORDS:
            continue
        counts[w] += 1
    return counts


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:      # noqa: BLE001
                continue
    raise SystemExit("no usable TrueType font found; add one to FONT_CANDIDATES")


def layout(terms: list[tuple[str, int]], size: tuple[int, int]):
    """Greedy spiral placement. Returns [(text, x, y, font, colour)]."""
    W, H = size
    rng = random.Random(SEED)
    placed: list[tuple[int, int, int, int]] = []
    out = []
    hi = terms[0][1]
    lo = terms[-1][1]

    def collides(box):
        x0, y0, x1, y1 = box
        if x0 < 4 or y0 < 4 or x1 > W - 4 or y1 > H - 4:
            return True
        for a0, b0, a1, b1 in placed:
            if x0 < a1 and a0 < x1 and y0 < b1 and b0 < y1:
                return True
        return False

    for i, (term, n) in enumerate(terms):
        # sqrt keeps the biggest term from dwarfing everything else
        t = 0.0 if hi == lo else (math.sqrt(n) - math.sqrt(lo)) / (math.sqrt(hi) - math.sqrt(lo))
        fs = int(round(FONT_MIN + t * (FONT_MAX - FONT_MIN)))
        font = load_font(fs)
        label = PRETTY.get(term, term)
        bbox = font.getbbox(label)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # spiral out from the middle until it fits
        cx, cy = W / 2, H / 2
        step, angle, placed_ok = 0.0, rng.uniform(0, 2 * math.pi), False
        while step < max(W, H):
            r = step
            x = int(cx + r * math.cos(angle) * 1.35 - tw / 2)
            y = int(cy + r * math.sin(angle) * 0.62 - th / 2)
            box = (x - 3, y - 3, x + tw + 3, y + th + 3)
            if not collides(box):
                placed.append(box)
                out.append((label, x - bbox[0], y - bbox[1], font,
                            PALETTE[i % len(PALETTE)]))
                placed_ok = True
                break
            angle += 0.35
            step += 1.1
        if not placed_ok:
            continue
    return out


def main() -> int:
    text = corpus()
    if not text.strip():
        print("!! no publication text found", file=sys.stderr)
        return 1

    counts = count_terms(text)
    terms = [(w, n) for w, n in counts.most_common() if n >= MIN_COUNT][:MAX_WORDS]
    if not terms:
        print("!! nothing above MIN_COUNT", file=sys.stderr)
        return 1

    items = layout(terms, SIZE)

    img = Image.new("RGBA", (SIZE[0] * SCALE, SIZE[1] * SCALE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for label, x, y, font, colour in items:
        big = ImageFont.truetype(font.path, font.size * SCALE)
        draw.text((x * SCALE, y * SCALE), label, font=big, fill=colour)

    os.makedirs(os.path.dirname(OUT_PNG), exist_ok=True)
    img.save(OUT_PNG, optimize=True)
    with open(OUT_JSON, "w", encoding="utf-8") as fh:
        json.dump({"generated_from": "content/publication/*/index.md",
                   "terms": [{"term": PRETTY.get(w, w), "count": n} for w, n in terms]},
                  fh, indent=1, ensure_ascii=False)

    print(f"wrote {os.path.relpath(OUT_PNG, ROOT)}  "
          f"{img.size[0]}x{img.size[1]}  {os.path.getsize(OUT_PNG)//1024} KB")
    print(f"  terms placed: {len(items)} of {len(terms)}")
    print("  top 12: " + ", ".join(f"{PRETTY.get(w, w)}({n})" for w, n in terms[:12]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
