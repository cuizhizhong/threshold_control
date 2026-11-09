# 定理类陈述与证明的变化

- 旧稿：7331333:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 9 条，新稿 9 条；共同 9 条，其中未变化 9 条，有变化 0 条。

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:inflection：汉字 134 → 135

```diff
@@ -11,2 +11,7 @@
-由式\eqref{eq:s1:q-control}，$q_c(S)$ 关于 $S$ 严格增加，且 $q_c(S_c)=q_0$、$q_c(2\bar S)=\qinf$、$q_c(S^*)=q_{\max}$，所以式\eqref{eq:s1:inflection-condition}等价于 $q_0<\qinf<q_{\max}$。
-(ii) 将 $S=2\bar S$ 代入式\eqref{eq:s1:S-analytic}即得 $t_{\rm inf}$，代入式\eqref{eq:s1:q-control}即得 $q_c(t_{\rm inf})=\qinf$。
+由式\eqref{eq:s1:q-control}与\eqref{eq:s1:barS}，
+\[
+q_c(2\bar S)=1-\frac{\gamma N}{2\beta c_0\bar S}=1-\frac{1}{2(1-\beta)}=\qinf.
+\]
+又 $q_c(S)$ 关于 $S$ 严格增加，且 $q_c(S_c)=q_0$、$q_c(S^*)=q_{\max}$，所以式\eqref{eq:s1:inflection-condition}等价于 $q_0<\qinf<q_{\max}$。
+(ii) 将 $S=2\bar S$ 代入式\eqref{eq:s1:S-analytic}即得 $t_{\rm inf}$；
+由 (i) 的证明，$q_c(t_{\rm inf})=q_c(2\bar S)=\qinf$。
```

