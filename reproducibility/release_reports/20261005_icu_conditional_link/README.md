# 条件性 ICU 容量联系：本轮整合与核查

## 完成状态

正式工程已更新并完整编译：正文 **52 页**，补充材料 **3 页**；正文打印 **21 条参考文献**。受控活动版本已从 `20261005_sec7_v2_refinement` 切换为 `20261005_icu_conditional_link`。

本轮只新增社区感染阈值到**平均 ICU 需求**的条件性充分联系。没有重新执行 A–D，没有拟合临床参数，没有新增 ICU 仓室或容量驱动算例，没有提交或推送 Git，也未使用 Nature 技能。

## 基准、修改及保护

- 基准是当前本地主稿及活动稿源，不是 Git HEAD 或候选整稿。Git 基准 `894fd49c99cc52fbaf8e2992c08457ff456c4749` 只用于标识；已有未提交改动原样保留。
- `before/` 保存 12 份修改前文件；完整路径、大小和 SHA 见 [baseline_manifest.json](baseline_manifest.json)。并行入口修改与备份复制曾发生时序交叠，仅对两份备份逆向去除本轮接口补丁恢复基准 SHA，未回滚工作稿或既有改动，详情已记入清单。
- 按来源包八个唯一锚点替换，并实施四项批准订正：`D0` 覆盖初始时刻以前全部已感染者的未来需求、固定本病容量与一次扣减、规模不变性段落的西安比例参考指引、引言的未经临床校准声明。
- 保留全时段 `c<=c0`、`I<=eta`、共同非负平均需求核及其积分 `pL`、共同初始未来需求上界等前提。容量条件只给出平均需求不超容量的充分联系，不是必要条件、随机安全保证或满载条件。
- `theta=0.002`、`rho_ICU` 比例参考、`I+Iq` 指标的原数值不变，且三者均未被重新解释为实测床位占用。容量选阈值不进入优化器。
- 原 91 个 `equation`、7 个 `align`、27 段证明、196 个标签及顺序、24 幅图、5 张正文表和 3 张补充表保持。补充材料 TEX 按字节不变；第7节 v2、第9节、能力补充及审计分流保留。
- 文献库保留全部原 21 条，只新增 `Baas2021Occupancy`，总条目 22；其中正文引用并打印 21 条。DOI 去重及旧引用保留核查通过。Baas仅支持流入—停留—占用建模思路，不被署为本文不等式来源。
- 根 `AGENTS.md` 仅修改一条现行阈值说明；历史记录没有重写。

原始输入、来源包、冻结包、两轮旧科学输出、历史验收及 24 幅正式图等共 **365 个保护文件**，正式发布后再次按原 SHA 核查通过。逐文件清单在 [review/revision.json](review/revision.json)。

## 本轮实际执行的检查

| 检查 | 实际结果与范围 |
|---|---|
| 文案与接口单测 | `reproducibility/tests` 共 94 项通过，见 [tests.log](review/tests.log)。覆盖锚点缺失/重复、源包改变、文献缺失/摘要不符/重复DOI/旧引用遗漏、保护内容改变、旧科学身份重包装、页面记录缺失或错绑定等拒绝路径。 |
| 旧科学发布守卫 | 只读身份正例 170 项及错误PDF摘要、失败双跑、错误数值发布摘要负例通过；不改旧结果或守卫门槛。见 [publication_guard_tests.json](review/publication_guard_tests.json)。 |
| 完整文案回归 | 两个隔离目录均使用同一指定旧验收输出生成文案，全文与批准候选一致；不是两次新科学运行。见 [verification.json](review/verification.json)。 |
| 隔离完整编译 | 同一副本中补充材料 XeLaTeX 两遍，正文 XeLaTeX → Biber → XeLaTeX → XeLaTeX，52+3 页，引用与文献正常。 |
| 页面实际查看 | 全部正文52页和补充3页概览；正文21张修改/相邻/参考文献页及补充全部3页独立页图细看。另有独立代理细看正文5、33、45、46、51、52页。见 [manual_review.json](review/manual_review.json)。 |
| 正式发布 | 运行 `latex/build_paper.ps1`，再比较正式稿与已审阅候选稿的全部55页；文本及120 dpi逐像素一致。比较通过且保护文件再次核查后才批准指针切换。见 [publication.json](review/publication.json)。 |

日志无未定义引用、缺字、Overfull 或 Biber 警告。保留原第9节段落 `lines 1915--1916` 的 Underfull hbox（badness 2376）；实际页面正常，不为消除该非阻断警告改动受保护文本。新增无编号注记及公式完整落在正文第5页；第33页末句自然续页。原作者 `XXX` 占位符及旧浮动页留白不属于本轮修改。

**中止记录：**曾误启动含小型数值积分的旧求解器单测组，发现后使用 Ctrl-C 中止，退出码1。该组未完成，不计为通过，不充当A–D验收；没有覆盖或发布科学输出。所有旧输出SHA随后核查不变。94项通过记录来自独立的文案/接口测试目录，不包含被中止组。

## 科学证据继承与发布入口

科学结果继承自 `runs/20261005_sec7_v2_refinement/run_1`、`run_2`，绑定原 `accepted_runs.json`、重复性记录、原发布与汇集清单及完整精度文件，不将其修改为新版本运行。旧报告、旧受控稿源和原始验收文件没有覆盖。本轮发布记录明确 `scientific_calculation_reexecuted=false`，没有新建冒充科学复算的选择清单。

新增 [document_revision.py](../../document_revision.py) 分为 `stage`、`verify`、`publish`；它显式校验未激活稿源及manifest SHA，在真实页面记录存在后受控发布。`paper_sync.py` 默认仍读取活动指针，没有冻结旧稿回退。版本支持可选文献库快照，隔离编译支持显式 `bibliography_path`，旧默认接口兼容。

本轮已执行的三个命令如下；`stage` 和 `publish` 对已有版本、目录或回执会拒绝覆盖，**不要为重复执行删除历史记录或指针**。

```powershell
& reproducibility\.venv\Scripts\python.exe -B reproducibility/document_revision.py --mode stage --output reproducibility/release_reports/20261005_icu_conditional_link/review --science-source reproducibility/runs/20261005_sec7_v2_refinement
& reproducibility\.venv\Scripts\python.exe -B reproducibility/document_revision.py --mode verify --output reproducibility/release_reports/20261005_icu_conditional_link/review
& reproducibility\.venv\Scripts\python.exe -B reproducibility/document_revision.py --mode publish --output reproducibility/release_reports/20261005_icu_conditional_link/review
```

本轮没有运行生产绘图器；24幅正式图全部直接继承原SHA。新manifest保留以后的完整科学复跑所需 `generated_figure_labels` 配置，但本轮明确 `all_figure_assets_inherited=true`，它不是本轮重画声明。通用单测的隔离测试图件也不是正式图或新科学结果。

## 交付与后续

- 正式源码与PDF仍位于 `latex/`。新受控主稿、原样补充稿与新文献库位于 `manuscript_versions/20261005_icu_conditional_link/`。
- 八块主稿差异见 [manuscript.diff](review/manuscript.diff)；相对本轮工作稿备份的入口、文献、AGENTS及指针差异见 [implementation.diff](implementation.diff)。新增纯文案模块和测试位于 `reproducibility/icu_revision_text.py`、`document_revision.py`、`tests/`。
- 新manifest SHA 为 `acb3631674ccbf9cf1227725076630399d842f8f0fcbfea16eb849a0ab7217c3`。旧指针备份及批准回执的精确路径见 `review/publication.json` 的 `version_activation`；旧指针未删除。
- 最终源码/PDF SHA、验收索引及范围见 [final_state.json](final_state.json)。候选和正式PDF元数据SHA不同，但全部页面文本及像素一致，未将其视作科学差异。
- 本轮5份活动入口/文案模块及4份相关测试原样保存于 `implementation_source/`，当前源码、归档副本和验收记录SHA在最终清单中绑定；没有修改历史源码收集记录。

临床需求核与初始未来需求校准、容量驱动的新阈值算例，以及既有比较相图标记绑定、连续人口允许区间核查，均未执行。它们继续列为后续工作，不在本轮局部整合的完成结论内。
