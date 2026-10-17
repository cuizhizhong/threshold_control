# 定理类陈述与证明的变化

- 旧稿：nr-base:paper/flatten_curve_analysis_cn.tex nr-base:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 31 条，新稿 35 条；共同 31 条，其中未变化 28 条，有变化 3 条。

只在新稿中（新增或改了首个标签）：rem:release-at-exit、lem:return:U、prop:return:final-size、cor:return:right-discontinuity

## 陈述有变化（逐条确认数学含义是否等价）

### prop:scaling

```diff
@@ -3 +3 @@
-最终累计新增感染除以 $N$ 后亦不依赖 $N$。
+计算至无限时刻的累计新增感染除以 $N$ 后亦不依赖 $N$。
```

### thm:joint:cost-minimum

```diff
@@ -3 +3 @@
-在相应的控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中（不另加总时长、调整次数或控制变化率等约束），二次干预成本的最小值可以达到，且
+在相应的控制类 $\mathcal A(\eta)$ 或 $\mathcal A(\eta;c_{\min},q_{\rm cap})$ 中（不另加总时长、调整次数或控制变化率等约束），二次干预强度成本的最小值可以达到，且
```

### prop:joint:terminal-allocation

```diff
@@ -1 +1 @@
-采用默认权重 $w_c=1$、$w_q=2$，不考虑能力约束。
+设 $w_c,w_q>0$，不考虑能力约束。
@@ -11 +11 @@
-\frac{(c_0-c_c^*(S))/c_0}{1-S_c/S}&=\frac23,\\
+\frac{(c_0-c_c^*(S))/c_0}{1-S_c/S}&=\frac{w_q}{w_c+w_q},\\
@@ -13 +13 @@
-\frac{(q_c^*(S)-q_0)/(1-q_0)}{1-S_c/S}&=\frac13.
+\frac{(q_c^*(S)-q_0)/(1-q_0)}{1-S_c/S}&=\frac{w_c}{w_c+w_q}.
```

## 证明

有证明的陈述：旧稿 20 条，新稿 23 条；证明有变化 1 条。

- prop:scaling：汉字 101 → 105

```diff
@@ -13 +13 @@
-例如，二次成本的归一化表达为
+例如，二次干预强度成本的归一化表达为
```

