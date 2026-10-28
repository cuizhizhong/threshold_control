# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 12 条，新稿 12 条；共同 12 条，其中未变化 12 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 12 条，新稿 12 条；证明有变化 4 条。

- lem:s1:trigger-boundary：汉字 64 → 62

```diff
@@ -7 +7 @@
-峰值随 $c_0$ 严格增加，$c_0\to\infty$ 时趋于 $I_0+\beta_2^0S_0/\beta_1^0$（$\beta_2^0/\beta_1^0$ 不含 $c_0$）。
+峰值随 $c_0$ 严格增加，且 $\lim_{c_0\to\infty}I_{\max}^{0}=I_0+\beta_2^0S_0/\beta_1^0$（$\beta_2^0/\beta_1^0$ 不含 $c_0$）。
```

- prop:contact-effects：汉字 135 → 143

```diff
@@ -24,3 +24,3 @@
-(iii) 当 $c_0\downarrow c_{0,\min}$ 时，$S^*\to S_c$，所以 $\Delta t\to0$。
-当 $c_0\to\infty$ 时，启动方程给出
-$S^*\to S_0-(\beta_1^0/\beta_2^0)(\eta-I_0)>0$，而 $S_c,\bar S$ 均为 $O(c_0^{-1})$，故
+(iii) 当 $c_0$ 从右侧趋于 $c_{0,\min}$ 时，$S^*$ 趋于 $S_c$，故 $\Delta t$ 趋于零。
+由启动方程，
+$\lim_{c_0\to\infty}S^*=S_0-(\beta_1^0/\beta_2^0)(\eta-I_0)>0$，而 $S_c,\bar S$ 均为 $O(c_0^{-1})$，故
@@ -28 +28,2 @@
-\Delta t=\frac{N}{c_0\eta}[\ln c_0+O(1)]\longrightarrow0.
+\Delta t=\frac{N}{c_0\eta}[\ln c_0+O(1)],\qquad
+\lim_{c_0\to\infty}\Delta t=0.
@@ -30 +31 @@
-$\Delta t$ 在内部为正且连续，两端趋零，因此在内部达到正的最大值；
+$\Delta t$ 在内部为正且连续，两端极限为零，因此在内部达到正的最大值；
```

- thm:joint:explicit：汉字 67 → 79

```diff
@@ -8 +8 @@
-两组公式在 $\alpha\downarrow0$ 时连续衔接。
+$\alpha>0$ 的公式在 $\alpha=0$ 处的右极限就是 $\alpha=0$ 的公式，两组公式连续衔接。
```

- prop:sup:jump：汉字 652 → 692

```diff
@@ -5 +5 @@
-第三，把允许区间写成 $p=1+x(\zeta-1)$、$x\in[0,1]$，由 $G$ 连续与 $[0,1]$ 紧，若 $\zeta_n\to\zeta$，$\zeta_n$ 上最小点的任一极限点都是 $\zeta$ 上的最小点；
+第三，把允许区间写成 $p=1+x(\zeta-1)$、$x\in[0,1]$，由 $G$ 连续与 $[0,1]$ 紧，若 $\lim_{n\to\infty}\zeta_n=\zeta$，则 $\zeta_n$ 上最小点的任一极限点都是 $\zeta$ 上的最小点；
@@ -28 +28 @@
-由第三个事实，两侧的极限点都是 $\zeta_{\rm j}$ 上的最小点，故两侧极限分别为 $p_+$ 与 $p_-$。
+由第三个事实，两侧的极限点都是 $\zeta_{\rm j}$ 上的最小点，故最小点在 $\zeta_{\rm j}$ 处的右极限与左极限分别为 $p_+$ 与 $p_-$。
@@ -34 +34 @@
-$\zeta\to\infty$ 时 $G(\zeta;\zeta)=rB(\zeta)\le r/(\zeta-b)\to0$，而 $p<\zeta_{\rm sw}$ 时 $G(p;\zeta)\ge A(p;\zeta)\ge(1-\zeta_{\rm sw}/\zeta)^2/(\zeta_{\rm sw}-b)$，$\zeta_{\rm sw}\le p<\zeta$ 时 $G(p;\zeta)\ge rB(p)>rB(\zeta)$。
+由 $G(\zeta;\zeta)=rB(\zeta)\le r/(\zeta-b)$，$\lim_{\zeta\to\infty}G(\zeta;\zeta)=0$，而 $p<\zeta_{\rm sw}$ 时 $G(p;\zeta)\ge A(p;\zeta)\ge(1-\zeta_{\rm sw}/\zeta)^2/(\zeta_{\rm sw}-b)$，$\zeta_{\rm sw}\le p<\zeta$ 时 $G(p;\zeta)\ge rB(p)>rB(\zeta)$。
@@ -47 +47 @@
-令 $\zeta\uparrow\zeta_0$，其极限点是 $\zeta_0$ 上的全局最小点，不大于 $\zeta_0-\varepsilon$，由第一个事实也不等于 $1$；
+令 $\zeta$ 从左侧趋于 $\zeta_0$，由第三个事实，这些全局最小点的任一极限点都是 $\zeta_0$ 上的全局最小点，不大于 $\zeta_0-\varepsilon$，由第一个事实也不等于 $1$；
@@ -49,2 +49,2 @@
-两种情形下，$\zeta>\zeta_0$ 时最小点为 $p=\zeta$，极限为 $\zeta_0$；
-由第二个事实，$\zeta<\zeta_0$ 时最小点不大于 $p_0$，其极限点是 $\zeta_0$ 上不大于 $p_0$ 的最小点，只能是 $p_0$。
+两种情形下，$\zeta>\zeta_0$ 时最小点为 $p=\zeta$，在 $\zeta_0$ 处的右极限为 $\zeta_0$；
+由第二个事实，$\zeta<\zeta_0$ 时最小点不大于 $p_0$，其极限点是 $\zeta_0$ 上不大于 $p_0$ 的最小点，只能是 $p_0$，故左极限为 $p_0$。
```

