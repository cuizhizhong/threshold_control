# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 8 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:start：汉字 130 → 132

```diff
@@ -1 +1,4 @@
-(i) 将 $I=\eta$ 代入式\eqref{eq:model:routine-orbit}，并利用 $\beta_2^0/\beta_1^0=\rho_1/S_c$，得
+(i) 由第~\ref{sec:model:strategy}~节，沿常规轨迹，$I(S)$ 在 $[S_c,S_0]$ 上关于 $S$ 严格递减。
+由 $I(S_c)=I_{\max}^{0}>\eta>I_0=I(S_0)$，$I(S)=\eta$ 在 $(S_c,S_0)$ 上恰有一根。
+$S^*=S(t_1)$ 满足 $I(S^*)=\eta$ 且 $S^*>S_c$（第~\ref{sec:model:strategy}~节），又 $S^*\le S_0$、$I(S_0)=I_0<\eta$，故 $S^*$ 就是这个根。
+将 $I=\eta$ 代入式\eqref{eq:model:routine-orbit}，并利用 $\beta_2^0/\beta_1^0=\rho_1/S_c$，得
@@ -3 +6 @@
-由 $S_0>S_c$ 及常规峰值公式\eqref{eq:s1:Imax-no}，得
+由 $S_0>S_c$ 及常规峰值公式\eqref{eq:s1:Imax-no}，
@@ -7 +10 @@
-由 $\eta<I_{\max}^{0}$，得 $z_\eta\in(-e^{-1},0)$。
+再由 $\eta<I_{\max}^{0}$ 得 $z_\eta\in(-e^{-1},0)$。
@@ -9,3 +12 @@
-$W_0$ 给出小于 $S_c$ 的根，对应 $I$ 下降时的交点。
-由式\eqref{eq:model:routine-orbit}，$I(S)$ 关于 $S$ 在 $[S_c,S_0]$ 上严格递减。
-由 $I(S_c)=I_{\max}^{0}>\eta>I_0=I(S_0)$，启动时的根唯一，取 $W_{-1}$ 分支即得式\eqref{eq:s1:Sstar-lambert}。
+由 $S^*>S_c$，$-S^*/S_c<-1$，故 $-S^*/S_c=W_{-1}(z_\eta)$，即得式\eqref{eq:s1:Sstar-lambert}。
```

