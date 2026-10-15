# check_tex 报告

- 旧稿：pre-rewrite-20261007:paper/flatten_curve_analysis_cn.tex, pre-rewrite-20261007:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex, paper/flatten_curve_supplement_cn.tex

## 1 标签与交叉引用

- 旧稿有、新稿缺的标签（8）：eq:cost:weighted、eq:dom:thetadefs、eq:duration-c0-equivalent、eq:joint:quartic、eq:model:beta12-general、eq:model:reduced-si、eq:reference-feasible-set、eq:s1:seg-high
- 新稿中悬空的引用（0）：无
- 新稿中重复定义的标签（0）：无

## 2 参考文献

- 新稿引用了但 bib 中没有（0）：无
- bib 中有但新稿未引用（2）：ShaanxiHealth2022、Zhang2026Behavior

## 3 数值字面量（多重集合比较）

旧稿 692 个，新稿 923 个；旧稿有、新稿缺 100 个；新稿新增 331 个。

### 旧稿有、新稿缺

| 数字 | 缺少次数 | 旧稿中的上下文（最多 3 处） |
|---|---:|---|
| 763 | 8 | aption{仅隔离控制与常规控制的时间轨迹。参数为 $N=763$、$S_0=762$、$I_0=1$、$S_q(0)=I_ ／ n{不同阈值比例下各指标随 $c_0$ 的变化。固定 $N=763,S_0=762,I_0=1,\beta=0.155,\ga ／ 常规接触率下各指标随 $\eta/N$ 的变化。固定 $N=763,S_0=762,I_0=1,\beta=0.155,\ga |
| 762 | 7 | 控制与常规控制的时间轨迹。参数为 $N=763$、$S_0=762$、$I_0=1$、$S_q(0)=I_q(0)=R(0)= ／ 下各指标随 $c_0$ 的变化。固定 $N=763,S_0=762,I_0=1,\beta=0.155,\gamma=0.35 ／ 标随 $\eta/N$ 的变化。固定 $N=763,S_0=762,I_0=1,\beta=0.155,\gamma=0.35 |
| 0.01526 | 6 | $c_0=10\ \mathrm d^{-1}$、$q_0=0.01526$、$\gamma=\delta_q=0.3504\ \ma ／ ma=0.3504\ \mathrm d^{-1},q_0=0.01526$，$\eta/N=0.2\%,0.6\%,1\%,2\%$ ／ ma=0.3504\ \mathrm d^{-1},q_0=0.01526$，$c_0=5,8,10,12$。(a) 启动时间；(b) |
| 0.155 | 6 | $S_q(0)=I_q(0)=R(0)=0$、$\beta=0.155$、$c_0=10\ \mathrm d^{-1}$、$q_ ／ 固定 $N=763,S_0=762,I_0=1,\beta=0.155,\gamma=0.3504\ \mathrm d^{-1} ／ 固定 $N=763,S_0=762,I_0=1,\beta=0.155,\gamma=0.3504\ \mathrm d^{-1} |
| 0.3504 | 6 | q_0=0.01526$、$\gamma=\delta_q=0.3504\ \mathrm d^{-1}$、$\eta=0.05N= ／ =762,I_0=1,\beta=0.155,\gamma=0.3504\ \mathrm d^{-1},q_0=0.01526$， ／ =762,I_0=1,\beta=0.155,\gamma=0.3504\ \mathrm d^{-1},q_0=0.01526$， |
| 0.1498 | 5 | u & 统计资料 \\ $\beta$ & 传播概率 & 0.1498 & 文献 \\ $\gamma$ & 非隔离感染者移出率（ ／ $。传播参数固定为文献~ 表 1 的估计值 $\beta=0.1498,\ \gamma=0.2953,\ \delta_q=0. ／ floor}=607.96+\frac{1497.67}{0.1498} =1.0606\times10^4\approx1.06 |
| 0.3230 | 4 | 制函数在初始时刻的值\\ $q_0$ & 常规隔离比例 & 0.3230 & 所采用控制函数在初始时刻的值\\ $I_0$ & 初始 ／ 4625,\qquad q_{\rm TDINN}(t)=(0.3230-0.9844)e^{-(0.0452t)^2}+0.984 ／ 此常规初始控制水平为 $c_0=12.8872,\ q_0=0.3230$。 社区累计新增感染 $I_{\rm cum}(t)$ |
| 0.4119 | 4 | 组参数中，将解析拐点时刻回代开环控制，所得隔离比例均约为 $0.4119$。该结果为解析公式回代，不是独立 ODE 积分验证。当 $ ／ ambda=0.861$，拐点处隔离比例约为 $\qinf=0.4119$。前者是本组参数下的近似结果，后者由仅含 $\beta$ ／ 3.43$ 时，$q_{\max}=0.383<\qinf=0.4119$，无内部拐点；$c_0=3.59$ 时，$q_{\max} |
| 0.05 | 3 | 0.3504\ \mathrm d^{-1}$、$\eta=0.05N=38.15$。此处的阈值比例用于说明解析结果，不作具体 ／ 迹仍保持 $c(t)\equiv c_0$。当 $\eta=0.05N$ 时，控制触发边界为 \[ c_{0,\min}(0.0 ／ .05N$ 时，控制触发边界为 \[ c_{0,\min}(0.05N)\approx3.327. \] 以下只比较满足式 的参 |
| 12.8872 | 3 | $ & 常规接触率（$\mathrm d^{-1}$） & 12.8872 & 所采用控制函数在初始时刻的值\\ $q_0$ & 常规 ／ n{equation} c_{\rm TDINN}(t)=(12.8872-3.4625)e^{-(0.0463t)^2}+3.462 ／ nd{equation} 因此常规初始控制水平为 $c_0=12.8872,\ q_0=0.3230$。 社区累计新增感染 $I_ |
| 0.2953 | 2 | 非隔离感染者移出率（$\mathrm d^{-1}$） & 0.2953 & 文献 \\ $\delta_q$ & 隔离感染者移出率 ／ 1 的估计值 $\beta=0.1498,\ \gamma=0.2953,\ \delta_q=0.3531$。 原文未给出拟合初 ／ 163{,}000,\beta=0.1498,\gamma=0.2953\ \mathrm d^{-1},\delta_q=0.35 |
| 0.3531 | 2 | 隔离感染者移出率（$\mathrm d^{-1}$） & 0.3531 & 文献 \\ $c_0$ & 常规接触率（$\mathr ／ 98,\ \gamma=0.2953,\ \delta_q=0.3531$。 原文未给出拟合初值。本文取 $S_q(0)=I_q( ／ 2953\ \mathrm d^{-1},\delta_q=0.3531\ \mathrm d^{-1},c_0=12.8872\ |
| 000 | 2 | 西安市 2021 年末常住人口 $N=13{,}163{,}000$。传播参数固定为文献~ 表 1 的估计值 $\beta= ／ 本节沿用正文表 的西安参数：$N=13{,}163{,}000,\beta=0.1498,\gamma=0.2953\ \ ／ 级参考} 正文西安算例采用 $N=13{,}163{,}000$ 、$\eta=0.002N=26{,}326$。本节保留 |
| 152.55 | 2 | ；人数四舍五入至整数。用于后续比较的 TDINN 参照为峰值152.55、总累计2105.63、清零时间45.29 d、$J=49. ／ $。若把感染上限降至 TDINN 社区峰值参照 $\eta=152.55$ 人，该低阈值情景给出 \[ \Delta t(\eta= ／ $ 人，该低阈值情景给出 \[ \Delta t(\eta=152.55)\approx1.48\times10^{4}\ \tex |
| 163 | 2 | 总人口取西安市 2021 年末常住人口 $N=13{,}163{,}000$。传播参数固定为文献~ 表 1 的估计值 $ ／ 阈值扫描} 本节沿用正文表 的西安参数：$N=13{,}163{,}000,\beta=0.1498,\gamma=0.2 ／ 表性阈值的量级参考} 正文西安算例采用 $N=13{,}163{,}000$ 、$\eta=0.002N=26{,}326 |
| 0.0002 | 1 | 209.55 & 826.4066 & 2155649\\ 0.0002 & 0.8469 & 855.09 & 1243.15 & ／ tBarrier 取 $\eta/N\in\{0.0001,0.0002,0.0005,0.001,0.0015,0.002,0.0 |
| 0.0005 | 1 | 243.15 & 412.9141 & 2182123\\ 0.0005 & 0.8466 & 341.75 & 620.77 & ／ r 取 $\eta/N\in\{0.0001,0.0002,0.0005,0.001,0.0015,0.002,0.003,0.00 |
| 0.001 | 1 | ta/N\in\{0.0001,0.0002,0.0005,0.001,0.0015,0.002,0.003,0.004,0.00 |
| 0.0015 | 1 | 389.32 & 82.1192 & 2293939\\ 0.0015 & 0.8458 & 113.59 & 304.01 & ／ n\{0.0001,0.0002,0.0005,0.001,0.0015,0.002,0.003,0.004,0.005,0.007 |
| 0.002 | 1 | 设定\\ $\eta$ & 非隔离感染人数上限（人） & $0.002N=\nu $ & 代表性设计情景，见第 节\\ \bott ／ lticolumn{6}{@{}l}{西安参数：$\eta=0.002N$；新增人数单位为 $10^6$ 人}\\ 仅减少接触 & ／ t)\equiv c_0$，在首次触及设计阈值 $\eta=0.002N$ 后维持 $I=\eta$，并于 $S=S_c$ 退出。 |
| 0.003 | 1 | 002,0.0005,0.001,0.0015,0.002,0.003,0.004,0.005,0.0075,0.01\}$，结果 |
| 0.004 | 1 | 0005,0.001,0.0015,0.002,0.003,0.004,0.005,0.0075,0.01\}$，结果见表~ 和 |
| 0.005 | 1 | .001,0.0015,0.002,0.003,0.004,0.005,0.0075,0.01\}$，结果见表~ 和图~ 。这些 |
| 0.0075 | 1 | 163.65 & 15.9550 & 2545663\\ 0.0075 & 0.8405 & 22.32 & 138.10 & 1 ／ .0015,0.002,0.003,0.004,0.005,0.0075,0.01\}$，结果见表~ 和图~ 。这些取值覆盖代表性 |
| 0.2 | 1 | m d^{-1},q_0=0.01526$，$\eta/N=0.2\%,0.6\%,1\%,2\%$，红色圆点表示 $\Del ／ 0$ 的一组可说明这一取舍。 当 $\eta/N$ 从 $0.2\%$ 增至 $2\%$ 时，控制时长由 $152.1$ d ／ =10$，改变 $\eta/N$}\\ $\eta/N=0.2\%$ & 0.3602 & 152.0574 & 180. |
| 0.22 | 1 | infty/N_{\rm floor}$ 的相对极差仅为 $0.22\%$。这一数值关系描述所考察参数范围内候选端点的变化，具体 ／ floor}\in[8.675,\,8.694]$，极差 $0.22\%$（$\beta=0.10/0.1498/0.20/0. |
| 0.26 | 1 | 时，仅隔离控制重新可行，接触率回到 $c_0$。随后约 $0.26$ d 为仅隔离控制段，$S<S_{\rm sw}$ 后两种 |
| 0.6 | 1 | 1},q_0=0.01526$，$\eta/N=0.2\%,0.6\%,1\%,2\%$，红色圆点表示 $\Delta t$ ／ _{\min}/c_0=0.5$、$q_{\rm cap}=0.6$。仅隔离控制需要 $q_{\max}\approx0.75 ／ 60.8005 & 173.0314\\ $\eta/N=0.6\%$ & 1.3001 & 50.5672 & 86.55 |
| 0.861 | 1 | 区域。 这些轨迹中的拐点相对位置均约为 $\lambda=0.861$，拐点处隔离比例约为 $\qinf=0.4119$。前者是 ／ 结果见图 。各参数组中，拐点相对位置约为 $\lambda=0.861$，绝对时刻随启动时间改变。 当 $N_{\rm eff} |
| 1.06 | 1 | e 人口相容条件 & $N_{\rm floor}$ & $1.06\times10^4$ & 比较时施加的下界\\ 峰值、成本 ／ 零时间的等值曲线。竖直实线为 $N_{\rm floor}=1.06\times10^4$。计算所得累计新增感染与成本条件的交点 ／ nfty\,\bigr] \approx\bigl[\,1.06\times10^{4},\ 9.22\times10^{4 |
| 1.0606 | 1 | 07.96+\frac{1497.67}{0.1498} =1.0606\times10^4\approx1.06\times10^ |
| 1.12 | 1 | 9$ d，下一个计算点在 $11.40$ d，其成本约为 $1.12J_{\min}$。这一相邻点比较未确定精确的临界时长。 ／ ,\,1.18\times10^4]$，上下端点之比不足 $1.12$。该范围接近人口下界，但其中各参数点是否同时满足峰值、成本 |
| 100 | 1 | (a) 为对数纵轴；(d) 为对称对数纵轴（线性区阈值为 $100$ 人），散点为观测累计量；(e) 的水平虚线为 $R_e= ／ ad c_0=\frac{20}{3},\quad I_0=100. \] 此时 $\beta_2^0/\beta_1^0=3 ／ 染比例随 $N$ 变化的结果。 固定绝对阈值 $\eta=100$，把 $N_{\rm eff}$ 从 $1.316\tim |
| 11.40 | 1 | 计算点中最大时长约为 $11.09$ d，下一个计算点在 $11.40$ d，其成本约为 $1.12J_{\min}$。这一相邻点 |
| 11813 | 1 | s10^4$。计算所得累计新增感染与成本条件的交点约为 $(11813,19.55)$，清零时间等值曲线位于人口下界左侧。圆点和方 ／ 见第 节。 累计新增感染与实际成本条件的数值交点约为 $(11813,19.55)$，对应候选人口界值 $N_{\rm cum, ／ 有效人口下的阈值比较。三行依次为 $N_{\rm eff}=11813,40553,92174$；左列为社区感染者人数（对数纵轴） |
| 13.92 | 1 | d（表 ）。 启动时间仅由 $18.55$ d 提前至 $13.92$ d，而低阈值情景的清零时间达到 $2210$ d。该网格 |
| 150 | 1 | ta=0.1498$，在 $\eta\in\{80,100,150\}$、$N_{\rm eff}\in\{4,5,6\}\t ／ 1047$；所考察的 $T_{\max}=45,60,90,150$ 天及不限制时长的设定均有 $\theta_{\rm bi ／ $，$\eta=22.7,33.1,75.2$ 分别对应 $150$ d 时长、成本和 $45$ d 时长条件；右列固定 $\ |
| 18.55 | 1 | d 增加至 $1711$ d（表 ）。 启动时间仅由 $18.55$ d 提前至 $13.92$ d，而低阈值情景的清零时间达 |
| 19.55 | 1 | 。计算所得累计新增感染与成本条件的交点约为 $(11813,19.55)$，清零时间等值曲线位于人口下界左侧。圆点和方点分别示意固 ／ 累计新增感染与实际成本条件的数值交点约为 $(11813,19.55)$，对应候选人口界值 $N_{\rm cum,\infty ／ 10^4$。它与实际成本条件的数值交点约为 $(11813,19.55)$，给出 $N_{\rm cum,\infty}^\ast |
| 2021 | 1 | 数 $I_{q_{\rm new}}(t)$。观测窗口覆盖 2021 年 12 月 9 日至 2022 年 1 月 17 日的 ／ 起算。日新增由相邻整数日累计量之差计算。 总人口取西安市 2021 年末常住人口 $N=13{,}163{,}000$。传播参 ／ 轨迹，以相邻整数日累计量之差计算日新增。40 个日区间从 2021 年 12 月 9 日起算；本图用于拟合重构的比较，并非独立 |
| 20261003 | 1 | nkurl{reproducibility/results/20261003_release_final/}。 \section{基准参 |
| 2210 | 1 | 提前至 $13.92$ d，而低阈值情景的清零时间达到 $2210$ d。该网格内二次成本与清零时间也随阈值降低而增加。控制时 |
| 26 | 1 | \begin{equation} \eta=0.002N=26{,}326. \end{equation} 其医疗资源相关 ／ 13{,}163{,}000$ 、$\eta=0.002N=26{,}326$。本节保留其比例情景的参考依据，并与上一小节的 |
| 26326 | 1 | 6 & 45.29 & 49.3894\\ 仅隔离控制 & 26326 & 2377943 & 258.10 & 40.7686\ ／ 和成本。两条参照线分别为设计情景 $\eta=0.002N=26326$ 和 TDINN 峰值 $\eta=I_{\rm peak ／ 染峰值 $\eta=152.55$ 和设计阈值 $\eta=26326$，等值线表示各指标的水平。} \end{fig |
| 326 | 1 | in{equation} \eta=0.002N=26{,}326. \end{equation} 其医疗资源相关的量级参考见 ／ 163{,}000$ 、$\eta=0.002N=26{,}326$。本节保留其比例情景的参考依据，并与上一小节的医疗需求充分 |
| 5.889 | 1 | 5.04$ d。 二次成本由 $60.80$ d 降至 $5.889$ d，总累计新增感染由 $173.0$ 人增至 $233. |
| 5.90 | 1 | .4 & 346.2 & 2.5462\\ 仅隔离控制 & 5.90 & 33.77 & 285.7 & 383.9 & 2.2 ／ 仅隔离控制的实际成本 $J[c_0]$。两个时长端点约为 $5.90$ 和 $7.75$ d，$J[c_0]\approx1.0 |
| 5184 | 1 | $N_{\rm clr}(\eta)$\\的最大取值} & 5184 & 扫描范围内仍低于下界\\ \bottomrule \e ／ 及插值中，清零时间等值线位于人口下界左侧，最大人口值 $N=5184$ 仍低于 $N_{\rm floor}=1.06\time ／ es10^{3}$，已有计算点及插值中的最大人口值为 $N=5184$。 本小节的累计新增感染均计算至各策略的清零时间，包含退 |
| 58 | 1 | 持续 $1.61$ d，完成阈值控制期 $S$ 总下降的 $58\%$，后段接触率最大降低约 $19.8\%$。 西安参数 |
| 6.7 | 1 | 。 常规控制的感染峰值约为 $300.4$ 人，出现在 $6.7$ d 附近。仅隔离控制在阈值控制期维持 $I=\eta=3 ／ 约 $7.3\%$。 西安参数下，相应变化为成本降低约 $6.7\%$、控制时长增加约 $27.9\%$、总累计新增感染增加 |
| 60.80 | 1 | 2.1$ d 缩短至 $15.04$ d。 二次成本由 $60.80$ d 降至 $5.889$ d，总累计新增感染由 $173 |
| 7.75 | 1 | 7 & 383.9 & 2.2236\\ 最小成本分配 & 7.75 & 35.62 & 306.6 & 363.0 & 2.1 ／ 本 $J[c_0]$。两个时长端点约为 $5.90$ 和 $7.75$ d，$J[c_0]\approx1.05J_{\min} |
| 80 | 1 | 固定 $\beta=0.1498$，在 $\eta\in\{80,100,150\}$、$N_{\rm eff}\in\{4 |

### 新稿新增

| 数字 | 新增次数 | 新稿中的上下文（最多 3 处） |
|---|---:|---|
| 10 | 10 | 。实践中两种干预往往同时使用。He 等 指出，2022 年 10 月以前中国实行动态清零政策，依靠严格的密切接触者追踪隔离乃 ／ $ & 常规接触率（$\mathrm d^{-1}$） & 10 & 12.8872 & 控制函数 在初始时刻的值\\ $q ／ 指标随阈值比例 $\eta/N$ 的变化，$c_0=5,8,10,12\ \mathrm d^{-1}$，其余参数见表~ 。 |
| 0.5 | 9 | 态轨迹与控制时长都有闭式表达，第~ ~节用 $\alpha=0.5$ 作对照；后文的最优控制则在全部允许的 $c_c(S)$ ／ 组参数下，控制时长从长到短依次为仅减少接触、$\alpha=0.5$、成本最优控制与仅隔离控制；由定理~ (iii)与推论~ ／ 11.9390 & 1.02\\ 显式族 $\alpha=0.5$ & 9.24 & 37.11 & 323.4 & 346 |
| 60 | 9 | 指数回流情景取平均停留 $1/\omega=7,14,30,60,120,365$ d（60 d 以上是长停留诊断，不代表实 ／ /\omega=7,14,30,60,120,365$ d（60 d 以上是长停留诊断，不代表实际隔离制度），控制律取仅隔离 ／ PeakRatioMax\,\eta$（基准参数，平均停留 60 d 的仅隔离控制）与 $\rsXianReturnPeak |
| 14 | 7 | 上，所考察的指数回流情景取平均停留 $1/\omega=7,14,30,60,120,365$ d（60 d 以上是长停留诊 ／ 触最长。 终止时累计感染随控制而变，例如基准参数平均停留 14 d 时，仅隔离、迁移律与仅减少接触分别为 $\rsBase ／ lMax}{\ensuremath{5\times10^{-14}}} \newcommand{\rsIrNxGapTwoT |
| 365 | 6 | 平均停留 $1/\omega=7,14,30,60,120,365$ d（60 d 以上是长停留诊断，不代表实际隔离制度），控 ／ eturnPeakRatioMax\,\eta$（西安参数，365 d 的仅隔离控制）；回升不等于越过阈值。各组参数与停留时间 ／ 平均停留 $1/\omega=7,14,30,60,120,365$ d 中，60 d 以上是长停留诊断，不代表实际隔离制度。 |
| 11 | 5 | 了易感者与感染者接触的频率和风险 。这些措施成效显著：欧洲 11 国的数据表明，以封控为代表的主要非药物干预大幅降低了传播， ／ ange}{\ensuremath{3\times10^{-11}}} \newcommand{\rsTolMaxAbsEC ／ lMid}{\ensuremath{4\times10^{-11}}} \newcommand{\rsMigNxGapTwo |
| 30 | 5 | 考察的指数回流情景取平均停留 $1/\omega=7,14,30,60,120,365$ d（60 d 以上是长停留诊断，不 ／ $c_0=3.43$ 时约 $367$ 天降至 $c_0=30$ 时约 $102$ 天：控制时长虽在部分区间增加，启动时间 ／ \emph{情景。}平均停留 $1/\omega=7,14,30,60,120,365$ d 中，60 d 以上是长停留诊断 |
| 120 | 4 | 流情景取平均停留 $1/\omega=7,14,30,60,120,365$ d（60 d 以上是长停留诊断，不代表实际隔离制 ／ 情景。}平均停留 $1/\omega=7,14,30,60,120,365$ d 中，60 d 以上是长停留诊断，不代表实际隔 ／ rm\\ \midrule \multirow{3}{*}{120} & 仅隔离控制 & \rsBaseStayOnetwen |
| 10.1982 | 3 | yThreesixtyfiveQonlyCtermMil}{10.1982} \newcommand{\rsXianStayThree ／ yThreesixtyfiveConlyCtermMil}{10.1982} \newcommand{\rsXianStayThree ／ tayThreesixtyfiveMigCtermMil}{10.1982} \newcommand{\rsReturnRunsTo |
| 12 | 3 | 阈值比例 $\eta/N$ 的变化，$c_0=5,8,10,12\ \mathrm d^{-1}$，其余参数见表~ 。(a) ／ Tang 和 Xiao 的工作 。观测窗口为 2021 年 12 月 9 日至 2022 年 1 月 17 日的 40 个日 ／ 为 TDINN 控制下的模型结果；观测窗口为 2021 年 12 月 9 日起的 40 个日区间。} \end{figu |
| 2001 | 3 | ph{立即返回对照模型。}逐状态最小化用等距网格 $N_x=2001,4001,8001$ 核对根法：在每组参数的退出附近对数加 ／ elta t$、$J$ 的最大相对差在 $N_z=1001,2001,4001$ 时分别约为 \rsIrNzQuadRelCoa ／ 内对 $\omega=0$ 的逐状态最小化同样用 $N_x=2001,4001,8001$ 核对，最大差分别为 \rsMigNx |
| 4001 | 3 | 返回对照模型。}逐状态最小化用等距网格 $N_x=2001,4001,8001$ 核对根法：在每组参数的退出附近对数加密的状态点 ／ t$、$J$ 的最大相对差在 $N_z=1001,2001,4001$ 时分别约为 \rsIrNzQuadRelCoarse、\ ／ omega=0$ 的逐状态最小化同样用 $N_x=2001,4001,8001$ 核对，最大差分别为 \rsMigNxGapTw |
| 0.224 | 2 | sBaseStaySixtyQonlyPeakRatio}{0.224} \newcommand{\rsBaseStaySixty ／ nd{\rsBaseReturnPeakRatioMax}{0.224} \newcommand{\rsXianReturnPea |
| 0.667 | 2 | } \newcommand{\rsBaseIrShare}{0.667} \newcommand{\rsXianQonlyDtIr ／ } \newcommand{\rsXianIrShare}{0.667} \newcommand{\rsBaseStaySeve |
| 0.723 | 2 | ThreesixtyfiveQonlyPeakRatio}{0.723} \newcommand{\rsXianStayThree ／ nd{\rsXianReturnPeakRatioMax}{0.723} \newcommand{\rsBaseReleaseS |
| 10.2184 | 2 | anStayOnetwentyQonlyCtermMil}{10.2184} \newcommand{\rsXianStayOnetw ／ anStayOnetwentyConlyCtermMil}{10.2184} \newcommand{\rsXianStayOnetw |
| 10.2483 | 2 | rsXianStaySixtyQonlyCtermMil}{10.2483} \newcommand{\rsXianStaySixty ／ {\rsXianStaySixtyMigCtermMil}{10.2483} \newcommand{\rsXianStayOnet |
| 19 | 2 | {引言} SARS、甲型 H1N1 流感与 COVID-19 等新发传染病的暴发给医疗系统带来了巨大压力：医疗机构既要应 ／ 降，病死率随之升高，医护人员的负担也急剧加重 ；COVID-19 早期中国各地的数据显示，病死率与发病率显著正相关，提示病死 ／ 超出承载能力，让每名感染者都能得到应有的救治 。COVID-19 暴发后，各国卫生部门认识到任由病毒传播很可能使医院容量饱和 |
| 2.3779 | 2 | 20\\ 仅隔离控制 & 85.07 & 258.10 & 2.3779 & 7.9791 & 40.7686 & 4.73\\ 成 ／ ommand{\rsXianQonlyCinfNrMil}{2.3779} \newcommand{\rsXianQonlyBelo ／ 离控制 & \rsXianQonlyCinfNrMil & 2.3779 & \rsXianLBoundMil & \rsXianQ |
| 2.5348 | 2 | \\ 成本最优控制 & 108.81 & 281.84 & 2.5348 & 7.8222 & 38.0209 & 4.73\\ \ ／ wcommand{\rsXianOptCinfNrMil}{2.5348} \newcommand{\rsXianOptBelowL ／ 本最优控制 & \rsXianOptCinfNrMil & 2.5348 & \rsXianLBoundMil & \rsXianO |
| 2.6390 | 2 | lpha=0.5$ & 124.57 & 297.60 & 2.6390 & 7.7180 & 44.5286 & 3.20\\ 仅 ／ ommand{\rsXianAlphaCinfNrMil}{2.6390} \newcommand{\rsXianAlphaBelo ／ .5$ & \rsXianAlphaCinfNrMil & 2.6390 & \rsXianLBoundMil & \rsXianA |
| 3.000 | 2 | \newcommand{\rsBaseIrSwitchZ}{3.000} \newcommand{\rsBaseIrShare}{ ／ \newcommand{\rsXianIrSwitchZ}{3.000} \newcommand{\rsXianIrShare}{ |
| 3.8566 | 2 | }\\ 仅减少接触 & 308.79 & 481.83 & 3.8566 & 6.5004 & 109.3648 & 1.46\\ ／ ommand{\rsXianConlyCinfNrMil}{3.8566} \newcommand{\rsXianConlyBelo ／ 少接触 & \rsXianConlyCinfNrMil & 3.8566 & \rsXianLBoundMil & \rsXianC |
| 4.044 | 2 | J$ 见式 。基准与西安参数下，$S^*/S_c$ 约为 $4.044$ 与 $4.378$，$S_{\rm sw}/S_c$（式 ／ command{\rsBaseZStarNoreturn}{4.044} \newcommand{\rsBaseZPlateauM |
| 8001 | 2 | 型。}逐状态最小化用等距网格 $N_x=2001,4001,8001$ 核对根法：在每组参数的退出附近对数加密的状态点上（含 $ ／ =0$ 的逐状态最小化同样用 $N_x=2001,4001,8001$ 核对，最大差分别为 \rsMigNxGapTwoThou |
| 0.1 | 1 | $r=w_q/w_c$ 依赖权重），图~ 给出 $r\in[0.1,20]$ 内不考虑能力约束时的成本最优控制；颜色 $y$ ／ \renewcommand{\textfraction}{0.1} \begin{figure}[htbp] \center ／ \renewcommand{\textfraction}{0.1} \renewcommand{\floatpagefrac |
| 0.205 | 1 | \rsBaseStaySixtyMigPeakRatio}{0.205} \newcommand{\rsBaseStaySixty |
| 0.277 | 1 | sixtyfiveQonlyE}{\ensuremath{-0.277}} \newcommand{\rsXianStayThre |
| 0.291 | 1 | sXianStaySixtyConlyPeakRatio}{0.291} \newcommand{\rsXianStaySixty |
| 0.294 | 1 | eesixtyfiveMigE}{\ensuremath{-0.294}} \newcommand{\rsXianStayThre |
| 0.372 | 1 | sixtyfiveConlyE}{\ensuremath{-0.372}} \newcommand{\rsXianStayThre |
| 0.384 | 1 | ayOnetwentyMigE}{\ensuremath{-0.384}} \newcommand{\rsXianStayOnet |
| 0.488 | 1 | OnetwentyConlyE}{\ensuremath{-0.488}} \newcommand{\rsXianStayOnet |
| 0.512 | 1 | nStayOnetwentyConlyPeakRatio}{0.512} \newcommand{\rsXianStayOnetw |
| 0.616 | 1 | ianStayOnetwentyMigPeakRatio}{0.616} \newcommand{\rsXianStayOnetw |
| 0.628 | 1 | ThreesixtyfiveConlyPeakRatio}{0.628} \newcommand{\rsXianStayThree |
| 0.706 | 1 | ayThreesixtyfiveMigPeakRatio}{0.706} \newcommand{\rsXianStayThree |
| 0.709 | 1 | StaySixtyConlyE}{\ensuremath{-0.709}} \newcommand{\rsXianStaySixt |
| 0.776 | 1 | StaySixtyQonlyE}{\ensuremath{-0.776}} \newcommand{\rsBaseStaySixt |
| 0.795 | 1 | seStaySixtyMigE}{\ensuremath{-0.795}} \newcommand{\rsBaseStaySixt |
| 0.838 | 1 | 降到 $0.0001N$ 时，$q_{\max}$ 只在 $0.838$ 与 $0.847$ 之间变化，控制时长与成本近似按阈值的 |
| 0.847 | 1 | N$ 时，$q_{\max}$ 只在 $0.838$ 与 $0.847$ 之间变化，控制时长与成本近似按阈值的反比增加，总累计新增 |
| 0.85 | 1 | 隔离控制只需保持 $R_e=1$（式 ），隔离比例最高约 $0.85$，此后随易感者减少而下降（补充表~ ）。非隔离感染者人数 |
| 0.98 | 1 | 预，接触率趋向常规水平的约 $27\%$，隔离比例趋向约 $0.98$；$R_e$ 因而较快降到 $1$ 以下，疫情在易感者仍接 |
| 1.02 | 1 | 制与仅减少接触下分别约为 $1.92$、$1.89$ 与 $1.02$（表~ ，图~ (c)）。这一峰值在基准参数下出现在后段， ／ 13 & 628.6 & 40.9 & 11.9390 & 1.02\\ 显式族 $\alpha=0.5$ & 9.24 & 3 |
| 1.10 | 1 | 为不考虑时长约束的最小成本）；延长控制期时，成本不超过 $1.10J_{\min}$ 的计算点最长约 $11.09$ d，而仅 |
| 1.53 | 1 | -S_c)$，这一下界与控制组合无关；西安全市参数下约为 $1.53\times10^6$ 人。 \end{enumerate} |
| 1.64 | 1 | 11 & 323.4 & 346.2 & 2.5462 & 1.64\\ 仅隔离控制 & 5.90 & 33.77 & 285. |
| 1.7 | 1 | GapEightThousand}{\ensuremath{1.7\times10^{-9}}} \newcommand{\r |
| 1.89 | 1 | 离控制、成本最优控制与仅减少接触下分别约为 $1.92$、$1.89$ 与 $1.02$（表~ ，图~ (c)）。这一峰值在基准 ／ 62 & 306.6 & 363.0 & 2.1183 & 1.89\\ \midrule \multicolumn{7}{@{ |
| 1.92 | 1 | ta$ 在仅隔离控制、成本最优控制与仅减少接触下分别约为 $1.92$、$1.89$ 与 $1.02$（表~ ，图~ (c)）。 ／ 77 & 285.7 & 383.9 & 2.2236 & 1.92\\ 成本最优控制 & 7.75 & 35.62 & 306 |
| 10.1386 | 1 | \newcommand{\rsXianInfIrMil}{10.1386} \newcommand{\rsXianSstarIrMi |
| 10.1889 | 1 | \newcommand{\rsXianLBoundMil}{10.1889} \newcommand{\rsXianQonlyCinf |
| 10.2183 | 1 | XianStayOnetwentyMigCtermMil}{10.2183} \newcommand{\rsXianStayThre |
| 10.2475 | 1 | rsXianStaySixtyConlyCtermMil}{10.2475} \newcommand{\rsXianStaySixty |
| 10.3018 | 1 | sXianStayThirtyConlyCtermMil}{10.3018} \newcommand{\rsXianStayThirt |
| 10.3031 | 1 | \rsXianStayThirtyMigCtermMil}{10.3031} \newcommand{\rsXianStaySixt |
| 10.3044 | 1 | sXianStayThirtyQonlyCtermMil}{10.3044} \newcommand{\rsXianStayThirt |
| 10.4498 | 1 | ianStayFourteenQonlyCtermMil}{10.4498} \newcommand{\rsXianStayFourt |
| 10.4520 | 1 | sXianStayFourteenMigCtermMil}{10.4520} \newcommand{\rsXianStayThir |
| 10.4538 | 1 | ianStayFourteenConlyCtermMil}{10.4538} \newcommand{\rsXianStayFourt |
| 10.5485 | 1 | rsXianStaySevenQonlyCtermMil}{10.5485} \newcommand{\rsXianStaySeven |
| 10.5491 | 1 | {\rsXianStaySevenMigCtermMil}{10.5491} \newcommand{\rsXianStayFour |
| 10.5495 | 1 | rsXianStaySevenConlyCtermMil}{10.5495} \newcommand{\rsXianStaySeven |
| 1001 | 1 | 的 $\Delta t$、$J$ 的最大相对差在 $N_z=1001,2001,4001$ 时分别约为 \rsIrNzQuadR |
| 10135 | 1 | nStayThreesixtyfiveConlyTend}{10135} \newcommand{\rsXianStayThree |
| 10187 | 1 | ianStayThreesixtyfiveMigTend}{10187} \newcommand{\rsXianStayThree |
| 10199 | 1 | nStayThreesixtyfiveQonlyTend}{10199} \newcommand{\rsXianStayThree |
| 11.0 | 1 | ommand{\rsXianIrCostGapQonly}{11.0} \newcommand{\rsXianIrSwitchZ |
| 11.980 | 1 | BaseStayThreesixtyfiveConlyJ}{11.980} \newcommand{\rsBaseStayThree |
| 116.23 | 1 | command{\rsXianStaySixtyMigJ}{116.23} \newcommand{\rsXianStaySixty |
| 116.98 | 1 | ianStayThreesixtyfiveQonlyDt}{116.98} \newcommand{\rsXianStayThree |
| 1180.9 | 1 | \newcommand{\rsBaseAlphaKqIr}{1180.9} \newcommand{\rsBaseOptDtIr}{ |
| 119.99 | 1 | mmand{\rsXianStaySixtyQonlyJ}{119.99} \newcommand{\rsXianStaySixty |
| 1197.9 | 1 | nd{\rsXianStaySevenConlyTend}{1197.9} \newcommand{\rsXianStaySeven |
| 12.057 | 1 | d{\rsBaseStayOnetwentyConlyJ}{12.057} \newcommand{\rsBaseStayOnetw |
| 12.160 | 1 | mmand{\rsBaseStaySixtyConlyJ}{12.160} \newcommand{\rsBaseStaySixty |
| 12.329 | 1 | mand{\rsBaseStayThirtyConlyJ}{12.329} \newcommand{\rsBaseStayThirt |
| 12.4 | 1 | ommand{\rsBaseIrCostGapQonly}{12.4} \newcommand{\rsBaseIrSwitchZ |
| 12.579 | 1 | nd{\rsBaseStayFourteenConlyJ}{12.579} \newcommand{\rsBaseStayFourt |
| 12.613 | 1 | mmand{\rsBaseStayThirtyMigDt}{12.613} \newcommand{\rsBaseStayThirt |
| 12.795 | 1 | mmand{\rsBaseStaySevenConlyJ}{12.795} \newcommand{\rsBaseStaySeven |
| 1213.2 | 1 | } \newcommand{\rsBaseOptKqIr}{1213.2} \newcommand{\rsBaseConlyDtIr |
| 127.76 | 1 | d{\rsBaseStayThirtyQonlyTend}{127.76} \newcommand{\rsBaseStayThirt |
| 1275.9 | 1 | \rsXianStayFourteenConlyTend}{1275.9} \newcommand{\rsXianStayFourt |
| 13.00 | 1 | 3.24 & 2.74\\ 出现仅隔离段的最大 $r$ & 13.00 & 7.41\\ 不出现仅隔离段的最小 $r$ & 13. |
| 13.106 | 1 | \newcommand{\rsBaseConlyJIr}{13.106} \newcommand{\rsBaseConlyKqIr |
| 13.1127 | 1 | newcommand{\rsXianSstarIrMil}{13.1127} \newcommand{\rsXianIrCostGap |
| 13.44 | 1 | .00 & 7.41\\ 不出现仅隔离段的最小 $r$ & 13.44 & 7.66\\ \bottomrule \end{tab |
| 131.23 | 1 | and{\rsBaseStayThirtyMigTend}{131.23} \newcommand{\rsBaseStayThirt |
| 1340.3 | 1 | d{\rsXianStayThirtyQonlyTend}{1340.3} \newcommand{\rsXianStayThirt |
| 136.53 | 1 | XianStayThreesixtyfiveConlyJ}{136.53} \newcommand{\rsXianStayThree |
| 1400.9 | 1 | and{\rsXianStayThirtyMigTend}{1400.9} \newcommand{\rsXianStayThirt |
| 152.84 | 1 | mand{\rsBaseStaySixtyMigTend}{152.84} \newcommand{\rsBaseStaySixty |
| 153.10 | 1 | ommand{\rsXianStayThirtyMigJ}{153.10} \newcommand{\rsXianStayThirt |
| 157.02 | 1 | nd{\rsBaseStaySixtyQonlyTend}{157.02} \newcommand{\rsBaseStaySixty |
| 1610.1 | 1 | \newcommand{\rsBaseQonlyKqIr}{1610.1} \newcommand{\rsBaseAlphaDtIr |
| 165.09 | 1 | sXianStayThreesixtyfiveMigDt}{165.09} \newcommand{\rsXianStayThree |
| 165.11 | 1 | mand{\rsXianStayThirtyQonlyJ}{165.11} \newcommand{\rsXianStayThirt |
| 1707.3 | 1 | d{\rsXianStayThirtyConlyTend}{1707.3} \newcommand{\rsXianStayThirt |
| 176.87 | 1 | mand{\rsXianStayFourteenMigJ}{176.87} \newcommand{\rsXianStayFourt |
| 18.104 | 1 | \newcommand{\rsBaseQonlyDtIr}{18.104} \newcommand{\rsBaseQonlyJIr} |
| 18.5862 | 1 | wcommand{\rsXianConlyKqIrMil}{18.5862} \newcommand{\rsXianInfIrMil} |
| 186.51 | 1 | command{\rsXianStaySevenMigJ}{186.51} \newcommand{\rsXianStaySeven |
| 189.69 | 1 | 8} \newcommand{\rsXianOptJIr}{189.69} \newcommand{\rsXianOptKqIrMi |
| 19.213 | 1 | d{\rsBaseStayFourteenQonlyDt}{19.213} \newcommand{\rsBaseStayFourt |
| 192.88 | 1 | nd{\rsXianStayFourteenQonlyJ}{192.88} \newcommand{\rsXianStayFourt |
| 2.1 | 1 | GapEightThousand}{\ensuremath{2.1\times10^{-9}}} \newcommand{\r |
| 2.1334 | 1 | rsBaseStayThreesixtyfiveMigJ}{2.1334} \newcommand{\rsBaseStayThree |
| 2.1661 | 1 | and{\rsBaseStayOnetwentyMigJ}{2.1661} \newcommand{\rsBaseStayOnetw |
| 2.215 | 1 | ommand{\rsBaseReleaseSqRatio}{2.215} \newcommand{\rsBaseReleaseRe |
| 2.2198 | 1 | command{\rsBaseStaySixtyMigJ}{2.2198} \newcommand{\rsBaseStaySixty |
| 2.2370 | 1 | BaseStayThreesixtyfiveQonlyJ}{2.2370} \newcommand{\rsBaseStayThree |
| 2.265 | 1 | .378$，$S_{\rm sw}/S_c$（式 ）约为 $2.265$ 与 $2.548$。 \end{tablenotes} |
| 2.2654 | 1 | d{\rsBaseStayOnetwentyQonlyJ}{2.2654} \newcommand{\rsBaseStayOnetw |
| 2.3109 | 1 | mmand{\rsBaseStaySixtyQonlyJ}{2.3109} \newcommand{\rsBaseStaySixty |
| 2.3523 | 1 | ommand{\rsBaseStayThirtyMigJ}{2.3523} \newcommand{\rsBaseStayThirt |
| 2.4176 | 1 | mand{\rsBaseStayThirtyQonlyJ}{2.4176} \newcommand{\rsBaseStayThirt |
| 2.65 | 1 | rm sw}$ 处连续切换的最大 $r$ & 3.13 & 2.65\\ 切换提前并跳变的最小 $r$ & 3.24 & 2.7 |
| 2.7 | 1 | 比例。在所算网格中，$r$ 约在 $3$ 以下（基准）或 $2.7$ 以下（西安）时，切换都发生在 $S_{\rm sw}$ |
| 2.714 | 1 | ommand{\rsXianReleaseSqRatio}{2.714} \newcommand{\rsXianReleaseRe |
| 2.74 | 1 | .65\\ 切换提前并跳变的最小 $r$ & 3.24 & 2.74\\ 出现仅隔离段的最大 $r$ & 13.00 & 7.4 |
| 2.8 | 1 | NxGapTwoThousand}{\ensuremath{2.8\times10^{-8}}} \newcommand{\r |
| 2.8229 | 1 | nd{\rsBaseStayFourteenQonlyJ}{2.8229} \newcommand{\rsBaseStayFourt |
| 2.8421 | 1 | mand{\rsBaseStayFourteenMigJ}{2.8421} \newcommand{\rsBaseStayFourt |
| 20 | 1 | _q/w_c$ 依赖权重），图~ 给出 $r\in[0.1,20]$ 内不考虑能力约束时的成本最优控制；颜色 $y$ 是接触 ／ ma=\frac1{10},\quad c_0=\frac{20}{3},\quad I_0=100. \] 此时 $\be ／ /40$。固定 $S^*=N/5$，对 $r\in\{21/20,2\}$ 分别构造 \[ S_0=rS^*,\qquad |
| 2022 | 1 | 带来的隔离负担。实践中两种干预往往同时使用。He 等 指出，2022 年 10 月以前中国实行动态清零政策，依靠严格的密切接触者 ／ o 的工作 。观测窗口为 2021 年 12 月 9 日至 2022 年 1 月 17 日的 40 个日区间，其间社区发现 58 ／ item 注：观测窗口为 2021 年 12 月 9 日至 2022 年 1 月 17 日，共 40 天；拟合行使用未取整的 $ |
| 204.08 | 1 | mmand{\rsXianStaySevenQonlyJ}{204.08} \newcommand{\rsXianStaySeven |
| 204.52 | 1 | d{\rsXianStayOnetwentyConlyJ}{204.52} \newcommand{\rsXianStayOnetw |
| 21.807 | 1 | and{\rsBaseStayFourteenMigDt}{21.807} \newcommand{\rsBaseStayFourt |
| 2106 | 1 | 、清零时间约为 $258.1$ d，TDINN 分别约为 $2106$ 人与 $45.29$ d。二次成本 $J$ 只衡量干预强 ／ }\\ \midrule TDINN 控制 & 153 & 2106 & 45.29 & 49.3894\\ 仅隔离控制 & 2 ／ 10^6, \] 已远高于 TDINN 在其清零时间的约 $2106$ 人。因此，在本模型与西安全市参数下，像 TDINN 那样 |
| 211.14 | 1 | \newcommand{\rsXianAlphaJIr}{211.14} \newcommand{\rsXianAlphaKqIr |
| 213.18 | 1 | \newcommand{\rsXianQonlyJIr}{213.18} \newcommand{\rsXianQonlyKqIr |
| 2187.3 | 1 | nd{\rsXianStaySixtyQonlyTend}{2187.3} \newcommand{\rsXianStaySixty |
| 2233.5 | 1 | mand{\rsXianStaySixtyMigTend}{2233.5} \newcommand{\rsXianStaySixty |
| 23.551 | 1 | } \newcommand{\rsBaseOptDtIr}{23.551} \newcommand{\rsBaseOptJIr}{8 |
| 23.775 | 1 | mand{\rsBaseStaySevenQonlyDt}{23.775} \newcommand{\rsBaseStaySeven |
| 23.994 | 1 | \newcommand{\rsBaseAlphaDtIr}{23.994} \newcommand{\rsBaseAlphaJIr} |
| 2469.3 | 1 | nd{\rsXianStaySixtyConlyTend}{2469.3} \newcommand{\rsXianStaySixty |
| 253.25 | 1 | mmand{\rsXianStaySixtyConlyJ}{253.25} \newcommand{\rsXianStaySixty |
| 26.111 | 1 | ommand{\rsBaseStaySevenMigDt}{26.111} \newcommand{\rsBaseStaySeven |
| 27 | 1 | NN 控制同时使用两种高强度干预，接触率趋向常规水平的约 $27\%$，隔离比例趋向约 $0.98$；$R_e$ 因而较快降 |
| 282.73 | 1 | mand{\rsXianStayThirtyConlyJ}{282.73} \newcommand{\rsXianStayThirt |
| 285.7 | 1 | 1.64\\ 仅隔离控制 & 5.90 & 33.77 & 285.7 & 383.9 & 2.2236 & 1.92\\ 成本最 ／ 仅隔离控制 & \rsBaseQonlyCinfNr & 285.7 & \rsBaseLBound & \rsBaseQonl |
| 286.6 | 1 | ewcommand{\rsBaseQonlyCinfNr}{286.6} \newcommand{\rsBaseQonlyBelo |
| 296.1 | 1 | StayThreesixtyfiveQonlyCterm}{296.1} \newcommand{\rsBaseStayThree |
| 299.49 | 1 | nd{\rsXianStayFourteenConlyJ}{299.49} \newcommand{\rsXianStayFourt |
| 3.13 | 1 | 在 $S_{\rm sw}$ 处连续切换的最大 $r$ & 3.13 & 2.65\\ 切换提前并跳变的最小 $r$ & 3.2 |
| 3.20 | 1 | & 2.6390 & 7.7180 & 44.5286 & 3.20\\ 仅隔离控制 & 85.07 & 258.10 & 2. |
| 3.215 | 1 | \newcommand{\rsBaseReleaseRe}{3.215} \newcommand{\rsXianReleaseSq |
| 3.24 | 1 | .13 & 2.65\\ 切换提前并跳变的最小 $r$ & 3.24 & 2.74\\ 出现仅隔离段的最大 $r$ & 13.0 |
| 3.327 | 1 | 式 ）时，无需启动控制；该边界随阈值升高，基准阈值下约为 $3.327$。相应的隔离比例轨迹与二维扫描见补充图~ 、 。 \beg |
| 3.6 | 1 | NxGapTwoThousand}{\ensuremath{3.6\times10^{-8}}} \newcommand{\r |
| 3.714 | 1 | \newcommand{\rsXianReleaseRe}{3.714} \newcommand{\rsBaseLBound}{ |
| 3.9851 | 1 | command{\rsBaseStaySevenMigJ}{3.9851} \newcommand{\rsBaseStaySeven |
| 3.9902 | 1 | mmand{\rsBaseStaySevenQonlyJ}{3.9902} \newcommand{\rsBaseStaySeven |
| 306.6 | 1 | .92\\ 成本最优控制 & 7.75 & 35.62 & 306.6 & 363.0 & 2.1183 & 1.89\\ \mi ／ & 成本最优控制 & \rsBaseOptCinfNr & 306.6 & \rsBaseLBound & \rsBaseOptB |
| 307.01 | 1 | mmand{\rsXianStaySevenConlyJ}{307.01} \newcommand{\rsXianStaySeven |
| 307.5 | 1 | \newcommand{\rsBaseOptCinfNr}{307.5} \newcommand{\rsBaseOptBelowL |
| 314.65 | 1 | \newcommand{\rsXianConlyJIr}{314.65} \newcommand{\rsXianConlyKqIr |
| 317.9 | 1 | seStayThreesixtyfiveMigCterm}{317.9} \newcommand{\rsXianStaySeve |
| 323.4 | 1 | $\alpha=0.5$ & 9.24 & 37.11 & 323.4 & 346.2 & 2.5462 & 1.64\\ 仅隔离 ／ a=0.5$ & \rsBaseAlphaCinfNr & 323.4 & \rsBaseLBound & \rsBaseAlph |
| 324.2 | 1 | ewcommand{\rsBaseAlphaCinfNr}{324.2} \newcommand{\rsBaseAlphaBelo |
| 326.9 | 1 | sBaseStayOnetwentyQonlyCterm}{326.9} \newcommand{\rsBaseStayOnetw |
| 34.8035 | 1 | wcommand{\rsXianAlphaKqIrMil}{34.8035} \newcommand{\rsXianOptDtIr}{ |
| 348.0 | 1 | \rsBaseStayOnetwentyMigCterm}{348.0} \newcommand{\rsBaseStayThre |
| 35.7645 | 1 | newcommand{\rsXianOptKqIrMil}{35.7645} \newcommand{\rsXianConlyDtIr |
| 36 | 1 | ewcommand{\rsReturnRunsTotal}{36} \newcommand{\rsReturnRunsCro |
| 36.423 | 1 | aseStayThreesixtyfiveConlyDt}{36.423} \newcommand{\rsBaseStayThree |
| 36.727 | 1 | {\rsBaseStayOnetwentyConlyDt}{36.727} \newcommand{\rsBaseStayOnetw |
| 36.740 | 1 | eStayThreesixtyfiveQonlyTend}{36.740} \newcommand{\rsBaseStayThree |
| 37.1 | 1 | ommand{\rsBaseIrCostGapConly}{37.1} \newcommand{\rsBaseIrCostGap |
| 37.117 | 1 | mand{\rsBaseStaySixtyConlyDt}{37.117} \newcommand{\rsBaseStaySixty |
| 37.711 | 1 | and{\rsBaseStayThirtyConlyDt}{37.711} \newcommand{\rsBaseStayThirt |
| 38.473 | 1 | d{\rsBaseStayFourteenConlyDt}{38.473} \newcommand{\rsBaseStayFourt |
| 38.494 | 1 | aseStayThreesixtyfiveMigTend}{38.494} \newcommand{\rsBaseStayThree |
| 384.26 | 1 | \newcommand{\rsXianQonlyDtIr}{384.26} \newcommand{\rsXianQonlyJIr} |
| 3848.1 | 1 | rsXianStayOnetwentyQonlyTend}{3848.1} \newcommand{\rsXianStayOnetw |
| 3868.2 | 1 | {\rsXianStayOnetwentyMigTend}{3868.2} \newcommand{\rsXianStayOnetw |
| 39.000 | 1 | mand{\rsBaseStaySevenConlyDt}{39.000} \newcommand{\rsBaseStaySeven |
| 39.584 | 1 | \newcommand{\rsBaseConlyDtIr}{39.584} \newcommand{\rsBaseConlyJIr} |
| 39.7 | 1 | ommand{\rsXianIrCostGapConly}{39.7} \newcommand{\rsXianIrCostGap |
| 397.69 | 1 | {\rsXianStayOnetwentyQonlyDt}{397.69} \newcommand{\rsXianStayOnetw |
| 3990.3 | 1 | rsXianStayOnetwentyConlyTend}{3990.3} \newcommand{\rsXianStayOnetw |
| 4.046 | 1 | ewcommand{\rsBaseZPlateauMax}{4.046} \newcommand{\rsXianZStarNore |
| 4.378 | 1 | 西安参数下，$S^*/S_c$ 约为 $4.044$ 与 $4.378$，$S_{\rm sw}/S_c$（式 ）约为 $2.26 ／ command{\rsXianZStarNoreturn}{4.378} \newcommand{\rsXianZPlateauM |
| 4.382 | 1 | ewcommand{\rsXianZPlateauMax}{4.382} \newcommand{\rsNrClosedForm |
| 4.42 | 1 | 在其清零时间恢复常规控制，按名义参数计算，有效再生数约为 $4.42$，$I$ 将重新上升。因此，比较不同策略时要连同退出要求一 |
| 40 | 1 | 靠严格的密切接触者追踪隔离乃至静态管理，几乎所有疫情都在约 40 天内清零。他们结合动力学模型与神经网络，从包括西安在内的疫 ／ 年 12 月 9 日至 2022 年 1 月 17 日的 40 个日区间，其间社区发现 583 例、隔离发现 1467 例 ／ 的初值，不是实际病例数；若改取 $I_0=1$，模型给出的 40 天累计病例约为 $1.08\times10^6$，远高于观 |
| 40.5879 | 1 | wcommand{\rsXianQonlyKqIrMil}{40.5879} \newcommand{\rsXianAlphaDtIr |
| 407.11 | 1 | mand{\rsXianStaySevenQonlyDt}{407.11} \newcommand{\rsXianStaySeven |
| 421.89 | 1 | ianStayThreesixtyfiveConlyDt}{421.89} \newcommand{\rsXianStayThree |
| 425.26 | 1 | d{\rsXianStayFourteenQonlyDt}{425.26} \newcommand{\rsXianStayFourt |
| 43.305 | 1 | rsXianStayThreesixtyfiveMigJ}{43.305} \newcommand{\rsXianStayThree |
| 44.7 | 1 | \newcommand{\rsBaseConlyKqIr}{44.7} \newcommand{\rsBaseInfIr}{53 |
| 45.266 | 1 | XianStayThreesixtyfiveQonlyJ}{45.266} \newcommand{\rsXianStayThree |
| 45.29 | 1 | 58.1$ d，TDINN 分别约为 $2106$ 人与 $45.29$ d。二次成本 $J$ 只衡量干预强度，较低的 $J$ 因 ／ drule TDINN 控制 & 153 & 2106 & 45.29 & 49.3894\\ 仅隔离控制 & 26326 & 2 ／ $152.55$、总累计 $2105.63$、清零时间 $45.29$ d、$J=49.39$。 \end{tablenotes |
| 451.10 | 1 | nd{\rsXianStayOnetwentyMigDt}{451.10} \newcommand{\rsXianStayOnetw |
| 452.04 | 1 | and{\rsXianStayThirtyQonlyDt}{452.04} \newcommand{\rsXianStayThirt |
| 462.73 | 1 | mand{\rsXianStaySixtyQonlyDt}{462.73} \newcommand{\rsXianStaySixty |
| 464.58 | 1 | ommand{\rsXianStaySevenMigDt}{464.58} \newcommand{\rsXianStaySeven |
| 484.65 | 1 | and{\rsXianStayFourteenMigDt}{484.65} \newcommand{\rsXianStayFourt |
| 493.58 | 1 | } \newcommand{\rsXianOptDtIr}{493.58} \newcommand{\rsXianOptJIr}{1 |
| 50.237 | 1 | {\rsBaseStayOnetwentyMigTend}{50.237} \newcommand{\rsBaseStayOnetw |
| 515.36 | 1 | \newcommand{\rsXianAlphaDtIr}{515.36} \newcommand{\rsXianAlphaJIr} |
| 516.26 | 1 | mmand{\rsXianStayThirtyMigDt}{516.26} \newcommand{\rsXianStayThirt |
| 52.489 | 1 | rsBaseStayOnetwentyQonlyTend}{52.489} \newcommand{\rsBaseStayOnetw |
| 525.89 | 1 | ommand{\rsXianStaySixtyMigDt}{525.89} \newcommand{\rsXianStaySixty |
| 537.4 | 1 | .7} \newcommand{\rsBaseInfIr}{537.4} \newcommand{\rsBaseSstarIr}{ |
| 556.4 | 1 | d{\rsBaseStaySixtyQonlyCterm}{556.4} \newcommand{\rsBaseStaySixty |
| 561.5 | 1 | and{\rsBaseStaySixtyMigCterm}{561.5} \newcommand{\rsBaseStayOnet |
| 586.8 | 1 | } \newcommand{\rsBaseLBound}{586.8} \newcommand{\rsBaseQonlyCinf |
| 594.4 | 1 | {\rsBaseStayThirtyQonlyCterm}{594.4} \newcommand{\rsBaseStayThirt |
| 595.9 | 1 | nd{\rsBaseStayThirtyMigCterm}{595.9} \newcommand{\rsBaseStaySixt |
| 6.0325 | 1 | aseStayThreesixtyfiveQonlyDt}{6.0325} \newcommand{\rsBaseStayThree |
| 6.3317 | 1 | {\rsBaseStayOnetwentyQonlyDt}{6.3317} \newcommand{\rsBaseStayOnetw |
| 6.8936 | 1 | mand{\rsBaseStaySixtyQonlyDt}{6.8936} \newcommand{\rsBaseStaySixty |
| 6.9 | 1 | xGapFourThousand}{\ensuremath{6.9\times10^{-9}}} \newcommand{\r |
| 61.839 | 1 | nd{\rsBaseStaySevenQonlyTend}{61.839} \newcommand{\rsBaseStaySeven |
| 619.5 | 1 | rsBaseStayFourteenQonlyCterm}{619.5} \newcommand{\rsBaseStayFourt |
| 62.059 | 1 | mand{\rsBaseStaySevenMigTend}{62.059} \newcommand{\rsBaseStaySeven |
| 620.5 | 1 | {\rsBaseStayFourteenMigCterm}{620.5} \newcommand{\rsBaseStayThir |
| 628.6 | 1 | 为人}\\ 仅减少接触 & 36.26 & 64.13 & 628.6 & 40.9 & 11.9390 & 1.02\\ 显式族 ／ 仅减少接触 & \rsBaseConlyCinfNr & 628.6 & \rsBaseLBound & \rsBaseConl |
| 629.5 | 1 | ewcommand{\rsBaseConlyCinfNr}{629.5} \newcommand{\rsBaseConlyBelo |
| 631.7 | 1 | StayThreesixtyfiveConlyCterm}{631.7} \newcommand{\rsBaseStayThree |
| 637.4 | 1 | sBaseStayOnetwentyConlyCterm}{637.4} \newcommand{\rsBaseStayOnetw |
| 64.587 | 1 | eStayThreesixtyfiveConlyTend}{64.587} \newcommand{\rsBaseStayThree |
| 644.4 | 1 | d{\rsBaseStaySixtyConlyCterm}{644.4} \newcommand{\rsBaseStaySixty |
| 65.401 | 1 | rsBaseStayOnetwentyConlyTend}{65.401} \newcommand{\rsBaseStayOnetw |
| 654.4 | 1 | {\rsBaseStayThirtyConlyCterm}{654.4} \newcommand{\rsBaseStayThirt |
| 655.3 | 1 | d{\rsBaseStaySevenQonlyCterm}{655.3} \newcommand{\rsBaseStaySeven |
| 657.5 | 1 | and{\rsBaseStaySevenMigCterm}{657.5} \newcommand{\rsBaseStayFour |
| 66.344 | 1 | nd{\rsBaseStaySixtyConlyTend}{66.344} \newcommand{\rsBaseStaySixty |
| 663.76 | 1 | {\rsXianStayOnetwentyConlyDt}{663.76} \newcommand{\rsXianStayOnetw |
| 665.8 | 1 | rsBaseStayFourteenConlyCterm}{665.8} \newcommand{\rsBaseStayFourt |
| 67.491 | 1 | d{\rsBaseStayThirtyConlyTend}{67.491} \newcommand{\rsBaseStayThirt |
| 672.5 | 1 | d{\rsBaseStaySevenConlyCterm}{672.5} \newcommand{\rsBaseStaySeven |
| 68.347 | 1 | \rsBaseStayFourteenConlyTend}{68.347} \newcommand{\rsBaseStayFourt |
| 68.515 | 1 | nd{\rsBaseStaySevenConlyTend}{68.515} \newcommand{\rsBaseStaySeven |
| 7.4 | 1 | ClosedFormRelMax}{\ensuremath{7.4\times10^{-13}}} \renewcom |
| 7.5 | 1 | r$ 越大，切换越早。$r$ 超过约 $13$（基准）或 $7.5$（西安）后，仅隔离段消失，整个阈值控制期都两者并用；转折所 |
| 7.9829 | 1 | sBaseStayThreesixtyfiveMigDt}{7.9829} \newcommand{\rsBaseStayThree |
| 70.725 | 1 | d{\rsXianStayOnetwentyQonlyJ}{70.725} \newcommand{\rsXianStayOnetw |
| 712.5 | 1 | } \newcommand{\rsBaseSstarIr}{712.5} \newcommand{\rsBaseIrCostGap |
| 72.740 | 1 | and{\rsXianStayOnetwentyMigJ}{72.740} \newcommand{\rsXianStayOnetw |
| 72.828 | 1 | d{\rsBaseStayFourteenMigTend}{72.828} \newcommand{\rsBaseStayFourt |
| 736.65 | 1 | nd{\rsXianStaySevenQonlyTend}{736.65} \newcommand{\rsXianStaySeven |
| 74.128 | 1 | \rsBaseStayFourteenQonlyTend}{74.128} \newcommand{\rsBaseStayFourt |
| 772.92 | 1 | mand{\rsXianStaySixtyConlyDt}{772.92} \newcommand{\rsXianStaySixty |
| 793.04 | 1 | mand{\rsXianStaySevenMigTend}{793.04} \newcommand{\rsXianStaySeven |
| 8.2376 | 1 | 1} \newcommand{\rsBaseOptJIr}{8.2376} \newcommand{\rsBaseOptKqIr}{ |
| 8.5132 | 1 | nd{\rsBaseStayOnetwentyMigDt}{8.5132} \newcommand{\rsBaseStayOnetw |
| 8.6 | 1 | xGapFourThousand}{\ensuremath{8.6\times10^{-9}}} \newcommand{\r |
| 8.9041 | 1 | and{\rsBaseStayThirtyQonlyDt}{8.9041} \newcommand{\rsBaseStayThirt |
| 8.9893 | 1 | \newcommand{\rsBaseAlphaJIr}{8.9893} \newcommand{\rsBaseAlphaKqIr |
| 827.91 | 1 | and{\rsXianStayThirtyConlyDt}{827.91} \newcommand{\rsXianStayThirt |
| 853.24 | 1 | \rsXianStayFourteenQonlyTend}{853.24} \newcommand{\rsXianStayFourt |
| 857.25 | 1 | d{\rsXianStayFourteenConlyDt}{857.25} \newcommand{\rsXianStayFourt |
| 870.08 | 1 | mand{\rsXianStaySevenConlyDt}{870.08} \newcommand{\rsXianStaySeven |
| 882.91 | 1 | \newcommand{\rsXianConlyDtIr}{882.91} \newcommand{\rsXianConlyJIr} |
| 9.4077 | 1 | \newcommand{\rsBaseQonlyJIr}{9.4077} \newcommand{\rsBaseQonlyKqIr |
| 9.5029 | 1 | ommand{\rsBaseStaySixtyMigDt}{9.5029} \newcommand{\rsBaseStaySixty |
| 907.20 | 1 | d{\rsXianStayFourteenMigTend}{907.20} \newcommand{\rsXianStayFourt |
