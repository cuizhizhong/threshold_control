# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex HEAD:paper/appendices/A_proofs_sensitivity.tex HEAD:paper/supplement_sections/S2_single_control.tex
- 新稿：paper/sections/03_single_control.tex paper/appendices/A_proofs_sensitivity.tex paper/supplement_sections/S2_single_control.tex

带标签的陈述：旧稿 12 条，新稿 12 条；共同 12 条，其中未变化 11 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### prop:threshold-tradeoff

```diff
@@ -10 +10 @@
-\item 成本满足 $\partial J_q/\partial\eta<0$、$\partial J/\partial\eta<0$；
+\item 隔离的线性强度积分 $J_q$ 与二次干预强度成本 $J$ 满足 $\partial J_q/\partial\eta<0$、$\partial J/\partial\eta<0$；
```

## 证明

有证明的陈述：旧稿 9 条，新稿 9 条；证明有变化 1 条。

- cor:s1:qc-structure：汉字 69 → 66

```diff
@@ -2 +2 @@
-由链式法则与式\eqref{eq:s1:S-analytic}，沿控制轨迹
+再由式\eqref{eq:s1:S-analytic}与链式法则，得
```

