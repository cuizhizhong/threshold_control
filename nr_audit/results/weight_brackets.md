# NR-3 N3：权重转折的复核与加密

目标括区宽度 < 0.001；类别 A、A'、B、C 见 audit_weights.py 说明。

## base

原网格类别：`AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBCCCCCCCCCCCCC`

与原分类不同的网格点：0 个

| 表 S5 | 网格点 | 原类别 | 本模块类别 |
|---|---|---|---|
| 3.13–3.24（A→B） | 3.130902–3.236316 | AB | A B |
| 13.0–13.44（B→C） | 13.003831–13.441655 | BC | B C |

| 网格区间 | 网格类别 | 加密括区 | 状态 | N_z=8001、16001 复核 | 括区端点的跳变 |
|---|---|---|---|---|---|
| 3.130902–3.236316 | A→B | [3.135441, 3.136090]（A→A'） | resolved | True | — |
| 3.130902–3.236316 | A→B | [3.204988, 3.205651]（A'→B） | resolved | True | lo：int→int 于 z = 2.265357，Δx = 0.2095；hi：hi→int 于 z = 2.265419，Δx = 0.2100 |
| 13.003831–13.441655 | B→C | [13.101081, 13.101759]（B→C） | resolved | True | lo：hi→int 于 z = 4.043875，Δx = 0.7137 |

## xian

原网格类别：`AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC`

与原分类不同的网格点：2 个：r = 2.5667（原 A，本模块 A'），r = 2.6532（原 A，本模块 A'）

| 表 S5 | 网格点 | 原类别 | 本模块类别 |
|---|---|---|---|
| 2.65–2.74（A→B） | 2.653153–2.742482 | AB | A' B |
| 7.41–7.66（B→C） | 7.406054–7.655407 | BC | B C |

| 网格区间 | 网格类别 | 加密括区 | 状态 | N_z=8001、16001 复核 | 括区端点的跳变 |
|---|---|---|---|---|---|
| 2.483130–2.566734 | A→A' | [2.547681, 2.548208]（A→A'） | resolved | True | hi：int→int 于 z = 2.506166，Δx = 0.0199 |
| 2.653153–2.742482 | A'→B | [2.708636, 2.709197]（A'→B） | resolved | True | lo：int→int 于 z = 2.548168，Δx = 0.3538；hi：hi→int 于 z = 2.548313，Δx = 0.3542 |
| 7.406054–7.655407 | B→C | [7.452952, 7.453723]（B→C） | resolved | True | lo：hi→int 于 z = 4.377653，Δx = 0.7360 |

