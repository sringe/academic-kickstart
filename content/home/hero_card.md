+++
# Hero widget (layouts/partials/widgets/hero_card.html).
# Three separate panels: research render | group photo | research render.
# All three crops are produced by scripts/make_hero.py -- re-run it after
# changing a source image or a zoom/focus constant.
widget = "hero_card"
headless = true
active = true
weight = 1

title = "RingeLab"
subtitle = "Computational modeling of electrified interfaces — Korea University / IBS"

# Paths relative to `assets/media/`.
image = "headers/hero_center.jpg"
alt = "The RingeLab group, 2026"

image_left = "headers/hero_left.jpg"
alt_left = "Continuum solvation model of a molecule in an electrolyte"

image_right = "headers/hero_right.jpg"
alt_right = "Water at an electrified metal surface"

cta_link = "gallery/#gallery-2026_08_Group_pic"
cta_text = "More from the group"
+++
