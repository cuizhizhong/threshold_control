# 定理类陈述与证明的变化

- 旧稿：pre-capacity-cut-20261115:paper/sections/05_quadratic_cost.tex
- 新稿：paper/sections/05_quadratic_cost.tex

带标签的陈述：旧稿 7 条，新稿 6 条；共同 6 条，其中未变化 0 条，有变化 6 条。

只在旧稿中（新稿中找不到该标签的陈述，需说明去向）：cor:joint:capacity-clip

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:cost-minimum

```diff
@@ -1,3 +1 @@
-设条件\eqref{eq:model:trigger}成立；
-考虑能力约束时另设式\eqref{eq:joint:feasibility}成立。
-在 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\max})$ 中：
+设条件\eqref{eq:model:trigger}成立，则在 $\mathcal A(\eta)$ 中：
@@ -10 +8 @@
-\min_{c^{-}(S)\le c\le c^{+}(S)}f(S,c)\,dS;
+\min_{c_0S_c/S\le c\le c_0}f(S,c)\,dS;
@@ -13 +11 @@
-\item 对每个 $S>S_c$，这样的最小点只能是 $c^{-}(S)$、$c^{+}(S)$ 或区间内 $f(S,\cdot)$ 的驻点，驻点方程可化为关于 $c$ 的五次多项式方程（附录式\eqref{eq:joint:stationary}）。
+\item 对每个 $S>S_c$，这样的最小点只能是端点 $c_0S_c/S$、$c_0$ 或区间内 $f(S,\cdot)$ 的驻点，驻点方程可化为关于 $c$ 的五次多项式方程（附录式\eqref{eq:joint:stationary}）。
```

### thm:joint:cost-structure

```diff
@@ -1 +1 @@
-设条件\eqref{eq:model:trigger}成立，$0<r\le r_{\rm cont}$，不考虑能力约束，则
+设条件\eqref{eq:model:trigger}成立，$0<r\le r_{\rm cont}$，则
```

### prop:joint:global-structure

```diff
@@ -4,2 +4,2 @@
-\item 不考虑能力约束时，对每个 $S\in(S_c,S^*]$，仅减少接触的取值 $c=c_0S_c/S$ 不是 $f(S,\cdot)$ 在允许区间 $[c_0S_c/S,c_0]$ 上的局部最小点；
-\item 不考虑能力约束时，对 $S\in(S_c,S^*]$，仅隔离控制的取值 $c=c_0$ 在 $S>S_{\rm sw}$ 时是严格局部最小点，在 $S<S_{\rm sw}$ 时不是局部最小点；
+\item 对每个 $S\in(S_c,S^*]$，仅减少接触的取值 $c=c_0S_c/S$ 不是 $f(S,\cdot)$ 在允许区间 $[c_0S_c/S,c_0]$ 上的局部最小点；
+\item 对 $S\in(S_c,S^*]$，仅隔离控制的取值 $c=c_0$ 在 $S>S_{\rm sw}$ 时是严格局部最小点，在 $S<S_{\rm sw}$ 时不是局部最小点；
@@ -7 +6,0 @@
-\item 考虑满足 $c_{\min}<c_0$、$q_{\max}>q_0$ 与式\eqref{eq:joint:feasibility}的能力约束时，$\mathcal A(\eta;c_{\min},q_{\max})$ 中的成本最优控制同样满足 (iii) 的两条结论。
```

### prop:joint:terminal-allocation

```diff
@@ -4 +4 @@
-\item 不考虑能力约束时，存在 $\delta>0$，使 $S_c<S<S_c+\delta$ 时
+\item 存在 $\delta>0$，使 $S_c<S<S_c+\delta$ 时
@@ -19,3 +19 @@
-\item 不考虑能力约束时，最小成本严格小于仅减少接触与仅隔离控制各自的成本；
-\item 考虑满足 $c_{\min}<c_0$、$q_{\max}>q_0$ 的能力约束时，(i) 仍成立；
-(ii) 中与某一种单控制的严格成本比较，在该单控制整段可行时仍成立。
+\item 最小成本严格小于仅减少接触与仅隔离控制各自的成本；
```

### prop:joint:minimum-threshold

```diff
@@ -1,7 +1,3 @@
-固定 $N,S_0,I_0,\beta,\gamma,c_0,q_0$ 与能力约束，记 $J_{\min}(\eta)$ 为阈值 $\eta$ 下式\eqref{eq:joint:minimum-cost}的最小值。
-\begin{enumerate}
-\renewcommand{\labelenumi}{(\roman{enumi})}
-\item 在控制被触发且式\eqref{eq:joint:feasibility}成立的阈值范围内，$J_{\min}$ 随 $\eta$ 严格下降；
-对其中任意两个阈值，可以选取成本最优控制，使二者在共同经过的易感者状态上取相同的 $c_c^*(S)$ 与 $q_c^*(S)$；
-\item 固定阈值时，降低 $c_{\min}$ 或提高 $q_{\max}$ 不会增大最小成本。
-\end{enumerate}
+固定 $N,S_0,I_0,\beta,\gamma,c_0,q_0$，记 $J_{\min}(\eta)$ 为阈值 $\eta$ 下式\eqref{eq:joint:minimum-cost}的最小值。
+则在控制被触发的阈值范围内，$J_{\min}$ 随 $\eta$ 严格下降；
+对其中任意两个阈值，可以选取成本最优控制，使二者在共同经过的易感者状态上取相同的 $c_c^*(S)$ 与 $q_c^*(S)$。
```

### prop:joint:weight-monotone

```diff
@@ -1 +1 @@
-固定 $w_c>0$ 与控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\max})$（后者设式\eqref{eq:joint:feasibility}成立）。
+固定 $w_c>0$。
```

## 证明

有证明的陈述：旧稿 0 条，新稿 0 条；证明有变化 0 条。

