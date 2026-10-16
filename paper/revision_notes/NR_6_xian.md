# NR-6 西安参数情景与补充材料整理（2026-10-16）

- 依据：NR 计划 5.5 节与第 6 节 NR-6 提示词；R7 裁决 D-R7-3（成本框架）、D-R7-4 第 3、4 项（章名、有效人口）、D-R7-5（初值说明）（`R7_review_triage.md`）；`NR_3_numbers.md`（G-N2，第 10 节第 4 项）；`NR_claims.md` X-8、X-9、N-11 至 N-15、D-3；`AGENTS.md` N6–N8、N11。比较基准 `nr-base`。
- 范围：第 7 章；补充 S3（新增 S3.1 的拟合误差、初值诊断、人口缩放，S3.2 阈值扫描）；补充 S4 整节移出正式稿；补充 S5 与 S1 的悬空引用；补充主文件前言；第 8 章一句因 S4 移出而悬空的话；引言路线句一个词；`nr_audit/` 的数字宏与一个复核脚本。不重新拟合，不新增疾病，不算线性成本；图像文件未改。
- 检查报告：`NR_6_check.md`、`NR_6_statements.md`、`NR_6_metrics.md`。

## 1 S4 引用依赖清单与处置（先于移动建立）

| S4 内容（旧标签） | 被谁引用 | 处置 |
|---|---|---|
| 设定（`sec:dom:setup`、式 `eq:dom:ratios`）：θ、$i_{\max}^0$ 定义；$I^{\rm T}_{\rm cum}=607.96$、$I^{\rm T}_{q_{\rm cum}}=1497.67$ | 仅 S4 内部 | $i_{\max}^0$ 在 S3.1 命题前一句重新定义；两个 TDINN 累计数移到正文 7.4 节，紧接 $N_{\rm floor}$ 的代入 |
| 比较条件（`sec:dom:theory`、`app:reference-comparison`、`eq:reference-cost-threshold`、`eq:reference-duration-threshold`、`eq:dom:theta-bind`、`eq:dom:band`、`eq:dom:Nstar`、`eq:dom:Nstar-infty`） | `app:reference-comparison` 被 S1 的一句括注引用；其余仅 S4 内部 | 删除（D-R7-4：多指标比较及 $\theta_{\rm cost}$、$\theta_{\rm dur}$ 等记号）；S1 中括注“（第 S4.2 节的端点扩展据此定义）”删去，其前后句完整 |
| 附加指标（`sec:dom:extra`、`eq:dom:cumarc`、`eq:dom:clrarc`、**`prop:reference-population`**） | 命题无外部引用 | 两个等值条件式删除；**命题及证明原样移入 S3.1，标签不变**（它是固定归一化初值下 $t_{\rm end}$、累计新增感染随 $N$ 严格增加的定理类结果，支撑 7.4 节“清零时间仍含人口尺度”，不属于被删的比较；NR_claims X-8 的去留由此确定） |
| 规模的作用（`sec:scaling`） | 无外部引用 | 两段原样（数字复核见第 3 节）移入 S3.1“人口缩放情景”；D-R7-4 第 4 项所列数值：$\theta=0.002$ 六个人口、$\Delta t\approx85.07$ d、相对极差 $4.71\times10^{-8}$、$1.17\times10^{-7}$、$t_1$ 由 $11.39$ 增至 $16.90$ d；另一段 $\eta=100$ 的结果与对数因子 $2.20\to2.15$ 一并移入，作为同一情景的另一组 |
| 候选范围（`sec:dom:xian`、`tab:dom:thresholds`、`eq:dom:main-interval`、`fig:dom`、`fig:dom:levers`） | 仅 S4 内部 | 删除（图 S7、S8 的引用） |
| 轨迹与临界案例（`app:panel_eta_N`、`fig:panel_N_decomp`、`fig:dom:critical-cases`） | 仅 S4 内部 | 删除（图 S9、S10 的引用） |
| 传播概率与等值线（`app:dom:numerics`） | 仅 S4 内部 | 删除 |
| 整节（`sec:sup:population`） | 正文 7.2 表注、7.4 末段；补充主文件前言 | 正文两处已改；前言改写（第 2 节） |

结论：S4 在移出上述内容后没有独立保留内容，故移除其 `\input`。源文件未删除，`git mv` 到 `paper/revision_notes/archive/NR_6_removed/S4_population.tex`（历史也在 `nr-base`）；四个图像文件（`fig_dom_combined.pdf`、`population_threshold_levers.pdf`、`fig_panel_B_trajectory_decomposition.pdf`、`critical_population_cases.pdf`）仍在 `paper/figures/`，已无引用，未删。

## 2 改动清单

| 文件 | 位置 | 改动 | 依据 |
|---|---|---|---|
| `07_xian` | 章名、章首 | “西安案例”改“西安参数情景”（标签不变）；新增章首两句：计算在无回流模型 (2.1) 中进行，参数取自统计资料与文献，初值与 TDINN 控制函数来自观测数据的重构 | D-R7-4 第 3 项；NR 5.5 |
| `07_xian` | 7.1 节 | 补观测算子（进入 $I$、$I_q$ 的流量在日区间 $[k,k+1]$ 上的积分）、时间原点、累计数的定义与四项等权，指向补充表（拟合误差）；补初值影响的具体范围：$I_0$ 取 0.1、10 倍时 $t_1$、$t_{\rm end}$ 移动约 2.28 d，$S^*$、$\Delta t$、$J$、总累计的相对变化不超过 $4.4\times10^{-9}$，并写明是固定参数下的前向诊断；图 9 图注“实线为拟合 $I_0$ 与 TDINN 控制下的模型结果” | D-R7-5 初值说明；NR 5.5；NR-3 N2、N5 |
| `07_xian` | 7.2 节 | 节名“与 TDINN 的比较”改“TDINN 参照”；首段补“表中各列是各自任务下的模型结果，不构成同一任务的优劣排名”；删去“仅隔离控制的二次成本低于 TDINN……较低的 $J$ 因而可以与大得多的感染规模并存”一段，改为两策略感染结果与清零时间的描述；末句“按二次成本计算后者更低；累计新增感染的规模则由退出要求决定”改为“前者在易感者几乎未减少时结束，后者要求 $S$ 降到 $S_c$，累计新增感染因而有下界” | D-R7-3；O33 的同一类表述 |
| `07_xian` | 表 3 | 删 $J$ 列；题名改“三种策略的模型结果”；表注写明三种策略任务不同（TDINN 为观测窗口内的重构，仅隔离控制为阈值策略，常规控制为反事实基准）、各列是描述性结果，并给 TDINN 峰值与总累计的未取整值 152.55、2105.63；删去“补充 S4 所用的 TDINN 参照值……$J=49.39$”与 $J$ 的两句说明 | D-R7-3；NR 5.5 |
| `07_xian` | 7.3 节 | “群体免疫阈值”改“常规传播临界值”；“本模型”改“无回流模型”；40.5 年补“按每年 365 d 计”；“这些长时结果是固定参数、全市人口下的模型外推”加“无回流”与“不是对真实政策年限的预测”；末句指向 S5 时说明是 $N=2\times10^4$ 的人口缩放情景 | O30；NR 5.5；NR-3 N1 |
| `07_xian` | 7.4 节 | 改为两段加命题：第一段讲人口缩放（命题 3.12 与式 (3.25)；固定绝对阈值时 $\theta$ 随人口改变，$J$ 含 $1/\theta$、控制时长近似与 $\theta$ 成反比；以 $I=1$ 为终点的量仍含人口尺度，指向补充命题；固定归一化初值与固定绝对 $I_0$ 分句；绝对初值的数值另起一句）；第二段保留 `prop:dom:floor`、证明与数值，写明“这是参照轨迹在无回流模型中的必要条件，不是对 $N_{\rm eff}$ 的估计”；删去最后一段（补充 S4 的比较及“清零都晚于 TDINN”） | D-R7-4 第 4 项；NR 5.5 |
| `S3_xian` | 新 S3.1“初值与人口缩放” | 新增：拟合准则的重建（观测算子、时间原点、四项等权）与四项误差表 `tab:sup:fit`；既有初值对照表 `tab:sup:initial` 保留；新增六条固定人口初值诊断表 `tab:sup:ic`（宏 `\nrICtab…`）与文字；新增人口缩放情景一段与 `prop:reference-population`（自 S4 移入，证明未改）；旧 S3.1 的阈值扫描表与图并为新的 S3.2“阈值扫描”（`sec:sup:xian:threshold-scan`），`sec:sup:xian:settings` 仍在 S3.1 | D-R7-4 第 4 项；NR-3 N2、N5；G-N2 第 4 项 |
| 补充主文件 | 前言 | 移除 `\input{S4_population}`；说明段改用 `\ref` 指向各节，不再手写 S1–S6 | NR 5.5 第 5、7 步 |
| `S5_contact` | 首句 | “一个有效人口情景”改“$N=2\times10^4$ 的人口缩放情景（指向 S3.1）”；其余结果与图保留（依赖的人口假设只有这个 $N$、$\theta=0.002$ 与绝对初值，已在原文第一小节写明） | NR 5.5 第 6 步 |
| `S1_baseline` | 末段 | 删括注“（第 S4.2 节的端点扩展据此定义）” | 悬空引用 |
| `08_discussion` | 展望一段 | 删“第三，满足各项比较条件的有效人口是否构成连续区间尚未确定，补充材料中的人口界值因而只是候选值。” | O35（G-N1 裁决：随 S4 清理删除）；该句所指的界值已随 S4 移出 |
| `01_introduction` | 路线句 | “西安案例”改“西安参数情景”，与章名一致（其余引言内容留给 NR-8） | 悬空称呼 |
| `nr_audit/` | `make_numbers.py`、`audit_population_scale.py`、`tests/test_numbers.py`、`README.md`、`results/population_scale.{json,md}`、`nr_numbers_map.json` | 追加 24 个宏（六条轨迹的 $t_1$、$\Delta t$、$J$、$t_{\rm end}$，共 67 个）；新增脚本复核人口缩放情景数字；测试 4 项通过 | N8 |

未改（按裁决）：补充 S3 的医疗需求与阈值量级两节（`sec:sup:medical-link`、`sec:sup:threshold-scale`）；`prop:dom:floor` 的陈述与证明；图 10、表 3 的数值；7.3 节的低阈值与退出下界（`prop:exit-infection-lower-bound` 的引用）；8.3 节“有效混合人口未知”一句的其余部分（NR-8）。

## 3 数字核对与变化

- **人口缩放情景（S3.1，自 S4 移入）**：这组数字 NR-3 没有复算，本步用 `audit_population_scale.py` 复核：六个人口下仅隔离控制 $\Delta t=85.0711$ d，相对极差 $4.706\times10^{-8}$（$\Delta t$）与 $1.169\times10^{-7}$（$J$），$t_1$ 由 $11.3878$ 增至 $16.8967$ d；$\eta=100$ 时 $N=1.3163\times10^7$ 的 $\Delta t=22523$ d（正文 $2.25\times10^4$），$N=5\times10^4$ 时 $85.07$ d；对数因子在 $\theta=5\times10^{-4}$、$8\times10^{-3}$ 处为 $2.2021$、$2.1538$（正文 2.20、2.15）。与原 `fixed_absolute_scale.csv`（只读）的 $t_1$、$\Delta t$、$J$ 最大相对差 $3.3\times10^{-13}$。所有正文数字与显示一致，无需修正。六个人口取自原 CSV 的六行（$5\times10^4$、$10^5$、$5\times10^5$、$10^6$、$5\times10^6$、$13163000$）；旧 S4 写作“$5\times10^4,\dots,1.316\times10^7$”，现在列出全部并把 $1.316\times10^7$ 写作 $1.3163\times10^7$。
- **S3.1 新增的拟合误差与初值诊断**：全部由宏引用 NR-3 的结果（`\nrFitMse…`、`\nrFitObjective`、`\nrICtab…`、`\nrICtOneShift`、`\nrICMaxRelTotal`）。
- **TDINN 累计数 607.96、1497.67**：来自旧 S4 设定一段，N1 复核了由它们得到的 $N_{\rm floor}\approx1.06\times10^4$ 与 $5.04$ 倍。
- **不再出现于稿件的数字**：TDINN 的 $J=49.39$（表 3 与表注，D-R7-3）、仅隔离控制 $J=40.7686$ 在第 7 章的两处（表 3 与正文；补充表 S5 的阈值扫描表仍有）、常规控制 $J=0$；S4 的全部比较数字（$N^*(45\,{\rm d})=4.06\times10^4$、$N^*_\infty=9.22\times10^4$、$N^*_{\rm cum,\infty}=1.18\times10^4$、$N_{\rm clr}$ 最大值 $5184$、$\theta_{\rm dur150}$、$\theta_{\rm cost}$、$\theta_{\rm dur45}$、三类临界人口 $11813/40553/92174$ 及其阈值、$\beta$ 扫描的 $8.675$–$8.694$ 与 $0.22\%$ 等，约 85 个不同的数字）。它们都没有在其他位置被引用；原始结果在 `reproducibility/results/…/population/` 与 `nr-base` 版本中。`NR_6_check.md` 的“缺 102 个不同数字”：85 个在 S4，17 个是 NR-5 已记录的替换（13 个）加上表 3 的 $J$ 列（3 个）与一处表注的 45.29（别处仍有）。
- 数字宏：`nr_numbers.tex` 由 43 个增至 67 个。

## 4 编号与引用变化

- 补充材料节号：S4（有效人口）移出后，常规接触率为 S4（原 S5），数值计算的细节为 S5（原 S6）；S3 新增 S3.1“初值与人口缩放”、S3.2“阈值扫描”，医疗需求与阈值量级顺延为 S3.3、S3.4。补充表号：拟合误差 S2、初值对照 S3、初值诊断 S4、阈值扫描 S5、收敛检查 S6、权重转折 S7（NR-5 记录中的“表 S6”现为表 S7）。正文均按标签引用，没有手写节号。
- 标签：旧稿有、新稿缺 24 个，全部在 S4 内（见第 1 节），除 `sec:sup:population`、`app:reference-comparison` 外没有被引用；这两个的引用已改。`prop:reference-population`、`sec:dominance`、`sec:dom:region` 保留。

## 5 待作者决定

1. **补充命题的去留已按“保留”处理**：`prop:reference-population` 是定理类结果，本步没有删除，原样移入 S3.1；若希望随 S4 一并删去，告知后删。
2. 四个已无引用的图像文件（`paper/figures/` 中的 `fig_dom_combined.pdf`、`population_threshold_levers.pdf`、`fig_panel_B_trajectory_decomposition.pdf`、`critical_population_cases.pdf`）与 S4 的源文件副本（`archive/NR_6_removed/`）是否从仓库删去，请定；默认保留。
3. 7.4 节第一段较长（命题 3.12、固定绝对阈值、固定绝对 $I_0$ 三层意思、五个数字）。按 D-R7-4 的写法合并为一段；若想拆成两段，告知后拆。
4. 第 8 章 8.3 节“阈值控制与 TDINN 因而未必对应同一个有效人口（第 7.4 节）”仍在，S4 比较移出后它只是一句提醒，是否保留留给 NR-8。

## 6 检查与编译

`paper\build.ps1`：主稿 34 页（与 NR-5 相同），补充材料 15 页（NR-5 为 21 页，S4 移出约 6 页）；undefined 0、multiply defined 0、超过 10pt 的 Overfull 0。看过的页：主稿第 24–26 页（7.1–7.4 节、图 9、图 10、表 3），补充第 6–7 页（S3.1 的两张新表、命题 S3.1）。静态检查：`check_tex` 悬空引用 0、标签缺失 24（均为 S4 内部标签，已裁决删除）；`statement_diff` 陈述与证明 0 变化（`prop:reference-population`、`prop:dom:floor` 逐字相同）；`nr_audit/tests/test_numbers.py` 4 项通过。静态检查加本机编译，PDF 验收仍归作者（G-NF）。

后续衔接：NR-7（回流接收评估，G-N3）与 NR-8（摘要、引言、讨论、结论）；第 8 章其余 O 项、摘要与引言的“群体免疫阈值”等仍按 `NR_1_theory.md` 第 4 节归 NR-8。
