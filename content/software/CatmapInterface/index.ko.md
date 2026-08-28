---
# 한국어 / Korean translation of index.md in this folder.
#
# Only title, summary, projecttext and the two image captions are
# translated. Author lists, relatedpublications, relatedfunds, image
# names and URLs must stay identical to the English file. Run
#     python3 scripts/sync_korean.py
# after editing the English to see what here has gone stale.
# Documentation: https://sourcethemes.com/academic/docs/managing-content/

title: "CatmapInterface.jl"
summary: "CatMAP 미시반응속도 명세를 속도 상수로 바꾸어 주는 Julia 패키지로, 반응 속도론과 물질 전달을 결합한 스택의 한 부분입니다."

authors: [admin]
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

projecttext: "CatmapInterface.jl은 CatMAP 미시반응속도 명세를 읽어, 전이 상태 이론을 이용해 시뮬레이션에 필요한 속도 상수로 변환합니다. 활성화 에너지는 명시적인 전이 상태, BEP 스케일링 관계, 또는 기준 전위에 대한 Butler-Volmer 형태 가운데 하나에서 얻으며, 생성 자유 에너지는 열역학 보정, 표면 전하 보정, 계산 수소 전극, 흡착종 간 상호작용을 조합하여 구성합니다.<br> <br> 이 패키지는 Julia 스택의 한 층입니다. Catalyst.jl이 반응 네트워크를 기술하고 — 전위에 의존하는 속도를 갖는 전기화학적 고체–액체 계면에 대해 한 번, 전위에 무관한 속도를 갖는 벌크 완충 평형에 대해 한 번 — LiquidElectrolytes.jl이 그로부터 얻어지는 일반화된 Poisson-Nernst-Planck 문제를 보로노이 유한체적 격자 위에서 풉니다. 에너지는 암시적 용매화와 진동 주파수를 포함한 슬랩 구조의 전자 구조 계산에서 가져옵니다.<br> <br> 이 페이지는 새로 작성된 것입니다. 설명을 확인해 주시고 저장소와 문서 링크를 추가해 주세요. "
projectimage: "catmap-scheme.png"
projectimagecaption: "미시반응속도론과 물질 전달을 결합한 Julia 스택입니다. CatmapInterface.jl이 CatMAP 명세로부터 속도 상수를 제공하고, Catalyst.jl이 반응 네트워크를 기술하며, LiquidElectrolytes.jl이 전해질 전달 문제를 풉니다."
projectimagecaptionshort: "스택에서 CatmapInterface.jl이 놓이는 자리."

---
