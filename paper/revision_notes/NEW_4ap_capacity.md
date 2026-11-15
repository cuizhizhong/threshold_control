# NEW-4ap 删去能力约束（N44）

基准 b1522b5（NEW-4ao），执行前标签 `pre-capacity-cut-20261115`。作者 2026-11-15 在对话中决定全删能力约束：所有目标都逐状态，能力约束只把每个状态上的允许区间收窄；$\mathcal A(\eta)$ 中 $q\le q_1<1$、$c>0$ 自动成立，与已有工作中控制不超过 $1$ 的平凡上界无本质区别。看过删改清单与新图 8 预览后回复“写入”。

## 1 段落蓝图（只列有变化的段落）

| 位置 | 改动 |
|---|---|
| 摘要 | 去掉“不限制干预能力时” |
| 引言第 7 段 | 研究问题由两个减为一个 |
| 引言第 8 段 | 去掉“可行性、”，“这两个问题”改“这一问题” |
| 引言第 9 段 | 主要结果由四条减为三条，删第四条（可行性只需在启动时检验；隔离能力不足时须同时减少接触） |
| 3 章首段 | “只要隔离能力允许”删去，引用改为推论 `cor:joint:whole-epidemic` |
| 3.1 节推论 3.3 后 | 删“追踪隔离能力达不到 $q_1$ 时……必须同时减少接触”一句 |
| 4 章首段 | 最优控制只在 $\mathcal A(\eta)$ 中取 |
| 4.1 节 | 删能力约束的定义、控制类、式 `eq:joint:bounds`、推论 `cor:joint:feasibility` 及其后两段；定理 4.1 后补一句：允许区间随 $S$ 增大而变宽，最强干预出现在启动时，隔离比例不超过 $q_1$，接触降幅不超过 $1-S_c/S^*$ |
| 4.2 节 | 补充材料指引去掉“能力约束下 $\alpha$ 的允许范围” |
| 4.3 节 | 删推论 `cor:joint:capped-comparison`、`cor:joint:single-endpoints`；推论 `cor:joint:whole-epidemic`(ii) 改写；其后一段改为“最优控制都是仅隔离控制”，唯一性改引定理 4.3(i) 的等号条件，中间时长改用显式族实现 |
| 5 章首段 | 首句写成“最优控制是仅隔离控制，即取允许区间的上端 $c_0$”；去掉“能力约束” |
| 5.1 节 | 允许区间直接写 $[c_0S_c/S,c_0]$；定理 5.1 后“约束只限制每个状态上的接触率”改“允许区间只依赖于所在的状态” |
| 5.2 节 | 定理 5.2、命题 5.3、5.4 去掉“不考虑能力约束”，删 5.3(iv)、5.4(iii)；“居中”一句去掉限定 |
| 5.3 节 | 改题“阈值与权重的影响”（标签不变）；命题 5.5 删 (ii) 后不再分条；删推论 5.6 及前后两句；命题 5.7 只对 $\mathcal A(\eta)$ 陈述；其后两段去掉限定 |
| 6 章 | 首段与 6.1 节去掉能力约束；删 6.3 节与图 5；表 2、图 4、图 6（现图 5）题注去掉“不考虑能力约束” |
| 7.2 节 | 删能力可行区域一段；权重段改引图 8(a)，新增一段读图 8(b)(c) |
| 7.3 节第 2 段 | 并入 TDINN 的强度（隔离比例约 0.98、接触降幅约 73%）及与阈值策略所需强度的比较，结论“差别不在强度，而在要维持多久”保留 |
| 8.1 节 | 删“追踪隔离能力不足时……辅以减少接触”；成本段去掉限定；“能力允许的最快控制”改“仅隔离控制” |
| 8.4 节 | 第 2 段改为“本文也不限制干预的强度与调整速度”，补一句：强度另有上限时，只要启动时仍能维持阈值，各目标仍可逐状态分析，只是允许区间变窄；第 3 段删“能力约束下隔离权重超过 $r_{\rm cont}$ 时的结构”一句 |
| 9 章 | 成本最优控制一句去掉限定，写明时长、感染与被隔离的未感染者人数居中 |
| 附录 A.7 | 允许区间参数化改用 $c_0[S_c/S+x(1-S_c/S)]$ |
| 附录 A.8、A.9、A.12 | 删 (iv)、(iii)、(ii) 的证明；A.12 改题“阈值的影响” |
| 附录 A.10、A.11 | 删推论 5.6 的证明；A.11(ii) 的允许区间只写 $[1,\zeta]$ |
| 补充 S3（显式族） | 删推论 `cor:joint:allocation-range` 及证明，引导句同步 |
| 补充 S4（权重结构） | 四处“不考虑能力约束”删去；“图 8(b)”改“图 8(a)”（三处） |
| 补充 S7（数值核验） | 收敛表“权重与能力代表点，共 12 组”改“权重，共 10 组”，容差一行去掉“能力代表点” |

## 2 指标

正文汉字（`paper/tmp/new4ap/metrics_*.md`）：引言 2477 → 2340，第 3 章 1785 → 1747，第 4 章 1192 → 878（陈述 580 → 413，证明 502 → 332），第 5 章 1619 → 1475（陈述 710 → 513），第 6 章 1792 → 1361，第 7 章 2112 → 2189，第 8 章 2516 → 2499，第 9 章 320 → 323。正文 37 → 35 页，补充材料 15 → 14 页。图号随之变化：原图 6、7、8、9 现为图 5、6、7、8（西安权重图即现图 7）。

## 3 删除清单

| 内容 | 类别 | 去向 |
|---|---|---|
| 推论 `cor:joint:feasibility`（可行条件 $c_{\min}(1-q_{\max})\le c_0(1-q_1)$）及式 `eq:joint:bounds`、`eq:joint:feasibility` | 删去（作者决定） | 8.4 节一句保留“只要启动时仍能维持阈值，仍可逐状态分析” |
| 推论 `cor:joint:capped-comparison`、`cor:joint:single-endpoints` | 删去 | 两端结论并入推论 `cor:joint:whole-epidemic`(ii) |
| 推论 `cor:joint:capacity-clip`（截断形式）及式 | 删去 | — |
| 命题 5.3(iv)、5.4(iii)、5.5(ii) 与附录证明 | 删去 | — |
| 补充推论 `cor:joint:allocation-range` 及式 | 删去 | — |
| 6.3 节与图 `fig:joint:capacity`；数字 $q_1\approx0.7565$ 处的“超出能力”、$75.3\%$、$J\approx2.361$ d、$\Delta t\approx8.34$ d、$1.94$ d、$39.1\%$、代表点 $c_{\min}/c_0=0.5$、$q_{\max}=0.6$ | 删去 | $q_1\approx0.7565$ 仍在 3.1 节与 8.4 节；其余数字在 `reproducibility/results/20261005_sec7_v2_refinement/joint_extra/capacity.json` 与 `nr_audit/results/regression.json`；图件 `figures/new4al/joint_capacity_baseline.pdf` 保留 |
| 7.2 节能力区域一段：$J\approx84.06$ d、$\Delta t\approx234.4$ d、$61.64$ d、代表点 $q_{\max}=0.75$ | 删去 | `nr_audit/results/new4w/xian_theta001.json`（`capacity` 字段）；“仅隔离控制可行要求 $q_{\max}\ge q_1\approx0.85$”的含义并入 7.3 节 |
| 3.1 节“追踪隔离能力达不到 $q_1$ 时……”、8.1 节“追踪隔离能力不足时……” | 删去 | 同一含义由 4.1 节新增句（最强干预在启动时）与 8.4 节新增句承担 |
| 引言主要结果第四条、研究问题 (2) | 删去 | — |

删除存疑：无。因篇幅删去的机制句：无（删去的都是能力约束本身的结论）。

## 4 陈述与数字

陈述（`NEW_4ap_statements_*.md`）：删去 `cor:joint:feasibility`、`cor:joint:capped-comparison`、`cor:joint:single-endpoints`、`cor:joint:capacity-clip`、`cor:joint:allocation-range` 五条及命题 5.3(iv)、5.4(iii)、5.5(ii) 三项。改动的陈述：

- `cor:joint:whole-epidemic`(ii)：由“能力约束下 $c^{+}$ 最快”改为“$\mathcal A(\eta)$ 中仅隔离控制同时使控制时长最短、清零最早、总累计感染最少，仅减少接触同时使三者最大”。两端都是定理 4.3(i) 的直接结论，证明改引该定理。
- `thm:joint:cost-minimum`、`prop:joint:minimum-threshold`、`prop:joint:weight-monotone`：只对 $\mathcal A(\eta)$ 陈述，允许区间写成 $[c_0S_c/S,c_0]$；原陈述在 $\mathcal A(\eta)$ 上的含义不变。
- `thm:joint:cost-structure`、`prop:joint:global-structure`、`prop:joint:terminal-allocation` 及补充 `lem:sup:upper-set`、`prop:sup:rhat`、`lem:sup:interior-tie`、`prop:sup:jump`：去掉“不考虑能力约束”，含义不变。

check_tex（`NEW_4ap_check.md`）：标签缺失 12 个，均为上述经授权删去的标签；悬空引用 0；数字缺 16、增 10。缺少的数字出自第 3 节所列各项及收敛宏的两个旧值；新增的是图 8 剖面读数（$2.63$、$2.99$、$56$、$75$、$0.39$）、收敛宏新值与“共 $10$ 组”。

新写出的读数：

| 读数 | 来源 |
|---|---|
| $r=4$ 时仅隔离段在 $S/S_c\approx2.99$ 处结束，接触率一次降低约 $56\%$（宏 `\nrXianWtFourSwitch`、`\nrXianWtFourCutPct`） | `nr_audit/results/new4ap_fig8.json` 的 `readings[r=4].jumps[0]` |
| $r=10$ 时启动即降低接触约 $75\%$，隔离比例约 $0.39$（宏 `\nrXianWtTenCutPct`、`\nrXianWtTenStartQ`） | 同上 `readings[r=10]` |
| $r=2.63$ 的跳变在 $S_{\rm sw}$ 稍下方 | 同上；入口断言它与补充命题 `prop:sup:jump` 的闭式 $\zeta_{\rm j}$ 相差不到两个网格步 |
| 收敛表 $\nrConvPlateauMax$：$4.6\times10^{-9}\to1.3\times10^{-9}$，$\nrConvExitMax$：$1.8\times10^{-7}\to3.8\times10^{-8}$ | `new4w/convergence.json` 去掉 kind=cap、capacity=true 的行后重取最大值；其余收敛宏不变，三者仍出自西安参数 |

图 8 的新增计算：五个权重各 2000 个状态的逐状态有限比较（定理 5.1，`allocation.argmin_state`），加 `profile_jumps` 的二分定位；不解 ODE，不重算相图背景。输入 `xian_theta001.json`、`xian_phase.npz` 按 `new4al_notation.json` 登记的 SHA-256 校验。图件 `paper/figures/new4ap/Main8.pdf`，剖面数组 `nr_audit/results/new4ap_fig8_profiles.npz`。

## 5 版面与测试

- 两份 PDF 编译至交叉引用稳定，0 个未定义引用，无超过 10pt 的 Overfull hbox；看过正文第 12–23 页。
- 新收据 `nr_audit/results/new4ap_scope.json`（入口 `nr_audit/new4ap_scope_receipt.py`，只登记身份与残留检查）与 `new4ap_fig8.json`；`figure_table_sources.py` 保持原样（它登记的是 NEW-4t 接收版的来源，测试据此核对）。
- 首次全量运行 10 项失败，都是断言被删的能力约束文字或旧图 8 路径；在 `test_new4ao.py`、`test_new4p_figures.py`、`test_new4t_figures.py`、`test_new4w.py`、`test_sources.py` 增加被 NEW-4ap 取代的分支，参照数值与容差未改。新测试 `test_new4ap.py`（6 项）。重跑后全量 440 项通过（原 434 项加新增 6 项，`NEW_4ap_pytest_full.xml`）。

## 6 待作者决定

无。
