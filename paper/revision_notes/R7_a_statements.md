# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/flatten_curve_analysis_cn.tex HEAD:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 29 条，新稿 31 条；共同 29 条，其中未变化 23 条，有变化 6 条。

只在新稿中（新增或改了首个标签）：lem:s1:trigger-boundary、cor:joint:single-endpoints

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:tend

```diff
@@ -6 +6 @@
-存在唯一的 $t_{\rm end}>t_2$ 满足 $I(t_{\rm end})=1$、$I'(t_{\rm end})<0$。
+存在唯一的 $t_{\rm end}>t_2$ 满足 $I(t_{\rm end})=1$、$\dot I(t_{\rm end})<0$。
```

### cor:joint:feasibility

```diff
@@ -1 +1 @@
-能力约束等价于 $\underline c(S)\le c_c(S)\le\overline c(S)$。
+能力约束等价于 $c^{-}(S)\le c_c(S)\le c^{+}(S)$。
```

### cor:joint:capped-comparison

```diff
@@ -3 +3 @@
-\Delta t[\overline c]\le\Delta t[c_c]\le\Delta t[\underline c],
+\Delta t[c^{+}]\le\Delta t[c_c]\le\Delta t[c^{-}],
@@ -5,2 +5,2 @@
-其中两端由式\eqref{eq:joint:duration}分别代入 $\overline c(S)$、$\underline c(S)$ 计算，且均可达到；
-达到左、右等号分别要求 $c_c=\overline c$、$c_c=\underline c$ 几乎处处成立。
+其中两端由式\eqref{eq:joint:duration}分别代入 $c^{+}(S)$、$c^{-}(S)$ 计算，且均可达到；
+达到左、右等号分别要求 $c_c=c^{+}$、$c_c=c^{-}$ 几乎处处成立。
```

### cor:joint:whole-epidemic

```diff
@@ -10 +10 @@
-能力约束下，$\overline c(S)$ 因而同时达到最短的控制时长、最早的清零时间和最少的全过程累计新增感染。
+能力约束下，$c^{+}(S)$ 因而同时达到最短的控制时长、最早的清零时间和最少的全过程累计新增感染。
```

### thm:joint:cost-minimum

```diff
@@ -1 +1 @@
-不考虑能力约束时取 $\underline c(S)=c_0S_c/S$、$\overline c(S)=c_0$（式\eqref{eq:joint:contact-range}）；
+不考虑能力约束时取 $c^{-}(S)=c_0S_c/S$、$c^{+}(S)=c_0$（式\eqref{eq:joint:contact-range}）；
@@ -7 +7 @@
-\min_{\underline c(S)\le c\le\overline c(S)}f(S,c)\,dS.
+\min_{c^{-}(S)\le c\le c^{+}(S)}f(S,c)\,dS.
@@ -10 +10 @@
-对每个 $S>S_c$，只需比较 $\underline c(S)$、$\overline c(S)$ 与区间内满足
+对每个 $S>S_c$，只需比较 $c^{-}(S)$、$c^{+}(S)$ 与区间内满足
@@ -13 +13 @@
-0={}&\frac{c^3}{c_0^2}(c-c_0)
+0={}&w_c\frac{c^3}{c_0^2}(c-c_0)
@@ -15 +15 @@
-&+2\left(c-\frac{c_0S_c}{S}\right)
+&+w_q\left(c-\frac{c_0S_c}{S}\right)
```

### prop:reference-population

```diff
@@ -1 +1 @@
-固定 $s_0,i_0,\theta$ 和模型参数，且 $i_0<\theta<i_{\max}^{no}$。
+固定 $s_0,i_0,\theta$ 和模型参数，且 $i_0<\theta<i_{\max}^{0}$。
```

## 证明

有证明的陈述：旧稿 18 条，新稿 20 条；证明有变化 4 条。

- thm:s1:start：汉字 90 → 90

```diff
@@ -5 +5 @@
-z_\eta=-e^{-1}\exp\!\left[-\frac{I_{\max}^{no}-\eta}{\rho_1}\right]\in(-e^{-1},0).
+z_\eta=-e^{-1}\exp\!\left[-\frac{I_{\max}^{0}-\eta}{\rho_1}\right]\in(-e^{-1},0).
@@ -9 +9 @@
-式\eqref{eq:model:routine-orbit}在 $S\in(S_c,S_0)$ 上关于 $S$ 严格递减，端点处的感染人数分别为 $I_{\max}^{no}$ 与 $I_0$，故该区间恰有一个交点，由 $W_{-1}$ 给出。
+式\eqref{eq:model:routine-orbit}在 $S\in(S_c,S_0)$ 上关于 $S$ 严格递减，端点处的感染人数分别为 $I_{\max}^{0}$ 与 $I_0$，故该区间恰有一个交点，由 $W_{-1}$ 给出。
```

- cor:joint:feasibility：汉字 65 → 65

```diff
@@ -7 +7 @@
-条件成立时取 $c_c=(\underline c+\overline c)/2$，由定理~\ref{thm:joint:representation}得到可行控制；
+条件成立时取 $c_c=(c^{-}+c^{+})/2$，由定理~\ref{thm:joint:representation}得到可行控制；
```

- cor:joint:capped-comparison：汉字 40 → 40

```diff
@@ -1 +1 @@
-在式\eqref{eq:joint:duration}中用 $\underline c\le c_c\le\overline c$ 比较即可。
+在式\eqref{eq:joint:duration}中用 $c^{-}\le c_c\le c^{+}$ 比较即可。
```

- prop:joint:minimum-threshold：汉字 158 → 158

```diff
@@ -1 +1 @@
-记 $m(S)=\min_{\underline c(S)\le c\le\overline c(S)}f(S,c)$。
+记 $m(S)=\min_{c^{-}(S)\le c\le c^{+}(S)}f(S,c)$。
```

