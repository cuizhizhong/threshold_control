# 定理类陈述与证明的变化

- 旧稿：nr-base:paper/supplement_sections/S6_numerics.tex nr-base:paper/sections/04_joint_control.tex nr-base:paper/sections/03_single_control.tex
- 新稿：paper/supplement_sections/S7_return.tex paper/supplement_sections/S6_numerics.tex paper/sections/04_joint_control.tex paper/sections/03_single_control.tex

带标签的陈述：旧稿 20 条，新稿 24 条；共同 20 条，其中未变化 19 条，有变化 1 条。

只在新稿中（新增或改了首个标签）：lem:return:U、prop:return:final-size、cor:return:right-discontinuity、rem:release-at-exit

## 陈述有变化（逐条确认数学含义是否等价）

### prop:scaling

```diff
@@ -3 +3 @@
-最终累计新增感染除以 $N$ 后亦不依赖 $N$。
+计算至无限时刻的累计新增感染除以 $N$ 后亦不依赖 $N$。
```

## 证明

有证明的陈述：旧稿 15 条，新稿 18 条；证明有变化 1 条。

- prop:scaling：汉字 101 → 105

```diff
@@ -13 +13 @@
-例如，二次成本的归一化表达为
+例如，二次干预强度成本的归一化表达为
```

