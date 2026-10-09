# 定理类陈述与证明的变化

- 旧稿：pre-rewrite-20261007:paper/appendices/A_proofs_sensitivity.tex pre-rewrite-20261007:paper/appendices/B_control_cost.tex pre-rewrite-20261007:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/appendices/A_proofs_sensitivity.tex paper/appendices/B_control_cost.tex paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 2 条，新稿 2 条；共同 2 条，其中未变化 2 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 1 条。

- prop:s1:lambda-sensitivity：汉字 81 → 81

```diff
@@ -30 +30 @@
-两项异号本身不足以证明导数能取两种符号；
+两项异号本身不足以说明导数能取两种符号；
```


## 附录 A 的证明

`statement_diff.py` 只把证明与同一文件中前面的带标签陈述配对，附录中的证明因此不在上面的统计中；本节按 `sec:proof:*` 标签配对，逐句列出差异（R4 另行生成）。

- `sec:proof:threshold-rationale`：有变化

```diff
@@ -1,7 +1,7 @@
- 常规轨迹在首次到达时满足 \[ \dot I(t_1)=\eta\left[\frac{\beta c_0(1-q_0)S^*}{N}-\gamma\right]>0. \] 若其后仍维持常规控制一段正时间，由连续性，感染人数会超过 $\eta$，故首次加强时刻不能晚于 $t_1$。
-在此之前不超过阈值则由首次到达的定义得到。
- 第二项直接由模型的感染者方程在 $I=\eta$ 时求得。
-对于有界可测时间控制，若 $I$ 在一个区间恒等于 $\eta$，则 $\dot I=0$ 几乎处处，故等号几乎处处成立。
- 恢复常规控制后有 \[ \dot I=\gamma I\left(\frac{S}{S_c}-1\right),\qquad \dot S=-\frac{c_0[\beta+(1-\beta)q_0]}{N}SI<0. \] 若恢复时 $S\le S_c$，此后 $S$ 严格下降，因而所有后续正时间均有 $\dot I<0$，感染人数不再超过 $\eta$。
-若恢复时 $S>S_c$，则恢复后的一个右邻域内有 $\dot I>0$，立即违反上限。
-阈值控制期内 $S$ 也严格下降，故沿该轨迹首次到达 $S_c$ 时即可恢复常规，而不能在此之前从阈值上直接退出。
+ (i) 常规轨迹在首次到达时满足 \[ \dot I(t_1)=\eta\left[\frac{\beta c_0(1-q_0)S^*}{N}-\gamma\right]>0. \] 若其后仍维持常规控制一段正时间，由连续性 $I$ 将超过 $\eta$，故首次加强时刻不能晚于 $t_1$；
+$[0,t_1]$ 上 $I\le\eta$ 由首次到达的定义得到。
+ (ii) 由感染者方程在 $I=\eta$ 处直接得到。
+对有界可测控制，若 $I$ 在一个区间上恒等于 $\eta$，则几乎处处 $\dot I=0$，故等号几乎处处成立。
+ (iii) 恢复常规控制后 \[ \dot I=\gamma I\left(\frac{S}{S_c}-1\right),\qquad \dot S=-\frac{c_0[\beta+(1-\beta)q_0]}{N}SI<0. \] 若恢复时 $S\le S_c$，此后 $S$ 严格下降，所有后续时刻都有 $\dot I<0$，$I$ 不再超过 $\eta$。
+若恢复时 $S>S_c$，则恢复后的一个右邻域内 $\dot I>0$，立即违反 $I\le\eta$。
+阈值控制期内 $S$ 也严格下降，故沿该轨迹首次到达 $S_c$ 时即可恢复常规控制，在此之前则不能从阈值上直接退出。
```

- `sec:proof:post-dynamics`：有变化

```diff
@@ -4 +4 @@
-$I$ 从 $\eta$ 严格下降至零，因而 $\eta>1$ 时存在唯一有限的 $t_{\rm end}$。
+$I$ 从 $\eta>1$ 严格下降至零，故存在唯一有限的 $t_{\rm end}$。
```

- `sec:proof:start-sensitivity`：未变化
- `sec:proof:threshold-tradeoff`：有变化

```diff
@@ -4 +4 @@
- 为分析累计新增感染，退出后 $I=1$ 的条件对 $\eta$ 求导得 \[ \frac{\partial S_{\rm end}}{\partial\eta} =-\frac1{\rho_1(1/S_{\rm end}-1/S_c)}<0. \] 对式\eqref{eq:s1:cumulative}求导， \begin{equation} \frac{\partial\Itcum}{\partial\eta} =\left[\frac{\beta S^*}{S^*-\bar S}-\frac{\beta}{\beta+q_0(1-\beta)}\right]\frac{\partial S^*}{\partial\eta} -\frac{\beta}{\beta+q_0(1-\beta)}\frac{\partial S_{\rm end}}{\partial\eta}>0. \label{eq:cumulative-eta} \end{equation} 其中使用 $\beta S_c/(S_c-\bar S)=\beta/[\beta+q_0(1-\beta)]$，以及 $S/(S-\bar S)$ 在 $S>\bar S$ 上非增。
+ 对累计新增感染，把退出后 $I=1$ 的条件对 $\eta$ 求导得 \[ \frac{\partial S_{\rm end}}{\partial\eta} =-\frac1{\rho_1(1/S_{\rm end}-1/S_c)}<0. \] 对式\eqref{eq:s1:cumulative}求导， \begin{equation} \frac{\partial\Itcum}{\partial\eta} =\left[\frac{\beta S^*}{S^*-\bar S}-\frac{\beta}{\beta+q_0(1-\beta)}\right]\frac{\partial S^*}{\partial\eta} -\frac{\beta}{\beta+q_0(1-\beta)}\frac{\partial S_{\rm end}}{\partial\eta}>0. \label{eq:cumulative-eta} \end{equation} 其中使用 $\beta S_c/(S_c-\bar S)=\beta/[\beta+q_0(1-\beta)]$，以及 $S/(S-\bar S)$ 在 $S>\bar S$ 上非增。
```

- `sec:proof:contact-effects`：未变化
- `sec:proof:representation`：有变化

```diff
@@ -1 +1 @@
- 在 $I=\eta>0$ 上，感染者方程给出 \begin{equation} c(t)(1-q(t))S(t)=\frac{\gamma N}{\beta} =c_0(1-q_0)S_c. \label{eq:joint:balance} \end{equation} 因而正的恒定感染阶段不允许 $q=1$。
+ 在 $I=\eta>0$ 上，感染者方程给出 \begin{equation} c(t)(1-q(t))S(t)=\frac{\gamma N}{\beta} =c_0(1-q_0)S_c. \label{eq:joint:balance} \end{equation} 因此在 $I=\eta>0$ 上 $q<1$。
```

- `sec:proof:cost-minimum`：有变化

```diff
@@ -4 +4 @@
- 为证明该下界可达到，先在本证明中将允许区间写为 $c=\underline c(S)+x[\overline c(S)-\underline c(S)]$，$x\in[0,1]$，并记 \[ H(S,x)=f\!\left(S,\underline c(S)+x[\overline c(S)-\underline c(S)]\right), \quad m(S)=\min_{0\le x\le1}H(S,x). \] $H$ 在紧集上连续，因而 $m$ 连续。
+ 为证明下界可以达到，将允许区间写为 $c=\underline c(S)+x[\overline c(S)-\underline c(S)]$，$x\in[0,1]$，并记 \[ H(S,x)=f\!\left(S,\underline c(S)+x[\overline c(S)-\underline c(S)]\right), \quad m(S)=\min_{0\le x\le1}H(S,x). \] $H$ 在紧集上连续，因而 $m$ 连续。
```

- `sec:proof:endpoint-properties`：有变化

```diff
@@ -1 +1 @@
- 在本证明中记 $n(c)=w_c(1-c/c_0)^2+w_q(1-c_0S_c/(cS))^2$。
+ 记 $n(c)=w_c(1-c/c_0)^2+w_q(1-c_0S_c/(cS))^2$。
@@ -5,3 +5,3 @@
-结合端点处的单侧比较，得到所述局部性质。
-由定理\ref{thm:joint:cost-minimum}，类内最小成本分配几乎处处取逐状态最小点；
-它不取左端点，在后一状态区间也不取右端点，故得到内部分配结论。
+结合端点处的单侧比较即得 (i)(ii)。
+由定理\ref{thm:joint:cost-minimum}，成本最优控制几乎处处取逐状态最小点；
+它不取左端点，在 $S_c<S<\min\{S_{\rm sw},S^*\}$ 上也不取右端点，故得到命题最后的结论。
```

- `sec:proof:terminal-allocation`：有变化

```diff
@@ -1 +1 @@
- 在本证明中令 $z=1-S_c/S$，并将允许接触率写为 $c=c_0(1-zx)$、$0\le x\le1$。
+ 令 $z=1-S_c/S$，把允许接触率写为 $c=c_0(1-zx)$、$0\le x\le1$。
@@ -7 +7 @@
-有能力限制且 $c_{\min}<c_0,q_{\rm cap}>q_0$ 时，充分接近 $S_c$ 的原允许区间仍为 $[c_0S_c/S,c_0]$，因此同一局部论证成立。
+考虑满足 $c_{\min}<c_0$、$q_{\rm cap}>q_0$ 的能力约束时，充分接近 $S_c$ 处的允许区间仍为 $[c_0S_c/S,c_0]$，同一局部论证成立。
```


## 附录 B

附录 B 没有定理类环境；下面是全文差异。

```diff
@@ -1,2 +1 @@
-% ===== theory_appendices =====
-\section{成本积分与单控制闭式表达}
+\section{成本积分}
@@ -4,2 +3,2 @@
-\subsection{仅隔离控制的成本积分}
-以下沿用默认权重 $w_c=1,w_q=2$。当 $\bar S>0$ 时，式\eqref{eq:cost:state}的积分结果为
+\subsection{仅隔离控制}
+取默认权重 $w_c=1$、$w_q=2$。由 $0<\bar S<S_c$，式\eqref{eq:cost:state}的两个积分为
@@ -22 +21 @@
-这两式可由下列部分分式展开逐项积分得到：
+两式由下列部分分式逐项积分得到：
@@ -32,7 +31 @@
-在 $\beta=1$、$\bar S=0$ 时，直接展开式\eqref{eq:cost:state}的被积函数，得
-\begin{align}
-J_q&=\frac{N}{c_0\eta}\left[\ln\frac{S^*}{S_c}+\frac{S_c}{S^*}-1\right],\\
-J&=\frac{2N}{c_0\eta}\left[\ln\frac{S^*}{S_c}+\frac{2S_c}{S^*}
--\frac{S_c^2}{2(S^*)^2}-\frac32\right].
-\end{align}
-这些表达与积分式相同；当 $\bar S$ 很小或 $S^*$ 接近 $S_c$ 时，可使用原积分式避免接近量相减所带来的浮点误差。
+$\bar S$ 很小或 $S^*$ 接近 $S_c$ 时，闭式中有相近的量相减，数值计算宜直接用积分式\eqref{eq:cost:state}。
@@ -40,2 +33,2 @@
-\subsection{仅减少接触及显式族的成本参照}
-显式族可作为成本比较的参照。仅减少接触时，
+\subsection{仅减少接触}
+仅减少接触时 $c_c(S)=c_0S_c/S$、$q\equiv q_0$，$S$ 的下降速度恒为 $c_0(S_c-\bar S)\eta/N$。由式\eqref{eq:joint:cost}，
@@ -44 +37 @@
-\left[S^*-\frac{S_c^2}{S^*}-2S_c\ln\frac{S^*}{S_c}\right],
+\left[S^*-\frac{S_c^2}{S^*}-2S_c\ln\frac{S^*}{S_c}\right].
@@ -47,3 +39,0 @@
-仅隔离控制时恢复式\eqref{eq:cost:state}。全部允许控制中的最小成本不高于式\eqref{eq:joint:allocation-range}内任一显式策略的成本，但显式族未必包含类内最优解，不能以该子族中的最小值替代式\eqref{eq:joint:minimum-cost}。
-
-
```
