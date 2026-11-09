# 定理类陈述与证明的变化

- 旧稿：a525dd5:paper/sections/03_single_control.tex
- 新稿：paper/sections/03_single_control.tex

带标签的陈述：旧稿 9 条，新稿 9 条；共同 9 条，其中未变化 8 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### thm:s1:inflection

```diff
@@ -4 +4 @@
-\item $q_c(t)$ 在 $(t_1,t_2)$ 内存在唯一拐点（下称内部拐点），当且仅当
+\item $q_c(t)$ 在 $(t_1,t_2)$ 内存在唯一拐点（下称内部拐点），当且仅当 $q_0<\qinf<q_{\max}$，等价地
@@ -6 +6 @@
-S_c<2\bar S<S^*,
+S_c<2\bar S<S^*;
@@ -8 +7,0 @@
-等价地，$1/2<(1-\beta)(1-q_0)<-W_{-1}(z_\eta)/2$；
@@ -13 +12 @@
-\qinf=1-\frac1{2(1-\beta)},
+q_c(t_{\rm inf})=\qinf;
@@ -15 +13,0 @@
-且 $q_0<\qinf<q_{\max}$；
```

## 证明

有证明的陈述：旧稿 5 条，新稿 5 条；证明有变化 1 条。

- thm:s1:inflection：汉字 141 → 134

```diff
@@ -11,3 +11,2 @@
-由式\eqref{eq:s1:barS}与\eqref{eq:s1:Sstar-lambert}，$2\bar S/S_c=2(1-\beta)(1-q_0)$，$S^*/S_c=-W_{-1}(z_\eta)$，即得等价形式。
-(ii) 将 $S=2\bar S$ 代入式\eqref{eq:s1:S-analytic}及\eqref{eq:s1:q-control}，即得时间和隔离比例。
-由于 $q_c(S)$ 关于 $S$ 严格增加且 $S_c<2\bar S<S^*$，有 $q_0=q_c(S_c)<\qinf<q_c(S^*)=q_{\max}$。
+由式\eqref{eq:s1:q-control}，$q_c(S)$ 关于 $S$ 严格增加，且 $q_c(S_c)=q_0$、$q_c(2\bar S)=\qinf$、$q_c(S^*)=q_{\max}$，所以式\eqref{eq:s1:inflection-condition}等价于 $q_0<\qinf<q_{\max}$。
+(ii) 将 $S=2\bar S$ 代入式\eqref{eq:s1:S-analytic}即得 $t_{\rm inf}$，代入式\eqref{eq:s1:q-control}即得 $q_c(t_{\rm inf})=\qinf$。
```

