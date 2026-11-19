# 定理类陈述与证明的变化

- 旧稿：92be471:paper/flatten_curve_analysis_cn.tex 92be471:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 32 条，新稿 32 条；共同 32 条，其中未变化 28 条，有变化 4 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:cost-structure

```diff
@@ -1 +1 @@
-设条件\eqref{eq:model:trigger}成立，$0<r\le r_{\rm cont}$，则
+设条件\eqref{eq:model:trigger}成立，$0<r\le r_*$，则
```

### lem:proof:fold-free

```diff
@@ -1 +1 @@
-设 $0<b<1$，$\sigma_c=\sqrt{r_{\rm cont}}$。
+设 $0<b<1$，$\sigma_c=\sqrt{r_*}$。
```

### prop:sup:rhat

```diff
@@ -6 +6 @@
-\item $9/4<\hat r<4$，且 $r_{\rm cont}<\hat r$。
+\item $9/4<\hat r<4$，且 $r_*<\hat r$。
```

### prop:sup:jump

```diff
@@ -5,2 +5,2 @@
-\item 若 $0<r\le r_{\rm cont}$，最小点处处唯一，没有跳变；
-\item 若 $r_{\rm cont}<r<\hat r$，则 $b+\sqrt{b^2-8b+8}<\zeta_{\rm j}<\zeta_{\rm sw}$；
+\item 若 $0<r\le r_*$，最小点处处唯一，没有跳变；
+\item 若 $r_*<r<\hat r$，则 $b+\sqrt{b^2-8b+8}<\zeta_{\rm j}<\zeta_{\rm sw}$；
```

## 证明

有证明的陈述：旧稿 20 条，新稿 20 条；证明有变化 2 条。

- prop:sup:rhat：汉字 140 → 140

```diff
@@ -15 +15 @@
-由 $\zeta_{\rm sw}=S_{\rm sw}/S_c$ 得 $b=\zeta_{\rm sw}(3-\zeta_{\rm sw})/2$，不等式 $r_{\rm cont}<\hat r$ 化为 $(\zeta_{\rm sw}-1)(\zeta_{\rm sw}-2)^2>0$。
+由 $\zeta_{\rm sw}=S_{\rm sw}/S_c$ 得 $b=\zeta_{\rm sw}(3-\zeta_{\rm sw})/2$，不等式 $r_*<\hat r$ 化为 $(\zeta_{\rm sw}-1)(\zeta_{\rm sw}-2)^2>0$。
```

- prop:sup:jump：汉字 702 → 702

```diff
@@ -8 +8 @@
-(ii) 由式\eqref{eq:joint:rcont}，$\sqrt{r_{\rm cont}}$ 是 $(1-b)\sigma^2+b\sigma=2$ 的正根，而 $k=2[(1-b)\sigma^2+b\sigma]$，故 $r>r_{\rm cont}$ 等价于 $k>4$。
+(ii) 由式\eqref{eq:joint:rcont}，$\sqrt{r_*}$ 是 $(1-b)\sigma^2+b\sigma=2$ 的正根，而 $k=2[(1-b)\sigma^2+b\sigma]$，故 $r>r_*$ 等价于 $k>4$。
@@ -17 +17 @@
-又 $\sigma>\sqrt{r_{\rm cont}}>1$ 给出 $\zeta_{\rm j}>2>p_-$，所以 $p_+<\zeta_{\rm j}$。
+又 $\sigma>\sqrt{r_*}>1$ 给出 $\zeta_{\rm j}>2>p_-$，所以 $p_+<\zeta_{\rm j}$。
@@ -20 +20 @@
-$\sigma=\sqrt{r_{\rm cont}}$ 时由 $(1-b)\sigma^2+b\sigma=2$ 得 $\zeta_{\rm j}=4/\sigma=b+\sqrt{b^2-8b+8}$；
+$\sigma=\sqrt{r_*}$ 时由 $(1-b)\sigma^2+b\sigma=2$ 得 $\zeta_{\rm j}=4/\sigma=b+\sqrt{b^2-8b+8}$；
```

