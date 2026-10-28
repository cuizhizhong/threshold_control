# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/flatten_curve_analysis_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex

带标签的陈述：旧稿 28 条，新稿 28 条；共同 28 条，其中未变化 26 条，有变化 2 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:joint:representation

```diff
@@ -22 +22 @@
-\item 选取满足式\eqref{eq:joint:contact-range}的逐点代表后，$t\uparrow t_2$ 时 $c(t)\to c_0$、$q(t)\to q_0$；
+\item 选取满足式\eqref{eq:joint:contact-range}的逐点代表后，$c$ 与 $q$ 在 $t_2$ 处的左极限分别为 $c_0$ 与 $q_0$；
```

### prop:joint:terminal-allocation

```diff
@@ -13 +13 @@
-\lim_{S\downarrow S_c}
+\lim_{S\to S_c^{+}}
@@ -15 +15 @@
-\lim_{S\downarrow S_c}
+\lim_{S\to S_c^{+}}
```

## 证明

有证明的陈述：旧稿 13 条，新稿 13 条；证明有变化 0 条。

