# NEW-4ai r16 陈述与证明的变化

---
## 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 8 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:inflection：汉字 140 → 122

```diff
@@ -1,11 +1,2 @@
-(i) 由链式法则与式\eqref{eq:s1:S-analytic}，对式\eqref{eq:s1:qprime}求导，得
-\begin{equation}
-\frac{d^2q_c(t)}{dt^2}
-=\frac{\gamma c_0\eta^2}{\beta N}
-\frac{(S-\bar S)(2\bar S-S)}{S^3}.
-\end{equation}
-由式\eqref{eq:s1:barS}，阈值控制期内 $S\ge S_c>\bar S$，故 $d^2q_c/dt^2$ 与 $2\bar S-S$ 同号。
-$S$ 在 $(t_1,t_2)$ 上从 $S^*$ 严格下降至 $S_c$。
-若式\eqref{eq:s1:inflection-condition}成立，$S$ 恰在一个时刻经过 $2\bar S$，$d^2q_c/dt^2$ 在该时刻由负变正，这是 $(t_1,t_2)$ 内唯一的拐点。
-否则 $2\bar S-S$ 在 $(t_1,t_2)$ 上不变号，没有拐点。
-由式\eqref{eq:s1:q-control}与\eqref{eq:s1:barS}，
+由式\eqref{eq:s1:q-control}与\eqref{eq:s1:barS}，$\nu=\bar S/S$，$q_c=1-\nu/(1-\beta)$；
+再由式\eqref{eq:s1:S-analytic}，$\nu$ 满足 logistic 方程
@@ -13 +4,2 @@
-q_c(2\bar S)=1-\frac{\gamma N}{2\beta c_0\bar S}=1-\frac{1}{2(1-\beta)}=\qinf.
+\dot\nu=\frac{c_0\eta}{N}\,\nu(1-\nu),\qquad\text{故}\qquad
+\frac{dq_c}{dt}=-\frac{c_0\eta}{(1-\beta)N}\,\nu(1-\nu).
@@ -15,5 +7,8 @@
-又 $q_c(S)$ 关于 $S$ 严格增加，且 $q_c(S_c)=q_0$、$q_c(S^*)=q_1$，所以式\eqref{eq:s1:inflection-condition}等价于 $q_0<\qinf<q_1$。
-(ii) 由 (i) 的证明，$d^2q_c/dt^2$ 在 $t_{\rm inf}$ 之前为负、之后为正；
-由式\eqref{eq:s1:qprime}，$dq_c/dt<0$。
-因此 $|dq_c/dt|$ 在 $(t_1,t_{\rm inf}]$ 上严格增加，在 $[t_{\rm inf},t_2)$ 上严格减少，于 $t_{\rm inf}$ 唯一取得最大值。
-又由 (i)，$S(t_{\rm inf})=2\bar S$，代入式\eqref{eq:s1:S-analytic}即得拐点时刻，代入 $q_c(S)$ 即得 $q_c(t_{\rm inf})=\qinf$。
+阈值控制期内 $S$ 从 $S^*$ 严格降至 $S_c$，故 $\nu$ 从 $\bar S/S^*$ 严格增至 $\bar S/S_c=(1-\beta)(1-q_0)<1$。
+$\nu(1-\nu)$ 在 $(0,1/2]$ 上严格增加、在 $[1/2,1)$ 上严格减少，所以 $\nu<1/2$ 时 $|dq_c/dt|$ 随时间严格增加，$q_c(t)$ 严格凹；
+$\nu>1/2$ 时 $|dq_c/dt|$ 严格减少，$q_c(t)$ 严格凸。
+(i) 因此 $q_c(t)$ 在 $(t_1,t_2)$ 内有拐点，当且仅当 $\nu$ 在其中越过 $1/2$，即 $\bar S/S^*<1/2<\bar S/S_c$，亦即式\eqref{eq:s1:inflection-condition}；
+$\nu$ 严格递增，故拐点唯一。
+$q_c$ 关于 $S$ 严格增加，且 $q_c(2\bar S)=\qinf$、$q_c(S_c)=q_0$、$q_c(S^*)=q_1$，故式\eqref{eq:s1:inflection-condition}等价于 $q_0<\qinf<q_1$。
+(ii) 由上，$|dq_c/dt|$ 在 $\nu=1/2$，即 $t_{\rm inf}$ 处唯一取得最大值。
+由 $\nu(t_{\rm inf})=1/2$ 得 $S(t_{\rm inf})=2\bar S$，代入式\eqref{eq:s1:S-analytic}即得 $t_{\rm inf}$，且 $q_c(t_{\rm inf})=\qinf$。
```


---
## 定理类陈述与证明的变化

- 旧稿：HEAD:paper/supplement_sections/S3_inflection.tex
- 新稿：paper/supplement_sections/S3_inflection.tex

带标签的陈述：旧稿 1 条，新稿 1 条；共同 1 条，其中未变化 1 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 1 条，新稿 1 条；证明有变化 0 条。


---
## 定理类陈述与证明的变化

- 旧稿：HEAD:paper/supplement_sections/S6_xian.tex
- 新稿：paper/supplement_sections/S6_xian.tex

带标签的陈述：旧稿 2 条，新稿 2 条；共同 2 条，其中未变化 2 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 1 条。

- prop:scaling：汉字 148 → 146

```diff
@@ -13 +13 @@
-且 $q_1=1-\gamma/(\beta c_0s^*)$，正文式\eqref{eq:s1:lambda}中的 $\lambda$ 也只含 $s^*,s_c,\bar s$。
+且 $q_1=1-\gamma/(\beta c_0s^*)$，式\eqref{eq:s1:lambda}中的 $\lambda$ 也只含 $s^*,s_c,\bar s$。
```

