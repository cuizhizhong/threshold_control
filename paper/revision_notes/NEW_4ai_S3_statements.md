# 定理类陈述与证明的变化

- 旧稿：cf2b849:paper/supplement_sections/S3_inflection.tex
- 新稿：paper/supplement_sections/S3_inflection.tex

带标签的陈述：旧稿 1 条，新稿 1 条；共同 1 条，其中未变化 0 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### prop:s1:lambda-sensitivity

```diff
@@ -1 +1 @@
-设触发条件与 $S_c<2\bar S<S^*$ 成立，并固定其余参数，则
+设触发条件\eqref{eq:model:trigger}与内部拐点的存在条件\eqref{eq:s1:inflection-condition}成立，并固定其余参数，则
@@ -4 +4 @@
-\item 有
+\item 拐点的相对位置满足
```

## 证明

有证明的陈述：旧稿 1 条，新稿 1 条；证明有变化 1 条。

- prop:s1:lambda-sensitivity：汉字 91 → 100

```diff
@@ -22 +22 @@
-这些符号给出 (i) 的三个结论。
+代入上式，三种情形的分子分别为负、正、正，即得 (i)。
@@ -30,3 +30,3 @@
-令方括号为零得到驻点条件。
-两项异号本身不足以说明导数能取两种符号；
-第~\ref{app:lambda}~节给出两个满足全部条件的参数点，并分别证明其导数为正和负。
+令方括号为零即得驻点条件。
+方括号中两项异号，导数的符号取决于二者的大小；
+第~\ref{app:lambda}~节构造两个满足全部条件的参数点，分别证明导数为正和为负。
```

