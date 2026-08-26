+++
# Video highlights widget.
# Rendered by layouts/partials/widgets/videos.html
widget = "videos"
headless = true  # This file represents a page section.
active = true    # Activate this section? true/false
weight = 15      # Order on the page (slider is 1, posts is 1).

title = "Simulations"
subtitle = "Our work, in motion"

# Link shown under the cards.
cta_link = "/research/"
cta_text = "More on our research"

[design.background]
  color = "white"

# Each item is one card. Nothing here is compulsory except `video`.
#   video   : path under static/, e.g. "media/videos/name.mp4"
#   poster  : still shown before playback. Nothing downloads until it is clicked.
#   caption : one or two sentences.
#   link / link_text : optional "read more" target.
#   badge   : small label in the corner of the card.

[[item]]
  title = "Water at a graphene interface"
  video = "media/videos/graphene-water-interface.mp4"
  poster = "media/videos/graphene-water-interface.jpg"
  caption = "Machine-learning accelerated molecular dynamics of the graphene–water interface, showing that graphene is hydrophobic and microscopically not wetting transparent."
  badge = "Nat. Commun. 2026"
  link = "/publication/dianwei-2026/"
  link_text = "Read the paper"

[[item]]
  title = "Ion solvation"
  video = "media/videos/ion-solvation.mp4"
  poster = "media/videos/ion-solvation.jpg"
  caption = "A solvated ion pair in explicit water, used to parameterise how the electrolyte screens charge near an electrode."
  badge = "Unpublished"

[[item]]
  title = "Adsorbates on a metal surface"
  video = "media/videos/adsorbate-dynamics.mp4"
  poster = "media/videos/adsorbate-dynamics.jpg"
  caption = "Adsorbate motion across a close-packed metal surface, the elementary step behind coverage and selectivity in electrocatalysis."
  badge = "Unpublished"
+++
