# NEW-4al 陈述与证明的变化（只换记号：q_{\max}→q_1，q_{\rm cap}→q_{\max}）

---

## 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 5 条，有变化 3 条。

## 陈述有变化（逐条确认数学含义是否等价）

### cor:s1:qc-structure

```diff
@@ -3 +3 @@
-q_{\max}=1-\frac{\gamma N}{\beta c_0S^*}>q_0,
+q_1=1-\frac{\gamma N}{\beta c_0S^*}>q_0,
```

### thm:s1:inflection

```diff
@@ -4 +4 @@
-\item $q_c(t)$ 在 $(t_1,t_2)$ 内存在唯一拐点（下称内部拐点），当且仅当 $q_0<\qinf<q_{\max}$，等价地
+\item $q_c(t)$ 在 $(t_1,t_2)$ 内存在唯一拐点（下称内部拐点），当且仅当 $q_0<\qinf<q_1$，等价地
```

### prop:threshold-tradeoff

```diff
@@ -7 +7 @@
-\frac{\partial q_{\max}}{\partial\eta}<0,\qquad
+\frac{\partial q_1}{\partial\eta}<0,\qquad
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:inflection：汉字 139 → 139

```diff
@@ -15 +15 @@
-又 $q_c(S)$ 关于 $S$ 严格增加，且 $q_c(S_c)=q_0$、$q_c(S^*)=q_{\max}$，所以式\eqref{eq:s1:inflection-condition}等价于 $q_0<\qinf<q_{\max}$。
+又 $q_c(S)$ 关于 $S$ 严格增加，且 $q_c(S_c)=q_0$、$q_c(S^*)=q_1$，所以式\eqref{eq:s1:inflection-condition}等价于 $q_0<\qinf<q_1$。
```


---

## 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/04_joint_control.tex
- 新稿：paper/sections/04_joint_control.tex

带标签的陈述：旧稿 6 条，新稿 6 条；共同 6 条，其中未变化 2 条，有变化 4 条。

## 陈述有变化（逐条确认数学含义是否等价）

### cor:joint:feasibility

```diff
@@ -5 +5 @@
-\item $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 非空，即从 $S^*$ 到 $S_c$ 的整段阈值控制可行，当且仅当
+\item $\mathcal A(\eta;c_{\min},q_{\max})$ 非空，即从 $S^*$ 到 $S_c$ 的整段阈值控制可行，当且仅当
@@ -7 +7 @@
-\frac{\beta c_{\min}(1-q_{\rm cap})S^*}{N}\le\gamma,
+\frac{\beta c_{\min}(1-q_{\max})S^*}{N}\le\gamma,
@@ -9 +9 @@
-或等价地 $c_{\min}(1-q_{\rm cap})\le c_0(1-q_{\max})$，其中 $q_{\max}$ 由式\eqref{eq:s1:qmax}给出。
+或等价地 $c_{\min}(1-q_{\max})\le c_0(1-q_1)$，其中 $q_1$ 由式\eqref{eq:s1:qmax}给出。
```

### cor:joint:capped-comparison

```diff
@@ -4 +4 @@
-\item $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的任一控制满足
+\item $\mathcal A(\eta;c_{\min},q_{\max})$ 中的任一控制满足
```

### cor:joint:whole-epidemic

```diff
@@ -12 +12 @@
-\item 设式\eqref{eq:joint:feasibility}成立，则在 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中，$c^{+}(S)$ 同时达到最短的控制时长、最早的清零时间和最少的全过程累计新增感染。
+\item 设式\eqref{eq:joint:feasibility}成立，则在 $\mathcal A(\eta;c_{\min},q_{\max})$ 中，$c^{+}(S)$ 同时达到最短的控制时长、最早的清零时间和最少的全过程累计新增感染。
```

### cor:joint:single-endpoints

```diff
@@ -1 +1 @@
-对能力约束下的控制类 $\mathcal A(\eta;c_{\min},q_{\rm cap})$，
+对能力约束下的控制类 $\mathcal A(\eta;c_{\min},q_{\max})$，
@@ -4,2 +4,2 @@
-\item 若 $q_{\rm cap}\ge q_{\max}$，则 $c^{+}(S)\equiv c_0$，因此无论 $c_{\min}$ 取何值，仅隔离控制都是该控制类中控制时长最短、累计新增感染最少的控制；
-\item 若 $c_{\min}\le c_0S_c/S^*$，则 $c^{-}(S)=c_0S_c/S$，因此无论 $q_{\rm cap}$ 取何值，仅减少接触都使该控制类中的新增隔离易感者人数最少。
+\item 若 $q_{\max}\ge q_1$，则 $c^{+}(S)\equiv c_0$，因此无论 $c_{\min}$ 取何值，仅隔离控制都是该控制类中控制时长最短、累计新增感染最少的控制；
+\item 若 $c_{\min}\le c_0S_c/S^*$，则 $c^{-}(S)=c_0S_c/S$，因此无论 $q_{\max}$ 取何值，仅减少接触都使该控制类中的新增隔离易感者人数最少。
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 2 条。

- cor:joint:feasibility：汉字 79 → 79

```diff
@@ -2,2 +2,2 @@
-由式\eqref{eq:joint:q}，$q_c\le q_{\rm cap}$ 等价于 $c_c(S)\le c_0(1-q_0)S_c/[(1-q_{\rm cap})S]$，与式\eqref{eq:joint:contact-range}合起来得上界 $c^{+}$。
-(ii) 在 $S\in[S_c,S^*]$ 上已有 $c_0S_c/S\le c_0$、$c_0S_c/S\le c_0(1-q_0)S_c/[(1-q_{\rm cap})S]$ 及 $c_{\min}\le c_0$，故只需检验
+由式\eqref{eq:joint:q}，$q_c\le q_{\max}$ 等价于 $c_c(S)\le c_0(1-q_0)S_c/[(1-q_{\max})S]$，与式\eqref{eq:joint:contact-range}合起来得上界 $c^{+}$。
+(ii) 在 $S\in[S_c,S^*]$ 上已有 $c_0S_c/S\le c_0$、$c_0S_c/S\le c_0(1-q_0)S_c/[(1-q_{\max})S]$ 及 $c_{\min}\le c_0$，故只需检验
@@ -5 +5 @@
-c_{\min}\le\frac{c_0(1-q_0)S_c}{(1-q_{\rm cap})S}.
+c_{\min}\le\frac{c_0(1-q_0)S_c}{(1-q_{\max})S}.
@@ -8 +8 @@
-由式\eqref{eq:s1:qmax}，$\beta c_0(1-q_{\max})S^*/N=\gamma$，故该式等价于 $c_{\min}(1-q_{\rm cap})\le c_0(1-q_{\max})$。
+由式\eqref{eq:s1:qmax}，$\beta c_0(1-q_1)S^*/N=\gamma$，故该式等价于 $c_{\min}(1-q_{\max})\le c_0(1-q_1)$。
```

- cor:joint:single-endpoints：汉字 39 → 39

```diff
@@ -1 +1 @@
-由式\eqref{eq:s1:qmax}与\eqref{eq:model:Sc}，$1-q_{\max}=(1-q_0)S_c/S^*$，故 $q_{\rm cap}\ge q_{\max}$ 等价于 $(1-q_{\rm cap})S^*\le(1-q_0)S_c$，从而对 $S\le S^*$ 有 $c_0(1-q_0)S_c/[(1-q_{\rm cap})S]\ge c_0$，由式\eqref{eq:joint:bounds}得 $c^{+}\equiv c_0$。
+由式\eqref{eq:s1:qmax}与\eqref{eq:model:Sc}，$1-q_1=(1-q_0)S_c/S^*$，故 $q_{\max}\ge q_1$ 等价于 $(1-q_{\max})S^*\le(1-q_0)S_c$，从而对 $S\le S^*$ 有 $c_0(1-q_0)S_c/[(1-q_{\max})S]\ge c_0$，由式\eqref{eq:joint:bounds}得 $c^{+}\equiv c_0$。
```


---

## 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/05_quadratic_cost.tex
- 新稿：paper/sections/05_quadratic_cost.tex

带标签的陈述：旧稿 7 条，新稿 7 条；共同 7 条，其中未变化 1 条，有变化 6 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:cost-minimum

```diff
@@ -3 +3 @@
-在 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中：
+在 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\max})$ 中：
```

### prop:joint:global-structure

```diff
@@ -7 +7 @@
-\item 考虑满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 与式\eqref{eq:joint:feasibility}的能力约束时，$\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的成本最优控制同样满足 (iii) 的两条结论。
+\item 考虑满足 $c_{\min}<c_0$、$q_{\max}>q_0$ 与式\eqref{eq:joint:feasibility}的能力约束时，$\mathcal A(\eta;c_{\min},q_{\max})$ 中的成本最优控制同样满足 (iii) 的两条结论。
```

### prop:joint:terminal-allocation

```diff
@@ -20 +20 @@
-\item 考虑满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 的能力约束时，(i) 仍成立；
+\item 考虑满足 $c_{\min}<c_0$、$q_{\max}>q_0$ 的能力约束时，(i) 仍成立；
```

### prop:joint:minimum-threshold

```diff
@@ -6 +6 @@
-\item 固定阈值时，降低 $c_{\min}$ 或提高 $q_{\rm cap}$ 不会增大最小成本。
+\item 固定阈值时，降低 $c_{\min}$ 或提高 $q_{\max}$ 不会增大最小成本。
```

### cor:joint:capacity-clip

```diff
@@ -2 +2 @@
-则 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的成本最优控制几乎处处等于
+则 $\mathcal A(\eta;c_{\min},q_{\max})$ 中的成本最优控制几乎处处等于
```

### prop:joint:weight-monotone

```diff
@@ -1 +1 @@
-固定 $w_c>0$ 与控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$（后者设式\eqref{eq:joint:feasibility}成立）。
+固定 $w_c>0$ 与控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\max})$（后者设式\eqref{eq:joint:feasibility}成立）。
```

## 证明

有证明的陈述：旧稿 0 条，新稿 0 条；证明有变化 0 条。


---

## 定理类陈述与证明的变化

- 旧稿：HEAD:paper/supplement_sections/S2_single_control.tex
- 新稿：paper/supplement_sections/S2_single_control.tex

带标签的陈述：旧稿 2 条，新稿 2 条；共同 2 条，其中未变化 1 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### prop:contact-effects

```diff
@@ -7 +7 @@
-\frac{\partial q_{\max}}{\partial c_0}>0,\qquad
+\frac{\partial q_1}{\partial c_0}>0,\qquad
```

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 1 条。

- prop:contact-effects：汉字 219 → 219

```diff
@@ -12 +12 @@
-\frac{\partial q_{\max}}{\partial c_0}
+\frac{\partial q_1}{\partial c_0}
```


---

## 定理类陈述与证明的变化

- 旧稿：HEAD:paper/supplement_sections/S4_explicit_control.tex
- 新稿：paper/supplement_sections/S4_explicit_control.tex

带标签的陈述：旧稿 2 条，新稿 2 条；共同 2 条，其中未变化 1 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### cor:joint:allocation-range

```diff
@@ -6 +6 @@
-\min\!\left\{1,\frac{S_c(q_{\rm cap}-q_0)}{(1-q_{\rm cap})(S^*-S_c)}\right\}.
+\min\!\left\{1,\frac{S_c(q_{\max}-q_0)}{(1-q_{\max})(S^*-S_c)}\right\}.
```

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 1 条。

- cor:joint:allocation-range：汉字 70 → 70

```diff
@@ -1 +1 @@
-由定理~\ref{thm:joint:explicit}(iii)，显式族中 $c$ 随时间不减、$q$ 不增，故只需在 $S=S^*$ 处检查 $c\ge c_{\min}$ 和 $q\le q_{\rm cap}$。
+由定理~\ref{thm:joint:explicit}(iii)，显式族中 $c$ 随时间不减、$q$ 不增，故只需在 $S=S^*$ 处检查 $c\ge c_{\min}$ 和 $q\le q_{\max}$。
@@ -5,2 +5,2 @@
-$c_{\min}S^*\le c_0(1-q_0)S_c/(1-q_{\rm cap})$，
-即式\eqref{eq:joint:feasibility}，故该区间与 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 同时非空。
+$c_{\min}S^*\le c_0(1-q_0)S_c/(1-q_{\max})$，
+即式\eqref{eq:joint:feasibility}，故该区间与 $\mathcal A(\eta;c_{\min},q_{\max})$ 同时非空。
```


---

## 定理类陈述与证明的变化

- 旧稿：HEAD:paper/supplement_sections/S6_xian.tex
- 新稿：paper/supplement_sections/S6_xian.tex

带标签的陈述：旧稿 2 条，新稿 2 条；共同 2 条，其中未变化 1 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### prop:scaling

```diff
@@ -4 +4 @@
-\item $t_1,\Delta t,q_{\max},J$ 以及存在内部拐点时的 $\lambda$ 只通过 $\theta=\eta/N$ 依赖于 $N$ 和 $\eta$；
+\item $t_1,\Delta t,q_1,J$ 以及存在内部拐点时的 $\lambda$ 只通过 $\theta=\eta/N$ 依赖于 $N$ 和 $\eta$；
```

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 1 条。

- prop:scaling：汉字 148 → 148

```diff
@@ -13 +13 @@
-且 $q_{\max}=1-\gamma/(\beta c_0s^*)$，正文式\eqref{eq:s1:lambda}中的 $\lambda$ 也只含 $s^*,s_c,\bar s$。
+且 $q_1=1-\gamma/(\beta c_0s^*)$，正文式\eqref{eq:s1:lambda}中的 $\lambda$ 也只含 $s^*,s_c,\bar s$。
```


