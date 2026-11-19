# 定理类陈述与证明的变化

- 旧稿：8a8de31:paper/flatten_curve_supplement_cn.tex 8a8de31:paper/flatten_curve_analysis_cn.tex
- 新稿：paper/flatten_curve_supplement_cn.tex paper/flatten_curve_analysis_cn.tex

带标签的陈述：旧稿 32 条，新稿 32 条；共同 32 条，其中未变化 31 条，有变化 1 条。

## 陈述有变化（逐条确认数学含义是否等价）

### prop:sup:jump

```diff
@@ -10 +10 @@
-\item 若 $r\ge\hat r$，记 $\zeta_0$ 为仅隔离控制取全局最小的最小状态，则 $\zeta_0\ge\max\{\zeta_{\rm sw},\,b+r(1-b)\}$，且 $\zeta_0=\zeta_{\rm sw}$ 当且仅当 $r=\hat r$；
+\item 若 $r\ge\hat r$，记 $\zeta_0$ 为使仅隔离控制成为全局最小点的最小 $\zeta$，则 $\zeta_0\ge\max\{\zeta_{\rm sw},\,b+r(1-b)\}$，且 $\zeta_0=\zeta_{\rm sw}$ 当且仅当 $r=\hat r$；
```

## 证明

有证明的陈述：旧稿 20 条，新稿 20 条；证明有变化 2 条。

- prop:contact-effects：汉字 226 → 228

```diff
@@ -6 +6 @@
-在式\eqref{eq:s1:t1}中，前置系数 $1/\beta_1^0$ 随 $c_0$ 下降；
+在式\eqref{eq:s1:t1}中，积分前的系数 $1/\beta_1^0$ 随 $c_0$ 下降；
@@ -16 +16 @@
-由式\eqref{eq:s1:t2}，$\Delta t=[N/(c_0\eta)]\ln[(S^*-\bar S)/(S_c-\bar S)]$，前置系数不含 $\beta,q_0$。
+由式\eqref{eq:s1:t2}，$\Delta t=[N/(c_0\eta)]\ln[(S^*-\bar S)/(S_c-\bar S)]$，其中系数 $N/(c_0\eta)$ 不含 $\beta,q_0$。
```

- prop:sup:rhat：汉字 129 → 140

```diff
@@ -10 +10 @@
-若 $r=\hat r$，方括号只在 $p=a$ 处为零，$c_0$ 与 $p=a$ 并列，$p=a$ 对应 $c=c_0S_c/(S_{\rm sw}-S_c)$。
+若 $r=\hat r$，方括号只在 $p=a$ 处为零，此时 $p=\zeta_{\rm sw}$ 与 $p=a$ 是两个全局最小点，分别对应 $c=c_0$ 与 $c=c_0S_c/(S_{\rm sw}-S_c)$。
```

