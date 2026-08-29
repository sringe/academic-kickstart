+++
# Research subgroups (layouts/partials/widgets/subgroups.html).
# The panel images are cut from the group's overview figure by
# scripts/make_research_panels.py, then cropped to the circle alone, at one
# diameter and centred, by scripts/make_subgroup_circles.py -- re-run both if
# the figure changes. The full annotated panels are the _circle-less names.
widget = "subgroups"
headless = true
active = true
weight = 10          # above the project portfolio (65)

title = "Research"
subtitle = "We work across three connected scales, from the electronic structure of a catalyst surface up to the behaviour of a full electrolyser."

[[group]]
  title = "Materials"
  color = "#b07a5c"
  image = "research/subgroup_materials_circle.png"
  summary = "How the catalyst works, and how it changes while it works."
  description = "Machine-learning-driven quantum chemically accurate calculations of the catalyst itself: which sites are active, how adsorbates bind, and how the surface reorganises under reaction conditions. The questions that set everything downstream are decided here — activity and selectivity descriptors, the reaction mechanism, and whether a material stays intact at operating potential."
  topics = [
    "Adsorption and reaction energetics from chemically accurate quantum chemistry",
    "Implicit solvation and the reaction environment of the double layer",
    "Transient oxidation states and sub-surface oxygen",
    "Grain boundaries and surface reconstruction",
    "High-throughput screening for activity and selectivity descriptors",
  ]
  members = ["han-seungchang", "chanjin-kim", "suyeon", "dongwonkim"]

  [[group.links]]
    name = "Materials"
    url = "/project/materials/"
    primary = true

[[group]]
  title = "Reactive solid–liquid interfaces"
  color = "#3f9184"
  image = "research/subgroup_interfaces_circle.png"
  summary = "The electrified interface where chemistry happens."
  description = "The region between catalyst and electrolyte, where the electric double layer, the local pH and the ion distribution together decide the rate. We model the interface by combining high-level quantum chemistry with multi-scale modeling techniques (many body expansion and machine learning potentials), deriving a predictive, atomistic picture of the interface and reaction processes."
  topics = [
    "Electric double layer structure and surface charging",
    "Cation and field effects on reaction kinetics",
    "Local pH, chemical reactions and buffer equilibria",
    "Ion diffusion, migration and steric repulsion",
    "Proton-coupled electron transfer",
  ]
  members = ["horbatenko-yevhen", "dianwei-hou", "juhee", "shuran-xu", "bosung", "sayeon-lee", "sahar"]

  [[group.links]]
    name = "Solvation and electrified interfaces"
    url = "/project/solvationandelectrifiedinterfaces/"
    primary = true

  [[group.links]]
    name = "MPBE solvation module"
    url = "/software/mpbe/"

[[group]]
  title = "Multi-scale modeling"
  color = "#4a648c"
  image = "research/subgroup_multiscale_circle.png"
  summary = "From a single active site to a working electrolyser."
  description = "Coupling the interface description to transport across a whole device: reactions, diffusion, migration and convection through a porous gas diffusion electrode. This is where a catalyst that looks good on paper meets the cell it has to work in, and where cell design turns out to govern which products come out."
  topics = [
    "Porous gas diffusion electrodes and multi-phase transport",
    "Poisson–Nernst–Planck and electroneutrality models",
    "Kinetics, porosity and surface roughness",
    "Digital twins of reported experimental electrolysers",
    "Product selectivity across the catalyst layer",
  ]
  members = ["adith", "byungmin-chun", "sumin-choi"]

  [[group.links]]
    name = "Multi-scale modeling"
    url = "/project/multiscalemodeling/"
    primary = true

  # The two packages this subgroup builds the models with.
  [[group.links]]
    name = "CatmapInterface.jl"
    url = "/software/catmapinterface/"

  [[group.links]]
    name = "CatINT"
    url = "/software/catint/"
+++
