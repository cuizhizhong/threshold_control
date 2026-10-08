# 定理类陈述与证明的变化

- 旧稿：pre-rewrite-20261007:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 10 条，新稿 10 条；共同 10 条，其中未变化 3 条，有变化 7 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:start

```diff
@@ -12 +12 @@
-\frac{dS}{S[I_0+\frac{\beta_2^0}{\beta_1^0}(S_0-S)+\rho_1\ln(S/S_0)]}>0.
+\frac{dS}{S[I_0+\frac{\beta_2^0}{\beta_1^0}(S_0-S)+\rho_1\ln(S/S_0)]}>0,
@@ -14 +14 @@
-这里 $W_{-1}$ 为 Lambert $W$ 函数的下实分支。
+其中 $W_{-1}$ 为 Lambert $W$ 函数的下实分支。
```

### cor:s1:qc-structure

```diff
@@ -5,2 +5,2 @@
-在 $(t_1,t_2)$ 严格递减，并在 $t_2$ 连续恢复为 $q_0$。
-若另有追踪隔离比例的上限 $q_0\le q_{\rm cap}<1$，则上述仅隔离控制可实施，当且仅当
+在 $(t_1,t_2)$ 上严格递减，并在 $t_2$ 连续恢复为 $q_0$。
+若隔离比例受能力约束 $q\le q_{\rm cap}$（$q_0\le q_{\rm cap}<1$），则上述仅隔离控制可实施，当且仅当
@@ -12 +12 @@
-该条件成立时，能力限制不改变上述控制轨迹、控制时长及成本公式。
+该条件成立时，能力约束不改变上述控制轨迹、控制时长及成本公式。
```

### thm:s1:tend

```diff
@@ -6 +6 @@
-若 $\eta>1$，则唯一的 $t_{\rm end}>t_2$ 满足 $I(t_{\rm end})=1$、$I'(t_{\rm end})<0$。
+存在唯一的 $t_{\rm end}>t_2$ 满足 $I(t_{\rm end})=1$、$I'(t_{\rm end})<0$。
```

### thm:s1:Itcum

```diff
@@ -1 +1 @@
-在前述仅隔离控制下，若 $\eta>1$，则
+仅隔离控制下，
@@ -8 +8 @@
-将 $S_{\rm end}$ 替换为 $S_\infty$，即得到计算至无限时刻的累计新增感染。
+将 $S_{\rm end}$ 替换为 $S_\infty$，即得计算至无限时刻的累计新增感染。
```

### prop:threshold-tradeoff

```diff
@@ -7 +7 @@
-\frac{\partial J}{\partial\eta}<0.
+\frac{\partial J}{\partial\eta}<0,
@@ -9 +9 @@
-若进一步有 $\eta>1$，则 $\partial\Itcum/\partial\eta>0$。
+且 $\partial\Itcum/\partial\eta>0$。
```

### prop:contact-effects

```diff
@@ -17 +17 @@
-固定 $I_0<\eta<I_0+\beta_2^0S_0/\beta_1^0$ 时，$\Delta t$ 在 $c_0\in(c_{0,\min},\infty)$ 内至少有一个极大值，但不据此断言极大值唯一。
+固定 $I_0<\eta<I_0+\beta_2^0S_0/\beta_1^0$ 时，$\Delta t$ 在 $c_0\in(c_{0,\min},\infty)$ 内至少有一个极大值。
```

### prop:scaling

```diff
@@ -2 +2 @@
-在阈值控制被触发时，$t_1,\Delta t,q_{\max},J$ 以及存在内部拐点时的 $\lambda$ 对 $N,\eta$ 的依赖仅通过 $\theta=\eta/N$ 表现。
+控制被触发时，$t_1,\Delta t,q_{\max},J$ 以及存在内部拐点时的 $\lambda$ 对 $N,\eta$ 的依赖仅通过 $\theta=\eta/N$ 表现。
```

## 证明

有证明的陈述：旧稿 6 条，新稿 6 条；证明有变化 6 条。

- thm:s1:start：汉字 93 → 90

```diff
@@ -3 +3 @@
-又由峰值公式，
+由式\eqref{eq:s1:Imax-no}，
@@ -7,3 +7,3 @@
-在此区间，$W_0(z)\in(-1,0)$、$W_{-1}(z)<-1$\cite{Corless1996}。
-前者给出的状态小于 $S_c$，对应感染人数下降后的交点。
-由于式\eqref{eq:model:routine-orbit}在 $S\in(S_c,S_0)$ 上关于 $S$ 严格递减，且端点感染人数分别为 $I_{\max}^{no}$ 与 $I_0$，该区间恰有一个交点，须取 $W_{-1}$。
+在此区间上 $W_0(z)\in(-1,0)$、$W_{-1}(z)<-1$\cite{Corless1996}。
+前者给出小于 $S_c$ 的状态，即感染人数下降时的交点。
+式\eqref{eq:model:routine-orbit}在 $S\in(S_c,S_0)$ 上关于 $S$ 严格递减，端点处的感染人数分别为 $I_{\max}^{no}$ 与 $I_0$，故该区间恰有一个交点，由 $W_{-1}$ 给出。
```

- thm:s1:qc-structure：汉字 135 → 131

```diff
@@ -2 +2 @@
-代入 $S$ 方程得
+代入 $S$ 的方程得
@@ -7 +7 @@
-由 $S^*>S_c>\bar S$，轨迹严格下降并在式\eqref{eq:s1:t2}给出的有限时间首次到达 $S_c$。
+由 $S^*>S_c>\bar S$，轨迹严格下降，并在式\eqref{eq:s1:t2}给出的有限时刻首次到达 $S_c$。
@@ -9,2 +9,2 @@
-反过来，将如此得到的时间函数 $q_c(t)$ 代回原方程，式\eqref{eq:s1:S-analytic}与 $I=\eta$ 满足前两个方程及启动初值，其余仓室由线性方程或积分确定。
-由命题\ref{prop:model:positive}的解唯一性，该控制确实实现恒定感染，而不只是形式上满足 $\dot I=0$。
+反过来，把所得的时间函数 $q_c(t)$ 代回原方程，式\eqref{eq:s1:S-analytic}与 $I=\eta$ 满足前两个方程及启动初值，其余仓室由线性方程或积分确定。
+由命题\ref{prop:model:positive}的解唯一性，该控制确实使 $I\equiv\eta$，而不只是形式上满足 $\dot I=0$。
@@ -12 +12,2 @@
-退出后 $S<S_c$，故 $\dot I<0$，全程不超过阈值。
+退出后 $S<S_c$，故 $\dot I<0$。
+因此全程不超过阈值。
```

- cor:s1:qc-structure：汉字 96 → 94

```diff
@@ -1 +1 @@
-由于 $q_c(S)$ 关于 $S$ 严格增加，$S^*>S_c$ 给出启动跳跃。
+$q_c(S)$ 关于 $S$ 严格增加，$S^*>S_c$ 给出启动时的跳升。
@@ -8 +8 @@
-控制比例的最大值在启动时取得，因此全时段的能力限制等价于检查这一最大值；
+隔离比例在启动时取得最大值，因此全时段的能力约束等价于检查这一最大值；
@@ -10 +10 @@
-当 $q_{\rm cap}=q_{\max}$ 时，控制只在启动时恰好达到能力上限，随后严格低于上限。
+$q_{\rm cap}=q_{\max}$ 时，控制只在启动时恰好达到能力上限，随后严格低于上限。
```

- thm:s1:Itcum：汉字 49 → 48

```diff
@@ -5,2 +5,2 @@
-所以两段积分分别由 $S_0-S^*$、$S_c-S_{\rm end}$ 给出。
-阈值控制期内使用 $dt=-N\,dS/[c_0\eta(S-\bar S)]$，得到
+所以两段的积分分别由 $S_0-S^*$、$S_c-S_{\rm end}$ 给出。
+阈值控制期内用 $dt=-N\,dS/[c_0\eta(S-\bar S)]$，得
@@ -13 +13 @@
-无穷时刻的表达由极限得到。
+无限时刻的表达由极限得到。
```

- prop:scaling：汉字 103 → 101

```diff
@@ -18 +18 @@
-其中仅含归一化状态和固定参数。
+其中只含归一化状态和固定参数。
@@ -21 +21 @@
-有限的操作性终点却为 $i=1/N$，因而保留绝对人口尺度。
+有限的终点 $I=1$ 却对应 $i=1/N$，因而保留绝对人口尺度。
```

- thm:s1:inflection：汉字 94 → 93

```diff
@@ -10,2 +10,2 @@
-条件\eqref{eq:s1:inflection-condition}蕴含 $\beta<1/2$，故所列 $\qinf$ 表达式有定义。
-二阶导数先负后正，而一阶导数始终为负，故 $|dq_c/dt|$ 在该时刻达到唯一最大值。
+条件\eqref{eq:s1:inflection-condition}蕴含 $\beta<1/2$，故 $\qinf$ 的表达式有定义。
+二阶导数先负后正，而一阶导数始终为负，故 $|dq_c/dt|$ 在该时刻唯一达到最大值。
```

