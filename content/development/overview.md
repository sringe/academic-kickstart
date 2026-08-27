+++
# Software overview — the same widget as the research subgroups
# (layouts/partials/widgets/subgroups.html).
widget = "subgroups"
headless = true
active = true
weight = 10        # above the portfolio listing

title = "Software"
subtitle = "Open packages we build and maintain, from the electronic structure of a surface through to a full electrolyte cell."

[[group]]
  title = "CatmapInterface.jl"
  color = "#4a648c"
  image = "software/catmapinterface.png"
  summary = "Rate constants for a microkinetic model, from a CatMAP specification."
  description = "Reads a CatMAP microkinetic specification and produces the rate constants a simulation needs, via transition-state theory. It is one layer of a Julia stack: Catalyst.jl expresses the reaction networks, and LiquidElectrolytes.jl solves the coupled electrolyte transport."
  topics = [
    "Activation energies from explicit transition states, BEP scaling or a Butler–Volmer form",
    "Free energies of formation with thermodynamic and surface-charge corrections",
    "Computational hydrogen electrode and adsorbate interactions",
    "Feeds Catalyst.jl and LiquidElectrolytes.jl",
  ]

  [[group.links]]
    name = "CatmapInterface.jl"
    url = "/software/catmapinterface/"
    primary = true

[[group]]
  title = "CatINT"
  color = "#3f9184"
  image = "software/catint.png"
  summary = "Couples microkinetics to mass transport for porous and gas-diffusion electrodes."
  description = "Modern electrode designs — porous materials, gas diffusion layers, solid electrolyte membranes — need kinetics and mass transport treated on an equal footing. CatINT provides the interface between the two, coupling CatMAP's mean-field rate equations to COMSOL's transport equations."
  topics = [
    "Mean-field microkinetics via CatMAP",
    "Diffusion, migration and convection via COMSOL",
    "Porous and gas-diffusion electrode geometries",
    "Open source and under active development",
  ]

  [[group.links]]
    name = "CatINT"
    url = "/software/catint/"
    primary = true

[[group]]
  title = "MPBE solver in FHI-aims"
  color = "#b07a5c"
  image = "software/mpbe.png"
  summary = "Implicit solvation with salt, inside an all-electron DFT code."
  description = "A (size-modified) Poisson–Boltzmann implicit solvation module for the all-electron DFT package FHI-aims, so that the electrolyte — including the presence of salt — enters the electronic-structure calculation itself."
  topics = [
    "Size-modified Poisson–Boltzmann electrolyte model",
    "Implicit solvation for all-electron DFT",
    "Ion size and salt concentration effects",
    "Transferable ionic parameters",
  ]

  [[group.links]]
    name = "MPBE module"
    url = "/software/mpbe/"
    primary = true
+++
