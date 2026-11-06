# 定理类陈述与证明的变化

- 旧稿：2892ded:paper/flatten_curve_analysis_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex

带标签的陈述：旧稿 28 条，新稿 28 条；共同 28 条，其中未变化 27 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### prop:model:threshold-rationale

```diff
@@ -4 +4 @@
-\item 若一个策略在首次加强干预之前采用 $(c_0,q_0)$，且始终满足 $I\le\eta$，则它首次加强干预的时刻不晚于 $t_1$，而常规轨迹在 $[0,t_1]$ 上满足 $I\le\eta$；
+\item 常规轨迹在 $[0,t_1)$ 上满足 $I<\eta$，而 $\dot I(t_1)>0$，因此在 $t_1$ 之后继续采用 $(c_0,q_0)$ 会立即越过阈值；
```

## 证明

有证明的陈述：旧稿 13 条，新稿 13 条；证明有变化 0 条。

