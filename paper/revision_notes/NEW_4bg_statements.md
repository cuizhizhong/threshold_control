# 定理类陈述与证明的变化

- 旧稿：b7b3554:paper/supplement_sections/S1_medical.tex
- 新稿：paper/supplement_sections/S1_medical.tex

带标签的陈述：旧稿 1 条，新稿 1 条；共同 1 条，其中未变化 1 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 1 条，新稿 1 条；证明有变化 0 条。

# 定理类陈述与证明的变化

- 旧稿：b7b3554:paper/supplement_sections/S2_single_control.tex
- 新稿：paper/supplement_sections/S2_single_control.tex

带标签的陈述：旧稿 2 条，新稿 2 条；共同 2 条，其中未变化 2 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 2 条，新稿 2 条；证明有变化 1 条。

- prop:contact-effects：汉字 219 → 226

```diff
@@ -27 +27 @@
-(iii) 当 $c_0$ 从右侧趋于 $c_{0,\min}(\eta)$ 时，$\eta$ 趋于常规峰值，$S^*$ 趋于 $S_c$，故 $\Delta t$ 趋于零。
+(iii) 当 $c_0$ 从右侧趋于 $c_{0,\min}(\eta)$ 时，常规峰值趋于 $\eta$，$S^*$ 趋于 $S_c$，故 $\Delta t$ 趋于零。
@@ -35 +35 @@
-由中值定理，其导数在最大值点两侧分别取正值与负值，这也给出 (ii) 中的符号不定。
+由中值定理，其导数在该最大值点左侧至少一处为正、右侧至少一处为负，这也给出 (ii) 中的符号不定。
```

# 定理类陈述与证明的变化

- 旧稿：b7b3554:paper/supplement_sections/S5_weight_structure.tex
- 新稿：paper/supplement_sections/S5_weight_structure.tex

带标签的陈述：旧稿 4 条，新稿 4 条；共同 4 条，其中未变化 3 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### lem:sup:upper-set

```diff
@@ -1 +1 @@
-设 $w_c,w_q>0$。
+设 $w_c,w_q>0$ 且 $S>S_c$。
```

## 证明

有证明的陈述：旧稿 4 条，新稿 4 条；证明有变化 4 条。

- lem:sup:upper-set：汉字 49 → 72

```diff
@@ -2 +2 @@
-由正文命题~\ref{prop:joint:global-structure}，$\zeta\ge\zeta_{\rm sw}$。
+由正文命题~\ref{prop:joint:global-structure}证明中的右端点导数公式，$1<\zeta<\zeta_{\rm sw}$ 时右端点不是局部最小点，故 $\zeta\ge\zeta_{\rm sw}$。
```

- prop:sup:rhat：汉字 147 → 129

```diff
@@ -2,2 +2,2 @@
-先看 $S_{\rm sw}$ 处，记 $\zeta=\zeta_{\rm sw}$。
-对 $p\in[1,\zeta)$，把 $G(p;\zeta)\ge G(\zeta;\zeta)=r(1-1/\zeta)^2/(\zeta-b)$ 两边乘以正数 $\zeta^2p^2(p-b)(\zeta-b)$，得到等价条件
+先看 $S_{\rm sw}$ 处，记 $\zeta=\zeta_{\rm sw}$、$a=\zeta/(\zeta-1)=\sqrt{\hat r}$。
+由 $\zeta_{\rm sw}^2-3\zeta_{\rm sw}+2b=0$，即 $2(\zeta-b)=\zeta(\zeta-1)$，直接计算得
@@ -5,2 +5 @@
-(\zeta-b)(\zeta-p)^2p^2+rK(p)\ge0,\qquad
-K(p)=\zeta^2(\zeta-b)(p-1)^2-(\zeta-1)^2p^2(p-b).
+G(p;\zeta)-G(\zeta;\zeta)=\frac{(\zeta-p)^2}{\zeta^2p^2(p-b)}\Bigl[(p-a)^2+(\hat r-r)\Bigl(\frac{2(\zeta-1)p}{\zeta}-1\Bigr)\Bigr].
@@ -8,11 +7,4 @@
-$K(\zeta)=0$，且 $K(p)=(\zeta-p)R(p)$，其中 $R(p)=(\zeta-1)^2p^2-(\zeta-b)(2\zeta-1)p+\zeta(\zeta-b)$；
-所以条件化为 $(\zeta-b)(\zeta-p)p^2+rR(p)\ge0$。
-由 $\zeta_{\rm sw}^2-3\zeta_{\rm sw}+2b=0$，即 $2(\zeta-b)=\zeta(\zeta-1)$，有 $R(p)=(\zeta-1)^2(p-\zeta)(p-p_2)$，$p_2=\zeta/[2(\zeta-1)]<1$。
-条件化为：
-对一切 $p\in[1,\zeta)$ 有
-\[
-r(p-p_2)\le\frac{(\zeta-b)p^2}{(\zeta-1)^2}.
-\]
-右端与 $p-p_2$ 之比在 $p=2p_2=\zeta/(\zeta-1)\in(1,\zeta)$ 取最小值 $4p_2(\zeta-b)/(\zeta-1)^2=\zeta^2/(\zeta-1)^2=\hat r$。
-(ii) 由此，若 $r<\hat r$，$p=\zeta_{\rm sw}$（即 $c_0$）是 $S_{\rm sw}$ 处的唯一全局最小点；
-若 $r=\hat r$，它与 $p=2p_2$ 并列，$p=2p_2$ 对应 $c=c_0S_c/(S_{\rm sw}-S_c)$。
+对 $1\le p<\zeta$，$2(\zeta-1)p/\zeta-1\ge(\zeta-2)/\zeta>0$；
+又 $\zeta\in(2,3)$ 给出 $1<a<\zeta$。
+(ii) 由此，若 $r<\hat r$，方括号对一切 $p\in[1,\zeta)$ 严格为正，$p=\zeta_{\rm sw}$（即 $c_0$）是 $S_{\rm sw}$ 处的唯一全局最小点；
+若 $r=\hat r$，方括号只在 $p=a$ 处为零，$c_0$ 与 $p=a$ 并列，$p=a$ 对应 $c=c_0S_c/(S_{\rm sw}-S_c)$。
@@ -20 +12 @@
-若 $r>\hat r$，则在 $S_{\rm sw}$ 处存在 $p<\zeta_{\rm sw}$ 使 $G(p;\zeta_{\rm sw})<G(\zeta_{\rm sw};\zeta_{\rm sw})$；
+若 $r>\hat r$，取 $p=a$，由上式 $G(a;\zeta_{\rm sw})<G(\zeta_{\rm sw};\zeta_{\rm sw})$；
```

- lem:sup:interior-tie：汉字 104 → 104

```diff
@@ -8,3 +8,3 @@
-比较常数项得 $k^2=r\zeta^2$，即 $k=\sqrt r\,\zeta$；
-比较一次项得 $k\ell=r\zeta^2=k^2$，即 $\ell=k$；
-比较三次项得 $m=2(\ell-\zeta)/\zeta^2=2(\sqrt r-1)/\zeta$；
+比较常数项得 $k^2=r\zeta^2$，即 $k=\sqrt r\,\zeta$。
+比较一次项得 $k\ell=r\zeta^2=k^2$，即 $\ell=k$。
+比较三次项得 $m=2(\ell-\zeta)/\zeta^2=2(\sqrt r-1)/\zeta$。
```

- prop:sup:jump：汉字 692 → 702

```diff
@@ -3 +3 @@
-$1<\zeta<\zeta_{\rm sw}$ 时右端点 $p=\zeta$ 也不是（正文命题~\ref{prop:joint:global-structure}）。
+$1<\zeta<\zeta_{\rm sw}$ 时右端点 $p=\zeta$ 也不是（正文命题~\ref{prop:joint:global-structure}证明中的端点导数公式）。
```

# 定理类陈述与证明的变化

- 旧稿：b7b3554:paper/supplement_sections/S6_xian.tex
- 新稿：paper/supplement_sections/S6_xian.tex

带标签的陈述：旧稿 0 条，新稿 0 条；共同 0 条，其中未变化 0 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 0 条，新稿 0 条；证明有变化 0 条。

# 定理类陈述与证明的变化

- 旧稿：b7b3554:paper/supplement_sections/S7_return.tex
- 新稿：paper/supplement_sections/S7_return.tex

带标签的陈述：旧稿 1 条，新稿 1 条；共同 1 条，其中未变化 0 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### rem:release-at-exit

```diff
@@ -8,2 +8 @@
-因此 $\xi S_q(t_2^-)>0$ 时，$I$ 在 $t_2$ 之后立即上升并超过 $\eta$。
-也就是说，退出时一次性解除对未感染接触者的隔离，会使社区传播重新扩大。
+因此，只要 $\xi S_q(t_2^-)>0$，退出时一次性释放未感染接触者就会使 $I$ 立即重新上升并超过阈值。
```

## 证明

有证明的陈述：旧稿 0 条，新稿 0 条；证明有变化 0 条。

# 定理类陈述与证明的变化

- 旧稿：b7b3554:paper/supplement_sections/S8_numerics.tex
- 新稿：paper/supplement_sections/S8_numerics.tex

带标签的陈述：旧稿 0 条，新稿 0 条；共同 0 条，其中未变化 0 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 0 条，新稿 0 条；证明有变化 0 条。

