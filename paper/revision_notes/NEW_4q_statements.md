# 定理类陈述与证明的变化

- 旧稿：e321645:paper/flatten_curve_analysis_cn.tex e321645:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 42 条，新稿 42 条；共同 42 条，其中未变化 35 条，有变化 7 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:cost-minimum

```diff
@@ -1,3 +1,5 @@
-不考虑能力约束时取 $c^{-}(S)=c_0S_c/S$、$c^{+}(S)=c_0$（式\eqref{eq:joint:contact-range}）；
-考虑能力约束时取式\eqref{eq:joint:bounds}，并设式\eqref{eq:joint:feasibility}成立。
-在相应的控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中，二次干预强度成本的最小值可以达到，且
+考虑能力约束时设式\eqref{eq:joint:feasibility}成立。
+在 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中：
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 二次干预强度成本的最小值可以达到，且
@@ -7 +9 @@
-\min_{c^{-}(S)\le c\le c^{+}(S)}f(S,c)\,dS.
+\min_{c^{-}(S)\le c\le c^{+}(S)}f(S,c)\,dS;
@@ -9,3 +11,3 @@
-允许函数 $c_c^*(S)$ 达到该值，当且仅当它几乎处处属于相应的一维最小化解集。
-对每个 $S>S_c$，只需比较 $c^{-}(S)$、$c^{+}(S)$ 与区间内 $f(S,\cdot)$ 的全部驻点处的 $f$ 值；
-驻点方程可化为关于 $c$ 的五次多项式方程（附录式\eqref{eq:joint:stationary}）。
+\item 允许控制 $c_c$ 达到最小值，当且仅当对几乎所有 $S$，$c_c(S)$ 是 $f(S,\cdot)$ 在允许区间上的最小点；
+\item 对每个 $S>S_c$，这样的最小点只能是 $c^{-}(S)$、$c^{+}(S)$ 或区间内 $f(S,\cdot)$ 的驻点，驻点方程可化为关于 $c$ 的五次多项式方程（附录式\eqref{eq:joint:stationary}）。
+\end{enumerate}
```

### thm:joint:cost-structure

```diff
@@ -2,4 +2,8 @@
-对每个 $S>S_c$，$f(S,\cdot)$ 在 $[c_0S_c/S,c_0]$ 上的最小点 $c_c^*(S)$ 唯一；
-$c_c^*$ 在 $(S_c,\infty)$ 上连续，且 $S\downarrow S_c$ 时 $c_c^*(S)\to c_0$；
-$S\ge S_{\rm sw}$ 时 $c_c^*(S)=c_0$，$S_c<S<S_{\rm sw}$ 时 $c_0S_c/S<c_c^*(S)<c_0$。
-因此，成本最优控制几乎处处唯一，可取为连续的状态反馈 $c_c^*$：
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 对每个 $S>S_c$，$f(S,\cdot)$ 在 $[c_0S_c/S,c_0]$ 上有唯一最小点 $c_c^*(S)$；
+$c_c^*$ 在 $(S_c,\infty)$ 上连续，且 $S\downarrow S_c$ 时 $c_c^*(S)\to c_0$。
+\item $S\ge S_{\rm sw}$ 时 $c_c^*(S)=c_0$；
+$S_c<S<S_{\rm sw}$ 时 $c_0S_c/S<c_c^*(S)<c_0$。
+\end{enumerate}
+因此，成本最优控制几乎处处等于连续的状态反馈 $c_c^*$：
```

### prop:joint:global-structure

```diff
@@ -1,2 +1,2 @@
-设 $w_c,w_q>0$，不考虑能力约束。
-对每个 $S\in(S_c,S^*]$，在允许区间 $[c_0S_c/S,c_0]$ 上：
+设 $w_c,w_q>0$，不考虑能力约束，$S\in(S_c,S^*]$。
+在允许区间 $[c_0S_c/S,c_0]$ 上：
@@ -8,3 +8,2 @@
-因此，任一成本最优控制在几乎所有 $S\in(S_c,S^*]$ 上满足 $q_c^*(S)>q_0$；
-在 $S_c<S<\min\{S_{\rm sw},S^*\}$ 上还满足 $c_0S_c/S<c_c^*(S)<c_0$，即两种措施同时强于常规水平。
-考虑满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 的能力约束（并设式\eqref{eq:joint:feasibility}成立）时，$\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的成本最优控制同样满足这两条结论。
+因此，任一成本最优控制在几乎所有 $S\in(S_c,S^*]$ 上满足 $q_c^*(S)>q_0$，在几乎所有 $S\in(S_c,\min\{S_{\rm sw},S^*\})$ 上满足 $c_0S_c/S<c_c^*(S)<c_0$，即两种措施同时强于常规水平。
+考虑满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 与式\eqref{eq:joint:feasibility}的能力约束时，$\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的成本最优控制同样满足这两条结论。
```

### prop:joint:terminal-allocation

```diff
@@ -1 +1 @@
-设 $w_c,w_q>0$。
+设 $w_c,w_q>0$，$c_c^*$ 为任一逐状态最小化选择。
@@ -4 +4 @@
-\item 不考虑能力约束时，任一逐状态最小化选择在充分接近退出状态的 $S>S_c$ 上满足
+\item 不考虑能力约束时，存在 $\delta>0$，使 $S_c<S<S_c+\delta$ 时
@@ -9 +9,2 @@
-即两种干预均严格强于常规水平，并且
+即两种干预均严格强于常规水平；
+并且
@@ -18,2 +19,2 @@
-\item 因此，不考虑能力约束时，最小成本严格小于仅减少接触与仅隔离控制各自的成本。
-\item 加入满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 的能力约束后，式\eqref{eq:joint:terminal-interior}--\eqref{eq:joint:terminal-ratio}仍成立；
+\item 不考虑能力约束时，最小成本严格小于仅减少接触与仅隔离控制各自的成本。
+\item 考虑满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 的能力约束时，(i) 仍成立；
```

### prop:joint:minimum-threshold

```diff
@@ -1 +1 @@
-固定 $N,S_0,I_0,\beta,\gamma,c_0,q_0$ 及能力约束。
+固定 $N,S_0,I_0,\beta,\gamma,c_0,q_0$ 与能力约束，记 $J_{\min}(\eta)$ 为阈值 $\eta$ 下式\eqref{eq:joint:minimum-cost}的最小值。
@@ -4,2 +4,2 @@
-\item 在控制被触发且满足式\eqref{eq:joint:feasibility}的阈值范围内，记 $J_{\min}(\eta)$ 为式\eqref{eq:joint:minimum-cost}的最小值，则 $J_{\min}$ 随 $\eta$ 严格下降；
-对于任意两个可行阈值，可以选取成本最优控制，使二者在共同经过的易感者状态上采用相同的 $c_c^*(S),q_c^*(S)$。
+\item 在控制被触发且式\eqref{eq:joint:feasibility}成立的阈值范围内，$J_{\min}$ 随 $\eta$ 严格下降；
+对其中任意两个阈值，可以选取成本最优控制，使二者在共同经过的易感者状态上取相同的 $c_c^*(S)$ 与 $q_c^*(S)$。
```

### cor:joint:capacity-clip

```diff
@@ -2 +2 @@
-则 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的成本最优控制几乎处处唯一，为
+则 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的成本最优控制几乎处处等于
```

### prop:joint:weight-monotone

```diff
@@ -1 +1,2 @@
-固定 $w_c>0$ 与允许控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$（后者设式\eqref{eq:joint:feasibility}成立），记 $c_r^*$、$q_r^*$ 为 $r=w_q/w_c$ 时的任一逐状态最小化选择。
+固定 $w_c>0$ 与控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$（后者设式\eqref{eq:joint:feasibility}成立）。
+对 $r=w_q/w_c$，记 $c_r^*$ 为任一逐状态最小化选择，$q_r^*$ 为相应的隔离比例。
@@ -4,2 +5,2 @@
-\item 若 $0<r_1<r_2$，则对每个 $S\in(S_c,S^*]$，$c_{r_2}^*(S)\le c_{r_1}^*(S)$，$q_{r_2}^*(S)\le q_{r_1}^*(S)$。
-因此，控制时长与阈值控制期累计新增感染随 $r$ 不减，新增隔离易感者人数随 $r$ 不增；
+\item 若 $0<r_1<r_2$，则对每个 $S\in(S_c,S^*]$ 有 $c_{r_2}^*(S)\le c_{r_1}^*(S)$、$q_{r_2}^*(S)\le q_{r_1}^*(S)$。
+因此，成本最优控制的控制时长与阈值控制期累计新增感染随 $r$ 不减，新增隔离易感者人数随 $r$ 不增；
```

## 证明

有证明的陈述：旧稿 26 条，新稿 26 条；证明有变化 1 条。

- lem:proof:fold-free：汉字 94 → 103

```diff
@@ -9 +9 @@
-在 $s\in(\sqrt2,2)$ 上，常数项随 $s$ 增，不小于 $9(\sqrt2-1)$；
+在 $s\in(\sqrt2,2)$ 上，$Q$ 的常数项随 $s$ 增，不小于 $9(\sqrt2-1)$；
@@ -14,2 +14,2 @@
-对 $0<s<s_c$：
-$F$ 是 $s$ 的二次式且 $F(p;0)=p^3>0$。
+再看 $0<s<s_c$。
+$F$ 是 $s$ 的二次式，且 $F(p;0)=p^3>0$。
@@ -17 +17 @@
-若 $X(p)>0$ 且 $F$ 有实根 $s_1\le s_2$，则 $X\le b^2w^2/p$，于是
+若 $X(p)>0$ 且 $F$ 有实根 $s_1\le s_2$，则判别式非负给出 $X\le b^2w^2/p$，于是
```

