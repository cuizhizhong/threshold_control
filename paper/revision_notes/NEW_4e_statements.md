# 定理类陈述与证明的变化

- 旧稿：f94fa73:paper/flatten_curve_analysis_cn.tex f94fa73:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 40 条，新稿 40 条；共同 40 条，其中未变化 35 条，有变化 5 条。

## 陈述有变化（逐条确认数学含义是否等价）

### rem:release-at-exit

```diff
@@ -7,3 +7,3 @@
-因此 $\xi S_q(t_2^-)>0$ 时，$I$ 在 $t_2$ 之后立即超过 $\eta$。
-这一释放不属于 $\mathcal A(\eta)$ 中的退出；
-定理~\ref{thm:s1:tend}只涉及不释放（$\xi=0$）的情形。
+因此 $\xi S_q(t_2^-)>0$ 时，$I$ 在 $t_2$ 之后立即超过 $\eta$：
+退出时一次性解除对未感染接触者的隔离，会使社区感染重新增长。
+$\mathcal A(\eta)$ 中的退出不作这种释放（$\xi=0$），定理~\ref{thm:s1:tend}针对的正是这一情形。
```

### thm:joint:cost-minimum

```diff
@@ -10,12 +10,2 @@
-对每个 $S>S_c$，只需比较 $c^{-}(S)$、$c^{+}(S)$ 与区间内满足
-\begin{equation}
-\begin{split}
-0={}&w_c\frac{c^3}{c_0^2}(c-c_0)
-\left(c+c_0-\frac{2c_0\bar S}{S}\right)\\
-&+w_q\left(c-\frac{c_0S_c}{S}\right)
-\left(-c^2+\frac{3c_0S_c}{S}c-
-\frac{2c_0^2\bar S S_c}{S^2}\right)
-\end{split}
-\end{equation}
-的全部实根处的 $f$ 值。
-该方程是五次多项式方程，故候选至多七个，重复的端点与重根只计一次。
+对每个 $S>S_c$，只需比较 $c^{-}(S)$、$c^{+}(S)$ 与区间内 $f(S,\cdot)$ 的全部驻点处的 $f$ 值。
+驻点方程可化为关于 $c$ 的五次多项式方程（附录式\eqref{eq:joint:stationary}），故候选至多七个，重复的端点与重根只计一次。
```

### thm:joint:cost-structure

```diff
@@ -1 +1 @@
-设 $0<r\le r_{\rm cont}(b)$，不考虑能力约束。
+设 $0<r\le r_{\rm cont}$，不考虑能力约束。
```

### cor:joint:capacity-clip

```diff
@@ -1 +1 @@
-设 $0<r\le r_{\rm cont}(b)$，式\eqref{eq:joint:feasibility}成立，$c_c^*$ 为定理~\ref{thm:joint:cost-structure}中不考虑能力约束的成本最优控制。
+设 $0<r\le r_{\rm cont}$，式\eqref{eq:joint:feasibility}成立，$c_c^*$ 为定理~\ref{thm:joint:cost-structure}中不考虑能力约束的成本最优控制。
```

### prop:sup:rhat

```diff
@@ -4 +4 @@
-r\le\hat r(b)=\Bigl(\frac{S_{\rm sw}}{S_{\rm sw}-S_c}\Bigr)^2 .
+r\le\hat r=\Bigl(\frac{S_{\rm sw}}{S_{\rm sw}-S_c}\Bigr)^2 .
@@ -6 +6 @@
-此外 $9/4<\hat r(b)<4$，且 $r_{\rm cont}(b)<\hat r(b)$。
+此外 $9/4<\hat r<4$，且 $r_{\rm cont}<\hat r$。
```

## 证明

有证明的陈述：旧稿 24 条，新稿 24 条；证明有变化 0 条。

