# 定理类陈述与证明的变化

- 旧稿：332091f:paper/flatten_curve_analysis_cn.tex 332091f:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 43 条，新稿 42 条；共同 40 条，其中未变化 35 条，有变化 5 条。

只在旧稿中（新稿中找不到该标签的陈述，需说明去向）：rem:joint:duration-constraint、prop:joint:duration-frontier、rem:joint:headcount-cost

只在新稿中（新增或改了首个标签）：lem:proof:fold-free、lem:sup:upper-set

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:cost-minimum

```diff
@@ -10,3 +10,2 @@
-对每个 $S>S_c$，只需比较 $c^{-}(S)$、$c^{+}(S)$ 与区间内 $f(S,\cdot)$ 的全部驻点处的 $f$ 值。
-驻点方程可化为关于 $c$ 的五次多项式方程（附录式\eqref{eq:joint:stationary}），故候选至多七个，重复的端点与重根只计一次。
-$S=S_c$ 时允许区间退化为 $c=c_0$，无需求根。
+对每个 $S>S_c$，只需比较 $c^{-}(S)$、$c^{+}(S)$ 与区间内 $f(S,\cdot)$ 的全部驻点处的 $f$ 值；
+驻点方程可化为关于 $c$ 的五次多项式方程（附录式\eqref{eq:joint:stationary}）。
```

### prop:joint:global-structure

```diff
@@ -9,0 +10 @@
+考虑满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 的能力约束（并设式\eqref{eq:joint:feasibility}成立）时，$\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的成本最优控制同样满足这两条结论。
```

### prop:joint:terminal-allocation

```diff
@@ -1,2 +1,4 @@
-设 $w_c,w_q>0$，不考虑能力约束。
-任一逐状态最小化选择在充分接近退出状态的 $S>S_c$ 上满足
+设 $w_c,w_q>0$。
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 不考虑能力约束时，任一逐状态最小化选择在充分接近退出状态的 $S>S_c$ 上满足
@@ -16,3 +18,4 @@
-因此，最小成本严格小于仅减少接触与仅隔离控制各自的成本。
-加入满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 的能力约束后，式\eqref{eq:joint:terminal-interior}--\eqref{eq:joint:terminal-ratio}仍成立；
-与某一种单控制的严格成本比较，在该单控制整段可行时仍成立。
+\item 因此，不考虑能力约束时，最小成本严格小于仅减少接触与仅隔离控制各自的成本。
+\item 加入满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 的能力约束后，式\eqref{eq:joint:terminal-interior}--\eqref{eq:joint:terminal-ratio}仍成立；
+(ii) 中与某一种单控制的严格成本比较，在该单控制整段可行时仍成立。
+\end{enumerate}
```

### prop:joint:minimum-threshold

```diff
@@ -2 +2,3 @@
-在控制被触发且满足式\eqref{eq:joint:feasibility}的阈值范围内，记 $J_{\min}(\eta)$ 为式\eqref{eq:joint:minimum-cost}的最小值，则 $J_{\min}$ 随 $\eta$ 严格下降。
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 在控制被触发且满足式\eqref{eq:joint:feasibility}的阈值范围内，记 $J_{\min}(\eta)$ 为式\eqref{eq:joint:minimum-cost}的最小值，则 $J_{\min}$ 随 $\eta$ 严格下降；
@@ -4 +6,2 @@
-固定阈值时，降低 $c_{\min}$ 或提高 $q_{\rm cap}$ 不会增大最小成本。
+\item 固定阈值时，降低 $c_{\min}$ 或提高 $q_{\rm cap}$ 不会增大最小成本。
+\end{enumerate}
```

### prop:sup:rhat

```diff
@@ -5,0 +6,2 @@
+$r<\hat r$ 时 $c_0$ 在 $S=S_{\rm sw}$ 处也是唯一全局最小点；
+$r=\hat r$ 时它在该处与 $c=c_0S_c/(S_{\rm sw}-S_c)$ 并列全局最优。
```

## 证明

有证明的陈述：旧稿 24 条，新稿 26 条；证明有变化 2 条。

- prop:sup:rhat：汉字 166 → 105

```diff
@@ -1,9 +1 @@
-沿用正文附录~\ref{sec:proof:cost-structure}的记号 $\zeta,p,G=A+rB$。
-先证上集性：
-若 $p=\zeta_0$ 是 $G(\cdot;\zeta_0)$ 的全局最小点，则对任意 $\zeta_1>\zeta_0$，$p=\zeta_1$ 是 $G(\cdot;\zeta_1)$ 的唯一全局最小点。
-由正文命题~\ref{prop:joint:global-structure}，$\zeta_0\ge\zeta_{\rm sw}$。
-对固定 $p<\zeta$，$A$ 关于 $\zeta$ 严格增；
-$B$ 与 $\zeta$ 无关，且 $B'(p)=-(p-1)(p^2-3p+2b)/[p^3(p-b)^2]$，故 $B$ 在 $[\zeta_{\rm sw},\infty)$ 上严格减。
-$p\le\zeta_0$ 时，$G(p;\zeta_1)>G(p;\zeta_0)\ge rB(\zeta_0)\ge rB(\zeta_1)=G(\zeta_1;\zeta_1)$；
-$\zeta_0<p<\zeta_1$ 时，$G(p;\zeta_1)\ge rB(p)>rB(\zeta_1)$。
-再看 $S_{\rm sw}$ 处。
+先看 $S_{\rm sw}$ 处。
@@ -18 +10 @@
-两种情形下，由上集性，对一切 $S>S_{\rm sw}$，$c_0$ 都是唯一全局最小点。
+两种情形下，由引理~\ref{lem:sup:upper-set}，对一切 $S>S_{\rm sw}$，$c_0$ 都是唯一全局最小点。
```

- prop:sup:jump：汉字 661 → 652

```diff
@@ -24 +24 @@
-$\zeta\ge\zeta_{\rm sw}$ 时，由命题~\ref{prop:sup:rhat}及其证明（含 $\zeta=\zeta_{\rm sw}$），右端点是唯一全局最小点；
+$\zeta\ge\zeta_{\rm sw}$ 时，由命题~\ref{prop:sup:rhat}，右端点是唯一全局最小点；
@@ -32 +32 @@
-由命题~\ref{prop:sup:rhat}证明中的上集性，$\zeta\in\Omega$ 蕴含 $\zeta'>\zeta$ 时 $p=\zeta'$ 是唯一全局最小点。
+由引理~\ref{lem:sup:upper-set}，$\zeta\in\Omega$ 蕴含 $\zeta'>\zeta$ 时 $p=\zeta'$ 是唯一全局最小点。
@@ -36 +36 @@
-由命题~\ref{prop:sup:rhat}，$\zeta_{\rm sw}\in\Omega$ 当且仅当 $r\le\hat r$，在本情形即 $r=\hat r$。
+由命题~\ref{prop:sup:rhat}与引理~\ref{lem:sup:upper-set}，$\zeta_{\rm sw}\in\Omega$ 当且仅当 $r\le\hat r$，在本情形即 $r=\hat r$。
@@ -43 +43 @@
-$r=\hat r$ 时 $\zeta_0=\zeta_{\rm sw}=\zeta_{\rm j}$，$k=\zeta_{\rm sw}^2/(\zeta_{\rm sw}-1)$，由式\eqref{eq:sup:jump-square}，全局最小点恰为 $\zeta_{\rm sw}$ 与 $a_0=\zeta_{\rm sw}/(\zeta_{\rm sw}-1)$。
+$r=\hat r$ 时 $\zeta_0=\zeta_{\rm sw}=\zeta_{\rm j}$，$k=\zeta_{\rm sw}^2/(\zeta_{\rm sw}-1)$，由式\eqref{eq:sup:jump-square}，全局最小点恰为 $\zeta_{\rm sw}$ 与 $p_0=\zeta_{\rm sw}/(\zeta_{\rm sw}-1)$。
@@ -48 +48 @@
-由上一段，这样的内部点只有一个，记为 $a_0$。
+由上一段，这样的内部点只有一个，记为 $p_0$。
@@ -50 +50 @@
-由第二个事实，$\zeta<\zeta_0$ 时最小点不大于 $a_0$，其极限点是 $\zeta_0$ 上不大于 $a_0$ 的最小点，只能是 $a_0$。
+由第二个事实，$\zeta<\zeta_0$ 时最小点不大于 $p_0$，其极限点是 $\zeta_0$ 上不大于 $p_0$ 的最小点，只能是 $p_0$。
```

