# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 7 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:qc-structure

```diff
@@ -1,4 +1,2 @@
-设条件\eqref{eq:model:trigger}成立，并固定 $c(t)=c_0$，则
-\begin{enumerate}
-\renewcommand{\labelenumi}{(\roman{enumi})}
-\item 阈值控制期内保持 $I(t)=\eta$ 所需的隔离比例几乎处处唯一，为
+设条件\eqref{eq:model:trigger}成立，则 $\mathcal A(\eta)$ 中接触率恒为 $c_0$ 的控制存在且几乎处处唯一，即仅隔离控制。
+它的阈值控制期为 $[t_1,t_2]$，期内 $I\equiv\eta$，
@@ -6,5 +4 @@
-q_c(S)=1-\frac{\gamma N}{\beta c_0S},\qquad S_c\le S\le S^*;
-\end{equation}
-\item 相应的状态轨迹和控制时长为
-\begin{equation}
-S(t)=\bar S+(S^*-\bar S)e^{-c_0\eta(t-t_1)/N},\qquad I(t)=\eta,\qquad t_1\le t\le t_2,
+S(t)=\bar S+(S^*-\bar S)e^{-c_0\eta(t-t_1)/N},\qquad t_1\le t\le t_2,
@@ -13 +7 @@
-\Delta t=t_2-t_1=\frac{N}{c_0\eta}\ln\frac{S^*-\bar S}{S_c-\bar S};
+\Delta t=t_2-t_1=\frac{N}{c_0\eta}\ln\frac{S^*-\bar S}{S_c-\bar S},
@@ -15 +9 @@
-\item 以式\eqref{eq:s1:S-analytic}代入式\eqref{eq:s1:q-control}定义 $q_c(t)$，则完整控制
+隔离比例为
@@ -17 +11 @@
-c(t)=c_0,\qquad q(t)=\begin{cases}
+q(t)=\begin{cases}
@@ -19,2 +13,2 @@
-q_c(t),&t_1\le t\le t_2,\\
-q_0,&t>t_2
+q_c(S(t)),&t_1\le t\le t_2,\\
+q_0,&t>t_2.
@@ -23,2 +16,0 @@
-属于 $\mathcal A(\eta)$，阈值控制期为 $[t_1,t_2]$，期内 $I\equiv\eta$。
-\end{enumerate}
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:qc-structure：汉字 187 → 184

```diff
@@ -1,3 +1,3 @@
-(i)(ii) 由引理~\ref{lem:model:balance}，维持 $I=\eta$ 时式\eqref{eq:model:balance}几乎处处成立；
-取 $c=c_0$，即几乎处处唯一地解出式\eqref{eq:s1:q-control}。
-由式\eqref{eq:s1:barS}与\eqref{eq:s1:q-control}，$\beta+(1-\beta)q_c(S)=1-\bar S/S$，代入 $S$ 的方程得
+先设 $(c_0,q)\in\mathcal A(\eta)$。
+由引理~\ref{lem:model:balance}，阈值控制期内几乎处处有式\eqref{eq:model:balance}，取 $c=c_0$ 即得 $q=q_c(S)$。
+由式\eqref{eq:s1:q-control}与\eqref{eq:s1:barS}，$\beta+(1-\beta)q_c(S)=1-\bar S/S$，代入 $S$ 的方程得
@@ -8,7 +8,7 @@
-由定理~\ref{thm:s1:start}与式\eqref{eq:s1:barS}，$S^*>S_c>\bar S$，故 $S$ 严格递减，首次降到 $S_c$ 的时刻 $t_2$ 由 $S(t_2)=S_c$ 确定，即得式\eqref{eq:s1:t2}中的控制时长。
-(iii) 逐条验证定义~\ref{def:model:threshold-strategy}。
-由式\eqref{eq:s1:q-control}，$q_c$ 关于 $S$ 严格递增，且 $q_c(S_c)=q_0$，故在 $[t_1,t_2]$ 上 $q_0\le q_c(t)<1$。
-所以式\eqref{eq:s1:q-piecewise}给出的控制有界可测，在 $t_1$ 之前和 $t_2$ 之后都是 $(c_0,q_0)$，并满足条件\eqref{eq:model:plateau-requirement}。
-把 $q_c(t)$ 代回原方程，式\eqref{eq:s1:S-analytic}与 $I=\eta$ 满足前两个方程及启动初值，其余仓室由线性方程或积分确定。
-由命题~\ref{prop:model:positive}中解的唯一性，该控制使 $[t_1,t_2]$ 上 $I\equiv\eta$。
-由 (ii) 的证明，$t_2$ 是 $S$ 首次降到 $S_c$ 的时刻。
+由定理~\ref{thm:s1:start}与式\eqref{eq:s1:barS}，$S^*>S_c>\bar S$，故 $S$ 严格递减，首次降到 $S_c$ 的时刻 $t_2$ 由 $S(t_2)=S_c$ 确定，即得式\eqref{eq:s1:t2}。
+再由定义~\ref{def:model:threshold-strategy}，$t_1$ 之前与 $t_2$ 之后 $q=q_0$，故 $q$ 几乎处处等于式\eqref{eq:s1:q-piecewise}。
+反过来验证式\eqref{eq:s1:q-piecewise}给出的控制属于 $\mathcal A(\eta)$。
+由式\eqref{eq:s1:q-control}，$q_c$ 关于 $S$ 严格递增，且 $q_c(S_c)=q_0$，故在 $[t_1,t_2]$ 上 $q_0\le q_c(S(t))<1$，该控制有界可测并满足条件\eqref{eq:model:plateau-requirement}。
+把它代回原方程，式\eqref{eq:s1:S-analytic}与 $I=\eta$ 满足前两个方程及启动初值，其余仓室由线性方程或积分确定；
+由命题~\ref{prop:model:positive}中解的唯一性，$[t_1,t_2]$ 上 $I\equiv\eta$。
+由上一段，$t_2$ 是 $S$ 首次降到 $S_c$ 的时刻。
```

