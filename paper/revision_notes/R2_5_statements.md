# 定理类陈述与证明的变化

- 旧稿：pre-rewrite-20261007:paper/sections/05_quadratic_cost.tex
- 新稿：paper/sections/05_quadratic_cost.tex

带标签的陈述：旧稿 5 条，新稿 5 条；共同 5 条，其中未变化 0 条，有变化 5 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:cost-minimum

```diff
@@ -1 +1,3 @@
-在规定的全部有界可测阈值控制中，二次成本最小值可达到，且
+不考虑能力约束时取 $\underline c(S)=c_0S_c/S$、$\overline c(S)=c_0$（式\eqref{eq:joint:contact-range}）；
+考虑能力约束时取式\eqref{eq:joint:bounds}，并设式\eqref{eq:joint:feasibility}成立。
+在相应的控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中（不另加总时长、调整次数或控制变化率等约束），二次干预成本的最小值可以达到，且
@@ -8 +10 @@
-对于每个 $S>S_c$，只需比较 $\underline c(S),\overline c(S)$ 与区间内满足
+对每个 $S>S_c$，只需比较 $\underline c(S)$、$\overline c(S)$ 与区间内满足
@@ -19,2 +21 @@
-该方程为五次多项式方程，故候选点至多七个；
-重复端点与重根只计一次。
+该方程是五次多项式方程，故候选至多七个，重复的端点与重根只计一次。
```

### prop:joint:minimum-threshold

```diff
@@ -1 +1 @@
-固定 $N,S_0,I_0,\beta,\gamma,c_0,q_0$ 及能力界限。
+固定 $N,S_0,I_0,\beta,\gamma,c_0,q_0$ 及能力约束。
@@ -3,2 +3,2 @@
-对于任意两个可行阈值，可以选择类内最小成本分配，使其在共同经过的易感者状态上采用相同的 $c_c^*(S),q_c^*(S)$。
-固定阈值时，降低 $c_{\min}$ 或提高 $q_{\rm cap}$ 不会增大类内最小成本。
+对于任意两个可行阈值，可以选取成本最优控制，使二者在共同经过的易感者状态上采用相同的 $c_c^*(S),q_c^*(S)$。
+固定阈值时，降低 $c_{\min}$ 或提高 $q_{\rm cap}$ 不会增大最小成本。
```

### prop:joint:terminal-allocation

```diff
@@ -1,2 +1,2 @@
-采用式\eqref{eq:cost:J}的权重 $1,2$。
-无额外能力限制时，任一逐状态最小化选择在充分接近退出状态的 $S>S_c$ 上满足
+采用默认权重 $w_c=1$、$w_q=2$，不考虑能力约束。
+任一逐状态最小化选择在充分接近退出状态的 $S>S_c$ 上满足
@@ -7,2 +7 @@
-即两种干预均严格强于常规水平。
-而且
+即两种干预均严格强于常规水平，并且
@@ -17,3 +16,3 @@
-因此，类内最小成本严格小于仅减少接触和仅隔离控制两种策略各自的成本。
-加入满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 的固定能力限制后，式\eqref{eq:joint:terminal-interior}--\eqref{eq:joint:terminal-ratio}仍成立；
-与某一种单控制的严格成本比较仅在该单控制整段可行时使用。
+因此，最小成本严格小于仅减少接触与仅隔离控制各自的成本。
+加入满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 的能力约束后，式\eqref{eq:joint:terminal-interior}--\eqref{eq:joint:terminal-ratio}仍成立；
+与某一种单控制的严格成本比较，在该单控制整段可行时仍成立。
```

### prop:joint:global-structure

```diff
@@ -1,4 +1,8 @@
-设 $w_c,w_q>0$，且无额外能力限制。
-对每个 $S\in(S_c,S^*]$，仅减少接触的取值 $c=c_0S_c/S$ 不是 $f(S,\cdot)$ 在允许区间 $[c_0S_c/S,c_0]$ 上的局部最小点。
-仅隔离控制的取值 $c=c_0$ 在 $S>S_{\rm sw}$ 时是相对于该区间的严格局部最小点，在 $S<S_{\rm sw}$ 时不是局部最小点。
-因此，任一实现类内最小成本的控制在几乎所有 $S\in(S_c,S^*]$ 上满足 $q_c^*(S)>q_0$；
+设 $w_c,w_q>0$，不考虑能力约束。
+对每个 $S\in(S_c,S^*]$，在允许区间 $[c_0S_c/S,c_0]$ 上：
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 仅减少接触的取值 $c=c_0S_c/S$ 不是 $f(S,\cdot)$ 的局部最小点；
+\item 仅隔离控制的取值 $c=c_0$ 在 $S>S_{\rm sw}$ 时是严格局部最小点，在 $S<S_{\rm sw}$ 时不是局部最小点。
+\end{enumerate}
+因此，任一成本最优控制在几乎所有 $S\in(S_c,S^*]$ 上满足 $q_c^*(S)>q_0$；
```

### rem:joint:duration-constraint

```diff
@@ -2 +2 @@
-对 $\kappa\in\mathbb R$，将 $f(S,c)$ 换为
+对 $\kappa\in\mathbb R$，把 $f(S,c)$ 换为
@@ -6,6 +6,6 @@
-即对 $J+\kappa\Delta t$ 逐状态最小化，定理\ref{thm:joint:cost-minimum}的存在性论证仍成立。
-记所得允许控制为 $c_\kappa$，并假设 $\Delta t[c_\kappa]=T$。
-当 $\kappa\ge0$ 时，它在时长上限约束 $\Delta t\le T$ 下使 $J$ 最小。
-当 $\kappa\le0$ 时，它在时长下限约束 $\Delta t\ge T$ 下使 $J$ 最小。
-对于等式约束 $\Delta t=T$，任意符号的 $\kappa$ 均给出这一充分条件。
-对满足相应约束的任一允许控制 $c_c$，有
+即对 $J+\kappa\Delta t$ 逐状态最小化，定理~\ref{thm:joint:cost-minimum}的存在性论证仍成立。
+设所得允许控制 $c_\kappa$ 满足 $\Delta t[c_\kappa]=T$。
+若 $\kappa\ge0$，它在时长上限约束 $\Delta t\le T$ 下使 $J$ 最小；
+若 $\kappa\le0$，它在时长下限约束 $\Delta t\ge T$ 下使 $J$ 最小；
+对等式约束 $\Delta t=T$，$\kappa$ 可取任意符号。
+这是因为满足相应约束的任一允许控制 $c_c$ 都有
@@ -15,3 +15,2 @@
-在 $0<\beta<1$ 时，由式\eqref{eq:joint:quarantine}，时长下限 $\Delta t\ge T$ 等价于阈值控制期新增隔离易感者人数不超过 $(1-\beta)[S^*-S_c-\gamma\eta T]$。
-上述充分条件不要求可达集凸，但不保证每个允许时长都有匹配的 $\kappa$。
-控制变化率或其他累计预算约束仍须另行处理。
+由式\eqref{eq:joint:quarantine}，时长下限 $\Delta t\ge T$ 等价于阈值控制期新增隔离易感者人数不超过 $(1-\beta)[S^*-S_c-\gamma\eta T]$。
+这一充分条件不要求可达集凸，但不保证每个允许时长都有匹配的 $\kappa$。
```

## 证明

有证明的陈述：旧稿 1 条，新稿 1 条；证明有变化 1 条。

- prop:joint:minimum-threshold：汉字 161 → 158

```diff
@@ -1,4 +1,3 @@
-记
-$m(S)=\min_{\underline c(S)\le c\le\overline c(S)}f(S,c)$。
-被积函数及允许界限均不含 $\eta$，且 $m$ 连续。
-对于 $S>S_c$，两项强度不可能同时为零，故 $m(S)>0$。
+记 $m(S)=\min_{\underline c(S)\le c\le\overline c(S)}f(S,c)$。
+被积函数与允许界限都不含 $\eta$，且 $m$ 连续；
+对 $S>S_c$，两项强度不能同时为零，故 $m(S)>0$。
@@ -9 +8 @@
-由 $\partial S^*/\partial\eta<0$，在可行区间内部有
+由 $\partial S^*/\partial\eta<0$（引理~\ref{lem:s1:Sstar-sensitivity}），在可行区间内部有
@@ -15,3 +14,3 @@
-端点处的严格比较也可直接由两个积分的上下限和正系数得到。
-将较低阈值下的逐状态最小化选择限制到较高阈值所经过的区间，仍在每个状态达到同一 $m(S)$，故产生兼容的最优控制。
-最后，扩大任一实施能力使每个状态的允许区间包含原区间，其最小被积函数值不增，积分后即得最后的结论。
+端点处的严格比较可直接由两个积分的上下限和正系数得到。
+把较低阈值下的逐状态最小化选择限制到较高阈值经过的区间上，它在每个状态仍达到 $m(S)$，即得兼容的成本最优控制。
+最后，放宽任一能力约束使每个状态的允许区间包含原区间，最小被积函数值不增，积分即得最后的结论。
```

