# 定理类陈述与证明的变化

- 旧稿：pre-capacity-cut-20261115:paper/sections/04_joint_control.tex
- 新稿：paper/sections/04_joint_control.tex

带标签的陈述：旧稿 6 条，新稿 3 条；共同 3 条，其中未变化 2 条，有变化 1 条。

只在旧稿中（新稿中找不到该标签的陈述，需说明去向）：cor:joint:feasibility、cor:joint:capped-comparison、cor:joint:single-endpoints

## 陈述有变化（逐条确认数学含义是否等价）

### cor:joint:whole-epidemic

```diff
@@ -12 +12,2 @@
-\item 设式\eqref{eq:joint:feasibility}成立，则在 $\mathcal A(\eta;c_{\min},q_{\max})$ 中，$c^{+}(S)$ 同时达到最短的控制时长、最早的清零时间和最少的全过程累计新增感染。
+\item 在 $\mathcal A(\eta)$ 中，仅隔离控制同时达到最短的控制时长、最早的清零时间和最少的总累计新增感染；
+仅减少接触同时达到最长的控制时长、最晚的清零时间和最多的总累计新增感染。
```

## 证明

有证明的陈述：旧稿 5 条，新稿 2 条；证明有变化 1 条。

旧稿有证明、新稿中未在其后找到证明（可能移至附录，需说明）：cor:joint:feasibility、cor:joint:capped-comparison、cor:joint:single-endpoints

- cor:joint:whole-epidemic：汉字 124 → 137

```diff
@@ -5 +5 @@
-(ii) 由推论~\ref{cor:joint:capped-comparison}，$c^{+}$ 的控制时长最短，再由 (i) 即得。
+(ii) 由定理~\ref{thm:joint:comparison}(i)，仅隔离控制的控制时长最短，仅减少接触的最长，再由 (i) 即得。
```

