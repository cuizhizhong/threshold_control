# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 6 条，有变化 2 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:Itcum

```diff
@@ -4 +4 @@
-\item 统计至 $t_{\rm end}$ 的总累计新增感染为
+\item 总累计新增感染为
@@ -7 +7 @@
-\Itcum={}&\frac{\beta}{\beta+q_0(1-\beta)}(S_0-S^*+S_c-S_{\rm end})\\
+\Itcum(t_{\rm end})={}&\frac{\beta}{\beta+q_0(1-\beta)}(S_0-S^*+S_c-S_{\rm end})\\
```

### prop:threshold-tradeoff

```diff
@@ -11 +11 @@
-\item $\partial\Itcum/\partial\eta>0$，计算至无限时刻的总累计新增感染也随 $\eta$ 严格增加。
+\item $\partial\Itcum(t_{\rm end})/\partial\eta>0$，计算至无限时刻的总累计新增感染也随 $\eta$ 严格增加。
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 0 条。

