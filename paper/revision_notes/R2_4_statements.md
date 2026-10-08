# 定理类陈述与证明的变化

- 旧稿：pre-rewrite-20261007:paper/sections/04_joint_control.tex
- 新稿：paper/sections/04_joint_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 1 条，有变化 7 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:representation

```diff
@@ -1 +1 @@
-规定的联合阈值控制与满足
+在几乎处处相等的意义下，$\mathcal A(\eta)$ 中的控制与满足
@@ -5 +5 @@
-的有界可测函数相对应。
+的有界可测函数 $c_c$ 一一对应。
```

### cor:joint:feasibility

```diff
@@ -1,2 +1,2 @@
-上述能力限制等价于 $\underline c(S)\le c_c(S)\le\overline c(S)$。
-从 $S^*$ 至 $S_c$ 的整段阈值控制可行，当且仅当
+能力约束等价于 $\underline c(S)\le c_c(S)\le\overline c(S)$。
+$\mathcal A(\eta;c_{\min},q_{\rm cap})$ 非空，即从 $S^*$ 到 $S_c$ 的整段阈值控制可行，当且仅当
```

### thm:joint:explicit

```diff
@@ -19 +19 @@
-$\alpha=0$ 对应仅减少接触，$\alpha=1$ 恢复第\ref{sec:s1}节的仅隔离控制。
+$\alpha=0$ 对应仅减少接触，$\alpha=1$ 恢复第~\ref{sec:s1}~节的仅隔离控制。
```

### cor:joint:allocation-range

```diff
@@ -1 +1 @@
-在式\eqref{eq:joint:bounds}的能力限制下，上述显式族可行当且仅当
+在能力约束下，上述显式族可行当且仅当
```

### thm:joint:comparison

```diff
@@ -1,2 +1,4 @@
-若两个允许控制的状态函数满足 $c_c^{(1)}(S)\ge c_c^{(2)}(S)$ 几乎处处成立，则
-$\Delta t[c_c^{(1)}]\le\Delta t[c_c^{(2)}]$。
+设 $c_c$、$c_c^{(1)}$、$c_c^{(2)}$ 是 $\mathcal A(\eta)$ 中控制的状态函数。
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 若 $c_c^{(1)}(S)\ge c_c^{(2)}(S)$ 几乎处处成立，则 $\Delta t[c_c^{(1)}]\le\Delta t[c_c^{(2)}]$；
@@ -8 +10 @@
-\frac{N(S^*-S_c)}{c_0\eta(S_c-\bar S)}.
+\frac{N(S^*-S_c)}{c_0\eta(S_c-\bar S)},
@@ -12,2 +14,2 @@
-显式族的 $\Delta t(\alpha)$ 在 $[0,1]$ 上严格递减。
-沿任一允许控制，其阈值控制期累计新增感染与新增隔离易感者人数分别满足
+\item 显式族的 $\Delta t(\alpha)$ 在 $[0,1]$ 上严格递减。
+\item 沿 $c_c$ 对应的控制，阈值控制期累计新增感染与新增隔离易感者人数分别满足
@@ -21,2 +23,2 @@
-当 $0<\beta<1$ 时，阈值控制期累计新增感染与控制时长具有相同排序，新增隔离易感者人数的排序相反；
-$\beta=1$ 时，累计新增感染均为 $S^*-S_c$，隔离易感者人数不增加。
+因此阈值控制期累计新增感染与控制时长具有相同排序，新增隔离易感者人数的排序相反。
+\end{enumerate}
```

### cor:joint:capped-comparison

```diff
@@ -1 +1 @@
-若式\eqref{eq:joint:feasibility}成立，则
+若式\eqref{eq:joint:feasibility}成立，则 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的任一控制满足
@@ -5 +5 @@
-其中两端由式\eqref{eq:joint:duration}分别代入 $\overline c(S)$、$\underline c(S)$ 计算，且均可达到。
+其中两端由式\eqref{eq:joint:duration}分别代入 $\overline c(S)$、$\underline c(S)$ 计算，且均可达到；
@@ -7 +7 @@
-$0<\beta<1$ 时，同一两个控制分别达到受限类内最少和最多的阈值控制期累计新增感染。
+这两个控制分别使阈值控制期累计新增感染在该控制类中最少和最多。
```

### cor:joint:whole-epidemic

```diff
@@ -1 +1 @@
-设两种允许策略在启动前及退出后均采用 $(c_0,q_0)$，并从同一初始状态首次到达同一阈值 $\eta>1$。
+设两个允许控制在启动前及退出后均采用 $(c_0,q_0)$，并从同一初始状态首次到达同一阈值 $\eta$。
@@ -10,2 +10 @@
-能力限制下，$\overline c(S)$ 因而同时达到最短控制时长、最早社区清零时间；
-当 $0<\beta<1$ 时，也达到最少的全过程累计新增感染。
+能力约束下，$\overline c(S)$ 因而同时达到最短的控制时长、最早的清零时间和最少的全过程累计新增感染。
```

## 证明

有证明的陈述：旧稿 7 条，新稿 7 条；证明有变化 6 条。

- cor:joint:feasibility：汉字 68 → 65
- thm:joint:explicit：汉字 66 → 66
- cor:joint:allocation-range：汉字 71 → 64
- thm:joint:comparison：汉字 136 → 136
- cor:joint:capped-comparison：汉字 40 → 40
- cor:joint:whole-epidemic：汉字 133 → 91
