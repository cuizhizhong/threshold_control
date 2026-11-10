# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 7 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:start

```diff
@@ -1 +1,2 @@
-设条件\eqref{eq:model:trigger}成立，记 $W_{-1}$ 为 Lambert $W$ 函数的下实分支，$z_\eta$ 由式\eqref{eq:s1:lambert-argument}给出，$I(S)$ 由式\eqref{eq:model:routine-orbit}给出，则
+设触发条件\eqref{eq:model:trigger}成立，$I(S)$ 和 $z_\eta$ 分别由式\eqref{eq:model:routine-orbit}和式\eqref{eq:s1:lambert-argument}给出。
+记 $W_{-1}$ 为 Lambert $W$ 函数的下实分支，则
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 3 条。

- thm:s1:start：汉字 113 → 114

```diff
@@ -3 +3 @@
-由式\eqref{eq:s1:Imax-no}（$S_0>S_c$），
+由 $S_0>S_c$ 及常规峰值公式\eqref{eq:s1:Imax-no}，得
@@ -7,5 +7,5 @@
-再由触发条件\eqref{eq:model:trigger}中的 $\eta<I_{\max}^{0}$，得 $z_\eta\in(-e^{-1},0)$。
-在此区间上 $W_0(z)\in(-1,0)$、$W_{-1}(z)<-1$\cite{Corless1996}。
-前者给出小于 $S_c$ 的根，即 $I$ 下降时的交点。
-由式\eqref{eq:model:routine-orbit}，$I(S)$ 在 $(S_c,S_0)$ 上关于 $S$ 严格递减，端点处的值分别为 $I_{\max}^{0}$ 与 $I_0$；
-由触发条件中的 $I_0<\eta<I_{\max}^{0}$，该区间上恰有一个根，由 $W_{-1}$ 给出。
+由 $\eta<I_{\max}^{0}$，得 $z_\eta\in(-e^{-1},0)$。
+在此区间上，Lambert $W$ 函数的主实分支满足 $W_0(z)\in(-1,0)$，下实分支满足 $W_{-1}(z)<-1$（Corless 等\cite{Corless1996}）。
+$W_0$ 给出小于 $S_c$ 的根，对应 $I$ 下降时的交点。
+由式\eqref{eq:model:routine-orbit}，$I(S)$ 关于 $S$ 在 $[S_c,S_0]$ 上严格递减。
+由 $I(S_c)=I_{\max}^{0}>\eta>I_0=I(S_0)$，启动时的根唯一，取 $W_{-1}$ 分支即得式\eqref{eq:s1:Sstar-lambert}。
```

- thm:s1:qc-structure：汉字 158 → 158

```diff
@@ -7,3 +7,4 @@
-故有式\eqref{eq:s1:S-analytic}。
-由定理~\ref{thm:s1:start}与式\eqref{eq:s1:barS}，$S^*>S_c>\bar S$，所以轨迹严格下降，并在式\eqref{eq:s1:t2}给出的有限时刻首次到达 $S_c$。
-该区间上 $q_c(S_c)=q_0$、$q_0\le q_c(S)<1$，控制满足界限。
+解此初值问题得式\eqref{eq:s1:S-analytic}。
+由定理~\ref{thm:s1:start}与式\eqref{eq:s1:barS}，$S^*>S_c>\bar S$，故 $S$ 严格递减。
+令 $S(t_2)=S_c$，即得式\eqref{eq:s1:t2}中的控制时长。
+在 $[S_c,S^*]$ 上，$q_c(S_c)=q_0$ 且 $q_0\le q_c(S)<1$，满足隔离比例的界限。
```

- cor:s1:qc-structure：汉字 80 → 69

```diff
@@ -8,2 +8,2 @@
-(ii) 由 (i)，隔离比例在启动时取得最大值，因此全时段的能力约束等价于检查这一最大值；
-由式\eqref{eq:s1:qmax}整理即得上述等价式。
+(ii) 由 (i)，隔离比例在启动时取得最大值，故全程可实施当且仅当 $q_{\max}\le q_{\rm cap}$。
+代入式\eqref{eq:s1:qmax}即得所述等价式。
```

