# 定理类陈述与证明的变化

- 旧稿：a5b7022:paper/flatten_curve_analysis_cn.tex a5b7022:paper/flatten_curve_supplement_cn.tex
- 新稿：paper/flatten_curve_analysis_cn.tex paper/flatten_curve_supplement_cn.tex

带标签的陈述：旧稿 35 条，新稿 40 条；共同 35 条，其中未变化 34 条，有变化 1 条。

只在新稿中（新增或改了首个标签）：thm:joint:cost-structure、cor:joint:capacity-clip、prop:joint:weight-monotone、prop:joint:duration-frontier、prop:sup:rhat

## 陈述有变化（逐条确认数学含义是否等价）

### rem:joint:duration-constraint

```diff
@@ -16 +16,2 @@
-这一充分条件不要求可达集凸，但不保证每个允许时长都有匹配的 $\kappa$。
+这一充分条件不要求可达集凸；
+下面的命题说明，最短与最长之间的每个时长都有匹配的 $\kappa$。
```

## 证明

有证明的陈述：旧稿 23 条，新稿 24 条；证明有变化 0 条。

