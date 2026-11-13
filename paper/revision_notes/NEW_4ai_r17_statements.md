# 定理类陈述与证明的变化

- 旧稿：HEAD:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 8 条，新稿 8 条；共同 8 条，其中未变化 8 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 2 条。

- cor:s1:qc-structure：汉字 32 → 32

```diff
@@ -3 +3 @@
-\begin{equation}
+\[
@@ -6 +6 @@
-\end{equation}
+\]
```

- thm:s1:inflection：汉字 122 → 118

```diff
@@ -10 +10 @@
-(i) 因此 $q_c(t)$ 在 $(t_1,t_2)$ 内有拐点，当且仅当 $\nu$ 在其中越过 $1/2$，即 $\bar S/S^*<1/2<\bar S/S_c$，亦即式\eqref{eq:s1:inflection-condition}；
+(i) 因此 $q_c(t)$ 在 $(t_1,t_2)$ 内有拐点，当且仅当 $\nu$ 在其中越过 $1/2$，即 $\nu(t_1)<1/2<\nu(t_2)$；
@@ -12 +12,2 @@
-$q_c$ 关于 $S$ 严格增加，且 $q_c(2\bar S)=\qinf$、$q_c(S_c)=q_0$、$q_c(S^*)=q_1$，故式\eqref{eq:s1:inflection-condition}等价于 $q_0<\qinf<q_1$。
+由 $\nu=(1-\beta)(1-q_c)$，这等价于 $q_0<\qinf<q_1$；
+由 $\nu=\bar S/S$，又等价于式\eqref{eq:s1:inflection-condition}。
```

