# 定理类陈述与证明的变化

- 旧稿：2d5cf6e:paper/sections/05_quadratic_cost.tex
- 新稿：paper/sections/05_quadratic_cost.tex

带标签的陈述：旧稿 7 条，新稿 7 条；共同 7 条，其中未变化 4 条，有变化 3 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:cost-minimum

```diff
@@ -1 +1,2 @@
-考虑能力约束时设式\eqref{eq:joint:feasibility}成立。
+设条件\eqref{eq:model:trigger}成立；
+考虑能力约束时另设式\eqref{eq:joint:feasibility}成立。
```

### thm:joint:cost-structure

```diff
@@ -1 +1 @@
-设 $0<r\le r_{\rm cont}$，不考虑能力约束。
+设条件\eqref{eq:model:trigger}成立，$0<r\le r_{\rm cont}$，不考虑能力约束，则
```

### prop:joint:global-structure

```diff
@@ -1,2 +1 @@
-设 $w_c,w_q>0$，不考虑能力约束，$S\in(S_c,S^*]$。
-在允许区间 $[c_0S_c/S,c_0]$ 上：
+设条件\eqref{eq:model:trigger}成立，$w_c,w_q>0$，则
@@ -5,2 +4,4 @@
-\item 仅减少接触的取值 $c=c_0S_c/S$ 不是 $f(S,\cdot)$ 的局部最小点；
-\item 仅隔离控制的取值 $c=c_0$ 在 $S>S_{\rm sw}$ 时是严格局部最小点，在 $S<S_{\rm sw}$ 时不是局部最小点。
+\item 不考虑能力约束时，对每个 $S\in(S_c,S^*]$，仅减少接触的取值 $c=c_0S_c/S$ 不是 $f(S,\cdot)$ 在允许区间 $[c_0S_c/S,c_0]$ 上的局部最小点；
+\item 不考虑能力约束时，对 $S\in(S_c,S^*]$，仅隔离控制的取值 $c=c_0$ 在 $S>S_{\rm sw}$ 时是严格局部最小点，在 $S<S_{\rm sw}$ 时不是局部最小点；
+\item 因此，$\mathcal A(\eta)$ 中的任一成本最优控制在几乎所有 $S\in(S_c,S^*]$ 上满足 $q_c^*(S)>q_0$，在几乎所有 $S\in(S_c,\min\{S_{\rm sw},S^*\})$ 上满足 $c_0S_c/S<c_c^*(S)<c_0$，即两种措施同时强于常规水平；
+\item 考虑满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 与式\eqref{eq:joint:feasibility}的能力约束时，$\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的成本最优控制同样满足 (iii) 的两条结论。
@@ -8,2 +8,0 @@
-因此，任一成本最优控制在几乎所有 $S\in(S_c,S^*]$ 上满足 $q_c^*(S)>q_0$，在几乎所有 $S\in(S_c,\min\{S_{\rm sw},S^*\})$ 上满足 $c_0S_c/S<c_c^*(S)<c_0$，即两种措施同时强于常规水平。
-考虑满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 与式\eqref{eq:joint:feasibility}的能力约束时，$\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的成本最优控制同样满足这两条结论。
```

## 证明

有证明的陈述：旧稿 0 条，新稿 0 条；证明有变化 0 条。

