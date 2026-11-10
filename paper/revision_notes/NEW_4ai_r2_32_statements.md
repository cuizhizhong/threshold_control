# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 7 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:inflection

```diff
@@ -8 +8 @@
-\item 内部拐点存在时，
+\item 若内部拐点存在，记其时刻为 $t_{\rm inf}$，则
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:inflection：汉字 135 → 139

```diff
@@ -16,2 +16,2 @@
-(ii) 将 $S=2\bar S$ 代入式\eqref{eq:s1:S-analytic}即得 $t_{\rm inf}$；
-由 (i) 的证明，$q_c(t_{\rm inf})=q_c(2\bar S)=\qinf$。
+(ii) 由 (i)，$S(t_{\rm inf})=2\bar S$。
+代入式\eqref{eq:s1:S-analytic}即得拐点时刻，代入 $q_c(S)$ 即得 $q_c(t_{\rm inf})=\qinf$。
```

