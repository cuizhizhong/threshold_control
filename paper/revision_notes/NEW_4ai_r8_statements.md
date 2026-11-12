# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 8 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:qc-structure：汉字 184 → 187

```diff
@@ -3 +3 @@
-利用 $\beta+(1-\beta)q_c(S)=1-\bar S/S$，代入 $S$ 的方程得
+由式\eqref{eq:s1:barS}与\eqref{eq:s1:q-control}，$\beta+(1-\beta)q_c(S)=1-\bar S/S$，代入 $S$ 的方程得
@@ -9 +8,0 @@
-在 $[S_c,S^*]$ 上，$q_c(S_c)=q_0$ 且 $q_0\le q_c(S)<1$。
@@ -11 +10,2 @@
-由 (ii) 的证明，$q_0\le q_c(t)<1$，所以式\eqref{eq:s1:q-piecewise}给出的控制有界可测，在 $t_1$ 之前和 $t_2$ 之后都是 $(c_0,q_0)$，并且满足条件\eqref{eq:model:plateau-requirement}。
+由式\eqref{eq:s1:q-control}，$q_c$ 关于 $S$ 严格递增，且 $q_c(S_c)=q_0$，故在 $[t_1,t_2]$ 上 $q_0\le q_c(t)<1$。
+所以式\eqref{eq:s1:q-piecewise}给出的控制有界可测，在 $t_1$ 之前和 $t_2$ 之后都是 $(c_0,q_0)$，并满足条件\eqref{eq:model:plateau-requirement}。
@@ -14 +14 @@
-由式\eqref{eq:s1:S-analytic}，$S$ 严格递减，$t_2$ 是 $S$ 首次降到 $S_c$ 的时刻。
+由 (ii) 的证明，$t_2$ 是 $S$ 首次降到 $S_c$ 的时刻。
```

