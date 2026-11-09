# 定理类陈述与证明的变化

- 旧稿：cf2b849:paper/supplement_sections/S2_single_control.tex
- 新稿：paper/supplement_sections/S2_single_control.tex

带标签的陈述：旧稿 2 条，新稿 2 条；共同 2 条，其中未变化 0 条，有变化 2 条。

## 陈述有变化（逐条确认数学含义是否等价）

### lem:s1:trigger-boundary

```diff
@@ -1,2 +1 @@
-固定其余参数，设 $I_0<\eta<I_0+\beta_2^0S_0/\beta_1^0$。
-则存在唯一的触发边界 $c_{0,\min}(\eta)$，满足
+固定其余参数，设 $I_0<\eta<I_0+\beta_2^0S_0/\beta_1^0$，则存在唯一的触发边界 $c_{0,\min}(\eta)$，满足
@@ -7 +6 @@
-且控制恰在 $c_0>c_{0,\min}(\eta)$ 时被触发。
+且触发条件\eqref{eq:model:trigger}成立当且仅当 $c_0>c_{0,\min}(\eta)$。
```

### prop:contact-effects

```diff
@@ -1 +1 @@
-设条件\eqref{eq:model:trigger}成立，则仅隔离控制满足：
+设条件\eqref{eq:model:trigger}成立，则对仅隔离控制，
@@ -4 +4 @@
-\item 有
+\item 启动时刻、最大隔离比例与控制时长满足
@@ -11 +11 @@
-\item 接触率对控制时长的影响由
+\item 控制时长对常规接触率的偏导数为
@@ -17 +17 @@
--\ln\frac{S^*-\bar S}{S_c-\bar S}\right\}
+-\ln\frac{S^*-\bar S}{S_c-\bar S}\right\},
@@ -19,2 +19,2 @@
-确定，其符号不能统一为正或负；
-\item 固定除 $c_0$ 外的参数，且 $I_0<\eta<I_0+\beta_2^0S_0/\beta_1^0$ 时，$\Delta t$ 作为 $c_0$ 的函数在 $(c_{0,\min},\infty)$ 内至少有一个极大值。
+它的符号不能统一为正或负；
+\item 设 $I_0<\eta<I_0+\beta_2^0S_0/\beta_1^0$，固定除 $c_0$ 外的参数，则 $\Delta t$ 作为 $c_0$ 的函数在 $(c_{0,\min}(\eta),\infty)$ 内至少有一个极大值。
```

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 2 条。

- lem:s1:trigger-boundary：汉字 62 → 77

```diff
@@ -1,2 +1,2 @@
-当 $c_0\le\gamma N/[\beta(1-q_0)S_0]$，即 $S_0\le S_c$ 时，常规峰值为 $I_0$；
-$c_0$ 超过这一值后，由式\eqref{eq:s1:Imax-no}，
+当 $c_0\le\gamma N/[\beta(1-q_0)S_0]$，即 $S_0\le S_c$ 时，常规峰值为 $I_0$。
+$c_0$ 超过这一值后，$S_c$ 与 $\rho_1$ 都与 $c_0$ 成反比，$\beta_2^0/\beta_1^0$ 不含 $c_0$，由式\eqref{eq:s1:Imax-no}得
@@ -7,3 +7,4 @@
-峰值随 $c_0$ 严格增加，且 $\lim_{c_0\to\infty}I_{\max}^{0}=I_0+\beta_2^0S_0/\beta_1^0$（$\beta_2^0/\beta_1^0$ 不含 $c_0$）。
-由 $I_0<\eta<I_0+\beta_2^0S_0/\beta_1^0$ 以及连续性与严格单调性，$I_{\max}^{0}=\eta$ 恰有一个根，且该根大于 $\gamma N/[\beta(1-q_0)S_0]$。
-触发条件\eqref{eq:model:trigger}即 $I_{\max}^{0}>\eta$，恰在 $c_0$ 大于该根时成立。
+因此峰值随 $c_0$ 严格增加。
+$c_0\to\infty$ 时 $S_c\to0$、$\rho_1\ln(S_c/S_0)\to0$，故 $\lim_{c_0\to\infty}I_{\max}^{0}=I_0+\beta_2^0S_0/\beta_1^0$。
+$I_{\max}^{0}$ 关于 $c_0$ 连续，由 $I_0<\eta<I_0+\beta_2^0S_0/\beta_1^0$ 与严格单调性，$I_{\max}^{0}=\eta$ 恰有一个根，且该根大于 $\gamma N/[\beta(1-q_0)S_0]$。
+在 $I_0<\eta$ 下，触发条件\eqref{eq:model:trigger}等价于 $I_{\max}^{0}>\eta$，因而恰在 $c_0$ 大于该根时成立。
```

- prop:contact-effects：汉字 143 → 219

```diff
@@ -1 +1 @@
-(i) 记 $I(S;c_0)=I_0+(\beta_2^0/\beta_1^0)(S_0-S)+\rho_1\ln(S/S_0)$。
+(i) 把式\eqref{eq:model:routine-orbit}中的 $I(S)$ 记为 $I(S;c_0)$，以显示它对 $c_0$ 的依赖。
@@ -6 +6,3 @@
-式\eqref{eq:s1:t1}中的前置系数 $1/\beta_1^0$ 随 $c_0$ 下降，下限 $S^*$ 随 $c_0$ 上升，被积函数也下降；
+在式\eqref{eq:s1:t1}中，前置系数 $1/\beta_1^0$ 随 $c_0$ 下降；
+由引理~\ref{lem:s1:Sstar-sensitivity}，下限 $S^*$ 随 $c_0$ 上升；
+由上式，被积函数 $1/[S\,I(S;c_0)]$ 也随 $c_0$ 下降。
@@ -8 +10 @@
-同时
+对式\eqref{eq:s1:qmax}求导，得
@@ -14 +16,2 @@
-对 $\Delta t$ 的对数因子求导时，
+由式\eqref{eq:s1:t2}，$\Delta t=[N/(c_0\eta)]\ln[(S^*-\bar S)/(S_c-\bar S)]$，前置系数不含 $\beta,q_0$。
+对 $\beta$ 求导时，
@@ -18 +21 @@
-\frac{\partial(S_c-\bar S)}{\partial\beta}=-\frac{q_0S_c}{\beta}\le0.
+\frac{\partial(S_c-\bar S)}{\partial\beta}=-\frac{q_0S_c}{\beta}\le0,
@@ -20,3 +23,3 @@
-结合 $\partial S^*/\partial\beta>0$ 得 $\partial\Delta t/\partial\beta>0$。
-由于 $\bar S$ 不含 $q_0$，而 $\partial S^*/\partial q_0<0$、$\partial S_c/\partial q_0=S_c/(1-q_0)>0$，得到 $\partial\Delta t/\partial q_0<0$。
-(ii) 利用 $\partial\bar S/\partial c_0=-\bar S/c_0$、$\partial S_c/\partial c_0=-S_c/c_0$ 及式\eqref{eq:s1:Sstar-eta-sign}，直接整理得到式\eqref{eq:duration-c0}。
+结合 $\partial S^*/\partial\beta>0$，对数的分子增大、分母不增，得 $\partial\Delta t/\partial\beta>0$。
+对 $q_0$ 求导时，$\bar S$ 不含 $q_0$，而 $\partial S^*/\partial q_0<0$、$\partial S_c/\partial q_0=S_c/(1-q_0)>0$，对数的分子减小、分母增大，得 $\partial\Delta t/\partial q_0<0$。
+(ii) 利用 $\partial\bar S/\partial c_0=-\bar S/c_0$、$\partial S_c/\partial c_0=-S_c/c_0$ 及式\eqref{eq:s1:Sstar-eta-sign}中的 $\partial S^*/\partial c_0$，对式\eqref{eq:s1:t2}求导并整理，即得式\eqref{eq:duration-c0}。
@@ -24,2 +27,2 @@
-(iii) 当 $c_0$ 从右侧趋于 $c_{0,\min}$ 时，$S^*$ 趋于 $S_c$，故 $\Delta t$ 趋于零。
-由启动方程，
+(iii) 当 $c_0$ 从右侧趋于 $c_{0,\min}(\eta)$ 时，$\eta$ 趋于常规峰值，$S^*$ 趋于 $S_c$，故 $\Delta t$ 趋于零。
+$\beta_1^0/\beta_2^0$ 不含 $c_0$，由启动方程 $I(S^*)=\eta$，
@@ -31,2 +34,2 @@
-$\Delta t$ 在内部为正且连续，两端极限为零，因此在内部达到正的最大值；
-中值定理同时保证其导数取正、负两种符号。
+$\Delta t$ 在 $(c_{0,\min}(\eta),\infty)$ 内为正且连续，两端极限为零，因此在内部取得正的最大值。
+由中值定理，其导数在最大值点两侧分别取正值与负值，这也给出 (ii) 中的符号不定。
```

