+++
# Hero widget (layouts/partials/widgets/hero_card.html).
# Group photo, with a research image rotating in the panel beside it.
# All crops are produced by scripts/make_hero.py -- re-run it after changing a
# source image or a zoom/crop constant, and after adding or removing a slide.
widget = "hero_card"
headless = true
active = true
weight = 1

title = "RingeLab"
subtitle = "Multi-scale modeling for next-generation energy systems — Korea University"

# Paths relative to `assets/media/`.
image = "headers/hero_center.jpg"
alt = "The RingeLab group, 2026"

cta_link = "gallery/#gallery-2026_08_Group_pic"
cta_text = "More from the group"

# Milliseconds between slides.
slide_interval = 6000

[[slides]]
  image = "headers/hero_side_1.jpg"
  alt = "Continuum solvation model of a molecule in an electrolyte"

[[slides]]
  image = "headers/hero_side_2.jpg"
  alt = "Water at an electrified metal surface"

[[slides]]
  image = "headers/hero_side_3.jpg"
  alt = "Electrochemical CO2 reduction in a gas diffusion electrolyser"
+++
