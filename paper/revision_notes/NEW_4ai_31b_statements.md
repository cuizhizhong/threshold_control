# 定理类陈述与证明的变化

- 旧稿：92d26de:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 9 条，新稿 9 条；共同 9 条，其中未变化 7 条，有变化 2 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:qc-structure

```diff
@@ -23 +23 @@
-使 $I(t)\le\eta$ 对一切 $t\ge0$ 成立。
+使 $I(t)=\eta$ 对 $t_1\le t\le t_2$ 成立，且 $I(t)\le\eta$ 对一切 $t\ge0$ 成立。
```

### cor:s1:qc-structure

```diff
@@ -13 +13 @@
-\frac{\beta c_0(1-q_{\rm cap})S^*}{N}\le\gamma,
+\frac{\beta c_0(1-q_{\rm cap})S^*}{N}\le\gamma.
@@ -15 +14,0 @@
-且该条件成立时，能力约束不改变上述控制轨迹、控制时长及成本公式。
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 2 条。

- thm:s1:qc-structure：汉字 157 → 158

```diff
@@ -11 +11 @@
-由命题~\ref{prop:model:positive}中解的唯一性，该控制确实使 $I\equiv\eta$。
+由命题~\ref{prop:model:positive}中解的唯一性，该控制确实使 $[t_1,t_2]$ 上 $I\equiv\eta$。
```

- cor:s1:qc-structure：汉字 112 → 80

```diff
@@ -10 +9,0 @@
-该条件成立时，原控制满足能力约束，故控制轨迹、控制时长与成本公式都不变。
```

