---
title: "Fully integrated, finite-volume-based, time-dependent multi-scale modeling of electrochemical CO<sub>2</sub> reduction"
date: 2026-09-24
publishDate: 2026-09-24
authors: [S. Maaß† , <b>S. Choi</b>†, J. Fuhrmann, <b>S. Ringe*</b>]
publication_types: ["2"]
abstract: "Electrochemical systems couple reaction kinetics and mass transport across multiple temporal and spatial scales. To address this multiscale coupling, we present an integrated Julia-based simulation framework for defining and solving complex kinetic–transport models. Specifically, CatmapInterface.jl enables the construction of mean-field reaction networks with adsorbate–adsorbate interactions and electric double layer charging-corrected electrochemical kinetics, while LiquidElectrolytes.jl enables detailed electric double layer and mass-transport models. The resulting equations are solved monolithically using the finite volume package VoronoiFVM.jl, yielding mass-conservative and numerically robust solutions under strong transport–kinetics coupling. As an example, we study CO<sub>2</sub> reduction on gold, for which steady-state simulations show consistent results with a previous finite-element-based implementation but improved numerical stability. Time-dependent cyclic-voltammetry simulations further provide an explanation for the experimentally observed double peak in CO re-oxidation during the anodic sweep as arising from hydroxide depletion and delayed buffer equilibration. The framework thus provides a powerful tool for nonequilibrium multiscale simulations of complex electrochemical systems."
featured: false
publication: "*Electrochim Acta*"
doi: "10.1016/j.electacta.2026.149932"
volume: "578"
pages: "149932"
---

