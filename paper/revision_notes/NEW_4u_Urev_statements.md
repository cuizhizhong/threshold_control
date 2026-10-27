# 定理类陈述与证明的变化

- 旧稿：c752f70:paper/sections/02_model.tex c752f70:paper/sections/03_single_control.tex c752f70:paper/sections/04_joint_control.tex c752f70:paper/sections/05_quadratic_cost.tex c752f70:paper/appendices/A_proofs_sensitivity.tex c752f70:paper/appendices/B_control_cost.tex c752f70:paper/supplement_sections/S1_medical.tex c752f70:paper/supplement_sections/S2_single_control.tex c752f70:paper/supplement_sections/S3_inflection.tex c752f70:paper/supplement_sections/S4_explicit_control.tex c752f70:paper/supplement_sections/S5_weight_structure.tex
- 新稿：paper/sections/02_model.tex paper/sections/03_single_control.tex paper/sections/04_joint_control.tex paper/sections/05_quadratic_cost.tex paper/appendices/A_proofs_sensitivity.tex paper/appendices/B_control_cost.tex paper/supplement_sections/S1_medical.tex paper/supplement_sections/S2_single_control.tex paper/supplement_sections/S3_inflection.tex paper/supplement_sections/S4_explicit_control.tex paper/supplement_sections/S5_weight_structure.tex

带标签的陈述：旧稿 37 条，新稿 37 条；共同 37 条，其中未变化 17 条，有变化 20 条。

## 陈述有变化（逐条确认数学含义是否等价）

### prop:model:positive

```diff
@@ -1,2 +1,6 @@
-在上述参数与初值假设下，设 $c(t)\ge0$ 局部有界且可测，$q(t)\in[0,1]$ 可测，则式\eqref{eq:model:full}存在唯一的全局绝对连续解，方程几乎处处成立。
-各仓室非负，总和恒为 $N$，且对一切 $t\ge0$ 有 $S(t),I(t)>0$。
+设参数与初值满足上述假设，$c(t)\ge0$ 局部有界且可测，$q(t)\in[0,1]$ 可测，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 式\eqref{eq:model:full}存在唯一的全局绝对连续解，方程几乎处处成立；
+\item 各仓室非负，总和恒为 $N$，且对一切 $t\ge0$ 有 $S(t),I(t)>0$。
+\end{enumerate}
```

### prop:model:threshold-rationale

```diff
@@ -4,2 +4 @@
-\item 若一个策略在首次加强干预之前采用 $(c_0,q_0)$，且始终满足 $I\le\eta$，则它首次加强干预的时刻不晚于 $t_1$。
-常规轨迹在 $[0,t_1]$ 上满足 $I\le\eta$。
+\item 若一个策略在首次加强干预之前采用 $(c_0,q_0)$，且始终满足 $I\le\eta$，则它首次加强干预的时刻不晚于 $t_1$，而常规轨迹在 $[0,t_1]$ 上满足 $I\le\eta$；
@@ -8 +7 @@
-\frac{\beta c(1-q)S}{N}\le\gamma.
+\frac{\beta c(1-q)S}{N}\le\gamma,
@@ -10,3 +9,2 @@
-若在某个时间区间上 $I\equiv\eta$，则该区间上几乎处处取等号。
-\item 从状态 $(S,\eta)$ 恢复并保持 $(c_0,q_0)$ 后始终有 $I\le\eta$，当且仅当 $S\le S_c$。
-因此，对任一从 $(S^*,\eta)$ 出发并持续维持 $I=\eta$ 的允许轨迹，$S$ 首次降到 $S_c$ 的时刻是该轨迹上可以直接恢复常规控制的最早时刻。
+且若在某个时间区间上 $I\equiv\eta$，则该区间上几乎处处取等号；
+\item 从状态 $(S,\eta)$ 恢复并保持 $(c_0,q_0)$ 后始终有 $I\le\eta$，当且仅当 $S\le S_c$，因此对任一从 $(S^*,\eta)$ 出发并持续维持 $I=\eta$ 的允许轨迹，$S$ 首次降到 $S_c$ 的时刻是该轨迹上可以直接恢复常规控制的最早时刻。
```

### thm:s1:start

```diff
@@ -1,7 +1 @@
-设条件\eqref{eq:model:trigger}成立。
-令
-\begin{equation}
-z_\eta=-\frac{1}{S_c}\exp\!\left[-\frac{C_0-\eta}{\rho_1}\right]
-=-\frac{S_0}{S_c}\exp\!\left[-\frac{S_0}{S_c}+\frac{\eta-I_0}{\rho_1}\right],
-\end{equation}
-并记 $W_{-1}$ 为 Lambert $W$ 函数的下实分支，则
+设条件\eqref{eq:model:trigger}成立，记 $W_{-1}$ 为 Lambert $W$ 函数的下实分支，则
```

### cor:s1:qc-structure

```diff
@@ -8 +8 @@
-在 $(t_1,t_2)$ 上严格递减，并在 $t_2$ 连续恢复为 $q_0$。
+在 $(t_1,t_2)$ 上严格递减，并在 $t_2$ 连续恢复为 $q_0$；
@@ -13 +13 @@
-\frac{\beta c_0(1-q_{\rm cap})S^*}{N}\le\gamma.
+\frac{\beta c_0(1-q_{\rm cap})S^*}{N}\le\gamma,
@@ -15 +15 @@
-该条件成立时，能力约束不改变上述控制轨迹、控制时长及成本公式。
+且该条件成立时，能力约束不改变上述控制轨迹、控制时长及成本公式。
```

### thm:s1:tend

```diff
@@ -1 +1,4 @@
-从 $(S_c,\eta)$ 恢复常规控制后，$S(t)$ 和 $I(t)$ 对 $t>t_2$ 均严格递减，且
+设 $t_2$ 时 $(S,I)=(S_c,\eta)$，此后恢复常规控制，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item $S(t)$ 和 $I(t)$ 对 $t>t_2$ 均严格递减，且
@@ -4 +7 @@
-S(t)\to S_\infty=-S_cW_0\!\left(-e^{-1-\eta/\rho_1}\right)\in(0,S_c).
+S(t)\to S_\infty=-S_cW_0\!\left(-e^{-1-\eta/\rho_1}\right)\in(0,S_c);
@@ -6,2 +9,2 @@
-存在唯一的 $t_{\rm end}>t_2$ 满足 $I(t_{\rm end})=1$、$\dot I(t_{\rm end})<0$。
-记 $S_{\rm end}=S(t_{\rm end})$，有
+\item 存在唯一的 $t_{\rm end}>t_2$，满足 $I(t_{\rm end})=1$、$\dot I(t_{\rm end})<0$；
+记 $S_{\rm end}=S(t_{\rm end})$，则
@@ -14,0 +18 @@
+\end{enumerate}
```

### prop:scaling

```diff
@@ -1 +1 @@
-对于仅隔离控制，固定 $s_0,i_0$ 和 $\beta,\gamma,c_0,q_0$，并设控制被触发，则
+固定 $s_0,i_0$ 和 $\beta,\gamma,c_0,q_0$，并设条件\eqref{eq:model:trigger}成立，则仅隔离控制满足：
@@ -4 +4 @@
-\item $t_1,\Delta t,q_{\max},J$ 以及存在内部拐点时的 $\lambda$ 对 $N,\eta$ 的依赖仅通过 $\theta=\eta/N$ 表现；
+\item $t_1,\Delta t,q_{\max},J$ 以及存在内部拐点时的 $\lambda$ 只通过 $\theta=\eta/N$ 依赖于 $N$ 和 $\eta$；
```

### cor:joint:feasibility

```diff
@@ -7 +7 @@
-\frac{\beta c_{\min}(1-q_{\rm cap})S^*}{N}\le\gamma.
+\frac{\beta c_{\min}(1-q_{\rm cap})S^*}{N}\le\gamma,
@@ -9,4 +9 @@
-利用式\eqref{eq:s1:qmax}，该条件也可写为
-\[
-c_{\min}(1-q_{\rm cap})\le c_0(1-q_{\max}).
-\]
+或等价地 $c_{\min}(1-q_{\rm cap})\le c_0(1-q_{\max})$，其中 $q_{\max}$ 由式\eqref{eq:s1:qmax}给出。
```

### thm:joint:comparison

```diff
@@ -4,2 +4 @@
-\item 若 $c_c^{(1)}(S)\ge c_c^{(2)}(S)$ 几乎处处成立，则 $\Delta t[c_c^{(1)}]\le\Delta t[c_c^{(2)}]$；
-若前一不等式在正测度集合上严格成立，则后一不等式严格。
+\item 若 $c_c^{(1)}(S)\ge c_c^{(2)}(S)$ 几乎处处成立，则 $\Delta t[c_c^{(1)}]\le\Delta t[c_c^{(2)}]$，且前一不等式在正测度集合上严格成立时后一不等式严格；
@@ -12,3 +11,2 @@
-左侧等号当且仅当 $c_c(S)=c_0$ 几乎处处，即仅隔离控制；
-右侧等号当且仅当 $c_c(S)=c_0S_c/S$ 几乎处处，即仅减少接触。
-\item 显式族的 $\Delta t(\alpha)$ 在 $[0,1]$ 上严格递减。
+左侧等号成立当且仅当 $c_c(S)=c_0$ 几乎处处（仅隔离控制），右侧等号成立当且仅当 $c_c(S)=c_0S_c/S$ 几乎处处（仅减少接触）；
+\item 显式族的 $\Delta t(\alpha)$ 在 $[0,1]$ 上严格递减；
@@ -21 +19 @@
-&=(1-\beta)\bigl[S^*-S_c-\gamma\eta\Delta t\bigr].
+&=(1-\beta)\bigl[S^*-S_c-\gamma\eta\Delta t\bigr];
```

### cor:joint:capped-comparison

```diff
@@ -1 +1,4 @@
-设式\eqref{eq:joint:feasibility}成立，则 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的任一控制满足
+设式\eqref{eq:joint:feasibility}成立，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中的任一控制满足
@@ -5,3 +8,3 @@
-其中两端由式\eqref{eq:joint:duration}分别代入 $c^{+}(S)$、$c^{-}(S)$ 计算，且均可达到；
-达到左、右等号分别要求 $c_c=c^{+}$、$c_c=c^{-}$ 几乎处处成立。
-这两个控制分别使阈值控制期累计新增感染在该控制类中最少和最多。
+其中两端由式\eqref{eq:joint:duration}分别代入 $c^{+}(S)$、$c^{-}(S)$ 计算，均可达到，且达到左、右等号分别要求 $c_c=c^{+}$、$c_c=c^{-}$ 几乎处处成立；
+\item $c^{+}$ 与 $c^{-}$ 对应的控制分别使阈值控制期累计新增感染在该控制类中最少和最多。
+\end{enumerate}
```

### cor:joint:single-endpoints

```diff
@@ -4,4 +4,2 @@
-\item 若 $q_{\rm cap}\ge q_{\max}$，则 $c^{+}(S)\equiv c_0$。
-因此无论 $c_{\min}$ 取何值，仅隔离控制都是该控制类中控制时长最短、累计新增感染最少的控制。
-\item 若 $c_{\min}\le c_0S_c/S^*$，则 $c^{-}(S)=c_0S_c/S$。
-因此无论 $q_{\rm cap}$ 取何值，仅减少接触都使该控制类中的新增隔离易感者人数最少。
+\item 若 $q_{\rm cap}\ge q_{\max}$，则 $c^{+}(S)\equiv c_0$，因此无论 $c_{\min}$ 取何值，仅隔离控制都是该控制类中控制时长最短、累计新增感染最少的控制；
+\item 若 $c_{\min}\le c_0S_c/S^*$，则 $c^{-}(S)=c_0S_c/S$，因此无论 $q_{\rm cap}$ 取何值，仅减少接触都使该控制类中的新增隔离易感者人数最少。
```

### prop:exit-infection-lower-bound

```diff
@@ -1 +1 @@
-对于模型\eqref{eq:model:full}，设控制满足命题~\ref{prop:model:positive}的条件，且某一有限时刻 $T$ 满足 $S(T)=S_c<S_0$，则
+设控制满足命题~\ref{prop:model:positive}的条件，模型\eqref{eq:model:full}的解在某一有限时刻 $T$ 满足 $S(T)=S_c<S_0$，则
```

### thm:joint:cost-structure

```diff
@@ -4,4 +4,4 @@
-\item 对每个 $S>S_c$，$f(S,\cdot)$ 在 $[c_0S_c/S,c_0]$ 上有唯一最小点 $c_c^*(S)$；
-$c_c^*$ 在 $(S_c,\infty)$ 上连续，且 $S\downarrow S_c$ 时 $c_c^*(S)\to c_0$。
-\item $S\ge S_{\rm sw}$ 时 $c_c^*(S)=c_0$；
-$S_c<S<S_{\rm sw}$ 时 $c_0S_c/S<c_c^*(S)<c_0$。
+\item 对每个 $S>S_c$，$f(S,\cdot)$ 在 $[c_0S_c/S,c_0]$ 上有唯一最小点 $c_c^*(S)$，$c_c^*$ 在 $(S_c,\infty)$ 上连续，且 $S\downarrow S_c$ 时 $c_c^*(S)\to c_0$；
+\item $S\ge S_{\rm sw}$ 时 $c_c^*(S)=c_0$，$S_c<S<S_{\rm sw}$ 时 $c_0S_c/S<c_c^*(S)<c_0$；
+\item 成本最优控制几乎处处等于连续的状态反馈 $c_c^*$，且 $S^*>S_{\rm sw}$ 时它在 $S\ge S_{\rm sw}$ 上为仅隔离控制，并在 $S_{\rm sw}$ 处连续地转为两种措施并用；
+$S^*\le S_{\rm sw}$ 时整个阈值控制期两种措施并用。
@@ -9,3 +8,0 @@
-因此，成本最优控制几乎处处等于连续的状态反馈 $c_c^*$：
-若 $S^*>S_{\rm sw}$，它在 $S\ge S_{\rm sw}$ 上为仅隔离控制，并在 $S_{\rm sw}$ 处连续地转为两种措施并用；
-若 $S^*\le S_{\rm sw}$，整个阈值控制期两种措施并用。
```

### prop:joint:terminal-allocation

```diff
@@ -16 +16 @@
-\frac{(q_c^*(S)-q_0)/(1-q_0)}{1-S_c/S}&=\frac{w_c}{w_c+w_q}.
+\frac{(q_c^*(S)-q_0)/(1-q_0)}{1-S_c/S}&=\frac{w_c}{w_c+w_q};
@@ -19 +19 @@
-\item 不考虑能力约束时，最小成本严格小于仅减少接触与仅隔离控制各自的成本。
+\item 不考虑能力约束时，最小成本严格小于仅减少接触与仅隔离控制各自的成本；
```

### prop:joint:minimum-threshold

```diff
@@ -5 +5 @@
-对其中任意两个阈值，可以选取成本最优控制，使二者在共同经过的易感者状态上取相同的 $c_c^*(S)$ 与 $q_c^*(S)$。
+对其中任意两个阈值，可以选取成本最优控制，使二者在共同经过的易感者状态上取相同的 $c_c^*(S)$ 与 $q_c^*(S)$；
```

### prop:joint:weight-monotone

```diff
@@ -5 +5 @@
-\item 若 $0<r_1<r_2$，则对每个 $S\in(S_c,S^*]$ 有 $c_{r_2}^*(S)\le c_{r_1}^*(S)$、$q_{r_2}^*(S)\le q_{r_1}^*(S)$。
+\item 若 $0<r_1<r_2$，则对每个 $S\in(S_c,S^*]$ 有 $c_{r_2}^*(S)\le c_{r_1}^*(S)$、$q_{r_2}^*(S)\le q_{r_1}^*(S)$；
@@ -7 +7 @@
-最小成本 $J_{\min}/w_c$ 是 $r$ 的凹且不减的函数。
+最小成本 $J_{\min}/w_c$ 是 $r$ 的凹且不减的函数；
```

### lem:proof:fold-free

```diff
@@ -1,2 +1,2 @@
-设 $0<b<1$，$s_c=\sqrt{r_{\rm cont}}$。
-对 $p>3/2$ 与 $s>0$，记
+设 $0<b<1$，$\sigma_c=\sqrt{r_{\rm cont}}$。
+对 $p>3/2$ 与 $\sigma>0$，记
@@ -4 +4 @@
-F(p;s)=s^2X(p)-2sbp\sqrt{2p-3}+p^3,\qquad X(p)=p^3-6p^2+6p+2b(3p-4).
+F(p;\sigma)=\sigma^2X(p)-2\sigma bp\sqrt{2p-3}+p^3,\qquad X(p)=p^3-6p^2+6p+2b(3p-4).
@@ -6,2 +6,2 @@
-则 $0<s<s_c$ 时 $F(p;s)>0$；
-$s=s_c$ 时 $F(p;s_c)\ge0$，且等号仅在 $p=2$ 成立。
+则 $0<\sigma<\sigma_c$ 时 $F(p;\sigma)>0$；
+$\sigma=\sigma_c$ 时 $F(p;\sigma_c)\ge0$，且等号仅在 $p=2$ 成立。
```

### prop:contact-effects

```diff
@@ -1 +1 @@
-在触发条件内部，对于仅隔离控制：
+设条件\eqref{eq:model:trigger}成立，则仅隔离控制满足：
@@ -20 +20 @@
-\item 固定 $I_0<\eta<I_0+\beta_2^0S_0/\beta_1^0$ 时，$\Delta t$ 在 $c_0\in(c_{0,\min},\infty)$ 内至少有一个极大值。
+\item 固定除 $c_0$ 外的参数，且 $I_0<\eta<I_0+\beta_2^0S_0/\beta_1^0$ 时，$\Delta t$ 作为 $c_0$ 的函数在 $(c_{0,\min},\infty)$ 内至少有一个极大值。
```

### prop:sup:rhat

```diff
@@ -1,8 +1,7 @@
-设 $w_c,w_q>0$，$r=w_q/w_c$，不考虑能力约束。
-对一切 $S>S_{\rm sw}$，$c=c_0$ 都是 $f(S,\cdot)$ 在 $[c_0S_c/S,c_0]$ 上的唯一全局最小点，当且仅当
-\[
-r\le\hat r=\Bigl(\frac{S_{\rm sw}}{S_{\rm sw}-S_c}\Bigr)^2 .
-\]
-$r<\hat r$ 时 $c_0$ 在 $S=S_{\rm sw}$ 处也是唯一全局最小点；
-$r=\hat r$ 时它在该处与 $c=c_0S_c/(S_{\rm sw}-S_c)$ 并列全局最优。
-此外 $9/4<\hat r<4$，且 $r_{\rm cont}<\hat r$。
+设 $w_c,w_q>0$，$r=w_q/w_c$，不考虑能力约束，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 对一切 $S>S_{\rm sw}$，$c=c_0$ 都是 $f(S,\cdot)$ 在 $[c_0S_c/S,c_0]$ 上的唯一全局最小点，当且仅当 $r\le\hat r$；
+\item $r<\hat r$ 时 $c_0$ 在 $S=S_{\rm sw}$ 处也是唯一全局最小点，$r=\hat r$ 时它在该处与 $c=c_0S_c/(S_{\rm sw}-S_c)$ 并列全局最优；
+\item $9/4<\hat r<4$，且 $r_{\rm cont}<\hat r$。
+\end{enumerate}
```

### lem:sup:interior-tie

```diff
@@ -1,3 +1,5 @@
-设 $w_c,w_q>0$，不考虑能力约束，$\zeta>1$。
-若 $G(\cdot;\zeta)$ 在 $(1,\zeta)$ 内有两个不同的全局最小点 $p_1<p_2$，则 $\zeta=\zeta_{\rm j}(r)$，且 $p_1+p_2=p_1p_2=\sqrt r\,\zeta_{\rm j}$。
-此外，对任意 $r>0$ 与 $p>b$，记 $k=\sqrt r\,\zeta_{\rm j}$，有
+设 $w_c,w_q>0$，不考虑能力约束，则
+\begin{enumerate}
+\renewcommand{\labelenumi}{(\roman{enumi})}
+\item 若对某个 $\zeta>1$，$G(\cdot;\zeta)$ 在 $(1,\zeta)$ 内有两个不同的全局最小点 $p_1<p_2$，则 $\zeta=\zeta_{\rm j}(r)$，且 $p_1+p_2=p_1p_2=\sqrt r\,\zeta_{\rm j}$；
+\item 对任意 $r>0$ 与 $p>b$，记 $k=\sqrt r\,\zeta_{\rm j}$，有
@@ -7,0 +10 @@
+\end{enumerate}
```

### prop:sup:jump

```diff
@@ -1,3 +1 @@
-设 $w_c,w_q>0$，不考虑能力约束。
-$G(\cdot;\zeta)$ 在 $[1,\zeta]$ 上的最小点除至多一个状态外唯一，并在其余状态上随 $\zeta$ 连续变化；
-因此成本最优控制几乎处处唯一，可取为除该状态外连续的状态反馈。
+设 $w_c,w_q>0$，不考虑能力约束，则 $G(\cdot;\zeta)$ 在 $[1,\zeta]$ 上的最小点除至多一个状态外唯一，并在其余状态上随 $\zeta$ 连续变化，因此成本最优控制几乎处处唯一，可取为除该状态外连续的状态反馈。
@@ -15 +13,2 @@
-随 $S$ 减小，最优选择在 $S_c\zeta_0$ 处由 $p=\zeta_0$ 跳到该内部取值。
+随 $S$ 减小，最优选择在 $S_c\zeta_0$ 处由 $p=\zeta_0$ 跳到该内部取值；
+\item 在 (ii)(iii) 的跳变处，沿时间方向接触率与隔离比例同时下降。
@@ -17 +15,0 @@
-在 (ii)(iii) 的跳变处，沿时间方向接触率与隔离比例同时下降。
```

## 证明

有证明的陈述：旧稿 22 条，新稿 22 条；证明有变化 15 条。

- cor:s1:qc-structure：汉字 104 → 136

```diff
@@ -9,0 +10 @@
+该条件成立时，原控制满足能力约束，故控制轨迹、控制时长与成本公式都不变。
```

- thm:s1:inflection：汉字 102 → 111

```diff
@@ -8,0 +9 @@
+由式\eqref{eq:s1:barS}与\eqref{eq:s1:Sstar-lambert}，$2\bar S/S_c=2(1-\beta)(1-q_0)$，$S^*/S_c=-W_{-1}(z_\eta)$，即得等价形式。
```

- cor:joint:feasibility：汉字 71 → 79

```diff
@@ -7,0 +8 @@
+由式\eqref{eq:s1:qmax}，$\beta c_0(1-q_{\max})S^*/N=\gamma$，故该式等价于 $c_{\min}(1-q_{\rm cap})\le c_0(1-q_{\max})$。
```

- thm:joint:comparison：汉字 162 → 195

```diff
@@ -1 +1,3 @@
-(i) 式\eqref{eq:joint:duration}的被积函数关于 $c_c(S)$ 严格递减，故得到一般排序。
+(i) 式\eqref{eq:joint:duration}的被积函数关于 $c_c(S)$ 严格递减。
+$c_c^{(1)}\ge c_c^{(2)}$ 几乎处处成立时，两被积函数之差几乎处处非负，积分即得 $\Delta t[c_c^{(1)}]\le\Delta t[c_c^{(2)}]$；
+差在正测度集合上为正时，不等式严格。
```

- cor:joint:capped-comparison：汉字 69 → 65

```diff
@@ -1 +1 @@
-由推论~\ref{cor:joint:feasibility}(i)，可行控制满足 $c^{-}\le c_c\le c^{+}$；
+(i) 由推论~\ref{cor:joint:feasibility}(i)，可行控制满足 $c^{-}\le c_c\le c^{+}$；
@@ -4 +4 @@
-感染的结论由定理~\ref{thm:joint:comparison}(iv) 得到。
+(ii) 由 (i) 与定理~\ref{thm:joint:comparison}(iv) 得到。
```

- prop:exit-infection-lower-bound：汉字 51 → 53

```diff
@@ -6,2 +6 @@
-$-\dot S\ge0$。
-由 $q\le1$，比例系数不小于 $\beta$；
+又 $-\dot S\ge0$，而由 $q\le1$，比例系数不小于 $\beta$；
```

- prop:joint:weight-monotone：汉字 181 → 200

```diff
@@ -2,0 +3 @@
+下面先证该解满足 (ii)，再由 (ii) 把它延拓到全部 $t\ge0$。
@@ -6 +7 @@
-I(t)&=I_0\exp\!\left[\int_0^t\left(\frac{\beta c(s)(1-q(s))}{N}S(s)-\gamma\right)ds\right],
+I(t)&=I_0\exp\!\left[\int_0^t\left(\frac{\beta c(s)(1-q(s))}{N}S(s)-\gamma\right)\,ds\right],
@@ -13 +14 @@
-由非负性与守恒，各分量都在 $[0,N]$ 中，解不会在有限时间内爆破，因而可以延拓到全部 $t\ge0$。
+由非负性与守恒，各分量都在 $[0,N]$ 中，解不会在有限时间内爆破，因而可以延拓到全部 $t\ge0$，即得 (i)。
```

- lem:proof:fold-free：汉字 103 → 106

```diff
@@ -1 +1 @@
-由式\eqref{eq:joint:rcont}，$s_c=4/(b+\sqrt{b^2-8b+8})\in(\sqrt2,2)$ 满足 $(1-b)s_c^2+bs_c-2=0$，即 $b=(s_c^2-2)/[s_c(s_c-1)]$。
+由式\eqref{eq:joint:rcont}，$\sigma_c=4/(b+\sqrt{b^2-8b+8})\in(\sqrt2,2)$ 满足 $(1-b)\sigma_c^2+b\sigma_c-2=0$，即 $b=(\sigma_c^2-2)/[\sigma_c(\sigma_c-1)]$。
@@ -4 +4 @@
-F(p;s_c)=\frac{(w-1)^2\,Q(w,s_c)}{8(s_c-1)},
+F(p;\sigma_c)=\frac{(w-1)^2\,Q(w,\sigma_c)}{8(\sigma_c-1)},
@@ -7 +7,4 @@
-Q(w,s)=(s-1)(s^2+1)w^3(w+2)+12(s-1)w^2-2(s^3+3s^2-11s+3)w+(9s^2+11s-s^3-27).
+\begin{split}
+Q(w,\sigma)={}&(\sigma-1)(\sigma^2+1)w^3(w+2)+12(\sigma-1)w^2\\
+&-2(\sigma^3+3\sigma^2-11\sigma+3)w+(9\sigma^2+11\sigma-\sigma^3-27).
+\end{split}
@@ -9,2 +12,2 @@
-在 $s\in(\sqrt2,2)$ 上，$Q$ 的常数项随 $s$ 增，不小于 $9(\sqrt2-1)$；
-一次项系数随 $s$ 减，不小于 $-2$；
+在 $\sigma\in(\sqrt2,2)$ 上，$Q$ 的常数项随 $\sigma$ 增，不小于 $9(\sqrt2-1)$；
+一次项系数随 $\sigma$ 减，不小于 $-2$；
@@ -13,5 +16,5 @@
-所以对 $w\ge0$ 有 $Q\ge9(\sqrt2-1)-2w+12(\sqrt2-1)w^2>0$（判别式为负），从而 $F(p;s_c)\ge0$，等号仅在 $w=1$ 即 $p=2$ 成立。
-再看 $0<s<s_c$。
-$F$ 是 $s$ 的二次式，且 $F(p;0)=p^3>0$。
-若 $X(p)\le0$，$F$ 在 $s>0$ 上严格减，故 $F(p;s)>F(p;s_c)\ge0$。
-若 $X(p)>0$ 且 $F$ 有实根 $s_1\le s_2$，则判别式非负给出 $X\le b^2w^2/p$，于是
+所以对 $w\ge0$ 有 $Q\ge9(\sqrt2-1)-2w+12(\sqrt2-1)w^2>0$（判别式为负），从而 $F(p;\sigma_c)\ge0$，等号仅在 $w=1$ 即 $p=2$ 成立。
+下证 $0<\sigma<\sigma_c$ 的情形。
+$F$ 是 $\sigma$ 的二次式，且 $F(p;0)=p^3>0$。
+若 $X(p)\le0$，$F$ 在 $\sigma>0$ 上严格减，故 $F(p;\sigma)>F(p;\sigma_c)\ge0$。
+若 $X(p)>0$ 且 $F$ 有实根 $\sigma_1\le\sigma_2$，则判别式非负给出 $X\le b^2w^2/p$，于是
@@ -19 +22 @@
-s_2\ge\frac{bpw}{X}\ge\frac{p^2}{bw}>\frac{p^2}{\sqrt{2p-3}}\ge4>s_c;
+\sigma_2\ge\frac{bpw}{X}\ge\frac{p^2}{bw}>\frac{p^2}{\sqrt{2p-3}}\ge4>\sigma_c;
@@ -21 +24 @@
-由 $F(p;s_c)\ge0$ 得 $s_c\le s_1$，故 $F(p;s)>0$。
+由 $F(p;\sigma_c)\ge0$ 得 $\sigma_c\le\sigma_1$，故 $F(p;\sigma)>0$。
```

- prop:contact-effects：汉字 135 → 135

```diff
@@ -1 +1 @@
-(i) 写 $I(S;c_0)=I_0+\frac{\beta_2^0}{\beta_1^0}(S_0-S)+\rho_1\ln(S/S_0)$。
+(i) 记 $I(S;c_0)=I_0+(\beta_2^0/\beta_1^0)(S_0-S)+\rho_1\ln(S/S_0)$。
@@ -26 +26 @@
-$S^*\to S_0-\frac{\beta_1^0}{\beta_2^0}(\eta-I_0)>0$，而 $S_c,\bar S$ 均为 $O(c_0^{-1})$，故
+$S^*\to S_0-(\beta_1^0/\beta_2^0)(\eta-I_0)>0$，而 $S_c,\bar S$ 均为 $O(c_0^{-1})$，故
```

- prop:s1:lambda-sensitivity：汉字 83 → 91

```diff
@@ -1 +1,2 @@
-(i) 记 $A=\ln[(S^*-\bar S)/\bar S]>0$、$B=\ln[\bar S/(S_c-\bar S)]>0$，则
+(i) 由 $S_c<2\bar S<S^*$，$\Lambda_1,\Lambda_2>0$。
+记 $\kappa$ 为 $\eta,c_0,\beta,q_0$ 中的任一参数，则
@@ -3,2 +4,2 @@
-\frac{\partial\lambda}{\partial p}
-=\frac{B\,\partial A/\partial p-A\,\partial B/\partial p}{(A+B)^2}.
+\frac{\partial\lambda}{\partial\kappa}
+=\frac{\Lambda_2\,\partial\Lambda_1/\partial\kappa-\Lambda_1\,\partial\Lambda_2/\partial\kappa}{(\Lambda_1+\Lambda_2)^2}.
@@ -6 +7 @@
-关于 $\eta$，$\partial A/\partial\eta=(\partial S^*/\partial\eta)/(S^*-\bar S)<0$，且 $\partial B/\partial\eta=0$。
+关于 $\eta$，$\partial\Lambda_1/\partial\eta=(\partial S^*/\partial\eta)/(S^*-\bar S)<0$，且 $\partial\Lambda_2/\partial\eta=0$。
@@ -9 +10 @@
-\frac{\partial A}{\partial c_0}=
+\frac{\partial\Lambda_1}{\partial c_0}=
@@ -11 +12 @@
-\qquad \frac{\partial B}{\partial c_0}=0.
+\qquad \frac{\partial\Lambda_2}{\partial c_0}=0.
@@ -15 +16 @@
-\frac{\partial A}{\partial\beta}
+\frac{\partial\Lambda_1}{\partial\beta}
@@ -18 +19 @@
-\frac{\partial B}{\partial\beta}
+\frac{\partial\Lambda_2}{\partial\beta}
@@ -25,3 +26,3 @@
-=\frac1{(A+B)^2}\left[
-\frac{B}{S^*-\bar S}\frac{\partial S^*}{\partial q_0}
-+\frac{A}{(1-q_0)[\beta+q_0(1-\beta)]}\right].
+=\frac1{(\Lambda_1+\Lambda_2)^2}\left[
+\frac{\Lambda_2}{S^*-\bar S}\frac{\partial S^*}{\partial q_0}
++\frac{\Lambda_1}{(1-q_0)[\beta+q_0(1-\beta)]}\right].
@@ -31 +32 @@
-第\ref{app:lambda}节给出两个满足全部条件的参数点，并分别证明其导数为正和负。
+第~\ref{app:lambda}~节给出两个满足全部条件的参数点，并分别证明其导数为正和负。
```

- thm:joint:explicit：汉字 68 → 67

```diff
@@ -9 +9 @@
-(iii) 对于 $0<\alpha<1$，
+(iii) 对 $0<\alpha<1$，
```

- lem:sup:upper-set：汉字 36 → 49

```diff
@@ -6,0 +7 @@
+故 $p=\zeta'$，即 $c=c_0$，是 $G(\cdot;\zeta')$ 在 $[1,\zeta']$ 上的唯一全局最小点。
```

- prop:sup:rhat：汉字 140 → 147

```diff
@@ -17 +17 @@
-若 $r<\hat r$，$p=\zeta_{\rm sw}$（即 $c_0$）是 $S_{\rm sw}$ 处的唯一全局最小点；
+(ii) 由此，若 $r<\hat r$，$p=\zeta_{\rm sw}$（即 $c_0$）是 $S_{\rm sw}$ 处的唯一全局最小点；
@@ -19 +19 @@
-两种情形下，由引理~\ref{lem:sup:upper-set}，对一切 $S>S_{\rm sw}$，$c_0$ 都是唯一全局最小点。
+(i) $r\le\hat r$ 时，由 (ii) 与引理~\ref{lem:sup:upper-set}，对一切 $S>S_{\rm sw}$，$c_0$ 都是唯一全局最小点。
@@ -21,2 +21,2 @@
-由连续性，这一严格不等式在 $S_{\rm sw}$ 稍上方仍成立。
-最后，$S_{\rm sw}/S_c\in(2,3)$ 给出 $9/4<\hat r<4$；
+由连续性，这一严格不等式在 $S_{\rm sw}$ 稍上方仍成立，$c_0$ 在那里不是全局最小点。
+(iii) $S_{\rm sw}/S_c\in(2,3)$ 给出 $9/4<\hat r<4$；
```

- lem:sup:interior-tie：汉字 107 → 104

```diff
@@ -1 +1 @@
-记两个最小点处的共同最小值为 $m$，令
+(i) 记两个最小点处的共同最小值为 $m$，令
@@ -16 +16 @@
-反过来，取 $\zeta=\zeta_{\rm j}$、$m=2(\sqrt r-1)/\zeta_{\rm j}$、$\ell=k=\sqrt r\,\zeta_{\rm j}$，上述四个系数等式都成立，$\Pi(p)=\zeta_{\rm j}^{-2}(p^2-kp+k)^2$ 对一切 $p$ 成立；
+(ii) 取 $\zeta=\zeta_{\rm j}$、$m=2(\sqrt r-1)/\zeta_{\rm j}$、$\ell=k=\sqrt r\,\zeta_{\rm j}$，上述四个系数等式都成立，$\Pi(p)=\zeta_{\rm j}^{-2}(p^2-kp+k)^2$ 对一切 $p$ 成立；
```

- prop:sup:jump：汉字 652 → 652

```diff
@@ -8 +8 @@
-(ii) 由式\eqref{eq:joint:rcont}，$\sqrt{r_{\rm cont}}$ 是 $(1-b)s^2+bs=2$ 的正根，而 $k=2[(1-b)s^2+bs]$，故 $r>r_{\rm cont}$ 等价于 $k>4$。
+(ii) 由式\eqref{eq:joint:rcont}，$\sqrt{r_{\rm cont}}$ 是 $(1-b)\sigma^2+b\sigma=2$ 的正根，而 $k=2[(1-b)\sigma^2+b\sigma]$，故 $r>r_{\rm cont}$ 等价于 $k>4$。
@@ -10 +10 @@
-该二次式在 $\zeta_{\rm j}$ 处的值为 $\zeta_{\rm j}[s-(s-1)\zeta_{\rm j}]$；
+该二次式在 $\zeta_{\rm j}$ 处的值为 $\zeta_{\rm j}[\sigma-(\sigma-1)\zeta_{\rm j}]$；
@@ -13 +13 @@
-s-(s-1)\zeta_{\rm j}=\bigl[\zeta_{\rm sw}-(\zeta_{\rm sw}-1)s\bigr]\bigl[(\zeta_{\rm sw}-2)s+3-\zeta_{\rm sw}\bigr].
+\sigma-(\sigma-1)\zeta_{\rm j}=\bigl[\zeta_{\rm sw}-(\zeta_{\rm sw}-1)\sigma\bigr]\bigl[(\zeta_{\rm sw}-2)\sigma+3-\zeta_{\rm sw}\bigr].
@@ -16,2 +16,2 @@
-$s<\sqrt{\hat r}=\zeta_{\rm sw}/(\zeta_{\rm sw}-1)$ 时第一个因子也为正，故该值为正。
-又 $s>\sqrt{r_{\rm cont}}>1$ 给出 $\zeta_{\rm j}>2>p_-$，所以 $p_+<\zeta_{\rm j}$。
+$\sigma<\sqrt{\hat r}=\zeta_{\rm sw}/(\zeta_{\rm sw}-1)$ 时第一个因子也为正，故该值为正。
+又 $\sigma>\sqrt{r_{\rm cont}}>1$ 给出 $\zeta_{\rm j}>2>p_-$，所以 $p_+<\zeta_{\rm j}$。
@@ -19,3 +19,3 @@
-$\zeta_{\rm j}$ 关于 $s$ 严格增：
-$s=\sqrt{r_{\rm cont}}$ 时由 $(1-b)s^2+bs=2$ 得 $\zeta_{\rm j}=4/s=b+\sqrt{b^2-8b+8}$；
-$s=\sqrt{\hat r}$ 时代入 $2(1-b)=(\zeta_{\rm sw}-1)(\zeta_{\rm sw}-2)$ 得 $\zeta_{\rm j}=\zeta_{\rm sw}$。
+$\zeta_{\rm j}$ 关于 $\sigma$ 严格增：
+$\sigma=\sqrt{r_{\rm cont}}$ 时由 $(1-b)\sigma^2+b\sigma=2$ 得 $\zeta_{\rm j}=4/\sigma=b+\sqrt{b^2-8b+8}$；
+$\sigma=\sqrt{\hat r}$ 时代入 $2(1-b)=(\zeta_{\rm sw}-1)(\zeta_{\rm sw}-2)$ 得 $\zeta_{\rm j}=\zeta_{\rm sw}$。
@@ -40 +40 @@
-但 $s\ge\sqrt{\hat r}$ 时式\eqref{eq:sup:jump-factor}的第一个因子不为正，该二次式在 $\zeta_{\rm j}$ 处的值不为正，较大的根不小于 $\zeta_{\rm j}$，不在内部。
+但 $\sigma\ge\sqrt{\hat r}$ 时式\eqref{eq:sup:jump-factor}的第一个因子不为正，该二次式在 $\zeta_{\rm j}$ 处的值不为正，较大的根不小于 $\zeta_{\rm j}$，不在内部。
@@ -51 +51 @@
-在 (ii)(iii) 的跳变处，$\zeta$ 连续而最小点 $p$ 下降，故 $c/c_0=p/\zeta$ 与 $q=1-(1-q_0)/p$ 同时下降。
+(iv) 在 (ii)(iii) 的跳变处，$\zeta$ 连续而最小点 $p$ 下降，故 $c/c_0=p/\zeta$ 与 $q=1-(1-q_0)/p$ 同时下降。
```

