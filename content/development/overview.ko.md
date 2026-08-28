+++
# 한국어 / Korean translation of overview.md
#
# Generated once from the English file, edited by hand since. Keep the
# untranslated keys (widget, weight, image, url, colour) identical to the
# English: only prose is translated. After changing the English, run
#     python3 scripts/sync_korean.py
# to see which strings here have gone stale.
widget = "subgroups"
headless = true
active = true
weight = 10
title = "소프트웨어"
subtitle = "표면의 전자 구조에서 전해질 셀 전체에 이르기까지, 우리가 개발하고 유지·관리하는 오픈소스 패키지입니다."
[[group]]
title = "CatmapInterface.jl"
color = "#4a648c"
image = "software/catmapinterface.png"
summary = "CatMAP 명세로부터 미시반응속도 모델에 필요한 속도 상수를 계산합니다."
description = "CatMAP 미시반응속도 명세를 읽어, 전이 상태 이론을 통해 시뮬레이션에 필요한 속도 상수를 만들어 냅니다. Julia 스택의 한 층으로, Catalyst.jl이 반응 네트워크를 기술하고 LiquidElectrolytes.jl이 이와 결합된 전해질 전달을 계산합니다."
topics = [ "명시적 전이 상태, BEP 스케일링 또는 Butler–Volmer 형태에서 얻는 활성화 에너지", "열역학 보정과 표면 전하 보정을 포함한 생성 자유 에너지", "계산 수소 전극과 흡착종 간 상호작용", "Catalyst.jl과 LiquidElectrolytes.jl로 연결",]
[[group.links]]
name = "CatmapInterface.jl"
url = "/software/catmapinterface/"
primary = true


[[group]]
title = "CatINT"
color = "#3f9184"
image = "software/catint.png"
summary = "다공성 및 기체확산 전극에서 미시반응속도론과 물질 전달을 결합합니다."
description = "다공성 소재, 기체확산층, 고체 전해질 막과 같은 최신 전극 설계에서는 반응 속도론과 물질 전달을 같은 비중으로 다루어야 합니다. CatINT는 그 둘을 잇는 인터페이스로, CatMAP의 평균장 속도 방정식과 COMSOL의 전달 방정식을 결합합니다."
topics = [ "CatMAP을 통한 평균장 미시반응속도론", "COMSOL을 통한 확산, 이동 및 대류", "다공성 및 기체확산 전극 형상", "오픈소스이며 현재도 활발히 개발 중",]
[[group.links]]
name = "CatINT"
url = "/software/catint/"
primary = true


[[group]]
title = "FHI-aims의 MPBE 솔버"
color = "#b07a5c"
image = "software/mpbe.png"
summary = "전 전자 DFT 코드 내부에서 염을 포함한 암시적 용매화를 다룹니다."
description = "전 전자 DFT 패키지인 FHI-aims를 위한 (크기 보정) Poisson–Boltzmann 암시적 용매화 모듈입니다. 염의 존재를 포함한 전해질이 전자 구조 계산 자체에 반영되도록 합니다."
topics = [ "크기 보정 Poisson–Boltzmann 전해질 모델", "전 전자 DFT를 위한 암시적 용매화", "이온 크기와 염 농도 효과", "다른 계에도 옮겨 쓸 수 있는 이온 파라미터",]
[[group.links]]
name = "MPBE 모듈"
url = "/software/mpbe/"
primary = true


+++
