# 定理类陈述与证明的变化

- 旧稿：d286b46:paper/sections/04_joint_control.tex
- 新稿：paper/sections/04_joint_control.tex

带标签的陈述：旧稿 7 条，新稿 7 条；共同 7 条，其中未变化 0 条，有变化 7 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:representation

```diff
@@ -1 +1,4 @@
-在几乎处处相等的意义下，$\mathcal A(\eta)$ 中的控制与满足
+设条件\eqref{eq:model:trigger}成立，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 在几乎处处相等的意义下，$\mathcal A(\eta)$ 中的控制与满足
@@ -5,2 +8 @@
-的有界可测函数 $c_c$ 一一对应。
-隔离比例由
+的有界可测函数 $c_c$ 一一对应，隔离比例由
@@ -11 +13,2 @@
-确定，状态轨迹与控制时长满足
+确定；
+\item 状态轨迹与控制时长满足
@@ -16 +19 @@
-\frac{dS}{c_c(S)S-c_0\bar S}.
+\frac{dS}{c_c(S)S-c_0\bar S},
@@ -18,2 +21,2 @@
-式\eqref{eq:joint:time}唯一确定严格递减的 $S(t)$。
-选取满足式\eqref{eq:joint:contact-range}的逐点代表后，退出时 $c(t)\to c_0$、$q(t)\to q_0$；
+式\eqref{eq:joint:time}唯一确定严格递减的 $S(t)$；
+\item 选取满足式\eqref{eq:joint:contact-range}的逐点代表后，退出时 $c(t)\to c_0$、$q(t)\to q_0$；
@@ -20,0 +24 @@
+\end{enumerate}
```

### cor:joint:feasibility

```diff
@@ -1,2 +1,5 @@
-能力约束等价于 $c^{-}(S)\le c_c(S)\le c^{+}(S)$。
-$\mathcal A(\eta;c_{\min},q_{\rm cap})$ 非空，即从 $S^*$ 到 $S_c$ 的整段阈值控制可行，当且仅当
+设条件\eqref{eq:model:trigger}成立，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 能力约束等价于 $c^{-}(S)\le c_c(S)\le c^{+}(S)$；
+\item $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 非空，即从 $S^*$ 到 $S_c$ 的整段阈值控制可行，当且仅当
@@ -9,0 +13 @@
+\end{enumerate}
```

### thm:joint:comparison

```diff
@@ -23 +23 @@
-因此阈值控制期累计新增感染与控制时长具有相同排序，新增隔离易感者人数的排序相反。
+\item 阈值控制期累计新增感染是控制时长的严格增函数，新增隔离易感者人数是控制时长的严格减函数。
```

### cor:joint:capped-comparison

```diff
@@ -1 +1 @@
-若式\eqref{eq:joint:feasibility}成立，则 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的任一控制满足
+设式\eqref{eq:joint:feasibility}成立，则 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的任一控制满足
```

### cor:joint:whole-epidemic

```diff
@@ -1,2 +1,4 @@
-设两个允许控制在启动前及退出后均采用 $(c_0,q_0)$，并从同一初始状态首次到达同一阈值 $\eta$。
-则
+设两个允许控制在启动前及退出后均采用 $(c_0,q_0)$，并从同一初始状态首次到达同一阈值 $\eta$，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 二者的清零时间与总累计新增感染满足
@@ -7 +9 @@
-&=\gamma\eta(1-\beta)\bigl(\Delta t^{(1)}-\Delta t^{(2)}\bigr).
+&=\gamma\eta(1-\beta)\bigl(\Delta t^{(1)}-\Delta t^{(2)}\bigr),
@@ -9,2 +11,3 @@
-第二式对计算至无限时刻的累计新增感染同样成立。
-能力约束下，$c^{+}(S)$ 因而同时达到最短的控制时长、最早的清零时间和最少的全过程累计新增感染。
+第二式对计算至无限时刻的累计新增感染同样成立；
+\item 设式\eqref{eq:joint:feasibility}成立，则在 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中，$c^{+}(S)$ 同时达到最短的控制时长、最早的清零时间和最少的全过程累计新增感染。
+\end{enumerate}
```

### cor:joint:single-endpoints

```diff
@@ -0,0 +1 @@
+对能力约束下的控制类 $\mathcal A(\eta;c_{\min},q_{\rm cap})$，
@@ -3,4 +4,4 @@
-\item 若 $q_{\rm cap}\ge q_{\max}$，则 $c^{+}(S)\equiv c_0$：
-无论 $c_{\min}$ 取何值，仅隔离控制都是 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中控制时长最短、累计新增感染最少的控制。
-\item 若 $c_{\min}\le c_0S_c/S^*$，则 $c^{-}(S)=c_0S_c/S$：
-无论 $q_{\rm cap}$ 取何值，仅减少接触都使新增隔离易感者人数最少。
+\item 若 $q_{\rm cap}\ge q_{\max}$，则 $c^{+}(S)\equiv c_0$。
+因此无论 $c_{\min}$ 取何值，仅隔离控制都是该控制类中控制时长最短、累计新增感染最少的控制。
+\item 若 $c_{\min}\le c_0S_c/S^*$，则 $c^{-}(S)=c_0S_c/S$。
+因此无论 $q_{\rm cap}$ 取何值，仅减少接触都使该控制类中的新增隔离易感者人数最少。
```

### prop:exit-infection-lower-bound

```diff
@@ -1 +1,4 @@
-对于模型\eqref{eq:model:full}，若 $0\le q(t)\le1$、$c(t)\ge0$，且某一有限时刻 $T$ 满足 $S(T)=S_c<S_0$，则
+对于模型\eqref{eq:model:full}，设控制满足命题~\ref{prop:model:positive}的条件，且某一有限时刻 $T$ 满足 $S(T)=S_c<S_0$，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 退出时刻的累计新增感染满足
@@ -3 +6 @@
-\Itcum(T)\ge\beta(S_0-S_c).
+\Itcum(T)\ge\beta(S_0-S_c);
@@ -5 +8 @@
-若整个 $[0,T]$ 上另有 $q(t)\le q_{\rm cap}<1$，则
+\item 若整个 $[0,T]$ 上另有 $q(t)\le q_{\rm cap}<1$，则
@@ -9,0 +13 @@
+\end{enumerate}
```

## 证明

有证明的陈述：旧稿 6 条，新稿 6 条；证明有变化 5 条。

- cor:joint:feasibility：汉字 65 → 71

```diff
@@ -1,2 +1,3 @@
-$c_c\ge c_{\min}$ 与式\eqref{eq:joint:contact-range}给出下界，式\eqref{eq:joint:q}中的 $q_c\le q_{\rm cap}$ 给出上界。
-在 $S\in[S_c,S^*]$ 上已有 $c_0S_c/S\le c_0$、$c_0S_c/S\le c_0(1-q_0)S_c/[(1-q_{\rm cap})S]$ 及 $c_{\min}\le c_0$，故只需检验
+(i) 由 $c_c\ge c_{\min}$ 与式\eqref{eq:joint:contact-range}得下界 $c^{-}$。
+由式\eqref{eq:joint:q}，$q_c\le q_{\rm cap}$ 等价于 $c_c(S)\le c_0(1-q_0)S_c/[(1-q_{\rm cap})S]$，与式\eqref{eq:joint:contact-range}合起来得上界 $c^{+}$。
+(ii) 在 $S\in[S_c,S^*]$ 上已有 $c_0S_c/S\le c_0$、$c_0S_c/S\le c_0(1-q_0)S_c/[(1-q_{\rm cap})S]$ 及 $c_{\min}\le c_0$，故只需检验
```

- thm:joint:comparison：汉字 136 → 162

```diff
@@ -1 +1 @@
-式\eqref{eq:joint:duration}的被积函数关于 $c_c(S)$ 严格递减，故得到一般排序。
+(i) 式\eqref{eq:joint:duration}的被积函数关于 $c_c(S)$ 严格递减，故得到一般排序。
@@ -10,2 +10,2 @@
-显式族中 $c_c(S;\alpha)$ 对 $S>S_c$ 随 $\alpha$ 严格增加，故其控制时长严格减少。
-积分式\eqref{eq:joint:Sdot}，得
+(ii) 显式族中 $c_c(S;\alpha)$ 对 $S>S_c$ 随 $\alpha$ 严格增加，由 (i)，其控制时长严格减少。
+(iii) 积分式\eqref{eq:joint:Sdot}，得
@@ -22,0 +23 @@
+(iv) 由 $0<\beta<1$，式\eqref{eq:joint:cumulative}中 $\Delta t$ 的系数 $\gamma\eta(1-\beta)$ 为正，式\eqref{eq:joint:quarantine}中的系数 $-(1-\beta)\gamma\eta$ 为负，其余各项对所有控制相同。
```

- cor:joint:capped-comparison：汉字 40 → 69

```diff
@@ -1,3 +1,4 @@
-在式\eqref{eq:joint:duration}中用 $c^{-}\le c_c\le c^{+}$ 比较即可。
-两个边界函数连续且满足能力约束，因而对应可行控制。
-感染的结论由式\eqref{eq:joint:cumulative}得到。
+由推论~\ref{cor:joint:feasibility}(i)，可行控制满足 $c^{-}\le c_c\le c^{+}$；
+按定理~\ref{thm:joint:comparison}(i) 的方式在式\eqref{eq:joint:duration}中比较，即得式\eqref{eq:joint:capped-duration}及等号条件。
+两个边界函数连续且满足能力约束，由定理~\ref{thm:joint:representation}对应可行控制，故两端均可达到。
+感染的结论由定理~\ref{thm:joint:comparison}(iv) 得到。
```

- cor:joint:whole-epidemic：汉字 91 → 124

```diff
@@ -1 +1 @@
-控制前两条轨迹相同，故 $t_1,S^*$ 相同。
+(i) 两个控制在启动前相同，由命题~\ref{prop:model:positive}中解的唯一性，控制前两条轨迹相同，故 $t_1,S^*$ 相同。
@@ -4,0 +5 @@
+(ii) 由推论~\ref{cor:joint:capped-comparison}，$c^{+}$ 的控制时长最短，再由 (i) 即得。
```

- prop:exit-infection-lower-bound：汉字 35 → 51

```diff
@@ -1 +1 @@
-由易感者方程和累计新增感染的定义，
+由式\eqref{eq:model:full}的易感者方程与第~\ref{sec:cost}~节中累计新增感染的定义，总新增感染的流入为 $\beta cSI/N$，而 $-\dot S=c[\beta+(1-\beta)q]SI/N$，故
@@ -6,3 +6,4 @@
-$-\dot S\ge0$，且比例系数分别不小于 $\beta$ 和
-$\beta/[\beta+(1-\beta)q_{\rm cap}]$。
-在 $[0,T]$ 上积分即得两式。
+$-\dot S\ge0$。
+由 $q\le1$，比例系数不小于 $\beta$；
+若 $q\le q_{\rm cap}$，它不小于 $\beta/[\beta+(1-\beta)q_{\rm cap}]$。
+在 $[0,T]$ 上积分即得 (i)(ii)。
```

