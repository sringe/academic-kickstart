---
# Documentation: https://sourcethemes.com/academic/docs/managing-content/

title: "CatmapInterface.jl"
summary: "Julia package turning a CatMAP microkinetic specification into rate constants, as part of a coupled kinetics and transport stack."

authors: [admin,sumin-choi,byungmin-chun]
tags: []
categories: []
date: 2026-08-27T10:00:00+09:00
relatedpublications: []

# Optional external URL for project (replaces project detail page).
external_link: ""

# Featured image
image:
  caption: ""
  focal_point: ""
  preview_only: true

url_code: ""
url_pdf: ""
url_slides: ""
url_video: ""

slides: ""

projecttext: "CatmapInterface.jl reads a CatMAP microkinetic specification and turns it into the rate constants a simulation needs, using transition-state theory. Activation energies come either from explicit transition states, from BEP scaling relations, or from a Butler-Volmer form referenced to a chosen potential; free energies of formation are assembled from thermodynamic corrections, surface-charge corrections, the computational hydrogen electrode and adsorbate interactions.<br>
<br>
It is one layer of a Julia stack. Catalyst.jl expresses the reaction network — once for the electrified solid-liquid interface with potential-dependent rates, once for the bulk buffer equilibria with potential-independent ones — and LiquidElectrolytes.jl solves the resulting generalised Poisson-Nernst-Planck problem on a Voronoi finite-volume grid. Energies enter from electronic-structure calculations of slab configurations with implicit solvation and vibrational frequencies.<br>
<br>
This page is new: please check the description and add the repository and documentation links.
"
projectimage: "catmap-scheme.png"
projectimagecaption: "The Julia stack for coupled microkinetics and transport. CatmapInterface.jl supplies rate constants from a CatMAP specification, Catalyst.jl expresses the reaction networks, and LiquidElectrolytes.jl solves the electrolyte transport problem."
projectimagecaptionshort: "Where CatmapInterface.jl sits in the stack."

---
