# 定理类陈述与证明的变化

- 旧稿：bef4962:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 9 条，新稿 9 条；共同 9 条，其中未变化 6 条，有变化 3 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:start

```diff
@@ -1 +1 @@
-设条件\eqref{eq:model:trigger}成立，记 $W_{-1}$ 为 Lambert $W$ 函数的下实分支，则
+设条件\eqref{eq:model:trigger}成立，记 $W_{-1}$ 为 Lambert $W$ 函数的下实分支，$z_\eta$ 由式\eqref{eq:s1:lambert-argument}给出，$I(S)$ 由式\eqref{eq:model:routine-orbit}给出，则
@@ -4 +4 @@
-\item $z_\eta\in(-e^{-1},0)$，启动状态唯一，为
+\item $z_\eta\in(-e^{-1},0)$，启动时的易感者人数 $S^*$ 是 $I(S)=\eta$ 在 $(S_c,S_0)$ 上的唯一根，为
@@ -10,2 +10 @@
-t_1=\frac{1}{\beta_1^0}\int_{S^*}^{S_0}
-\frac{dS}{S[I_0+\frac{\beta_2^0}{\beta_1^0}(S_0-S)+\rho_1\ln(S/S_0)]}>0.
+t_1=\frac{1}{\beta_1^0}\int_{S^*}^{S_0}\frac{dS}{S\,I(S)},\qquad 0<t_1<\infty.
```

### thm:s1:qc-structure

```diff
@@ -4 +4 @@
-\item 阈值控制期内保持 $I(t)=\eta$ 所需的隔离比例唯一，为
+\item 阈值控制期内保持 $I(t)=\eta$ 所需的隔离比例几乎处处唯一，为
@@ -10 +10 @@
-S(t)=\bar S+(S^*-\bar S)e^{-c_0\eta(t-t_1)/N},\qquad I(t)=\eta,
+S(t)=\bar S+(S^*-\bar S)e^{-c_0\eta(t-t_1)/N},\qquad I(t)=\eta,\qquad t_1\le t\le t_2,
```

### cor:s1:qc-structure

```diff
@@ -9 +9 @@
-\item 设隔离比例受能力约束 $q\le q_{\rm cap}$，其中 $q_0\le q_{\rm cap}<1$，则上述仅隔离控制可实施，当且仅当
+\item 设隔离比例受能力约束 $q\le q_{\rm cap}$，其中 $q_0\le q_{\rm cap}<1$，则上述仅隔离控制可实施（即全程 $q(t)\le q_{\rm cap}$），当且仅当
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 3 条。

- thm:s1:start：汉字 102 → 113

```diff
@@ -1 +1 @@
-(i) 将 $I=\eta$ 代入式\eqref{eq:model:first-integral}，并利用 $\beta_2^0/\beta_1^0=\rho_1/S_c$，得
+(i) 将 $I=\eta$ 代入式\eqref{eq:model:routine-orbit}，并利用 $\beta_2^0/\beta_1^0=\rho_1/S_c$，得
@@ -9,5 +9,5 @@
-前者给出小于 $S_c$ 的状态，即 $I$ 下降时的交点。
-式\eqref{eq:model:routine-orbit}在 $S\in(S_c,S_0)$ 上关于 $S$ 严格递减，端点处的值分别为 $I_{\max}^{0}$ 与 $I_0$；
-由触发条件中的 $I_0<\eta<I_{\max}^{0}$，该区间上恰有一个交点，由 $W_{-1}$ 给出。
-(ii) 沿常规易感者方程分离变量即得式\eqref{eq:s1:t1}。
-积分区间上 $I(S)\ge I_0>0$，所以 $t_1$ 有限。
+前者给出小于 $S_c$ 的根，即 $I$ 下降时的交点。
+由式\eqref{eq:model:routine-orbit}，$I(S)$ 在 $(S_c,S_0)$ 上关于 $S$ 严格递减，端点处的值分别为 $I_{\max}^{0}$ 与 $I_0$；
+由触发条件中的 $I_0<\eta<I_{\max}^{0}$，该区间上恰有一个根，由 $W_{-1}$ 给出。
+(ii) 沿常规控制下的易感者方程 $\dot S=-\beta_1^0SI$ 分离变量，即得式\eqref{eq:s1:t1}。
+积分区间上 $I(S)\ge I_0>0$，被积函数为正且有界，又 $S^*<S_0$，所以 $0<t_1<\infty$。
```

- thm:s1:qc-structure：汉字 158 → 157

```diff
@@ -2 +2 @@
-取 $c=c_0$，即唯一解出式\eqref{eq:s1:q-control}。
+取 $c=c_0$，即几乎处处唯一地解出式\eqref{eq:s1:q-control}。
@@ -11 +11 @@
-由命题~\ref{prop:model:positive}中解的唯一性，该控制确实使 $I\equiv\eta$，而不只是形式上满足 $\dot I=0$。
+由命题~\ref{prop:model:positive}中解的唯一性，该控制确实使 $I\equiv\eta$。
@@ -13 +13 @@
-由命题~\ref{prop:model:threshold-rationale}(iii)，退出后 $S<S_c$、$\dot I<0$。
+退出时 $S=S_c$，由命题~\ref{prop:model:threshold-rationale}(iii)，退出后 $I\le\eta$。
```

- cor:s1:qc-structure：汉字 136 → 112

```diff
@@ -11 +10,0 @@
-$q_{\rm cap}=q_{\max}$ 时，控制只在启动时恰好达到能力上限，随后严格低于上限。
```

