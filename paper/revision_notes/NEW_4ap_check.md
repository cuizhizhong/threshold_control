# check_tex 报告

- 旧稿：pre-capacity-cut-20261115:paper/flatten_curve_analysis_cn.tex, pre-capacity-cut-20261115:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex, paper/flatten_curve_supplement_cn.tex

## 1 标签与交叉引用

- 旧稿有、新稿缺的标签（12）：cor:joint:allocation-range、cor:joint:capacity-clip、cor:joint:capped-comparison、cor:joint:feasibility、cor:joint:single-endpoints、eq:joint:allocation-range、eq:joint:bounds、eq:joint:capacity-clip、eq:joint:capped-duration、eq:joint:feasibility、fig:joint:capacity、sec:joint:capacity-numerics
- 新稿中悬空的引用（0）：无
- 新稿中重复定义的标签（0）：无

## 2 参考文献

- 新稿引用了但 bib 中没有（0）：无
- bib 中有但新稿未引用（13）：Arnouss2026Isolation、Aumann1965、Baas2021Occupancy、Balakrishnan2023、Chen2021ICUForecast、Fraser2004Controllable、Ketcheson2021Finite、Kucharski2020、Pung2023Undetected、ShaanxiHealth2022、Wang2023XianSevere、Zhang2026Behavior、Zheng2023ICUBeds

## 3 数值字面量（多重集合比较）

旧稿 539 个，新稿 533 个；旧稿有、新稿缺 16 个；新稿新增 10 个。

### 旧稿有、新稿缺

| 数字 | 缺少次数 | 旧稿中的上下文（最多 3 处） |
|---|---:|---|
| 0.5 | 2 | 其余参数同图~ ；标记形状区分 $\eta/N=0.2\%,0.5\%,1\%,2\%,5\%$。时间与成本以天计，累计新增感 ／ 允许范围见补充材料第~ ~节。第~ ~节用 $\alpha=0.5$ 作对照；后文的最优控制则在全部满足式 的 $c_c(S) ／ 四种控制。控制时长从长到短依次为仅减少接触、$\alpha=0.5$、成本最优控制与仅隔离控制；由定理~ (iv)与推论~ ， |
| 12 | 2 | ) 成本 $J$ 对总累计新增感染。$c_0=5,8,10,12\ \mathrm d^{-1}$ 各一条曲线（颜色区分）， ／ Tang 和 Xiao 的工作 。观测窗口为 2021 年 12 月 9 日至 2022 年 1 月 17 日的 40 个日 ／ _0=N-I_0$，时间原点 $t=0$ 为 2021 年 12 月 9 日的开始，并用最小二乘估计 $I_0$。拟合准则为 |
| 0.6 | 1 | $c_{\min}/c_0=0.5$、$q_{\max}=0.6$。(b) 该代表点上能力约束下的成本最优控制：蓝线为隔离比 ／ 常规接触率 $c_0$ 的变化，$\eta/N=0.2\%,0.6\%,1\%,2\%$ 的曲线依次为绿色、品红色、蓝色和黑色 ／ 黑色；(b) $c_0=10$，$\eta/N=0.2\%,0.6\%,1\%,2\%$ 的曲线依次为绿色、品红色、蓝色和黑色 |
| 0.75 | 1 | $c_{\min}/c_0=0.5$、$q_{\max}=0.75$。(b) 固定 $w_c=1$、改变 $r=w_q/w_c |
| 1.8 | 1 | \newcommand{\nrConvExitMax}{1.8\times10^{-7}} \newcommand{\ |
| 1.94 | 1 | 增加的成本与时长全部来自能力约束起作用的前一段。启动后约 $1.94$ d 内，隔离比例停在上限，接触率同时降低，降幅从启动时的 |
| 2.361 | 1 | 了控制期：能力约束下的成本最优控制给出 $J\approx 2.361$ d、$\Delta t\approx 8.34$ d，都 |
| 234.4 | 1 | rox 84.06$ d、$\Delta t\approx 234.4$ d，都高于表~ 中的值（启动后约 $61.64$ d 内 |
| 39.1 | 1 | 内，隔离比例停在上限，接触率同时降低，降幅从启动时的约 $39.1\%$ 随 $S$ 下降而减小（图~ (b)）；易感者降到 |
| 4.6 | 1 | newcommand{\nrConvPlateauMax}{4.6\times10^{-9}} \newcommand{\ |
| 61.64 | 1 | prox 234.4$ d，都高于表~ 中的值（启动后约 $61.64$ d 内隔离比例停在上限）。TDINN 重构的干预使隔离比 |
| 75.3 | 1 | approx0.7565$，仅减少接触需要把接触率降低约 $75.3\%$，都超出能力。因此由推论~ ，最快与最慢的控制 $c^ |
| 8.34 | 1 | rox 2.361$ d、$\Delta t\approx 8.34$ d，都高于表~ 中的值。最小成本的增加与命题~ (ii) |
| 84.06 | 1 | 控制可行；能力约束下的成本最优控制给出 $J\approx 84.06$ d、$\Delta t\approx 234.4$ d， |

### 新稿新增

| 数字 | 新增次数 | 新稿中的上下文（最多 3 处） |
|---|---:|---|
| 10 | 3 | $\gamma=\delta_q=0.3504$，$c_0=10$，$q_0=0.01526$，$\eta=0.05N=38 ／ 制时长和成本成倍增加，总累计新增感染的降幅却较小。$c_0=10$ 时把 $\eta/N$ 从 $2\%$ 降到 $0.2\ ／ (b) 成本 $J$ 对总累计新增感染。$c_0=5,8,10,12\ \mathrm d^{-1}$ 各一条曲线（颜色区 |
| 0.39 | 1 | ewcommand{\nrXianWtTenStartQ}{0.39} \renewcommand{\bottomf |
| 1.3 | 1 | newcommand{\nrConvPlateauMax}{1.3\times10^{-9}} \newcommand{\ ／ \newcommand{\nrConvMassMax}{1.3\times10^{-6}} \newcommand{\ |
| 2.63 | 1 | 在 $S_{\rm sw}$ 处由仅隔离转为两者并用。$r=2.63$ 介于 $r_{\rm cont}$ 与 $\hat r$ |
| 2.99 | 1 | wcommand{\nrXianWtFourSwitch}{2.99} \newcommand{\nrXianWtFourC |
| 3.8 | 1 | \newcommand{\nrConvExitMax}{3.8\times10^{-8}} \newcommand{\ |
| 56 | 1 | wcommand{\nrXianWtFourCutPct}{56} \newcommand{\nrXianWtTenCu |
| 75 | 1 | ewcommand{\nrXianWtTenCutPct}{75} \newcommand{\nrXianWtTenSt |
