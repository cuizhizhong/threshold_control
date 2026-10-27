# 定理类陈述与证明的变化

- 旧稿：5665cae:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 10 条，新稿 10 条；共同 10 条，其中未变化 2 条，有变化 8 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:start

```diff
@@ -1 +1,2 @@
-设条件\eqref{eq:model:trigger}成立，并令
+设条件\eqref{eq:model:trigger}成立。
+令
@@ -4 +5 @@
-=-\frac{S_0}{S_c}\exp\!\left[-\frac{S_0}{S_c}+\frac{\eta-I_0}{\rho_1}\right].
+=-\frac{S_0}{S_c}\exp\!\left[-\frac{S_0}{S_c}+\frac{\eta-I_0}{\rho_1}\right],
@@ -6 +7,4 @@
-则 $z_\eta\in(-e^{-1},0)$，唯一的启动状态及相应时间为
+并记 $W_{-1}$ 为 Lambert $W$ 函数的下实分支，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item $z_\eta\in(-e^{-1},0)$，启动状态唯一，为
@@ -8 +12 @@
-S^*=-S_cW_{-1}(z_\eta),\qquad S_c<S^*<S_0,
+S^*=-S_cW_{-1}(z_\eta),\qquad S_c<S^*<S_0;
@@ -9,0 +14 @@
+\item 启动时刻为
@@ -12 +17 @@
-\frac{dS}{S[I_0+\frac{\beta_2^0}{\beta_1^0}(S_0-S)+\rho_1\ln(S/S_0)]}>0,
+\frac{dS}{S[I_0+\frac{\beta_2^0}{\beta_1^0}(S_0-S)+\rho_1\ln(S/S_0)]}>0.
@@ -14 +19 @@
-其中 $W_{-1}$ 为 Lambert $W$ 函数的下实分支。
+\end{enumerate}
```

### thm:s1:qc-structure

```diff
@@ -1,2 +1,4 @@
-在条件\eqref{eq:model:trigger}下，固定 $c(t)=c_0$。
-阈值控制期内保持 $I(t)=\eta$ 所需的隔离比例唯一为
+设条件\eqref{eq:model:trigger}成立，并固定 $c(t)=c_0$，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 阈值控制期内保持 $I(t)=\eta$ 所需的隔离比例唯一，为
@@ -4 +6 @@
-q_c(S)=1-\frac{\gamma N}{\beta c_0S},\qquad S_c\le S\le S^*.
+q_c(S)=1-\frac{\gamma N}{\beta c_0S},\qquad S_c\le S\le S^*;
@@ -6 +8 @@
-相应的状态轨迹和控制时长为
+\item 相应的状态轨迹和控制时长为
@@ -11 +13 @@
-\Delta t=t_2-t_1=\frac{N}{c_0\eta}\ln\frac{S^*-\bar S}{S_c-\bar S}.
+\Delta t=t_2-t_1=\frac{N}{c_0\eta}\ln\frac{S^*-\bar S}{S_c-\bar S};
@@ -13 +15 @@
-以式\eqref{eq:s1:S-analytic}代入式\eqref{eq:s1:q-control}定义 $q_c(t)$，则完整控制为
+\item 以式\eqref{eq:s1:S-analytic}代入式\eqref{eq:s1:q-control}定义 $q_c(t)$，则完整控制
@@ -18 +20 @@
-q_0,&t>t_2.
+q_0,&t>t_2
@@ -21 +23,2 @@
-它满足 $I(t)\le\eta$ 对所有 $t\ge0$ 成立。
+使 $I(t)\le\eta$ 对一切 $t\ge0$ 成立。
+\end{enumerate}
```

### cor:s1:qc-structure

```diff
@@ -1 +1,4 @@
-上述控制在 $t_1$ 从 $q_0$ 跳升至
+对定理~\ref{thm:s1:qc-structure}中的仅隔离控制，
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 隔离比例在 $t_1$ 从 $q_0$ 跳升至
@@ -6 +9 @@
-若隔离比例受能力约束 $q\le q_{\rm cap}$（$q_0\le q_{\rm cap}<1$），则上述仅隔离控制可实施，当且仅当
+\item 设隔离比例受能力约束 $q\le q_{\rm cap}$，其中 $q_0\le q_{\rm cap}<1$，则上述仅隔离控制可实施，当且仅当
@@ -12,0 +16 @@
+\end{enumerate}
```

### thm:s1:inflection

```diff
@@ -1 +1,4 @@
-在条件\eqref{eq:model:trigger}下，$q_c(t)$ 在 $(t_1,t_2)$ 内存在唯一拐点，当且仅当
+设条件\eqref{eq:model:trigger}成立，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item $q_c(t)$ 在 $(t_1,t_2)$ 内存在唯一拐点，当且仅当
@@ -5,2 +8,2 @@
-等价地，$\frac12<(1-\beta)(1-q_0)<-\frac12W_{-1}(z_\eta)$。
-内部拐点存在时，
+等价地，$\frac12<(1-\beta)(1-q_0)<-\frac12W_{-1}(z_\eta)$；
+\item 内部拐点存在时，
@@ -10 +13 @@
-\qinf=1-\frac1{2(1-\beta)}.
+\qinf=1-\frac1{2(1-\beta)},
@@ -12 +15,2 @@
-此时 $q_0<\qinf<q_{\max}$，且隔离比例的下降速度在 $t_{\rm inf}$ 唯一达到最大值。
+且 $q_0<\qinf<q_{\max}$，隔离比例的下降速度在 $t_{\rm inf}$ 唯一达到最大值。
+\end{enumerate}
```

### rem:release-at-exit

```diff
@@ -1 +1,2 @@
-若在 $t_2$ 恢复常规控制的同时，另把比例 $\xi\in[0,1]$ 的隔离易感者一次性转回 $S$（$S_q(t_2^-)$ 为转回前的人数，$I,I_q,R$ 连续，总人口不变），则
+设在 $t_2$ 恢复常规控制的同时，另把比例 $\xi\in[0,1]$ 的隔离易感者一次性转回 $S$。
+记 $S_q(t_2^-)$ 为转回前的隔离易感者人数，转回时 $I,I_q,R$ 连续，总人口不变，则
@@ -7,2 +8 @@
-因此 $\xi S_q(t_2^-)>0$ 时，$I$ 在 $t_2$ 之后立即超过 $\eta$：
-退出时一次性解除对未感染接触者的隔离，会使社区感染重新增长。
+因此 $\xi S_q(t_2^-)>0$ 时，$I$ 在 $t_2$ 之后立即超过 $\eta$，即退出时一次性解除对未感染接触者的隔离，会使社区感染重新增长。
```

### thm:s1:Itcum

```diff
@@ -1 +1 @@
-仅隔离控制下，
+设条件\eqref{eq:model:trigger}成立，则仅隔离控制下统计至 $t_{\rm end}$ 的总累计新增感染为
```

### prop:threshold-tradeoff

```diff
@@ -1 +1 @@
-对于仅隔离控制，在触发区间内有
+设条件\eqref{eq:model:trigger}成立，则仅隔离控制满足
@@ -9 +9 @@
-且 $\partial\Itcum/\partial\eta>0$。
+且 $\partial\Itcum/\partial\eta>0$；
```

### prop:scaling

```diff
@@ -1,4 +1,7 @@
-对于仅隔离控制，固定 $s_0,i_0$ 和 $\beta,\gamma,c_0,q_0$。
-控制被触发时，$t_1,\Delta t,q_{\max},J$ 以及存在内部拐点时的 $\lambda$ 对 $N,\eta$ 的依赖仅通过 $\theta=\eta/N$ 表现。
-计算至无限时刻的累计新增感染除以 $N$ 后亦不依赖 $N$。
-但是，使用绝对终点 $I=1$ 时，$t_{\rm end}$ 及计算至该终点的累计新增感染比例一般仍含 $N$。
+对于仅隔离控制，固定 $s_0,i_0$ 和 $\beta,\gamma,c_0,q_0$，并设控制被触发，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item $t_1,\Delta t,q_{\max},J$ 以及存在内部拐点时的 $\lambda$ 对 $N,\eta$ 的依赖仅通过 $\theta=\eta/N$ 表现；
+\item 计算至无限时刻的累计新增感染除以 $N$ 后亦不依赖 $N$；
+\item 使用绝对终点 $I=1$ 时，$t_{\rm end}$ 及计算至该终点的累计新增感染比例一般仍含 $N$。
+\end{enumerate}
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 5 条。

- thm:s1:start：汉字 90 → 102

```diff
@@ -1 +1 @@
-将 $I=\eta$ 代入式\eqref{eq:model:first-integral}，得
+(i) 将 $I=\eta$ 代入式\eqref{eq:model:first-integral}，并利用 $\beta_2^0/\beta_1^0=\rho_1/S_c$，得
@@ -3 +3 @@
-由式\eqref{eq:s1:Imax-no}，
+由式\eqref{eq:s1:Imax-no}（$S_0>S_c$），
@@ -5 +5 @@
-z_\eta=-e^{-1}\exp\!\left[-\frac{I_{\max}^{0}-\eta}{\rho_1}\right]\in(-e^{-1},0).
+z_\eta=-e^{-1}\exp\!\left[-\frac{I_{\max}^{0}-\eta}{\rho_1}\right],
@@ -6,0 +7 @@
+再由触发条件\eqref{eq:model:trigger}中的 $\eta<I_{\max}^{0}$，得 $z_\eta\in(-e^{-1},0)$。
@@ -8,3 +9,4 @@
-前者给出小于 $S_c$ 的状态，即感染人数下降时的交点。
-式\eqref{eq:model:routine-orbit}在 $S\in(S_c,S_0)$ 上关于 $S$ 严格递减，端点处的感染人数分别为 $I_{\max}^{0}$ 与 $I_0$，故该区间恰有一个交点，由 $W_{-1}$ 给出。
-沿常规易感者方程分离变量即得式\eqref{eq:s1:t1}；
+前者给出小于 $S_c$ 的状态，即 $I$ 下降时的交点。
+式\eqref{eq:model:routine-orbit}在 $S\in(S_c,S_0)$ 上关于 $S$ 严格递减，端点处的值分别为 $I_{\max}^{0}$ 与 $I_0$；
+由触发条件中的 $I_0<\eta<I_{\max}^{0}$，该区间上恰有一个交点，由 $W_{-1}$ 给出。
+(ii) 沿常规易感者方程分离变量即得式\eqref{eq:s1:t1}。
```

- thm:s1:qc-structure：汉字 131 → 158

```diff
@@ -1,2 +1,3 @@
-由 $I=\eta>0$ 和 $\dot I=0$，式\eqref{eq:model:balance}唯一解出式\eqref{eq:s1:q-control}。
-代入 $S$ 的方程得
+(i)(ii) 由命题~\ref{prop:model:threshold-rationale}(ii)，维持 $I=\eta$ 时式\eqref{eq:model:balance}几乎处处成立；
+取 $c=c_0$，即唯一解出式\eqref{eq:s1:q-control}。
+利用 $\beta+(1-\beta)q_c(S)=1-\bar S/S$，代入 $S$ 的方程得
@@ -7 +8 @@
-由 $S^*>S_c>\bar S$，轨迹严格下降，并在式\eqref{eq:s1:t2}给出的有限时刻首次到达 $S_c$。
+由定理~\ref{thm:s1:start}与式\eqref{eq:s1:barS}，$S^*>S_c>\bar S$，所以轨迹严格下降，并在式\eqref{eq:s1:t2}给出的有限时刻首次到达 $S_c$。
@@ -9,4 +10,4 @@
-反过来，把所得的时间函数 $q_c(t)$ 代回原方程，式\eqref{eq:s1:S-analytic}与 $I=\eta$ 满足前两个方程及启动初值，其余仓室由线性方程或积分确定。
-由命题~\ref{prop:model:positive}的解唯一性，该控制确实使 $I\equiv\eta$，而不只是形式上满足 $\dot I=0$。
-启动前 $I<\eta$；
-退出后 $S<S_c$，故 $\dot I<0$。
+(iii) 反过来，把所得的时间函数 $q_c(t)$ 代回原方程，式\eqref{eq:s1:S-analytic}与 $I=\eta$ 满足前两个方程及启动初值，其余仓室由线性方程或积分确定。
+由命题~\ref{prop:model:positive}中解的唯一性，该控制确实使 $I\equiv\eta$，而不只是形式上满足 $\dot I=0$。
+由 $t_1$ 的定义，启动前 $I<\eta$；
+由命题~\ref{prop:model:threshold-rationale}(iii)，退出后 $S<S_c$、$\dot I<0$。
```

- cor:s1:qc-structure：汉字 94 → 104

```diff
@@ -1,2 +1,2 @@
-$q_c(S)$ 关于 $S$ 严格增加，$S^*>S_c$ 给出启动时的跳升。
-沿控制轨迹，
+(i) 由式\eqref{eq:s1:q-control}，$q_c(S)$ 关于 $S$ 严格增加，$S^*>S_c$ 给出启动时的跳升。
+由链式法则与式\eqref{eq:s1:S-analytic}，沿控制轨迹
@@ -8 +8 @@
-隔离比例在启动时取得最大值，因此全时段的能力约束等价于检查这一最大值；
+(ii) 由 (i)，隔离比例在启动时取得最大值，因此全时段的能力约束等价于检查这一最大值；
```

- thm:s1:inflection：汉字 91 → 102

```diff
@@ -1 +1 @@
-对式\eqref{eq:s1:qprime}求导，得
+(i) 由链式法则与式\eqref{eq:s1:S-analytic}，对式\eqref{eq:s1:qprime}求导，得
@@ -7 +7 @@
-由于 $S>\bar S$，其符号由 $2\bar S-S$ 决定。
+由式\eqref{eq:s1:barS}，阈值控制期内 $S\ge S_c>\bar S$，故其符号由 $2\bar S-S$ 决定。
@@ -9 +9 @@
-将该状态代入式\eqref{eq:s1:S-analytic}及\eqref{eq:s1:q-control}，即得时间和隔离比例。
+(ii) 将 $S=2\bar S$ 代入式\eqref{eq:s1:S-analytic}及\eqref{eq:s1:q-control}，即得时间和隔离比例。
```

- thm:s1:Itcum：汉字 48 → 66

```diff
@@ -1 +1 @@
-前后常规阶段均有
+由式\eqref{eq:model:full}，常规控制下总新增感染的流入为 $\beta c_0SI/N$，而 $-\dot S=c_0[\beta+(1-\beta)q_0]SI/N$，故前后常规阶段均有
```

