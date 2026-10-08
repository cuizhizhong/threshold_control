# 定理类陈述与证明的变化

- 旧稿：pre-rewrite-20261007:paper/sections/02_model.tex
- 新稿：paper/sections/02_model.tex

带标签的陈述：旧稿 2 条，新稿 3 条；共同 2 条，其中未变化 1 条，有变化 1 条。

只在新稿中（新增或改了首个标签）：eq:model:plateau-requirement

## 陈述有变化（逐条确认数学含义是否等价）

### prop:model:threshold-rationale

```diff
@@ -4,2 +4,2 @@
-\item 在首次加强干预之前采用 $(c_0,q_0)$ 的策略，若始终满足 $I\le\eta$，则首次加强干预的时刻不能晚于 $t_1$；
-常规轨迹在 $[0,t_1]$ 上满足该上限。
+\item 在首次加强干预之前采用 $(c_0,q_0)$ 的策略若始终满足 $I\le\eta$，则首次加强干预的时刻不能晚于 $t_1$；
+常规轨迹在 $[0,t_1]$ 上满足 $I\le\eta$。
@@ -11 +11 @@
-\item 从状态 $(S,\eta)$ 起恢复并保持 $(c_0,q_0)$，其后始终满足感染上限，当且仅当 $S\le S_c$。
+\item 从状态 $(S,\eta)$ 起恢复并保持 $(c_0,q_0)$，其后始终满足 $I\le\eta$，当且仅当 $S\le S_c$。
```

## 证明

有证明的陈述：旧稿 1 条，新稿 1 条；证明有变化 1 条。

- prop:model:positive：汉字 117 → 99
