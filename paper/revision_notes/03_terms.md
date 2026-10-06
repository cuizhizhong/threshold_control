# 任务3：术语统一与安全清理

日期：2026-10-06。起点：`main`，`19ae43ab03944bc60bb82bcf9ff3b90ccc1d0db5`。状态：**待作者验收**。

依据实际 `AGENTS.md`、`STATUS.md`、`01_decisions.md` 的 D-04／D-05 和 `CODEX_EXECUTION.md` 的通用约定、任务3执行。2b 已由作者验收，本轮只处理文字术语及无用生成器注释。

## 实际修改

修改16份TeX：主入口 `flatten_curve_analysis_cn.tex`，`sections/01_introduction.tex`—`08_discussion.tex`，`appendices/A_proofs_sensitivity.tex`、`B_control_cost.tex`，以及 `supplement_sections/S1_baseline.tex`—`S5_contact.tex`。补充入口、模型公式、参考文献、构建入口和图源未改。

| 对象及实际锚点 | 本轮处理 |
|---|---|
| `sec:model`、`eq:s1:q-control`、`thm:joint:representation` | 首次定义保留“被有效追踪并隔离的接触者比例”，行文称“追踪隔离比例”，后文简称“隔离比例”；删除沿用“隔离率”的旧说明。控制选取表达仍称“隔离控制函数”。 |
| `eq:model:plateau-requirement`、`eq:s1:t2` | 平台期／控制期统一为“阈值控制期”，指向 `Delta t` 的控制持续时间／控制时间统一为“控制时长”。`t_1,t_2,t_end,t_inf` 的时刻身份不变；“感染持续时间”“疫情持续时间”及TDINN的干预持续时间保持各自含义。 |
| `sec:cost`、`thm:s1:tend`、`tab:joint:compare` | 定义处保留操作性“社区清零时间”，后文简称“清零时间”：社区非隔离感染者下降至1，不表示有限时间严格灭绝或可安全恢复常规。`eta>1`、下降段及隔离感染者不必归零等条件原样保留。 |
| `sec:s1`、`tab:joint:compare`、`tab:xian_summary` | 统一“仅隔离控制”“仅减少接触”“联合阈值控制”“TDINN控制”“常规控制”。第3章标题仅随术语改为“仅隔离控制的解析基准”，目录层级、位置及label不变。 |
| `thm:joint:cost-minimum`、`prop:joint:minimum-threshold`、`rem:joint:duration-constraint` | 控制／策略统一称“最小成本分配”；标量 `J_min` 仍为“最小成本”，保留类内、受限、正权重、几乎处处及固定状态等原条件，不把标量改成控制。 |
| `sec:cost`、`sec:xian`、`prop:dom:floor` | 统一“累计新增感染”，明确社区累计、隔离累计和总累计三个量，保留全部符号、积分及终点；未把现存感染、日新增、累计病例或易感者流出合并为同一量。 |
| `eq:s1:q-time-explicit`、`sec:num:methods` | 预生成后输入完整仓室方程的时间函数称“开环控制”。名义模型、退出时刻、参数、参考比例值及容量保持原意；状态参数化未改成实时反馈。 |
| `sec:discussion`、`sec:scaling` | 终点状态检查和九组拐点回代保留公式回代边界，不包装成独立ODE积分验证。“本稿”改“本文”；已有计算／检验用语逐处调整。E-POP的“仍须核查”“尚待核查”原样保留。 |

“感染平台”两处按语义改为“在同一阈值上维持恒定感染的要求”，保留整段恒定感染约束，未弱化为仅有峰值上限。`c_min`／`c_{0,min}(eta)`、`q_cap`／`q_max`、`theta`／`alpha`／`lambda` 全部保留。控制类的数学命名仍留任务4a，不提前加入新记号。

表S3（`tab:sup:eta`）末列表头加长后压缩数字列间距，PDF检查发现后仅将“总累计新增感染／（人）”分成两行；列数、数值、精度、单位和统计终点不变。

## 删除、移动及待确认

- 删除12行确认无用的生成器注释：`% BEGIN JOINT_EXTRA:comparison`、`:capacity`、`:phase`、`:duration`、`:xian`、`:conclusion` 及各自的 `% END JOINT_EXTRA:...`。现行构建和检查脚本不读取这些标记。未删除正文段落、结果、证明、数据行或图表。
- 上表列出的旧术语仅作等义替换。仍调用的宏、所有兼容label和TODO保留，包括 `jointcapacitypostexitdays` 的定义与图注调用。
- 移动清单：无。移入 `limitations_pool.md`：无。数字变动：无。未增加文献或研究计算。
- 本轮无新增数学／数值待确认项。E-POP、E-WEIGHT、E-MULTIPLIER、E-INTERSECTION保持既有有限证据和未解决说明。D-XIAN-LINEAR继续 **deferred / non-blocking**，未研究、追溯或认证。

## 图内术语差异（仅登记，未改图）

按实际24个图块及图源文字检查。下列是后续英文图任务的名称或简写候选，不表示本轮授权重绘。

| 实际label／图源（相对 `paper/figures/`） | 图内原文及后续候选 |
|---|---|
| `fig:xian:strategy-process`／`layout_v5/xian_strategy_process.pdf` | `Routine control` → `Baseline control`；本图的 `Threshold control` 可明确为 `Quarantine-only control`。 |
| `fig:dom:levers`／`layout_v5/population_threshold_levers.pdf` | `routine`／`routine band` → `baseline control`／`baseline-control band`；`clear` → `clearance time`；`dur` → `control duration`。 |
| `fig:dom:critical-cases`／`layout_v5/critical_population_cases.pdf` | `routine`、`dur` 同上。 |
| `fig:dom`／`fig_dom_combined.pdf` | `dur`、`clear` 同上；`cumulative` 可展开为 `cumulative total new infections`，仍对应总累计量。 |
| `fig:c0-panel`／`layout_v5/c0_sensitivity_panel.pdf` | `total infections by clearance` 可明确为 `cumulative total new infections at clearance`。 |
| `fig:c0-scan`／`c0_sensitivity_scan.pdf` | `tail (days)` 可展开为 `post-control decline duration (days)`，保持退出后至清零的时长。 |
| `fig:joint:compare`、`fig:joint:frontier`、`fig:joint:phase`／`joint_v2/` | `Contact reduction only`／`Quarantine only`／`quarantine only` 后续可与批准英文策略名统一；现有 `Minimum-cost allocation` 已一致。 |

未发现图内 `quarantine rate`、`platform` 或 `dynamic zero`。全部图文件的SHA256与本轮起点一致；四保护图同时与D-03记录一致。图2／4／5／6的label分别为 `fig:scenario1:single-sim`、`fig:scenario1_summary_eta`、`fig:joint:compare`、`fig:joint:capacity`。仅相应中文图注用词改变，面板、曲线、数据、图内记号、显示尺寸和图意不变。

## 本轮实际检查

- `check_tex.py` 对本轮起点临时快照与当前两入口实际运行，递归覆盖15个输入子文件；报告见 `03_check.md`。标签缺失、悬空引用、重复标签及bib缺键均0。两个原有未引用bib键未处理。
- 逐文件静态比对：17份源文件中的1733个数学片段、218个label、引用命令及宏定义保持一致，全部数字token顺序一致；28个定理类环境、27个证明、24图、8张编号表及未编号极值小表保留。检查器的数值字面量为756→756，缺0、增0；同时人工复核参数组、策略、指标、终点与单位语义，未用计数替代口径检查。
- 按 `paper/build.ps1` 实际构建两轮，均先补充后主文，各 XeLaTeX → Biber → XeLaTeX → XeLaTeX；第二轮对应表S3表头修复。最终主文36页、补充21页，未定义引用、重复标签、Overfull／Underfull及LaTeX Warning均0，Biber日志无WARN／ERROR。终端有既有Perl locale回退提示，未影响构建。
- 57页全部渲染并查看逐页总览；另外放大主文1、3、6、7、11、15、17、18、21、23、26、27、29、30、34页和补充1、6、7、8、14、16、19、20页。关键定义、开环说明、两组四策略表、外部参照表、保护图注、敏感性表及相关补充图注可读。表S3修复后第7页另以140dpi复看，数字列间距恢复；最终两轮渲染仅该页不同，其余56页像素一致。28个双向跨文档链接目标全部有效。
- 展开正文汉字数（含主文附录）：主文22358→22580，补充7431→7455；增量来自完整术语和语义澄清。保留既有浮动页留白，未执行任务5b的整体版式调整。
- Git空白检查采用允许现有CRLF的 `core.whitespace=blank-at-eol,blank-at-eof,space-before-tab,cr-at-eol`，结果通过；未为消除CRLF提示整份转换入口文件。

未执行科学计算、Linux构建、逐字全文校对或下一任务。起点未跟踪材料、执行手册及编译产物排除本地提交。完成提交号由Git及本轮回复给出，不回填自身hash。下一任务仅建议4a，须作者验收并另行点名。
