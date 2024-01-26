---
# Documentation: https://sourcethemes.com/academic/docs/managing-content/

title: "(Size-modified) Poisson-Boltzmann implicit solvation module in FHI-aims -- (S)MPBE"
summary: "Module in the all-electron DFT package FHI-aims for implicit solvent simulations including the presence of salt."

authors: [admin]
tags: []
categories: []
date: 2020-05-20T10:52:49+09:00
relatedpublications: [ringe-2016-ti,ringe-2017-dm,hille-2019-fn,ringe-2021-xd,ringe-2022-xd]

# Optional external URL for project (replaces project detail page).
external_link: ""

# Featured image
# To use, add an image named `featured.jpg/png` to your page's folder.
# Focal points: Smart, Center, TopLeft, Top, TopRight, Left, Right, BottomLeft, Bottom, BottomRight.
image:
  caption: "This is the picture"
  focal_point: ""
  preview_only: true

# Custom links (optional).
#   Uncomment and edit lines below to show custom links.
# links:
# - name: Follow
#   url: https://twitter.com
#   icon_pack: fab
#   icon: twitter

url_code: ""
url_pdf: ""
url_slides: ""
url_video: ""


# Slides (optional).
#   Associate this project with Markdown slides.
#   Simply enter your slide deck's filename without extension.
#   E.g. `slides = "example-slides"` references `content/slides/example-slides.md`.
#   Otherwise, set `slides = ""`.
slides: ""

# projecttitle: 
projecttext: "Implicit solvation techniques have become the method of choice in many areas of research, such as biochemistry, electrochemistry or colloid chemistry. The size-modified Poisson-Boltzmann implicit solvation module in the all-electron DFT code FHI-aims enables to account for the presence of solvent and possibly ions in conventional DFT calculations. The table sums up the currently supported features. For more information, the FHI-aims user manual provides a detailed documentation. The module is implemented in the current version of FHI-aims, for any support, feel free to contact one of the members below."
projecttable: "
<center>
<table>
<thead>
<tr>
<th>Feature</th>
<th>Status</th>
</tr>
</thead>
<tbody>
<tr>
<td>Solvent models</td>
<td>SCCS implicit solvent + size-modified and linearized Poisson-Boltzmann for salt description</td>
</tr>
<tr>
<td>Available solvent parameters</td>
<td>water, almost all organic solvents</td>
</tr>
<tr>
<td>Available salt parameters</td>
<td>monovalent ions in water</td>
</tr>
<tr>
<td>Forces (for geometry relaxation/MD)</td>
<td><p>&#10004;</p></td>
</tr>
<tr>
<td>Periodic systems</td>
<td><p>&#10008; (in work)</p></td>
</tr>
</tbody>
</table>
</center>"

projectimage: "cover.png"
projectimagecaption: "Electric field screening by solvent fluctuations is accounted for by including an isotropic dielectric background in the DFT calculation. Further the presence of salt can be included by means of a statistical modified Boltzmann distribution which allows for the simulation of possibly charged quantum systems in electrolytic environments"
projectimagecaptionshort: "Scheme depicting the implicit solvation model in FHI-aims."

---
