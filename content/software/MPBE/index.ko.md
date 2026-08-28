---
# 한국어 / Korean translation of index.md in this folder.
#
# Only title, summary, projecttext and the two image captions are
# translated. Author lists, relatedpublications, relatedfunds, image
# names and URLs must stay identical to the English file. Run
#     python3 scripts/sync_korean.py
# after editing the English to see what here has gone stale.
# Documentation: https://sourcethemes.com/academic/docs/managing-content/

title: "FHI-aims의 (크기 보정) Poisson-Boltzmann 암시적 용매화 모듈 — (S)MPBE"
summary: "염의 존재를 포함한 암시적 용매 시뮬레이션을 위한, 전 전자 DFT 패키지 FHI-aims의 모듈입니다."

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
projecttext: "암시적 용매화 기법은 생화학, 전기화학, 콜로이드 화학 등 여러 연구 분야에서 표준적인 방법으로 자리 잡았습니다. 전 전자 DFT 코드인 FHI-aims의 크기 보정 Poisson-Boltzmann 암시적 용매화 모듈을 사용하면 일반적인 DFT 계산에서 용매와, 필요한 경우 이온의 존재까지 함께 고려할 수 있습니다. 아래 표는 현재 지원되는 기능을 정리한 것입니다. 자세한 내용은 FHI-aims 사용자 설명서에 문서화되어 있습니다. 이 모듈은 현재 버전의 FHI-aims에 구현되어 있으며, 문의 사항이 있으면 아래 구성원 중 누구에게든 편하게 연락해 주세요."
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
projectimagecaption: "용매의 요동에 의한 전기장 차폐는 DFT 계산에 등방성 유전 배경을 포함시켜 기술합니다. 나아가 통계적으로 보정된 Boltzmann 분포를 이용하면 염의 존재까지 포함할 수 있어, 전해질 환경에 놓인 전하를 띤 양자계도 시뮬레이션할 수 있습니다."
projectimagecaptionshort: "FHI-aims의 암시적 용매화 모델 개략도."

---
