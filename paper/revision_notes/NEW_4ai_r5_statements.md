# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 7 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:qc-structure

```diff
@@ -23 +23 @@
-使 $I(t)=\eta$ 对 $t_1\le t\le t_2$ 成立，且 $I(t)\le\eta$ 对一切 $t\ge0$ 成立。
+属于 $\mathcal A(\eta)$，阈值控制期为 $[t_1,t_2]$，期内 $I\equiv\eta$。
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:qc-structure：汉字 158 → 184

```diff
@@ -8,8 +8,8 @@
-由定理~\ref{thm:s1:start}与式\eqref{eq:s1:barS}，$S^*>S_c>\bar S$，故 $S$ 严格递减。
-令 $S(t_2)=S_c$，即得式\eqref{eq:s1:t2}中的控制时长。
-在 $[S_c,S^*]$ 上，$q_c(S_c)=q_0$ 且 $q_0\le q_c(S)<1$，满足隔离比例的界限。
-(iii) 反过来，把所得的时间函数 $q_c(t)$ 代回原方程，式\eqref{eq:s1:S-analytic}与 $I=\eta$ 满足前两个方程及启动初值，其余仓室由线性方程或积分确定。
-由命题~\ref{prop:model:positive}中解的唯一性，该控制确实使 $[t_1,t_2]$ 上 $I\equiv\eta$。
-由 $t_1$ 的定义，启动前 $I<\eta$；
-退出时 $S=S_c$，由命题~\ref{prop:model:threshold-rationale}(ii)，退出后 $I\le\eta$。
-因此全程不超过阈值。
+由定理~\ref{thm:s1:start}与式\eqref{eq:s1:barS}，$S^*>S_c>\bar S$，故 $S$ 严格递减，首次降到 $S_c$ 的时刻 $t_2$ 由 $S(t_2)=S_c$ 确定，即得式\eqref{eq:s1:t2}中的控制时长。
+在 $[S_c,S^*]$ 上，$q_c(S_c)=q_0$ 且 $q_0\le q_c(S)<1$。
+(iii) 逐条验证定义~\ref{def:model:threshold-strategy}。
+由 (ii) 的证明，$q_0\le q_c(t)<1$，所以式\eqref{eq:s1:q-piecewise}给出的控制有界可测，在 $t_1$ 之前和 $t_2$ 之后都是 $(c_0,q_0)$，并且满足条件\eqref{eq:model:plateau-requirement}。
+把 $q_c(t)$ 代回原方程，式\eqref{eq:s1:S-analytic}与 $I=\eta$ 满足前两个方程及启动初值，其余仓室由线性方程或积分确定。
+由命题~\ref{prop:model:positive}中解的唯一性，该控制使 $[t_1,t_2]$ 上 $I\equiv\eta$。
+由式\eqref{eq:s1:S-analytic}，$S$ 严格递减，$t_2$ 是 $S$ 首次降到 $S_c$ 的时刻。
+因此该控制属于 $\mathcal A(\eta)$，阈值控制期为 $[t_1,t_2]$。
```

