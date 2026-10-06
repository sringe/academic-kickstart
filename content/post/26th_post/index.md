---
# Documentation: https://sourcethemes.com/academic/docs/managing-content/

title: "Our new paper is out in Electrochimica Acta! Congratulations to Sumin Choi!"
subtitle: "Our new work on a multi-scale modeling framework for electrocatalysis - an example of how mathematicians and chemists can together tackle complex problems in electrochemistry (https://lnkd.in/g3pVF9vc). In 2019, during my Postdoc, I was working on a multi-scale model for electrochemical CO<sub>2</sub> reduction (CO<sub>2</sub>RR) on Au and figured out that the interplay of electric double layer effects and mass-transport limitations is critical, and a pain for numerical solution at the same time (https://lnkd.in/gpYjjB2i). I spent weeks trying to converge the finite element solution to the differential equations by carefully ramping up the non-linearities, eventually having to give up the solution at too high overpotentials. In 2023 I then met Jürgen Fuhrmann from WIAS in Germany in the Netherlands. He had worked in parallel on developing a code for electric double layer transport based on the Voronoi Finite Volume Method (VoronoiFVM.jl). We immediately started working together on implementing my CO2RR@Au kinetic model into his code, guided by his student Steffen Maaß, realizing quickly that this method is numerically significantly more robust. This fueled our collaboration, going on until today, with the main result so far being the CatMapInterface.jl, a Julia package replication of the famous CatMAP Python package of the Nørskov group, which can be used to set up the differential equations for complex reaction kinetics. We coupled this with advanced electric double layer transport models and solved the resulting equations monolithically using the VoronoiFVM.jl framework. As a result, we are now able to obtain stable numerical results for complex electrocatalytic systems on both the kinetics and transport sides, not only for steady-state, but also for time-dependent experiments. The first outcome is this publication, in which my student Sumin Choi could showcase the excellent numerical performance as well as reveal new insights into the Cyclic Voltammetry response of CO<sub>2</sub>RR@Au.I really recommend everyone working in multi-scale simulations to check out this work and give the Julia packages we developed a try. I must admit that this package is significantly more robust than what I developed during my Postdoc. But this is how a collaboration works: everyone contributes what they are best at, and this makes me look forward to the years to come!"

summary: ""
authors: [sumin-choi]
tags: []
categories: []
date: 2026-09-24
lastmod: 
featured: false
draft: false


# Featured image
# To use, add an image named `featured.jpg/png` to your page's folder.
# Focal points: Smart, Center, TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight.
image:
  caption: ""
  focal_point: ""
  preview_only: false

# Projects (optional).
#   Associate this post with one or more of your projects.
#   Simply enter your project's folder or file name without extension.
#   E.g. `projects = ["internal-project"]` references `content/project/deep-learning/index.md`.
#   Otherwise, set `projects = []`.
projects: []
---

