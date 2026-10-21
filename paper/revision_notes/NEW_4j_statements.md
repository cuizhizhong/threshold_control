# 定理类陈述与证明的变化

- 旧稿：97a54a3:paper/flatten_curve_analysis_cn.tex 97a54a3:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 41 条，新稿 41 条；共同 41 条，其中未变化 39 条，有变化 2 条。

## 陈述有变化（逐条确认数学含义是否等价）

### prop:joint:weight-monotone

```diff
@@ -6 +6 @@
-最小成本 $J_{\min}/w_c$ 是 $r$ 的凹增函数。
+最小成本 $J_{\min}/w_c$ 是 $r$ 的凹且不减的函数。
```

### prop:reference-population

```diff
@@ -2 +2 @@
-在 $N\theta>1$ 的范围内，仅隔离控制的清零时间和计算至该终点的累计新增感染均随 $N$ 严格增加。
+在 $N\theta>1$ 的范围内，仅隔离控制的清零时间、计算至该终点的累计新增感染及其占人口的比例均随 $N$ 严格增加。
```

## 证明

有证明的陈述：旧稿 23 条，新稿 23 条；证明有变化 1 条。

- prop:reference-population：汉字 77 → 85

```diff
@@ -16 +16,6 @@
-将式\eqref{eq:s1:cumulative}除以 $N$ 后，只有 $s_{\rm end}$ 含 $N$，因而
+将式\eqref{eq:s1:cumulative}除以 $N$ 后，只有 $s_{\rm end}$ 含 $N$，因而比例满足
+\[
+\frac{\partial(\Itcum/N)}{\partial N}
+=-\frac{\beta}{\beta+q_0(1-\beta)}\frac{\partial s_{\rm end}}{\partial N}>0,
+\]
+人数满足
```

