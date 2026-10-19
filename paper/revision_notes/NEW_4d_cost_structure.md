# NEW-4d 成本结构定理入稿记录

依据：作者 2026-10-19 授权（“我授权你修改,然后都安你的建议来”），规则见 `AGENTS.md` N14，计划见 `ai/NEW_4d_cost_structure_plan.md`，来源为专稿 `ai/成本最优/`。比较基准 a5b7022（NEW-4d 开始前）。提交：D0 abe0581、D1 edc711b、D2 db2b459、D3 dfe42fa、D4 本提交。检查报告：`NEW_4d_check.md`、`NEW_4d_statements.md`、`NEW_4d_metrics.md`。

## 1 入稿内容

| # | 位置 | 内容 |
|---|---|---|
| 1 | 5.3 节，式 `eq:joint:rcont` | $b=(1-\beta)(1-q_0)$、$r=w_q/w_c$、$r_{\rm cont}(b)=16/(b+\sqrt{b^2-8b+8})^2\in(2,4)$ |
| 2 | 定理 `thm:joint:cost-structure` | $0<r\le r_{\rm cont}$、不考虑能力约束：逐状态最小点唯一，反馈律在 $(S_c,\infty)$ 上连续，$S\ge S_{\rm sw}$ 时为仅隔离控制，$S_c<S<S_{\rm sw}$ 时严格内部；按 $S^*$ 与 $S_{\rm sw}$ 的大小写出控制期内的结构 |
| 3 | 推论 `cor:joint:capacity-clip` | 同一权重范围内，能力约束下的成本最优控制是把无约束控制截断到 $[c^-,c^+]$（式 `eq:joint:capacity-clip`） |
| 4 | 命题 `prop:joint:weight-monotone` | (i) $r$ 增大时每个状态上 $c^*$、$q^*$ 不增；控制时长与控制期感染不减、新增隔离易感者不增；$J_{\min}/w_c$ 是 $r$ 的凹增函数。(ii) 固定 $r$，隔离比例随时间不增。对 $\mathcal A(\eta)$ 与能力约束类都成立 |
| 5 | 命题 `prop:joint:duration-frontier`（注记 `rem:joint:duration-constraint` 末句改为引出它） | $V(T)$ 可达、凸；内点时长都有有限的匹配乘子 $\kappa$ |
| 6 | 附录 A 新增两小节 `sec:proof:cost-structure`、`sec:proof:duration-frontier` | #2–#5 的证明（$E$ 函数单峰论证、截断、$G=A+rB$ 的单调比较、Aumann 定理） |
| 7 | 补充 S6：命题 `prop:sup:rhat` 及证明；表 S6 增“闭式”列 | $\hat r=(S_{\rm sw}/(S_{\rm sw}-S_c))^2$ 是 $S_{\rm sw}$ 处连续切换的最大权重；闭式值都落在原括区内 |

不入稿（N14）：$r_{\rm loc}$、$r_\infty$、$r_C$ 相切方程、跳变曲线、“恰有一次跳变”、伽罗瓦群、$K,L$ 公式，以及专稿中“$r>r_{\rm cont}$ 时至少有一次跳变”的锐性部分（正文只写“$r_{\rm cont}$ 是每个状态上的成本保持单峰的界”，跳变写作可能出现、由数值给出）。

## 2 叙述改动（D3）

- 摘要：在“控制后期两者并用”后加一句“隔离成本权重不超过接触成本权重的两倍时，它先仅加强隔离，再连续地转为两者并用”（$r_{\rm cont}>2$，故 $r\le2$ 是充分条件）。
- 引言贡献 (4)：原“在所计算的两组参数与默认权重下，数值上呈‘先仅隔离、后两者并用’”改为 $r_{\rm cont}$ 条件下的定理结论，加截断与权重单调两句。
- 6.3 节：前段结构改为由定理保证，数值比较“与之一致”。6.4 节：截断一句引推论。6.5 节：图 7 范围改 $r\in[1,20]$；$r<1$ 一句用命题 (i) 的凹性给出“$1-J_{\min}/J[c_0]$ 随 $r$ 不减，$r=1$ 时约 2.3%、3.0%”；两个转折改用闭式 $r_{\rm cont}$、$\hat r$；补“隔离比例随时间下降、权重越大两种强度越低”；退出处等高线趋于水平线 $r=y/(1-y)$。时长一段引命题 #5。
- 8.1 节：前段全局最优由数值结果改为定理，加权重单调一句。8.4 节：原“前段何时为仅隔离、转折位置、唯一连续单调都未确定；计算点之间未匹配乘子”两条改为“$r>r_{\rm cont}$ 时跳变次数与仅隔离段消失位置只有数值结果，能力约束下这一范围未刻画”。
- 5.3 节末句：“前段全局最优只有数值结果”改为“$r>r_{\rm cont}$ 时前段与跳变的结构只有数值结果”。

## 3 图表（D2）

- 图 7（`fig:joint:phase`）改为 `figures/joint_v2/joint_phase_contour.pdf`：(a)(b) 基准、西安的等高线相图，$r\in[1,20]$，横轴 $S/S_c$ 按时间方向；(c)(d) 基准参数下 $r=1,2,3.17,5,15$ 的接触率与隔离比例随时间变化。由 `nr_audit/plot_figure7_contour.py` 在 $r\in[0.9,20]\times[S_c,S^*]$ 的 $300\times300$ 网格上用正式逐状态求解器重新计算（作者已授权重算背景）；预览 `NEW_4d_figure7_after.png`。
- 原图 7 的局部加密面板移入补充图 `fig:sup:phase-detail`（`joint_phase_detail.pdf`），只读复用 NEW-2 缓存并经原校验函数核对，叠加闭式点。
- `figure_table_sources.py` 登记两图来源，映射表 34 行（21 图 13 表）。

## 4 数字

新增宏 6 个（共 114）：`nrCostRcontBase/Xian` = 3.1358/2.5477，`nrCostRhatBase/Xian` = 3.2051/2.7090，`nrCostGapOneBase/Xian` = 2.3/3.0（%）；映射见 `nr_audit/results/nr_numbers_map.json`。6.5 节原近似宏 `\nrWt…AToApApx`、`\nrWt…ApToBApx` 不再在正文使用，括区仍在表 S6。check_tex：标签缺失 0、悬空 0；“缺”的 0.1、161 是正文 $r\in[0.1,20]$ 与网格描述的改写，原网格与括区仍在补充 S6；新增数字为闭式中的常数（16、27、11 等）、新宏与新网格 $300$、$[0.9,20]$。旧数字无改动。

## 5 核验

- `nr_audit/audit_cost_structure.py`（结果 `results/new4d_cost_structure.json/.md`）：$E$、$E_p$、$E_\zeta$、$\varphi'$ 恒等式与 $F$ 在 $r_{\rm cont}$ 处的因式分解（sympy）；$Q>0$ 下界；$r_{\rm cont}\in(2,4)$ 且随 $b$ 增；两组参数下单峰扫描无违例、$r_{\rm cont}$ 之上出现折叠；$r_{\rm cont}$、$\hat r$ 落在 NR-3 括区内；$\hat r$ 处仅隔离控制恰在 $S_{\rm sw}$ 上方为全局最优；截断式与带约束求解器在两个能力代表点上最大差 0；$c^*$、$q^*$ 对 $r$ 的单调性与 $q^*$ 的时间单调性；$r=1$ 成本差（2.267%、3.021%）。`all_checks_ok=True`。
- 测试：`nr_audit` 全部 289 项通过（含新 `tests/test_cost_structure.py`）。
- 构建：主稿 38 页（NEW-4c 为 35 页）、补充 20 页，undefined 0，Overfull 0；渲染核对主稿第 1、3、21、23、28、30 页与图 7 页、补充 S6 页。
- 证明：按作者意见不另做逐行人工复核；以上符号与数值核验覆盖关键代数步骤，不代替量词与可测性论证。

## 6 文献

新增 `Aumann1965`（R. J. Aumann, Integrals of set-valued functions, J. Math. Anal. Appl. 12(1):1–12, 1965, doi:10.1016/0022-247X(65)90049-1）。出版信息经网络检索核对（Crossref 与原文 PDF 在本环境被代理拦截）；定理 4（闭值、可积有界的集值函数的积分是紧集）的表述经检索摘录核对；定理 1（无原子测度下积分是凸集）按标准引用，未打开原文核对编号。见 `NEW_author_inputs.md` 第 4 项。

## 7 专稿订正（`ai/成本最优/`）

两处过强表述已改，PDF 与打包文件同步重建（16 页，undefined 0）：
1. “混合两种措施带来的成本节省、控制时长与感染的增量都与 $\eta$ 无关”（摘要第 5 条、命题 `prop:mixcost` 标题与正文）→ 多出的感染与 $\eta$ 无关，成本节省与控制时长增量与 $\eta/N$ 成反比（$J_{\rm QO}-J_{\min}=w_cK/(c_0\theta)$，$\theta=\eta/N$），并加“$S^*$ 不低于仅隔离段起点时”的条件。
2. “成本最优控制在整个控制期连续，当且仅当 $r\le r_{A'}$”（摘要第 3、4 条、阈值表、结论清单）→ 反馈律在 $(S_c,\infty)$ 上连续当且仅当 $r\le r_{A'}$；对具体控制期 $[S_c,S^*]$ 只是充分条件（$r\ge r_C(U^*)$ 时控制期内也连续，与专稿第 6 节一致）。

## 8 待作者决定

见 `NEW_author_inputs.md` 第 4 项：五条新增陈述与证明的审阅；Aumann 定理编号对原文的核对。
