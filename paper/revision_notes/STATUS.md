# 当前修订状态

更新时间：2026-10-06。

## 当前任务

- 阶段0：**按作者报告已完成，接收既有成果**。复用 `00_baseline.md`、`00_check.md`；不重新清理、覆盖baseline、恢复旧管线、打标签或切换分支。
- 阶段1／任务1：**决定草案已形成，待作者确认／验收**。论文尚未修改。
- 本轮起点分支：`main`。
- 本轮起点提交：`4691f5c5c0474065168da3a9eba7e77ccfa92a7c`。
- 本轮交付：`paper/revision_notes/01_diagnosis.md`、`01_decisions.md`、`STATUS.md`，仅本地说明提交，不push。当前完成提交号从Git及回复读取，不回填自身hash。

## 批准决定与当前范围

**D-XIAN-LINEAR：作者已决定；deferred / non-blocking。** 西安线性成本反转数值暂不研究、追溯、补算或验证，不新增反转断言；仅作者另行明确授权后恢复。保留既有 `J_c,J_q` 定义、二次成本主线、两组四策略比较及西安外部参照，不把此项作为后续写作前置条件。

项目既定目标沿用根规则：Bulletin of Mathematical Biology类英文期刊；先中文定稿，再另行授权英文阶段。本轮未将其他学术建议标成作者已批准。

| 草案编号 | 当前状态 |
|---|---|
| D-01 八章目录与文件组织 | 待批准 |
| D-02 旧内容、结果与证明迁移 | 待批准 |
| D-03 全部图表及保护安排 | 待批准 |
| D-04 术语与已有成本推广组织 | 待批准 |
| D-05 冗余删除及未完成事项处理 | 待批准 |
| D-06 最小规则补丁P-01—P-09 | 待批准，未应用 |

批准可细分，未明确批准的子项保持待确认。完整内容和原始定位见 `01_decisions.md`；补丁、检查边界及真正依赖见 `01_diagnosis.md`。

## 当前正式文件与检查

- 主文：`paper/flatten_curve_analysis_cn.tex`及同名PDF。
- 补充：`paper/flatten_curve_supplement_cn.tex`及同名PDF。
- Windows构建入口：`paper/build.ps1`，先补充后主文，各XeLaTeX → Biber → XeLaTeX → XeLaTeX；Linux入口 `paper/build.sh`。
- 阶段0构建证据复用：主文51页、补充5页，未定义项0、重复定义0、超过10pt的Overfull hbox 0；标签及数字比较见 `00_check.md`。
- 本轮实际确认：两份正式TeX与baseline SHA256一致；PDF页数及缩略阅读，保护图所在主文第8、26、27、28页定位；结果和图表去向清单核对。
- 本轮未重新编译、未运行研究计算、未重绘或修改PDF、未做全仓审计。说明检查不等于科学内容验收。

保护原图2/8/9/10的实际label分别为 `fig:scenario1:single-sim`、`fig:scenario1_summary_eta`、`fig:joint:compare`、`fig:joint:capacity`。图8不参与合并。图10有效宏 `jointcapacitypostexitdays` 仍保留。

## 未完成事项及下一任务

E-POP（人口连续允许区间）、E-WEIGHT（连续权重转折）、E-MULTIPLIER（点间时长匹配）、E-INTERSECTION（一般交点唯一性）的处理建议待批准；不新增计算、不认证一般结论，只影响依赖它们的表述。它们不与D-XIAN-LINEAR混同，也不阻塞独立章节。

下一步先由作者验收并点名批准D编号；“1确认”只登记决定、应用获批最小规则补丁，不改论文。**下一执行任务建议2a（可由作者明确跳过）**，须另行授权；2a只拆文件，2b才做结构迁移。

本轮到阶段1停止。未进入阶段2，未开始全文润色。开始时已有其他未跟踪材料保留并排除本轮提交。
