# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/flatten_curve_analysis_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex

带标签的陈述：旧稿 28 条，新稿 28 条；共同 28 条，其中未变化 28 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 13 条，新稿 13 条；证明有变化 1 条。

- lem:proof:fold-free：汉字 106 → 144

```diff
@@ -12,4 +12,4 @@
-在 $\sigma\in(\sqrt2,2)$ 上，$Q$ 的常数项随 $\sigma$ 增，不小于 $9(\sqrt2-1)$；
-一次项系数随 $\sigma$ 减，不小于 $-2$；
-二次项系数大于 $12(\sqrt2-1)$；
-三、四次项非负。
+在 $\sigma\in(\sqrt2,2)$ 上逐项估计 $Q$ 的系数。
+常数项 $9\sigma^2+11\sigma-\sigma^3-27$ 的导数 $18\sigma+11-3\sigma^2$ 为正，故常数项随 $\sigma$ 增，不小于其在 $\sigma=\sqrt2$ 处的值 $9(\sqrt2-1)$。
+一次项系数为 $-2(\sigma^3+3\sigma^2-11\sigma+3)$，括号内的导数 $3\sigma^2+6\sigma-11$ 为正，故该系数随 $\sigma$ 减，不小于其在 $\sigma=2$ 处的值 $-2$。
+二次项系数 $12(\sigma-1)$ 大于 $12(\sqrt2-1)$，三、四次项非负。
```

